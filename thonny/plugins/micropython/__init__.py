import ast
import logging
import io
import os
import platform
import queue
import re
import subprocess
import sys
import textwrap
import threading
import time
import tokenize
import traceback
import webbrowser
from queue import Queue
from textwrap import dedent
from time import sleep
from tkinter import ttk, messagebox
from thonny.ui_utils import askopenfilename, create_url_label
from typing import Optional

import jedi
import serial.tools.list_ports
from serial import SerialException

from thonny import common, get_runner, get_shell, get_workbench, running
from thonny.common import (
    BackendEvent,
    InlineResponse,
    MessageFromBackend,
    ToplevelCommand,
    ToplevelResponse,
    InterruptCommand,
    EOFCommand,
)
from thonny.config_ui import ConfigurationPage
from thonny.misc_utils import find_volumes_by_name, TimeHelper
from thonny.plugins.backend_config_page import BackendDetailsConfigPage
from thonny.running import BackendProxy, SubprocessProxy
from thonny.ui_utils import SubprocessDialog, create_string_var, show_dialog

DEFAULT_WEBREPL_URL = "ws://192.168.4.1:8266/"


class MicroPythonProxy(SubprocessProxy):
    def __init__(self, clean):
        self._port = get_workbench().get_option(self.backend_name + ".port")
        self._clean_start = clean

        if self._port == "auto":
            potential = self._detect_potential_ports()
            if len(potential) == 1:
                self._port = potential[0][0]
            else:
                self._port = None
                message = dedent(
                    """\
                    Couldn't find the device automatically. 
                    Check the connection (making sure the device is not in bootloader mode)
                    or choose "Tools → Options → Backend" to select the port manually."""
                )

                if len(potential) > 1:
                    _, descriptions = zip(*potential)
                    message += "\n\nLikely candidates are:\n * " + "\n * ".join(descriptions)

                self._show_error(message)

        super().__init__(clean, running.get_frontend_python())

    def _get_launcher_with_args(self):
        import thonny.plugins.micropython.backend

        return [
            thonny.plugins.micropython.backend.__file__,
            "--clean",
            str(self._clean_start),
            "--port",
            str(self._port),
            "--api_stubs_path",
            self._get_api_stubs_path(),
        ]

    def interrupt(self):
        self._send_msg(InterruptCommand())
        """
        # For some reason following kills the backend and KeyboardInterrupt can't be caught 
        if self._proc is not None and self._proc.poll() is None:
            if running_on_windows():
                try:
                    os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # @UndefinedVariable
                except Exception:
                    logging.exception("Could not interrupt backend process")
            else:
                self._proc.send_signal(signal.SIGINT)
        """

    def _soft_reboot_and_run_main(self):
        self._send_msg(EOFCommand())

    def _clear_environment(self):
        "TODO:"

    def _detect_potential_ports(self):
        all_ports = list_serial_ports()
        """
        for p in all_ports:
            print(p.description,
                  p.device,
                  None if p.vid is None else hex(p.vid),
                  None if p.pid is None else hex(p.pid),
                  )
        """
        return [
            (p.device, p.description)
            for p in all_ports
            if (p.vid, p.pid) in self.known_usb_vids_pids
            or p.description in self.known_port_descriptions
            or ("USB" in p.description and "serial" in p.description.lower())
            or "UART" in p.description
            or "DAPLink" in p.description
        ]

    @property
    def known_usb_vids_pids(self):
        """Return set of pairs of USB device VID, PID"""
        return set()

    @property
    def known_port_descriptions(self):
        return set()

    def _get_api_stubs_path(self):
        import inspect

        return os.path.join(os.path.dirname(inspect.getfile(self.__class__)), "api_stubs")

    def has_own_filesystem(self):
        return self._proc is not None

    def uses_local_filesystem(self):
        return False

    def can_do_file_operations(self):
        return self._proc is not None and get_runner().is_waiting_toplevel_command()

    def supports_directories(self):
        return self._cwd is not None

    def is_connected(self):
        return self._proc is not None

    def is_functional(self):
        return self.is_connected()

    def _show_error(self, text):
        get_shell().print_error("\n" + text + "\n")

    def disconnect(self):
        self.destroy()

    def get_node_label(self):
        if "CircuitPython" in self._welcome_text:
            return _("CircuitPython device")
        elif "micro:bit" in self._welcome_text.lower():
            return "micro:bit"
        else:
            return _("MicroPython device")


