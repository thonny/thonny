import logging
import os
import platform
import shutil
import sys
from textwrap import dedent
from tkinter import messagebox, ttk
from typing import Optional

from thonny import common, get_runner, get_shell, get_workbench, running, ui_utils
from thonny.common import (
    CommandToBackend,
    EOFCommand,
    ImmediateCommand,
    InlineCommand,
)
from thonny.languages import tr
from thonny.plugins.backend_config_page import (
    BackendDetailsConfigPage,
    BaseSshProxyConfigPage,
    get_ssh_password,
)
from thonny.running import SubprocessProxy
from thonny.ui_utils import (
    create_string_var,
    create_url_label,
)

DEFAULT_WEBREPL_URL = "ws://192.168.4.1:8266/"

VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND = set()


class MicroPythonProxy(SubprocessProxy):
    def __init__(self, clean):
        self._lib_dirs = []
        super().__init__(clean, running.get_interpreter_for_subprocess())

    def get_pip_gui_class(self):
        from thonny.plugins.micropython.pip_gui import MicroPythonPipDialog

        return MicroPythonPipDialog

    def get_pip_target_dir(self) -> Optional[str]:

        lib_dirs = self.get_lib_dirs()
        if not lib_dirs:
            return None

        for path in lib_dirs:
            if path.startswith("/home/"):
                return path

        for path in ["/lib", "/flash/lib"]:
            if path in lib_dirs:
                return path

        return lib_dirs[0]

    def get_lib_dirs(self):
        return self._lib_dirs

    def _store_state_info(self, msg):
        super(MicroPythonProxy, self)._store_state_info(msg)
        if "lib_dirs" in msg:
            self._lib_dirs = msg["lib_dirs"]

    def _get_time_args(self):
        result = {
            "sync_time": get_workbench().get_option(self.backend_name + ".sync_time", False),
            "validate_time": get_workbench().get_option(
                self.backend_name + ".validate_time", False
            ),
        }
        return result


