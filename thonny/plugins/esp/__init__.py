import logging
import os
import signal
import subprocess
import threading
import time
import tkinter as tk
from collections import OrderedDict
from tkinter import messagebox, ttk
from typing import Optional

from thonny import get_runner, ui_utils
from thonny.languages import tr
from thonny.misc_utils import (
    running_on_windows,
)
from thonny.plugins.micropython import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
    add_micropython_backend,
    list_serial_ports_with_descriptions,
)
from thonny.running import get_interpreter_for_subprocess
from thonny.workdlg import WorkDialog

logger = logging.getLogger(__name__)


class ESPProxy(BareMetalMicroPythonProxy):
    @classmethod
    def _is_potential_port(cls, p):
        # They have UART adapter
        return (
            (p.vid, p.pid) in cls.get_known_usb_vids_pids()
            or (p.vid, None) in cls.get_known_usb_vids_pids()
            or p.description in cls.get_known_port_descriptions()
            or cls.should_consider_unknown_devices()
            and (p.vid, p.pid) not in cls.get_vids_pids_to_avoid()
            and (
                ("USB" in p.description and "serial" in p.description.lower())
                or "UART" in p.description
                or "DAPLink" in p.description
                or "STLink" in p.description
            )
            and getattr(p, "manufacturer", "") != "MicroPython"  # adapter can't have this?
            and "python" not in p.description.lower()
        )

    @classmethod
    def get_vids_pids_to_avoid(self):
        # micro:bit
        return {(0x0D28, 0x0204)}


class ESP8266Proxy(ESPProxy):
    description = "MicroPython on ESP8266"
    config_page_constructor = "ESP8266"

    @classmethod
    def get_known_usb_vids_pids(cls):
        return cls.get_uart_adapter_vids_pids()

    def _get_api_stubs_path(self):
        return os.path.join(os.path.dirname(__file__), "esp8266_api_stubs")


class ESP32Proxy(ESPProxy):
    @classmethod
    def get_known_usb_vids_pids(cls):
        return cls.get_uart_adapter_vids_pids()

    def _get_api_stubs_path(self):
        return os.path.join(os.path.dirname(__file__), "esp32_api_stubs")


class ESPConfigPage(BareMetalMicroPythonConfigPage):
    def __init__(self, master, chip, firmware_start_address):
        self._chip = chip
        self._firmware_start_address = firmware_start_address
        super().__init__(master)

    def _has_flashing_dialog(self):
        return True

    def _open_flashing_dialog(self):
        dlg = ESPFlashingDialog(self.winfo_toplevel(), self._chip, self._firmware_start_address)
        ui_utils.show_dialog(dlg)

    @property
    def allow_webrepl(self):
        return True


class ESP8266ConfigPage(ESPConfigPage):
    def __init__(self, master):
        super().__init__(master, "esp8266", "0x0")


class ESP32ConfigPage(ESPConfigPage):
    def __init__(self, master):
        super().__init__(master, "esp32", "0x1000")