class MicroPythonConfigPage(BackendDetailsConfigPage):
    backend_name = None  # Will be overwritten on Workbench.add_backend

    def __init__(self, master):
        super().__init__(master)
        intro_text = (
            _("Connect your device to the computer and select corresponding port below")
            + "\n"
            + "("
            + _('look for your device name, "USB Serial" or "UART"')
            + ").\n"
            + _("If you can't find it, you may need to install proper USB driver first.")
        )
        if self.allow_webrepl:
            intro_text = (
                ("Connecting via USB cable:")
                + "\n"
                + intro_text
                + "\n\n"
                + ("Connecting via WebREPL protocol:")
                + "\n"
                + (
                    "If your device supports WebREPL, first connect via serial, make sure WebREPL is enabled\n"
                    + "(import webrepl_setup), connect your computer and device to same network and select < WebREPL > below"
                )
            )

        intro_label = ttk.Label(self, text=intro_text)
        intro_label.grid(row=0, column=0, sticky="nw")

        driver_url = self._get_usb_driver_url()
        if driver_url:
            driver_url_label = create_url_label(self, driver_url)
            driver_url_label.grid(row=1, column=0, sticky="nw")

        port_label = ttk.Label(self, text="Port or WebREPL" if self.allow_webrepl else _("Port"))
        port_label.grid(row=3, column=0, sticky="nw", pady=(10, 0))

        self._ports_by_desc = {
            p.description
            if p.device in p.description
            else p.description + " (" + p.device + ")": p.device
            for p in list_serial_ports()
        }
        self._ports_by_desc["< " + _("Try to detect port automatically") + " >"] = "auto"

        self._WEBREPL_OPTION_DESC = "< WebREPL >"
        if self.allow_webrepl:
            self._ports_by_desc[self._WEBREPL_OPTION_DESC] = "webrepl"

        def port_order(p):
            _, name = p
            if name is None:
                return ""
            elif name.startswith("COM") and len(name) == 4:
                # Make one-digit COM ports go before COM10
                return name.replace("COM", "COM0")
            else:
                return name

        # order by port, auto first
        port_descriptions = [key for key, _ in sorted(self._ports_by_desc.items(), key=port_order)]

        self._port_desc_variable = create_string_var(
            self.get_current_port_desc(), self._on_change_port
        )
        self._port_combo = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=self._port_desc_variable,
            values=port_descriptions,
        )
        self._port_combo.state(["!disabled", "readonly"])

        self._port_combo.grid(row=4, column=0, sticky="new")
        self.columnconfigure(0, weight=1)

        if self.allow_webrepl:
            self._init_webrepl_frame()

        self._on_change_port()

    def _init_webrepl_frame(self):
        self._webrepl_frame = ttk.Frame(self)

        self._webrepl_url_var = create_string_var(DEFAULT_WEBREPL_URL)
        url_label = ttk.Label(self._webrepl_frame, text="URL (eg. %s)" % DEFAULT_WEBREPL_URL)
        url_label.grid(row=0, column=0, sticky="nw", pady=(10, 0))
        url_entry = ttk.Entry(self._webrepl_frame, textvariable=self._webrepl_url_var, width=24)
        url_entry.grid(row=1, column=0, sticky="nw")

        self._webrepl_password_var = create_string_var(
            get_workbench().get_option(self.backend_name + ".webrepl_password")
        )
        pw_label = ttk.Label(
            self._webrepl_frame, text="Password (the one specified with `import webrepl_setup`)"
        )
        pw_label.grid(row=2, column=0, sticky="nw", pady=(10, 0))
        pw_entry = ttk.Entry(self._webrepl_frame, textvariable=self._webrepl_password_var, width=9)
        pw_entry.grid(row=3, column=0, sticky="nw")

    def get_current_port_desc(self):
        name = get_workbench().get_option(self.backend_name + ".port")
        for desc in self._ports_by_desc:
            if self._ports_by_desc[desc] == name:
                return desc

        return ""

    def is_modified(self):
        return (
            self._port_desc_variable.modified  # pylint: disable=no-member
            or self.allow_webrepl
            and self._webrepl_password_var.modified  # pylint: disable=no-member
            or self.allow_webrepl
            and self._webrepl_url_var.modified
        )  # pylint: disable=no-member

    def should_restart(self):
        return self.is_modified()

    def apply(self):
        if not self.is_modified():
            return

        else:
            port_desc = self._port_desc_variable.get()
            port_name = self._ports_by_desc[port_desc]
            get_workbench().set_option(self.backend_name + ".port", port_name)
            if self.allow_webrepl:
                get_workbench().set_option(
                    self.backend_name + ".webrepl_url", self._webrepl_url_var.get()
                )
                get_workbench().set_option(
                    self.backend_name + ".webrepl_password", self._webrepl_password_var.get()
                )

    def _on_change_port(self, *args):
        if self._port_desc_variable.get() == self._WEBREPL_OPTION_DESC:
            self._webrepl_frame.grid(row=6, column=0, sticky="nwe")
        elif self.allow_webrepl and self._webrepl_frame.winfo_ismapped():
            self._webrepl_frame.grid_forget()

    def _get_usb_driver_url(self):
        return None

    @property
    def allow_webrepl(self):
        return False