class BareMetalMicroPythonProxy(MicroPythonProxy):
    def __init__(self, clean):
        self._port = get_workbench().get_option(self.backend_name + ".port")
        self._have_stored_pidwid = False
        self._clean_start = clean
        self._fix_port()

        super().__init__(clean)

        # Following is required for compatibility with older MP plugins (ESP)
        # TODO: remove it later
        self.micropython_upload_enabled = False

    def _fix_port(self):
        if self._port == "webrepl":
            return

        elif self._port == "auto":
            potential = self._detect_potential_ports()
            if len(potential) == 1:
                self._port = potential[0][0]
            else:
                if not potential and self.device_is_present_in_bootloader_mode():
                    if self._propose_install_firmware():
                        print("POSITIVE")
                        return self._fix_port()

                self._port = None
                message = dedent(
                    """\
                    Couldn't find the device automatically. 
                    Check the connection (making sure the device is not in bootloader mode) or choose
                    "Configure interpreter" in the interpreter menu (bottom-right corner of the window)
                    to select specific port or another interpreter."""
                )

                if len(potential) > 1:
                    _, descriptions = zip(*potential)
                    message += "\n\nLikely candidates are:\n * " + "\n * ".join(descriptions)

                self._show_error(message)
        elif not port_exists(self._port):
            if self.device_is_present_in_bootloader_mode():
                self._port = None
                self._propose_install_firmware()

    def _propose_install_firmware(self):
        """Subclass may show firmware installation dialog and return True if installation succeeds"""
        self._show_error(
            "Your device seems to be in bootloader mode.\n"
            "In this mode you can install or upgrade MicroPython firmware.\n\n"
            "If your device already has MicroPython, then you can start using it after you put it into normal mode."
        )

        return False

    def _start_background_process(self, clean=None, extra_args=[]):
        if self._port is None:
            return

        super()._start_background_process(clean=clean, extra_args=extra_args)

    def _get_launcher_with_args(self):
        import thonny.plugins.micropython.bare_metal_backend

        args = {
            "clean": self._clean_start,
            "port": self._port,
            "dtr": get_workbench().get_option(self.backend_name + ".dtr"),
            "rts": get_workbench().get_option(self.backend_name + ".rts"),
            "submit_mode": get_workbench().get_option(self.backend_name + ".submit_mode"),
            "api_stubs_path": self._get_api_stubs_path(),
            "write_block_size": self._get_write_block_size(),
            "write_block_delay": self._get_write_block_delay(),
            "proxy_class": self.__class__.__name__,
        }
        if self._port == "webrepl":
            args["url"] = get_workbench().get_option(self.backend_name + ".webrepl_url")
            args["password"] = get_workbench().get_option(self.backend_name + ".webrepl_password")

        args.update(self._get_time_args())

        cmd = [
            thonny.plugins.micropython.bare_metal_backend.__file__,
            repr(args),
        ]

        return cmd

    def _get_write_block_size(self):
        return get_workbench().get_option(self.backend_name + ".write_block_size")

    def _get_write_block_delay(self):
        return get_workbench().get_option(self.backend_name + ".write_block_delay")

    def interrupt(self):
        # Don't interrupt local process, but direct it to device
        self._send_msg(ImmediateCommand("interrupt"))

    def send_command(self, cmd: CommandToBackend) -> Optional[str]:
        if isinstance(cmd, EOFCommand):
            get_shell().restart()  # Runner doesn't notice restart

        return super().send_command(cmd)

    def _clear_environment(self):
        "TODO:"

    @classmethod
    def _detect_potential_ports(cls):
        all_ports = list_serial_ports()
        """
        for p in all_ports:
            print(vars(p))
        """
        return [(p.device, p.description) for p in all_ports if cls._is_potential_port(p)]

    @classmethod
    def _is_potential_port(cls, p):
        return (
            (p.vid, p.pid) in cls.get_known_usb_vids_pids()
            or (p.vid, None) in cls.get_known_usb_vids_pids()
            or p.description in cls.get_known_port_descriptions()
            or cls.should_consider_unknown_devices()
            and (p.vid, p.pid) not in cls.get_vids_pids_to_avoid()
            and (
                getattr(p, "manufacturer", "") == "MicroPython"
                or ("USB" in p.description and "serial" in p.description.lower())
                or "UART" in p.description
                or "DAPLink" in p.description
                or "STLink" in p.description
                or "python" in p.description.lower()
            )
        )

    @classmethod
    def get_known_usb_vids_pids(cls):
        """Return set of pairs of USB device VID, PID"""
        return cls.get_used_usb_vidpids()

    @classmethod
    def get_vids_pids_to_avoid(cls):
        """Return set of pairs of USB device VID, PID to explicitly not consider
        either because they are not compatible or to reduce the number of choices
        in the switcher.
        """
        return set()

    @classmethod
    def get_used_usb_vidpids(cls):
        return get_workbench().get_option(cls.backend_name + ".used_vidpids")

    @classmethod
    def get_uart_adapter_vids_pids(cls):
        return {
            (0x1A86, 0x7523),  # HL-340
            (0x10C4, 0xEA60),  # CP210x"),
            (0x0403, 0x6001),  # FT232/FT245 (XinaBox CW01, CW02)
            (0x0403, 0x6010),  # FT2232C/D/L/HL/Q (ESP-WROVER-KIT)
            (0x0403, 0x6011),  # FT4232
            (0x0403, 0x6014),  # FT232H
            (0x0403, 0x6015),  # FT X-Series (Sparkfun ESP32)
            (0x0403, 0x601C),  # FT4222H
        }

    @classmethod
    def should_consider_unknown_devices(cls):
        return True

    @classmethod
    def get_known_port_descriptions(cls):
        return set()

    def _get_api_stubs_path(self):
        import inspect

        return os.path.join(os.path.dirname(inspect.getfile(self.__class__)), "api_stubs")

    def supports_remote_files(self):
        return self.is_connected()

    def uses_local_filesystem(self):
        return False

    def ready_for_remote_file_operations(self):
        return self.is_connected() and get_runner().is_waiting_toplevel_command()

    def supports_remote_directories(self):
        return self._cwd is not None and self._cwd != ""

    def supports_trash(self):
        return False

    def is_connected(self):
        return self._port is not None and self._proc is not None

    def _show_error(self, text):
        get_shell().print_error("\n" + text + "\n")

    def disconnect(self):
        self.destroy()

    def get_node_label(self):
        if "CircuitPython" in self._welcome_text:
            return tr("CircuitPython device")
        elif "micro:bit" in self._welcome_text.lower():
            return "micro:bit"
        else:
            return tr("MicroPython device")

    def get_full_label(self):
        if self.is_connected():
            return self.get_node_label() + " @ " + self._port
        else:
            return self.get_node_label() + " (" + tr("Not connected") + ")"

    def get_exe_dirs(self):
        return []

    def can_run_local_files(self):
        return False

    def can_run_remote_files(self):
        return False

    def fetch_next_message(self):
        msg = super(BareMetalMicroPythonProxy, self).fetch_next_message()
        if (
            not self._have_stored_pidwid
            and getattr(msg, "event_type", None) == "ToplevelResponse"
            and self._port != "webrepl"
        ):
            # Let's remember that this vidpid was used with this backend
            # need to copy and store explicitly, because otherwise I may change the default value
            used_vidpids = get_workbench().get_option(self.backend_name + ".used_vidpids").copy()
            from serial.tools.list_ports_common import ListPortInfo

            info = get_port_info(self._port)
            used_vidpids.add((info.vid, info.pid))
            self._have_stored_pidwid = True
            get_workbench().set_option(self.backend_name + ".used_vidpids", used_vidpids)

        return msg

    @classmethod
    def device_is_present_in_bootloader_mode(cls):
        return False

    @classmethod
    def should_show_in_switcher(cls):
        if cls.device_is_present_in_bootloader_mode():
            return True

        # Show only if it looks like we can connect using current configuration
        port = get_workbench().get_option(cls.backend_name + ".port")
        if port == "webrepl":
            return True
        if port == "auto":
            potential_ports = cls._detect_potential_ports()
            return len(potential_ports) > 0
        else:
            for p in list_serial_ports():
                if p.device == port:
                    return True

            return False

    @classmethod
    def get_switcher_entries(cls):
        if cls.should_show_in_switcher():
            return [(cls.get_current_switcher_configuration(), cls.backend_description)]
        else:
            return []

    def has_custom_system_shell(self):
        return self._port and self._port != "webrepl"

    def open_custom_system_shell(self):
        from thonny import terminal

        get_runner().send_command_and_wait(InlineCommand("prepare_disconnect"), "Disconnecting")

        self.disconnect()

        terminal.run_in_terminal(
            [
                running.get_interpreter_for_subprocess(sys.executable),
                "-m",
                # "serial.tools.miniterm",
                "thonny.plugins.micropython.miniterm_wrapper",
                "--exit-char",
                "20",
                "--menu-char",
                "29",
                "--filter",
                "direct",
                "--quiet",
                self._port,
                "115200",
            ],
            cwd=get_workbench().get_local_cwd(),
            keep_open=False,
            title=self._port,
        )

    def get_supported_features(self):
        return {"run", "run_in_terminal"}

    def run_script_in_terminal(self, script_path, args, interactive, keep_open):
        messagebox.showinfo(
            "Running in terminal",
            "In order to run your script in terminal, save it on the device\n"
            "as main script, select 'Tools => Open system shell' and press Ctrl+D",
        )


