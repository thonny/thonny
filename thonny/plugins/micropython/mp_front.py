import os
import shutil
import sys
import time
from logging import getLogger
from textwrap import dedent
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional, Tuple

from thonny import get_runner, get_shell, get_workbench, running, ui_utils
from thonny.common import CommandToBackend, EOFCommand, ImmediateCommand, InlineCommand
from thonny.languages import tr
from thonny.misc_utils import list_volumes
from thonny.plugins.backend_config_page import (
    BackendDetailsConfigPage,
    BaseSshProxyConfigPage,
    get_ssh_password,
)
from thonny.running import SubprocessProxy
from thonny.ui_utils import create_string_var, create_url_label, ems_to_pixels

logger = getLogger(__name__)

DEFAULT_WEBREPL_URL = "ws://192.168.4.1:8266/"
WEBREPL_PORT_VALUE = "webrepl"
VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND = set()


class MicroPythonProxy(SubprocessProxy):
    def __init__(self, clean):
        self._lib_dirs = []
        super().__init__(clean, running.get_front_interpreter_for_subprocess())

    def get_pip_gui_class(self):
        return None

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
            "local_rtc": get_workbench().get_option(self.backend_name + ".local_rtc", False),
        }
        return result

    def _installer_runs_locally(self):
        return True

    def has_local_interpreter(self):
        return False

    def can_debug(self) -> bool:
        return False

    def can_run_in_terminal(self) -> bool:
        return False

    @classmethod
    def is_valid_configuration(cls, conf: Dict[str, Any]) -> bool:
        return True