class GenericMicroPythonProxy(MicroPythonProxy):
    @property
    def known_usb_vids_pids(self):
        """Return set of pairs of USB device (VID, PID)"""
        return {
            # Generic MicroPython Board, see http://pid.codes/org/MicroPython/
            (0x1209, 0xADDA)
        }


class GenericMicroPythonConfigPage(MicroPythonConfigPage):
    @property
    def allow_webrepl(self):
        return False


def list_serial_ports():
    # serial.tools.list_ports.comports() can be too slow
    # because os.path.islink can be too slow (https://github.com/pyserial/pyserial/pull/303)
    # Workarond: temporally patch os.path.islink
    try:
        old_islink = os.path.islink
        if platform.system() == "Windows":
            os.path.islink = lambda _: False
        return list(serial.tools.list_ports.comports())
    finally:
        os.path.islink = old_islink


def add_micropython_backend(name, proxy_class, description, config_page):
    get_workbench().set_default(name + ".port", "auto")
    get_workbench().set_default(name + ".webrepl_url", DEFAULT_WEBREPL_URL)
    get_workbench().set_default(name + ".webrepl_password", "")
    get_workbench().add_backend(name, proxy_class, description, config_page)


def load_plugin():
    add_micropython_backend(
        "GenericMicroPython",
        GenericMicroPythonProxy,
        _("MicroPython (generic)"),
        GenericMicroPythonConfigPage,
    )

    def explain_deprecation():
        messagebox.showinfo(
            "Moved commands",
            dedent(
                """
            MicroPython commands have been moved or replaced:
            
            * "Select device"
                    * Moved into "Run" menu as "Select interpreter"
            * "Upload current script as main script"
            * "Upload current script as boot script"
            * "Upload current script with current name"
                    * use "File => Save copy..."
            * "Show device's main script"
            * "Show device's boot script"
                    * Double-click in Files view (Show => Files)
            * "Upload ____ firmware"
                    * Moved into "Tools" menu
            * "Soft reboot"
                    * Moved into "Run" menu as "Send EOF / Soft reboot"
            " "Close serial connection"
                    * Moved into "Run" menu as "Disconnect"
        """
            ),
        )

    get_workbench().add_command(
        "devicedeprecation",
        "tempdevice",
        "Where are all the commands?",
        explain_deprecation,
        group=1,
    )