class BareMetalMicroPythonConfigPage(BackendDetailsConfigPage):
    backend_name = None  # Will be overwritten on Workbench.add_backend

    def __init__(self, master):
        super().__init__(master)

        self._has_opened_firmware_flasher = False

        intro_label = ttk.Label(self, text=self._get_intro_text())
        intro_label.grid(row=0, column=0, sticky="nw")

        driver_url = self._get_usb_driver_url()
        if driver_url:
            driver_url_label = create_url_label(self, driver_url)
            driver_url_label.grid(row=1, column=0, sticky="nw")

        port_label = ttk.Label(
            self, text=tr("Port or WebREPL") if self.allow_webrepl else tr("Port")
        )
        port_label.grid(row=3, column=0, sticky="nw", pady=(10, 0))

        self._ports_by_desc = {
            p.description
            if p.device in p.description
            else p.description + " (" + p.device + ")": p.device
            for p in list_serial_ports()
        }
        self._ports_by_desc["< " + tr("Try to detect port automatically") + " >"] = "auto"

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
            self.get_stored_port_desc(), self._on_change_port
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

        self._webrepl_frame = None

        last_row = ttk.Frame(self)
        last_row.grid(row=100, sticky="swe")
        self.rowconfigure(100, weight=1)
        last_row.columnconfigure(1, weight=1)

        advanced_link = ui_utils.create_action_label(
            last_row, tr("Advanced options"), lambda event: self._show_advanced_options()
        )
        # advanced_link.grid(row=0, column=1, sticky="e")

        if self._has_flashing_dialog():
            firmware_link = ui_utils.create_action_label(
                last_row,
                tr("Install or update firmware"),
                self._on_click_firmware_installer_link,
            )
            firmware_link.grid(row=1, column=1, sticky="e")

        self._on_change_port()

    def _on_click_firmware_installer_link(self, event=None):
        self._open_flashing_dialog()
        self._has_opened_firmware_flasher = True

    def _show_advanced_options(self):
        pass

    def _get_intro_text(self):
        result = (
            tr("Connect your device to the computer and select corresponding port below")
            + "\n"
            + "("
            + tr('look for your device name, "USB Serial" or "UART"')
            + ").\n"
            + tr("If you can't find it, you may need to install proper USB driver first.")
        )
        if self.allow_webrepl:
            result = (
                ("Connecting via USB cable:")
                + "\n"
                + result
                + "\n\n"
                + ("Connecting via WebREPL (EXPERIMENTAL):")
                + "\n"
                + (
                    "If your device supports WebREPL, first connect via serial, make sure WebREPL is enabled\n"
                    + "(import webrepl_setup), connect your computer and device to same network and select\n"
                    + "< WebREPL > below"
                )
            )

        return result

    def _get_webrepl_frame(self):

        if self._webrepl_frame is not None:
            return self._webrepl_frame

        self._webrepl_frame = ttk.Frame(self)

        self._webrepl_url_var = create_string_var(
            get_workbench().get_option(self.backend_name + ".webrepl_url")
        )
        url_label = ttk.Label(self._webrepl_frame, text="URL (eg. %s)" % DEFAULT_WEBREPL_URL)
        url_label.grid(row=0, column=0, sticky="nw", pady=(10, 0))
        url_entry = ttk.Entry(self._webrepl_frame, textvariable=self._webrepl_url_var, width=30)
        url_entry.grid(row=1, column=0, sticky="nw")

        self._webrepl_password_var = create_string_var(
            get_workbench().get_option(self.backend_name + ".webrepl_password")
        )
        pw_label = ttk.Label(self._webrepl_frame, text=tr("Password"))
        pw_label.grid(row=0, column=1, sticky="nw", pady=(10, 0), padx=(10, 0))
        pw_entry = ttk.Entry(self._webrepl_frame, textvariable=self._webrepl_password_var, width=15)
        pw_entry.grid(row=1, column=1, sticky="nw", padx=(10, 0))

        return self._webrepl_frame

    def get_stored_port_desc(self):
        name = get_workbench().get_option(self.backend_name + ".port")
        for desc in self._ports_by_desc:
            if self._ports_by_desc[desc] == name:
                return desc

        return ""

    def get_selected_port_name(self):
        port_desc = self._port_desc_variable.get()
        if not port_desc:
            return None
        return self._ports_by_desc[port_desc]

    def is_modified(self):
        return (
            self._port_desc_variable.modified
            or self.webrepl_selected()
            and self._webrepl_password_var.modified
            or self.webrepl_selected()
            and self._webrepl_url_var.modified
        )

    def webrepl_selected(self):
        return self.get_selected_port_name() == "webrepl"

    def should_restart(self):
        return self.is_modified() or self._has_opened_firmware_flasher

    def apply(self):
        if not self.is_modified():
            return

        else:
            port_name = self.get_selected_port_name()
            get_workbench().set_option(self.backend_name + ".port", port_name)
            if self.webrepl_selected():
                get_workbench().set_option(
                    self.backend_name + ".webrepl_url", self._webrepl_url_var.get()
                )
                get_workbench().set_option(
                    self.backend_name + ".webrepl_password", self._webrepl_password_var.get()
                )

    def _on_change_port(self, *args):
        if self._port_desc_variable.get() == self._WEBREPL_OPTION_DESC:
            self._get_webrepl_frame().grid(row=6, column=0, sticky="nwe")
        else:
            if self._webrepl_frame and self._webrepl_frame.winfo_ismapped():
                self._webrepl_frame.grid_forget()

    def _get_usb_driver_url(self) -> Optional[str]:
        return None

    def _has_flashing_dialog(self):
        return False

    def _open_flashing_dialog(self):
        raise NotImplementedError()

    @property
    def allow_webrepl(self):
        return False