class BareMetalMicroPythonProxy(MicroPythonProxy):
    def __init__(self, clean):
        self._port = get_workbench().get_option(self.backend_name + ".port")
        self._clean_start = clean
        self._fix_port()

        super().__init__(clean)

    def get_target_executable(self) -> Optional[str]:
        return None

    def get_pip_gui_class(self):
        from thonny.plugins.micropython.pip_gui import MicroPythonPipDialog

        return MicroPythonPipDialog

    def destroy(self, for_restart: bool = False):
        super().destroy(for_restart=for_restart)
        if self._port != WEBREPL_PORT_VALUE:
            # let the OS release the port
            time.sleep(0.1)

    def _fix_port(self):
        if self._port == WEBREPL_PORT_VALUE:
            return

        elif self._port == "auto":
            potential = self._detect_potential_ports()
            if len(potential) == 1:
                self._port = potential[0][0]
            else:
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

    def _start_background_process(self, clean=None, extra_args=[]):
        if self._port is None:
            return

        super()._start_background_process(clean=clean, extra_args=extra_args)

    def _get_launcher_with_args(self):
        args = {
            "clean": self._clean_start,
            "port": self._port,
            "dtr": get_workbench().get_option(self.backend_name + ".dtr"),
            "rts": get_workbench().get_option(self.backend_name + ".rts"),
            "submit_mode": get_workbench().get_option(self.backend_name + ".submit_mode"),
            "interrupt_on_connect": get_workbench().get_option(
                self.backend_name + ".interrupt_on_connect"
            ),
            "write_block_size": self._get_write_block_size(),
            "write_block_delay": self._get_write_block_delay(),
            "proxy_class": self.__class__.__name__,
        }
        if self._port == WEBREPL_PORT_VALUE:
            args["url"] = get_workbench().get_option(self.backend_name + ".webrepl_url")
            args["password"] = get_workbench().get_option(self.backend_name + ".webrepl_password")

        args.update(self._get_time_args())

        cmd = [
            self._get_backend_launcher_path(),
            repr(args),
        ]

        return cmd

    def should_restart_interpreter_before_run(self):
        return get_workbench().get_option(self.backend_name + ".restart_interpreter_before_run")

    def stop_restart_kills_user_program(self) -> bool:
        return False

    def _get_backend_launcher_path(self) -> str:
        import thonny.plugins.micropython.bare_metal_backend

        return thonny.plugins.micropython.bare_metal_backend.__file__

    def _get_write_block_size(self):
        return get_workbench().get_option(self.backend_name + ".write_block_size")

    def _get_write_block_delay(self):
        return get_workbench().get_option(self.backend_name + ".write_block_delay")

    def interrupt(self):
        # Don't interrupt local process, but direct it to device
        self._send_msg(ImmediateCommand("interrupt"))

    def send_command(self, cmd: CommandToBackend) -> Optional[str]:
        if isinstance(cmd, EOFCommand):
            # Runner doesn't notice restart
            get_shell().restart(was_running=get_runner().is_running())

        return super().send_command(cmd)

    def _prepare_clean_launch(self):
        """Nothing to do in this level. The backend takes care of the clearing"""

    @classmethod
    def _detect_potential_ports(cls) -> List[Tuple[str, str]]:
        all_ports = list_serial_ports()
        """
        for p in all_ports:
            print(vars(p))
        """
        last_backs = {}  # get_workbench().get_option("serial.last_backend_per_vid_pid")
        return [(p.device, p.description) for p in all_ports if cls._is_potential_port(p)]

    @classmethod
    def _is_for_micropython(cls):
        return True

    @classmethod
    def _is_for_circuitpython(cls):
        return False

    @classmethod
    def _is_potential_port(cls, p):
        if "CircuitPython CDC2 " in (p.interface or ""):
            return False

        last_backs = get_workbench().get_option("serial.last_backend_per_vid_pid")
        if last_backs.get((p.vid, p.pid), "") == cls.backend_name:
            return True

        if "CircuitPython CDC " in (p.interface or ""):
            return cls._is_for_circuitpython()

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
                or "python" in p.description.lower()
                or "MicroPython" in (p.manufacturer or "")
            )
        )

    @classmethod
    def get_known_usb_vids_pids(cls):
        """Return set of pairs of USB device VID, PID"""
        return set()

    @classmethod
    def get_vids_pids_to_avoid(cls):
        """Return set of pairs of USB device VID, PID to explicitly not consider
        either because they are not compatible or to reduce the number of choices
        in the switcher.
        """
        return set()

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

    def _check_remember_current_configuration(self) -> None:
        super()._check_remember_current_configuration()

        current_conf = self.get_current_switcher_configuration()
        port = current_conf[f"{self.backend_name}.port"]
        if port and port != WEBREPL_PORT_VALUE:
            last_backs = get_workbench().get_option("serial.last_backend_per_vid_pid")
            info = get_port_info(port)
            last_backs[(info.vid, info.pid)] = self.backend_name
            get_workbench().set_option("serial.last_backend_per_vid_pid", last_backs)

    def _should_remember_configuration(self, configuration: Dict[str, Any]) -> bool:
        return bool(configuration.get(f"{self.backend_name}.webrepl_url", False))

    def get_current_switcher_configuration(self) -> Dict[str, Any]:
        # NB! using current port value, not the configured one (which may be "auto")
        conf = {
            "run.backend_name": self.backend_name,
            f"{self.backend_name}.port": self._port,
        }
        if self._port == WEBREPL_PORT_VALUE:
            conf[f"{self.backend_name}.webrepl_url"] = get_workbench().get_option(
                f"{self.backend_name}.webrepl_url"
            )

        return conf

    @classmethod
    def get_switcher_configuration_label(cls, conf: Dict[str, Any]) -> str:
        port = conf[f"{cls.backend_name}.port"]
        if port == WEBREPL_PORT_VALUE:
            url = conf[f"{cls.backend_name}.webrepl_url"]
            return f"{cls.backend_description}  •  {url}"
        else:
            try:
                p = get_port_info(port)
            except Exception:
                p = None
                logger.exception("Could not get port info for %r", port)

            if p:
                return f"{cls.backend_description}  •  {get_serial_port_label(p)}"
            else:
                return f"{cls.backend_description}  •  {port}"

    @classmethod
    def get_switcher_entries(cls):
        def should_show(conf):
            port = conf[f"{cls.backend_name}.port"]
            if port == WEBREPL_PORT_VALUE:
                return True
            elif port == "auto":
                potential_ports = cls._detect_potential_ports()
                return len(potential_ports) > 0
            else:
                for p in list_serial_ports():
                    if p.device == port:
                        return True

                return False

        relevant_confs = list(filter(should_show, cls.get_last_configurations()))

        for device, desc in cls._detect_potential_ports():
            conf = {"run.backend_name": cls.backend_name, f"{cls.backend_name}.port": device}
            if conf not in relevant_confs:
                relevant_confs.append(conf)

        sorted_confs = sorted(relevant_confs, key=cls.get_switcher_configuration_label)
        return [(conf, cls.get_switcher_configuration_label(conf)) for conf in sorted_confs]

    def has_custom_system_shell(self):
        return self._port and self._port != WEBREPL_PORT_VALUE

    def open_custom_system_shell(self):
        from thonny import terminal

        get_runner().send_command_and_wait(InlineCommand("prepare_disconnect"), "Disconnecting")

        self.disconnect()

        terminal.run_in_terminal(
            [
                running.get_front_interpreter_for_subprocess(sys.executable),
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

        self._has_opened_python_flasher = False

        intro_text = self._get_intro_text()
        if intro_text:
            intro_label = ttk.Label(self, text=intro_text)
            intro_label.grid(row=0, column=0, sticky="nw")

        intro_url = self._get_intro_url()
        if intro_url:
            intro_url_label = create_url_label(self, intro_url)
            intro_url_label.grid(row=1, column=0, sticky="nw")

        port_label = ttk.Label(
            self, text=tr("Port or WebREPL") if self.allow_webrepl else tr("Port")
        )
        port_label.grid(row=3, column=0, sticky="nw", pady=(10, 0))

        self._ports_by_desc = {get_serial_port_label(p) for p in list_serial_ports()}
        self._ports_by_desc["< " + tr("Try to detect port automatically") + " >"] = "auto"

        self._WEBREPL_OPTION_DESC = "< WebREPL >"
        if self.allow_webrepl:
            self._ports_by_desc[self._WEBREPL_OPTION_DESC] = WEBREPL_PORT_VALUE

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

        self.add_checkbox(
            self.backend_name + ".interrupt_on_connect",
            row=10,
            description=tr("Interrupt working program on connect"),
            pady=(ems_to_pixels(2.0), 0),
        )

        if self.may_have_rtc():
            self.add_checkbox(
                self.backend_name + ".sync_time",
                row=11,
                description=tr("Synchronize device's real time clock"),
            )

            self.add_checkbox(
                self.backend_name + ".local_rtc",
                row=12,
                description=tr("Use local time in real time clock"),
            )

        self.add_checkbox(
            self.backend_name + ".restart_interpreter_before_run",
            row=13,
            description=tr("Restart interpreter before running a script"),
        )

        last_row = ttk.Frame(self)
        last_row.grid(row=100, sticky="swe")
        self.rowconfigure(100, weight=1)
        last_row.columnconfigure(1, weight=1)

        kinds = self.get_flashing_dialog_kinds()
        for i, kind in enumerate(kinds):

            def _click_flashing_link(event, kind=kind):
                self._handle_python_installer_link(kind=kind)

            if i == 0:
                link_text = self._get_flasher_link_title()
            else:
                link_text = ""

            if kind != "":
                if link_text:
                    link_text += " "
                link_text += f"({kind})"

            python_link = ui_utils.create_action_label(
                last_row,
                link_text,
                _click_flashing_link,
            )
            python_link.grid(row=i, column=1, sticky="e")

        self._on_change_port()

    def _get_flasher_link_title(self) -> str:
        return tr("Install or update %s") % "MicroPython"

    def _handle_python_installer_link(self, kind: str):
        self._open_flashing_dialog(kind)
        self._has_opened_python_flasher = True

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
                + ("Connecting via WebREPL:")
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
        return self.get_selected_port_name() == WEBREPL_PORT_VALUE

    def should_restart(self):
        return self.is_modified() or self._has_opened_python_flasher

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

    def may_have_rtc(self):
        return True

    def _get_intro_url(self) -> Optional[str]:
        return None

    def get_flashing_dialog_kinds(self) -> List[str]:
        return []

    def _open_flashing_dialog(self, kind: str) -> None:
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
            (0x1209, 0xADDA),
            (0x0694, 0x0009),  # SPIKE Prime
            (0x0694, 0x0010),  # Robot Inventor
        } | get_uart_adapter_vids_pids()

    @classmethod
    def get_vids_pids_to_avoid(self):
        return VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND


class GenericBareMetalMicroPythonConfigPage(BareMetalMicroPythonConfigPage):
    @property
    def allow_webrepl(self):
        return False


class LocalMicroPythonProxy(MicroPythonProxy):
    def __init__(self, clean):
        exe = get_workbench().get_option("LocalMicroPython.executable")
        if os.path.isabs(exe):
            self._target_executable = exe
        else:
            self._target_executable = shutil.which(exe)

        super().__init__(clean)

    def get_target_executable(self) -> Optional[str]:
        return self._target_executable

    def _get_launcher_with_args(self):
        import thonny.plugins.micropython.os_mp_backend

        cmd = [
            thonny.plugins.micropython.os_mp_backend.__file__,
            repr(
                {
                    "interpreter": self._target_executable,
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
            # Runner doesn't notice restart
            get_shell().restart(was_running=get_runner().is_running())

        return super().send_command(cmd)

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
        return self._target_executable

    def get_exe_dirs(self):
        return []

    def can_run_local_files(self):
        return True

    def can_run_remote_files(self):
        return False

    @classmethod
    def _get_switcher_conf_for_executable(cls, executable):
        return {"run.backend_name": cls.backend_name, f"{cls.backend_name}.executable": executable}

    def get_current_switcher_configuration(self):
        return self._get_switcher_conf_for_executable(
            get_workbench().get_option(f"{self.backend_name}.executable")
        )

    @classmethod
    def get_switcher_entries(cls):
        confs = sorted(
            cls.get_last_configurations(), key=lambda conf: conf[f"{cls.backend_name}.executable"]
        )

        return [
            (conf, cls.get_switcher_configuration_label(conf))
            for conf in confs
            if os.path.exists(conf[f"{cls.backend_name}.executable"])
            or shutil.which(conf[f"{cls.backend_name}.executable"])
        ]

    @classmethod
    def get_switcher_configuration_label(cls, conf: Dict[str, Any]) -> str:
        return cls.backend_description + "  •  " + conf[f"{cls.backend_name}.executable"]

    @classmethod
    def is_valid_configuration(cls, conf: Dict[str, Any]) -> bool:
        executable = conf[f"{cls.backend_name}.executable"]
        return os.path.exists(executable) or shutil.which(executable)


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
        self._host = get_workbench().get_option(f"{self.backend_name}.host")
        self._user = get_workbench().get_option(f"{self.backend_name}.user")
        self._target_executable = get_workbench().get_option(f"{self.backend_name}.executable")

        super().__init__(clean)

    def _get_launcher_with_args(self):
        import thonny.plugins.micropython.os_mp_backend

        args = {
            "cwd": get_workbench().get_option(f"{self.backend_name}.cwd") or "",
            "interpreter": self._target_executable,
            "host": self._host,
            "user": self._user,
        }

        args.update(self._get_time_args())
        args.update(self._get_extra_launcher_args())

        cmd = [
            thonny.plugins.micropython.os_mp_backend.__file__,
            repr(args),
        ]
        return cmd

    def _send_initial_input(self) -> None:
        assert self._proc is not None
        self._proc.stdin.write((get_ssh_password(self.backend_name) or "") + "\n")
        self._proc.stdin.flush()

    def _get_extra_launcher_args(self):
        return {}

    def get_target_executable(self) -> Optional[str]:
        return self._target_executable

    def interrupt(self):
        # Don't interrupt local process, but direct it to the device
        self._send_msg(ImmediateCommand("interrupt"))

    def send_command(self, cmd: CommandToBackend) -> Optional[str]:
        if isinstance(cmd, EOFCommand):
            # Runner doesn't notice restart
            get_shell().restart(was_running=get_runner().is_running())

        return super().send_command(cmd)

    def _get_initial_cwd(self):
        return get_workbench().get_option(f"{self.backend_name}.cwd")

    def _publish_cwd(self, cwd):
        return get_workbench().set_option(f"{self.backend_name}.cwd", cwd)

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
        return self._target_executable + " @ " + self._host

    def get_exe_dirs(self):
        return []

    def can_run_local_files(self):
        return False

    def can_run_remote_files(self):
        return True

    def get_current_switcher_configuration(self) -> Dict[str, Any]:
        return {
            "run.backend_name": self.backend_name,
            f"{self.backend_name}.executable": get_workbench().get_option(
                f"{self.backend_name}.executable"
            ),
            f"{self.backend_name}.host": get_workbench().get_option(f"{self.backend_name}.host"),
            f"{self.backend_name}.user": get_workbench().get_option(f"{self.backend_name}.user"),
        }

    @classmethod
    def get_switcher_configuration_label(cls, conf: Dict[str, Any]) -> str:
        user = conf[f"{cls.backend_name}.user"]
        host = conf[f"{cls.backend_name}.host"]
        executable = conf[f"{cls.backend_name}.executable"]
        return f"{cls.backend_description}  •  {user} @ {host} : {executable}"

    @classmethod
    def get_switcher_entries(cls):
        confs = sorted(cls.get_last_configurations(), key=cls.get_switcher_configuration_label)
        return [(conf, cls.get_switcher_configuration_label(conf)) for conf in confs]

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

    @classmethod
    def is_valid_configuration(cls, conf: Dict[str, Any]) -> bool:
        return True


class SshMicroPythonConfigPage(BaseSshProxyConfigPage):
    pass


_PORTS_CACHE = []
_PORTS_CACHE_TIME = 0


def get_serial_port_label(p) -> str:
    # On Windows, port is given also in description
    if p.product:
        desc = p.product
    elif p.interface:
        desc = p.interface
    else:
        desc = p.description.replace(f" ({p.device})", "")

    if desc == "USB Serial Device":
        # Try finding something less generic
        if p.product:
            desc = p.product
        elif p.interface:
            desc = p.interface

    return f"{desc} @ {p.device}"


def list_serial_ports(max_cache_age: float = 0.5):
    global _PORTS_CACHE, _PORTS_CACHE_TIME

    cur_time = time.time()
    if cur_time - _PORTS_CACHE_TIME > max_cache_age:
        _PORTS_CACHE = _list_serial_ports_uncached()
        _PORTS_CACHE_TIME = cur_time

    return _PORTS_CACHE


def _list_serial_ports_uncached():
    logger.info("Listing serial ports")
    # serial.tools.list_ports.comports() can be too slow
    # because os.path.islink can be too slow (https://github.com/pyserial/pyserial/pull/303)
    # Workarond: temporally patch os.path.islink
    old_islink = os.path.islink
    try:
        if sys.platform == "win32":
            os.path.islink = lambda _: False

        if sys.platform == "win32":
            try:
                from adafruit_board_toolkit._list_ports_windows import comports
            except ImportError:
                logger.info("Falling back to serial.tools.list_ports.comports")
                from serial.tools.list_ports import comports
        elif sys.platform == "darwin":
            try:
                from adafruit_board_toolkit._list_ports_osx import comports
            except ImportError:
                logger.info("Falling back to serial.tools.list_ports.comports")
                from serial.tools.list_ports import comports
        else:
            from serial.tools.list_ports import comports

        return comports()
    finally:
        os.path.islink = old_islink


def port_exists(device):
    for port in list_serial_ports():
        if port.device == device:
            return True

    return False


def get_uart_adapter_vids_pids():
    # https://github.com/per1234/zzInoVIDPID
    # https://github.com/per1234/zzInoVIDPID/blob/master/zzInoVIDPID/boards.txt
    # http://esp32.net/usb-uart/
    # https://www.usb.org/developers
    return {
        (0x1A86, 0x7523),  # CH340 (HL-340?)
        (0x1A86, 0x5523),  # CH341
        (0x1A86, 0x55D4),  # CH9102F, seen at Adafruit Feather ESP32 V2
        (0x10C4, 0xEA60),  # CP210x,
        (0x0403, 0x6001),  # FT232/FT245 (XinaBox CW01, CW02)
        (0x0403, 0x6010),  # FT2232C/D/L/HL/Q (ESP-WROVER-KIT)
        (0x0403, 0x6011),  # FT4232
        (0x0403, 0x6014),  # FT232H
        (0x0403, 0x6015),  # FT X-Series (Sparkfun ESP32)
        (0x0403, 0x601C),  # FT4222H
        (0x303A, 0x1001),  # Espressif's built-in USB-to-Serial, seen at QtPy C3
    }


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
    validate_time=False,
    sync_time=None,
    local_rtc=True,
    submit_mode=None,
    write_block_size=None,
    write_block_delay=None,
    dtr=None,
    rts=None,
):
    if bare_metal:
        get_workbench().set_default(name + ".port", "auto")
        get_workbench().set_default(name + ".webrepl_url", DEFAULT_WEBREPL_URL)
        get_workbench().set_default(name + ".webrepl_password", "")
        get_workbench().set_default(name + ".submit_mode", submit_mode)
        get_workbench().set_default(name + ".write_block_size", write_block_size)
        get_workbench().set_default(name + ".write_block_delay", write_block_delay)
        get_workbench().set_default(name + ".dtr", dtr)
        get_workbench().set_default(name + ".rts", rts)
        get_workbench().set_default(name + ".interrupt_on_connect", True)
        get_workbench().set_default(name + ".restart_interpreter_before_run", True)

        if sync_time is None:
            sync_time = True
    else:
        if sync_time is None:
            sync_time = False

    get_workbench().set_default(name + ".sync_time", sync_time)
    get_workbench().set_default(name + ".local_rtc", local_rtc)
    get_workbench().set_default(name + ".validate_time", validate_time)
    get_workbench().add_backend(name, proxy_class, description, config_page, sort_key=sort_key)