class ESPFlashingDialog(WorkDialog):
    def __init__(self, master, chip, start_address):
        self._chip = chip
        self._start_address = start_address

        super().__init__(master)

        self._esptool_command = self._get_esptool_command()
        if not self._esptool_command:
            messagebox.showerror(
                "Can't find esptool",
                "esptool not found.\n" + "Install it via 'Tools => Manage plug-ins'\n" + "or "
                "using your OP-system package manager.",
                master=self,
            )
            self.close()

    def get_title(self):
        return "%s firmware installer" % self._chip.upper()

    def get_instructions(self) -> Optional[str]:
        return (
            "This dialog allows installing or updating firmware on %s using the most common settings.\n"
            % self._chip.upper()
            + "If you need to set other options, then please use 'esptool' on the command line.\n\n"
            + "Note that there are many variants of MicroPython for ESP devices. If the firmware provided\n"
            + "at micropython.org/download doesn't work for your device, then there may exist better\n"
            + "alternatives -- look around in your device's documentation or at MicroPython forum."
        )

    def is_ready_for_work(self):
        return self._port_desc_variable.get() and self._firmware_entry.get()

    def get_action_text_max_length(self):
        return 35

    def populate_main_frame(self):
        epadx = self.get_padding()
        ipadx = self.get_internal_padding()
        epady = epadx
        ipady = ipadx

        # Port
        port_label = ttk.Label(self.main_frame, text="Port")
        port_label.grid(row=1, column=1, sticky="w", padx=(epadx, 0), pady=(epady, 0))

        self._port_desc_variable = tk.StringVar(value="")
        self._port_combo = ttk.Combobox(
            self.main_frame, exportselection=False, textvariable=self._port_desc_variable, values=[]
        )
        self._port_combo.state(["!disabled", "readonly"])
        self._port_combo.grid(row=1, column=2, sticky="nsew", padx=ipadx, pady=(epady, 0))

        port_reload_button = ttk.Button(self.main_frame, text="Reload", command=self._reload_ports)
        port_reload_button.grid(row=1, column=3, sticky="ew", padx=(0, epadx), pady=(epady, 0))

        # Firmware
        firmware_label = ttk.Label(self.main_frame, text="Firmware")
        firmware_label.grid(row=2, column=1, sticky="w", padx=(epadx, 0), pady=(ipady, 0))

        self._firmware_entry = ttk.Entry(self.main_frame, width=55)
        self._firmware_entry.grid(row=2, column=2, sticky="nsew", padx=ipadx, pady=(ipady, 0))

        browse_button = ttk.Button(self.main_frame, text="Browse...", command=self._browse)
        browse_button.grid(row=2, column=3, sticky="we", padx=(0, epadx), pady=(ipady, 0))

        # FLASH_MODE
        self._flashmode = tk.StringVar(None, "keep")
        flashmode_group = ttk.Labelframe(self.main_frame, text="Flash mode")
        flashmode_group.grid(
            row=4, column=1, columnspan=2, sticky="w", padx=(epadx, 0), pady=(ipady * 2, 0)
        )

        self._flashmode_keep_radiobutton = ttk.Radiobutton(
            flashmode_group, text="From image file (keep)", variable=self._flashmode, value="keep"
        )
        self._flashmode_keep_radiobutton.grid(row=0, column=0, sticky="w")

        # self._flashmode_variable.value=False
        self._flashmode_qio_radiobutton = ttk.Radiobutton(
            flashmode_group, text="Quad I/O (qio)", variable=self._flashmode, value="qio"
        )
        self._flashmode_qio_radiobutton.grid(row=0, column=1, sticky="w")

        self._flashmode_dio_radiobutton = ttk.Radiobutton(
            flashmode_group, text="Dual I/O (dio)", variable=self._flashmode, value="dio"
        )
        self._flashmode_dio_radiobutton.grid(row=1, column=0, sticky="w")

        self._flashmode_dout_radiobutton = ttk.Radiobutton(
            flashmode_group, text="Dual Output (dout)", variable=self._flashmode, value="dout"
        )
        self._flashmode_dout_radiobutton.grid(row=1, column=1, sticky="w")

        # Erase
        self._erase_variable = tk.BooleanVar(value=True)
        self._erase_checkbutton = ttk.Checkbutton(
            self.main_frame, text="Erase flash before installing", variable=self._erase_variable
        )
        self._erase_checkbutton.grid(
            row=6, column=1, columnspan=2, sticky="w", padx=(epadx, 0), pady=(ipady, epady)
        )

        self._reload_ports()

    def _get_esptool_command(self):
        try:
            import esptool

            return [get_interpreter_for_subprocess(), "-u", "-m", "esptool"]
        except ImportError:
            import shutil

            result = shutil.which("esptool")
            if result:
                return [result]
            else:
                result = shutil.which("esptool.py")
                if result:
                    return [result]
                else:
                    return None

    def _reload_ports(self):
        pairs = list_serial_ports_with_descriptions()
        self._ports_by_desc = OrderedDict(pairs)
        self._port_combo.configure(values=list(self._ports_by_desc.keys()))

    def _browse(self):
        initialdir = os.path.normpath(os.path.expanduser("~/Downloads"))
        if not os.path.isdir(initialdir):
            initialdir = None

        path = ui_utils.askopenfilename(
            filetypes=[("bin-files", ".bin"), ("all files", ".*")],
            parent=self.winfo_toplevel(),
            initialdir=initialdir,
        )
        if path:
            self._firmware_entry.delete(0, "end")
            self._firmware_entry.insert(0, path)

    def _check_connection(self, port):
        # wait a bit in case existing connection was just closed
        time.sleep(1.5)

        # Maybe another program is connected
        # or the user doesn't have sufficient permissions?
        try:
            import serial

            conn = serial.Serial(port)
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Can't connect", str(e), master=self)
            return False

    def start_work(self):
        port = self._ports_by_desc[self._port_desc_variable.get()]
        if not self._port_desc_variable.get():
            messagebox.showerror("Select port", "Please select port", parent=self)
            return False

        firmware_path = self._firmware_entry.get()
        if not os.path.exists(firmware_path):
            messagebox.showerror(
                "Bad firmware path", "Can't find firmware, please check path", master=self
            )
            return False

        flash_mode = self._flashmode.get()
        erase_flash = self._erase_variable.get()

        proxy = get_runner().get_backend_proxy()
        port_was_used_in_thonny = (
            isinstance(proxy, BareMetalMicroPythonProxy) and proxy._port == port
        )
        if port_was_used_in_thonny:
            proxy.disconnect()

        commands = []
        threading.Thread(
            target=self.work_in_thread,
            daemon=True,
            args=[port, firmware_path, flash_mode, erase_flash, port_was_used_in_thonny],
        ).start()

    def work_in_thread(self, port, firmware_path, flash_mode, erase_flash, port_was_used_in_thonny):
        if port_was_used_in_thonny:
            time.sleep(1.5)

        erase_command = self._esptool_command + [
            "--chip",
            self._chip,
            "--port",
            port,
            "erase_flash",
        ]

        write_command = self._esptool_command + [
            "--chip",
            self._chip,
            "--port",
            port,
            "write_flash",
            "--flash_mode",
            flash_mode,
            "--flash_size",  # default changed in esptool 3.0
            "detect",
            self._start_address,
            firmware_path,
        ]

        if not self._check_connection(port):
            self.set_action_text("Problem")
            self.append_text("Could not connect to port\n")
            self.report_done(False)
            return

        if erase_flash:
            self.set_action_text("Erasing flash")
            self.append_text(subprocess.list2cmdline(erase_command) + "\n")
            self._proc = self._create_subprocess(erase_command)
            while True:
                line = self._proc.stdout.readline()
                if not line:
                    break
                self.append_text(line)
                self.set_action_text_smart(line)
            returncode = self._proc.wait()
            if returncode:
                self.set_action_text("Error")
                self.append_text("\nErase command returned with error code %s" % returncode)
                self.report_done(False)
                return
            else:
                self.append_text("Erasing done\n------------------------------------\n\n")

        self.set_action_text("Writing firmware")
        self.append_text(subprocess.list2cmdline(write_command) + "\n")
        self._proc = self._create_subprocess(write_command)
        while True:
            line = self._proc.stdout.readline()
            if not line:
                break
            self.append_text(line)
            self.set_action_text_smart(line)
        returncode = self._proc.wait()
        if returncode:
            self.set_action_text("Error")
            self.append_text("\nWrite command returned with error code %s" % returncode)
        else:
            self.set_action_text("Done!")
            self.append_text("Done!")
        self.report_done(returncode == 0)

    def _create_subprocess(self, cmd) -> subprocess.Popen:
        return subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )

    def get_ok_text(self):
        return tr("Install")

    def cancel_work(self):
        super().cancel_work()
        # try gently first
        try:
            try:
                if running_on_windows():
                    os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # pylint: disable=no-member
                else:
                    os.kill(self._proc.pid, signal.SIGINT)

                self._proc.wait(2)
            except subprocess.TimeoutExpired:
                if self._proc.poll() is None:
                    # now let's be more concrete
                    self._proc.kill()
        except OSError as e:
            messagebox.showerror("Error", "Could not kill subprocess: " + str(e), master=self)
            logger.error("Could not kill subprocess", exc_info=e)


def load_plugin():
    add_micropython_backend(
        "ESP32",
        ESP32Proxy,
        "MicroPython (ESP32)",
        ESP32ConfigPage,
        sort_key="35",
    )
    add_micropython_backend(
        "ESP8266", ESP8266Proxy, "MicroPython (ESP8266)", ESP8266ConfigPage, sort_key="36"
    )