class GenericBareMetalMicroPythonProxy(BareMetalMicroPythonProxy):
    @classmethod
    def get_known_usb_vids_pids(cls):
        """Return set of pairs of USB device (VID, PID)"""
        return {
            # Generic MicroPython Board, see http://pid.codes/org/MicroPython/
            (0x1209, 0xADDA)
        } | cls.get_uart_adapter_vids_pids()

    @classmethod
    def get_vids_pids_to_avoid(self):
        return VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND


class GenericBareMetalMicroPythonConfigPage(BareMetalMicroPythonConfigPage):
    @property
    def allow_webrepl(self):
        return False


class LocalMicroPythonProxy(MicroPythonProxy):
    def __init__(self, clean):
        self._mp_executable = get_workbench().get_option("LocalMicroPython.executable")
        super().__init__(clean)

    def _get_launcher_with_args(self):
        import thonny.plugins.micropython.os_mp_backend

        cmd = [
            thonny.plugins.micropython.os_mp_backend.__file__,
            repr(
                {
                    "interpreter": self._mp_executable,
                    "api_stubs_path": self._get_api_stubs_path(),
                    "cwd": self.get_cwd(),
                }
            ),
        ]
        return cmd

    def interrupt(self):
        # Don't interrupt local process, but direct it to the device
        self._send_msg(ImmediateCommand("interrupt"))

    def send_command(self, cmd: CommandToBackend) -> Optional[str]:
        if isinstance(cmd, EOFCommand):
            get_shell().restart()  # Runner doesn't notice restart

        return super().send_command(cmd)

    def _get_api_stubs_path(self):
        import inspect

        return os.path.join(os.path.dirname(inspect.getfile(self.__class__)), "api_stubs")

    def _get_initial_cwd(self):
        return get_workbench().get_local_cwd()

    def supports_remote_files(self):
        return False
        # return self._proc is not None

    def uses_local_filesystem(self):
        return True

    def ready_for_remote_file_operations(self):
        return False

    def supports_remote_directories(self):
        return False

    def supports_trash(self):
        return True

    def is_connected(self):
        return self._proc is not None

    def _show_error(self, text):
        get_shell().print_error("\n" + text + "\n")

    def disconnect(self):
        self.destroy()

    def get_node_label(self):
        return "Local"

    def get_full_label(self):
        return self._mp_executable

    def get_exe_dirs(self):
        return []

    def get_pip_gui_class(self):
        from thonny.plugins.micropython.pip_gui import LocalMicroPythonPipDialog

        return LocalMicroPythonPipDialog

    def can_run_local_files(self):
        return True

    def can_run_remote_files(self):
        return False

    @classmethod
    def should_show_in_switcher(cls):
        # Show when the executable is configured and exists
        executable = get_workbench().get_option("LocalMicroPython.executable")
        import shutil

        return bool(executable) and (
            os.path.isabs(executable) and os.path.exists(executable) or shutil.which(executable)
        )

    @classmethod
    def get_switcher_entries(cls):
        if cls.should_show_in_switcher():
            return [(cls.get_current_switcher_configuration(), cls.backend_description)]
        else:
            return []


class LocalMicroPythonConfigPage(BackendDetailsConfigPage):
    backend_name = None  # Will be overwritten on Workbench.add_backend

    def __init__(self, master):
        super().__init__(master)

        self._changed = False
        self._executable_var = self._add_text_field(
            "Interpreter", "LocalMicroPython.executable", 30
        )

    def _on_change(self):
        self._changed = True

    def apply(self):
        get_workbench().set_option("LocalMicroPython.executable", self._executable_var.get())

    def should_restart(self):
        return self._changed


class SshMicroPythonProxy(MicroPythonProxy):
    def __init__(self, clean):
        self._host = get_workbench().get_option("SshMicroPython.host")
        self._user = get_workbench().get_option("SshMicroPython.user")
        self._mp_executable = get_workbench().get_option("SshMicroPython.executable")

        super().__init__(clean)

    def _get_launcher_with_args(self):
        import thonny.plugins.micropython.os_mp_backend

        args = {
            "cwd": get_workbench().get_option("SshMicroPython.cwd") or "",
            "interpreter": self._mp_executable,
            "api_stubs_path": self._get_api_stubs_path(),
            "host": self._host,
            "user": self._user,
            "password": get_ssh_password("SshMicroPython"),
        }

        args.update(self._get_time_args())

        cmd = [
            thonny.plugins.micropython.os_mp_backend.__file__,
            repr(args),
        ]
        return cmd

    def interrupt(self):
        # Don't interrupt local process, but direct it to the device
        self._send_msg(ImmediateCommand("interrupt"))

    def send_command(self, cmd: CommandToBackend) -> Optional[str]:
        if isinstance(cmd, EOFCommand):
            get_shell().restart()  # Runner doesn't notice restart

        return super().send_command(cmd)

    def _get_api_stubs_path(self):
        import inspect

        return os.path.join(os.path.dirname(inspect.getfile(self.__class__)), "api_stubs")

    def _get_initial_cwd(self):
        return get_workbench().get_option("SshMicroPython.cwd")

    def _publish_cwd(self, cwd):
        return get_workbench().set_option("SshMicroPython.cwd", cwd)

    def supports_remote_files(self):
        return True
        # return self._proc is not None

    def uses_local_filesystem(self):
        return False

    def ready_for_remote_file_operations(self):
        return self.is_connected()

    def supports_remote_directories(self):
        return True

    def supports_trash(self):
        return False

    def is_connected(self):
        return self._proc is not None

    def _show_error(self, text):
        get_shell().print_error("\n" + text + "\n")

    def disconnect(self):
        self.destroy()

    def get_node_label(self):
        return self._host

    def get_full_label(self):
        return self._mp_executable + " @ " + self._host

    def get_exe_dirs(self):
        return []

    def can_run_local_files(self):
        return False

    def can_run_remote_files(self):
        return True

    @classmethod
    def should_show_in_switcher(cls):
        # Show when the executable, user and host are configured
        return (
            get_workbench().get_option("SshMicroPython.host")
            and get_workbench().get_option("SshMicroPython.user")
            and get_workbench().get_option("SshMicroPython.executable")
        )

    @classmethod
    def get_switcher_entries(cls):
        if cls.should_show_in_switcher():
            return [(cls.get_current_switcher_configuration(), cls.backend_description)]
        else:
            return []

    def has_custom_system_shell(self):
        return True

    def open_custom_system_shell(self):
        if not shutil.which("ssh"):
            messagebox.showerror(
                "Command not found", "Command 'ssh' not found", master=get_workbench()
            )
            return

        from thonny import terminal

        userhost = "%s@%s" % (self._user, self._host)
        terminal.run_in_terminal(
            ["ssh", userhost], cwd=get_workbench().get_local_cwd(), keep_open=False, title=userhost
        )


class SshMicroPythonConfigPage(BaseSshProxyConfigPage):
    backend_name = None  # Will be overwritten on Workbench.add_backend

    def __init__(self, master):
        super().__init__(master, "SshMicroPython")


def list_serial_ports():
    # serial.tools.list_ports.comports() can be too slow
    # because os.path.islink can be too slow (https://github.com/pyserial/pyserial/pull/303)
    # Workarond: temporally patch os.path.islink
    import serial.tools.list_ports

    try:
        old_islink = os.path.islink
        if platform.system() == "Windows":
            os.path.islink = lambda _: False
        return list(serial.tools.list_ports.comports())
    finally:
        os.path.islink = old_islink


def port_exists(device):
    for port in list_serial_ports():
        if port.device == device:
            return True

    return False


def list_serial_ports_with_descriptions():
    def port_order(p):
        name = p.device
        if name is None:
            return ""
        elif name.startswith("COM") and len(name) == 4:
            # Make one-digit COM ports go before COM10
            return name.replace("COM", "COM0")
        else:
            return name

    sorted_ports = sorted(list_serial_ports(), key=port_order)

    return [
        (
            p.description if p.device in p.description else p.description + " (" + p.device + ")",
            p.device,
        )
        for p in sorted_ports
    ]


def get_port_info(port):
    for info in list_serial_ports():
        if info.device == port:
            return info
    raise RuntimeError("Port %s not found" % port)


def add_micropython_backend(
    name,
    proxy_class,
    description,
    config_page,
    bare_metal=True,
    sort_key=None,
    validate_time=True,
    sync_time=None,
    write_block_size=None,
    write_block_delay=None,
    dtr=None,
    rts=None,
):
    if bare_metal:
        get_workbench().set_default(name + ".port", "auto")
        get_workbench().set_default(name + ".webrepl_url", DEFAULT_WEBREPL_URL)
        get_workbench().set_default(name + ".webrepl_password", "")
        get_workbench().set_default(name + ".write_block_size", write_block_size)
        # write_block_delay is used only with "raw" submit_mode
        get_workbench().set_default(name + ".write_block_delay", write_block_delay)
        get_workbench().set_default(name + ".used_vidpids", set())
        get_workbench().set_default(name + ".dtr", dtr)
        get_workbench().set_default(name + ".rts", rts)
        get_workbench().set_default(name + ".submit_mode", None)

        if sync_time is None:
            sync_time = True
        get_workbench().set_default(name + ".sync_time", sync_time)
    else:
        if sync_time is None:
            sync_time = False
        get_workbench().set_default(name + ".sync_time", sync_time)

    get_workbench().set_default(name + ".validate_time", validate_time)
    get_workbench().add_backend(name, proxy_class, description, config_page, sort_key=sort_key)


def load_plugin():
    add_micropython_backend(
        "GenericMicroPython",
        GenericBareMetalMicroPythonProxy,
        tr("MicroPython (generic)"),
        GenericBareMetalMicroPythonConfigPage,
        sort_key="49",
    )

    if platform.system() in ("Linux", "Darwin"):
        add_micropython_backend(
            "LocalMicroPython",
            LocalMicroPythonProxy,
            tr("MicroPython (local)"),
            LocalMicroPythonConfigPage,
            bare_metal=False,
            sort_key="21",
        )
        get_workbench().set_default("LocalMicroPython.executable", "micropython")

    add_micropython_backend(
        "SshMicroPython",
        SshMicroPythonProxy,
        tr("MicroPython (SSH)"),
        SshMicroPythonConfigPage,
        bare_metal=False,
        sort_key="22",
    )
    get_workbench().set_default("SshMicroPython.executable", "micropython")
    get_workbench().set_default("SshMicroPython.cwd", None)
    get_workbench().set_default("SshMicroPython.host", "")
    get_workbench().set_default("SshMicroPython.user", "")
    get_workbench().set_default("SshMicroPython.auth_method", "password")
