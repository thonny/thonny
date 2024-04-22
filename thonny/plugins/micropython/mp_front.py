import dataclasses
import os
import shutil
import sys
import time
from logging import getLogger
from textwrap import dedent
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional, Tuple

from packaging.utils import canonicalize_name

from thonny import get_runner, get_shell, get_workbench, running, ui_utils
from thonny.common import CommandToBackend, DistInfo, EOFCommand, ImmediateCommand, InlineCommand
from thonny.config_ui import (
    add_option_checkbox,
    add_option_combobox,
    add_option_entry,
    add_text_row,
    add_vertical_separator,
)
from thonny.languages import tr
from thonny.misc_utils import download_and_parse_json, levenshtein_distance
from thonny.plugins.backend_config_page import (
    BaseSshProxyConfigPage,
    TabbedBackendDetailsConfigurationPage,
    get_ssh_password,
)
from thonny.running import SubprocessProxy
from thonny.ui_utils import (
    TreeFrame,
    create_string_var,
    create_url_label,
    ems_to_pixels,
    get_last_grid_row,
)

logger = getLogger(__name__)

DEFAULT_WEBREPL_URL = "ws://192.168.4.1:8266/"
WEBREPL_OPTION_DESC = "< WebREPL >"
WEBREPL_PORT_VALUE = "webrepl"
VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND = set()

MICROPYTHON_LIB_INDEX_URL = "https://micropython.org/pi/v2/index.json"
MICROPYTHON_LIB_METADATA_URL = (
    "https://raw.githubusercontent.com/thonny/thonny/master/data/micropython-lib-metadata.json"
)
_mp_lib_index_cache = None
_mp_lib_metadata_cache = None


class MicroPythonProxy(SubprocessProxy):
    def __init__(self, clean):
        self._lib_dirs = []
        super().__init__(clean, running.get_front_interpreter_for_subprocess())

    def get_packages_target_dir_with_comment(self) -> Tuple[Optional[str], Optional[str]]:
        lib_dirs = self.get_lib_dirs()
        if not lib_dirs:
            return None, "could not determine target directory"

        for path in lib_dirs:
            if path.startswith("/home/"):
                return path, None

        for path in ["/lib", "/flash/lib"]:
            if path in lib_dirs:
                return path, None

        return lib_dirs[0], None

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

    def get_package_installation_confirmations(self, dist_info: DistInfo) -> List[str]:
        result = super().get_package_installation_confirmations(dist_info)

        if not self.looks_like_suitable_package(dist_info):
            result.append(
                tr(
                    "This doesn't look like MicroPython/CircuitPython package.\n"
                    "Are you sure you want to install it?"
                )
            )
        return result

    def looks_like_suitable_package(self, dist_info: DistInfo) -> bool:
        if dist_info.source == "micropython-lib":
            return True

        for token in ["micropython", "circuitpython", "pycopy"]:
            if token in dist_info.name.lower():
                return True

        logger.debug("package classifiers: %s", dist_info.classifiers)
        for classifier in [
            "Programming Language :: Python :: Implementation :: MicroPython",
            "Programming Language :: Python :: Implementation :: CircuitPython",
        ]:
            if classifier in dist_info.classifiers:
                return True

        return False

    @classmethod
    def search_packages(cls, query: str) -> List[DistInfo]:
        from thonny.plugins.pip_gui import perform_pypi_search

        norm_query = canonicalize_name(query.strip())

        def distance(item: DistInfo) -> int:
            norm_name = canonicalize_name(item.name)
            if norm_name == norm_query:
                # don't argue with exact match
                return 0

            result = levenshtein_distance(norm_name, norm_query)

            if "micropython" in norm_query and item.source == "micropython-lib":
                # direct the user towards micropython-lib and names without "micropython"
                new_result = levenshtein_distance(
                    norm_name, norm_query.replace("micropython", "").strip("-")
                )
                if new_result < result:
                    result = new_result

            # try matching without qualifiers
            simple_name = norm_name
            simple_query = norm_query
            for qualifier in ["adafruit-circuitpython", "circuitpython", "micropython"]:
                simple_name = simple_name.replace(qualifier, "").replace("--", "-").strip("-")
                simple_query = simple_query.replace(qualifier, "").replace("--", "-").strip("-")

            new_result = levenshtein_distance(simple_name, simple_query)
            if new_result < result:
                result = new_result + 1

            return result

        mp_lib_result = cls._get_micropython_lib_dist_infos()
        pypi_result = perform_pypi_search(query)
        if "micropython" not in query.lower() and "circuitpython" not in query.lower():
            pypi_result += perform_pypi_search("micropython " + query)
            pypi_result += perform_pypi_search("circuitpython " + query)

        combined_result = []
        mp_lib_names = set()

        for item in mp_lib_result:
            combined_result.append(item)
            mp_lib_names.add(canonicalize_name(item.name))

        for item in pypi_result:
            norm_name = canonicalize_name(item.name)
            if norm_name in mp_lib_names:
                # will be shadowed by micropython-lib
                continue

            if item in combined_result:
                # avoid duplicates
                continue

            lower_summary = (item.summary and item.summary.lower()) or ""
            mentions_right_tokens = any(
                (
                    token in norm_name or token in lower_summary
                    for token in ["micropython", "circuitpython"]
                )
            )
            if norm_name == norm_query or mentions_right_tokens:
                combined_result.append(item)

        sorted_result = sorted(combined_result, key=distance)
        filtered_result = filter(lambda x: distance(x) < 4, sorted_result[:20])

        return list(filtered_result)

    @classmethod
    def _get_micropython_lib_dist_infos(cls) -> List[DistInfo]:
        data = cls._get_micropython_lib_index_data()

        result = []
        for package in data["packages"]:
            result.append(
                cls._augment_dist_info(
                    DistInfo(
                        name=package["name"],
                        version=package["version"],
                        summary=package["description"] or None,
                        source="micropython-lib",
                    )
                )
            )

        logger.info("Got %r items", len(result))
        return result

    @classmethod
    def _get_micropython_lib_index_data(cls) -> Dict[str, Any]:
        global _mp_lib_index_cache
        if not _mp_lib_index_cache:
            logger.info("Fetching %r", MICROPYTHON_LIB_INDEX_URL)
            _mp_lib_index_cache = download_and_parse_json(MICROPYTHON_LIB_INDEX_URL, timeout=10)

        return _mp_lib_index_cache

    @classmethod
    def _get_micropython_lib_metadata(cls) -> Dict[str, Any]:
        global _mp_lib_metadata_cache
        if not _mp_lib_metadata_cache:
            _mp_lib_metadata_cache = download_and_parse_json(
                MICROPYTHON_LIB_METADATA_URL, timeout=10
            )

        return _mp_lib_metadata_cache

    @classmethod
    def get_package_info_from_index(cls, name: str, version: str) -> DistInfo:
        # Try mp.org first
        index_data = cls._get_micropython_lib_index_data()

        for package in index_data["packages"]:
            if canonicalize_name(package["name"]) == canonicalize_name(name):
                if version not in package["versions"]["py"]:
                    raise RuntimeError(
                        f"Could not find version {version} of {name} in micropython-lib index"
                    )

                return cls._augment_dist_info(
                    DistInfo(
                        name=package["name"],
                        version=version,
                        source="micropython-lib",
                        author=package.get("author") or None,
                        summary=package.get("description") or None,
                        license=package.get("license") or None,
                    )
                )
                # TODO: deps?

        return super().get_package_info_from_index(name, version)

    def get_version_list_from_index(self, name: str) -> List[str]:
        # Try mp.org first
        index_data = self._get_micropython_lib_index_data()

        for package in index_data["packages"]:
            if canonicalize_name(package["name"]) == canonicalize_name(name):
                return package["versions"].get("py", [])

        return super().get_version_list_from_index(name)

    def get_search_button_text(self) -> str:
        return tr("Search micropython-lib and PyPI")

    @classmethod
    def _augment_dist_info(cls, dist_info: DistInfo) -> DistInfo:
        metadata = cls._get_micropython_lib_metadata()
        norm_name = canonicalize_name(dist_info.name)
        home_page = dist_info.home_page
        summary = dist_info.summary

        if (home_page is None or summary is None) and norm_name in metadata:
            if home_page is None:
                home_page = metadata[norm_name].get("project_url")
            if summary is None:
                summary = metadata[norm_name].get("description")
            return dataclasses.replace(dist_info, summary=summary, home_page=home_page)

        return dist_info


class BareMetalMicroPythonProxy(MicroPythonProxy):
    def __init__(self, clean):
        self._port = get_workbench().get_option(self.backend_name + ".port")
        self._clean_start = clean
        self._fix_port()

        super().__init__(clean)

    def get_target_executable(self) -> Optional[str]:
        return None

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

        # refresh the ports cache, so that the next uncached request (in BackendRestart handler)
        # is less likely to race with the back-end process trying to open a port and getting a
        # PermissionError (has happened in Windows)
        list_serial_ports(max_cache_age=0, skip_logging=False)
        super()._start_background_process(clean=clean, extra_args=extra_args)

    def _get_launcher_with_args(self):
        args = {
            "clean": self._clean_start,
            "port": self._port,
            "dtr": get_workbench().get_option(self.backend_name + ".dtr"),
            "rts": get_workbench().get_option(self.backend_name + ".rts"),
            "submit_mode": self._get_submit_mode(),
            "write_block_size": self._get_write_block_size(),
            "write_block_delay": self._get_write_block_delay(),
            "interrupt_on_connect": get_workbench().get_option(
                self.backend_name + ".interrupt_on_connect"
            ),
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

    def _get_submit_mode(self):
        if self._port == WEBREPL_PORT_VALUE:
            return get_workbench().get_option(self.backend_name + ".webrepl_submit_mode")
        else:
            return get_workbench().get_option(self.backend_name + ".submit_mode")

    def _get_write_block_size(self):
        if self._port == WEBREPL_PORT_VALUE:
            return get_workbench().get_option(self.backend_name + ".webrepl_write_block_size")
        else:
            return get_workbench().get_option(self.backend_name + ".write_block_size")

    def _get_write_block_delay(self):
        if self._port == WEBREPL_PORT_VALUE:
            return get_workbench().get_option(self.backend_name + ".webrepl_write_block_delay")
        else:
            return get_workbench().get_option(self.backend_name + ".write_block_delay")

    def interrupt(self):
        # Don't interrupt local process, but direct it to device
        self._send_msg(ImmediateCommand("interrupt"))

    def send_command(self, cmd: CommandToBackend) -> Optional[str]:
        if isinstance(cmd, EOFCommand):
            # Runner doesn't notice restart
            get_shell().restart(was_running=get_runner().is_running())

        if cmd.name.lower() == "run":
            cmd.populate_argv = get_workbench().get_option(self.backend_name + ".populate_argv")

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

        # Avoid CDC2 interfaces, see
        # https://github.com/adafruit/Adafruit_Board_Toolkit/blob/d1d3423ffa8fc91f7752b4eda8584d333e3da7d2/adafruit_board_toolkit/circuitpython_serial.py#L80
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

    def can_install_packages_from_files(self) -> bool:
        return True


class BareMetalMicroPythonConfigPage(TabbedBackendDetailsConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        self._has_opened_python_flasher = False
        self._port_names_by_desc = {}
        self._ports_by_desc = {}
        self._port_polling_after_id = None

        self._webrepl_frame = None
        self._serial_frame = None

        self.connection_page = self.create_and_add_empty_page(tr("Connection"))
        self.options_page = self.create_and_add_empty_page(tr("Options"))
        self.stubs_page = self.create_and_add_stubs_page(proxy_class=self.proxy_class)
        self.advanced_page = self.create_and_add_empty_page(tr("Advanced"), weighty_column=5)

        self._init_connection_page()
        self._init_options_page()
        self._init_advanced_page()

        self.notebook.select(self.connection_page)

    def _init_connection_page(self) -> None:
        intro_text = self._get_intro_text()
        if intro_text:
            add_text_row(self.connection_page, intro_text)

        intro_url = self._get_intro_url()
        if intro_url:
            intro_url_label = create_url_label(self.connection_page, intro_url)
            intro_url_label.grid(row=1, column=0, columnspan=2, sticky="nw")

        port_label = ttk.Label(
            self.connection_page, text=tr("Port or WebREPL") if self.allow_webrepl else tr("Port")
        )
        port_label.grid(row=3, column=0, columnspan=2, sticky="nw", pady=(10, 0))

        self._port_desc_variable = create_string_var("", self._on_change_port)
        self._port_combo = ttk.Combobox(
            self.connection_page,
            exportselection=False,
            textvariable=self._port_desc_variable,
            values=[],
        )
        self._port_combo.state(["!disabled", "readonly"])

        self._port_combo.grid(row=4, column=0, columnspan=2, sticky="new")
        self.columnconfigure(0, weight=1)

        # following should go to the bottom
        self.connection_page.rowconfigure(100, weight=1)
        last_row = ttk.Frame(self.connection_page)
        last_row.grid(row=100, columnspan=2, sticky="se")

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
            python_link.grid(row=i, column=1, sticky="se")

        self._keep_refreshing_ports(first_time=True)

    def _init_options_page(self) -> None:
        add_option_checkbox(
            self.options_page,
            self.backend_name + ".interrupt_on_connect",
            tr("Interrupt working program on connect"),
        )

        if self.may_have_rtc():
            add_option_checkbox(
                self.options_page,
                self.backend_name + ".sync_time",
                tr("Synchronize device's real time clock"),
            )

            add_option_checkbox(
                self.options_page,
                self.backend_name + ".local_rtc",
                tr("Use local time in real time clock"),
            )

        add_option_checkbox(
            self.options_page,
            self.backend_name + ".restart_interpreter_before_run",
            tr("Restart interpreter before running a script"),
        )

        add_option_checkbox(
            self.options_page,
            self.backend_name + ".populate_argv",
            tr("Populate sys.argv on run"),
        )

    def _init_advanced_page(self) -> None:
        add_text_row(
            self.advanced_page,
            "Your device, serial driver and OS may require specific DTR / RTS signals for proper connection",
            columnspan=6,
        )

        # dtr and rts options are stored separately, but it's more useful to present
        # and describe the combination
        dtr_rts_combobox = add_option_combobox(
            self.advanced_page,
            None,
            "DTR / RTS",
            choices={
                "True / True   (good for most boards, may reset ESP-s on Windows)": (
                    True,
                    True,
                ),
                "True / False   (best for some ESP-s)": (
                    True,
                    False,
                ),
                "False / True   (bad for most boards)": (False, True),
                "False / False   (best for most ESP-s on Windows)": (False, False),
            },
            width=60,
            combobox_columnspan=5,
        )

        dtr = get_workbench().get_option(self.backend_name + ".dtr")
        if dtr is None:
            dtr = True
        rts = get_workbench().get_option(self.backend_name + ".rts")
        if rts is None:
            rts = True

        dtr_rts_combobox.select_value((dtr, rts))

        def set_dtr_rts_options(event):
            dtr, rts = dtr_rts_combobox.get_selected_value()
            get_workbench().set_option(self.backend_name + ".dtr", dtr)
            get_workbench().set_option(self.backend_name + ".rts", rts)

        dtr_rts_combobox.bind("<<ComboboxSelected>>", set_dtr_rts_options, True)

        # Submit modes
        def add_submit_mode_widgets(
            option_name_qualifier: str,
            raw_paste_comment: str,
            paste_comment: str,
            raw_comment: str,
        ):
            mode_combobox = add_option_combobox(
                self.advanced_page,
                f"{self.backend_name}.{option_name_qualifier}submit_mode",
                "Submit mode",
                choices={
                    f"raw-paste   ({raw_paste_comment})": "raw_paste",
                    f"paste   ({paste_comment})": "paste",
                    f"raw   ({raw_comment})": "raw",
                },
                column=0,
                width=30,
            )

            row = get_last_grid_row(self.advanced_page)

            size_combobox = add_option_combobox(
                self.advanced_page,
                f"{self.backend_name}.{option_name_qualifier}write_block_size",
                "block size",
                choices={
                    f"512": 512,
                    f"256": 256,
                    f"255": 255,
                    f"128": 128,
                    f"64": 64,
                    f"32": 32,
                    f"30": 30,
                },
                width=4,
                label_padx=ems_to_pixels(0.5),
                row=row,
                column=2,
            )
            size_label = self.advanced_page.grid_slaves(row=row, column=2)[0]

            delay_combobox = add_option_combobox(
                self.advanced_page,
                f"{self.backend_name}.{option_name_qualifier}write_block_delay",
                "block delay",
                choices={
                    f"0.01": 0.01,
                    f"0.02": 0.02,
                    f"0.05": 0.05,
                    f"0.1": 0.1,
                    f"0.2": 0.2,
                    f"0.5": 0.5,
                },
                width=4,
                label_padx=ems_to_pixels(0.5),
                row=row,
                column=4,
            )
            delay_label = self.advanced_page.grid_slaves(row=row, column=4)[0]

            def update_visible_fields(event=None):
                if mode_combobox.get_selected_value() == "raw":
                    delay_combobox.grid()
                    delay_label.grid()
                else:
                    delay_combobox.grid_remove()
                    delay_label.grid_remove()

                if mode_combobox.get_selected_value() in ["paste", "raw"]:
                    size_combobox.grid()
                    size_label.grid()
                else:
                    size_combobox.grid_remove()
                    size_label.grid_remove()

            mode_combobox.bind("<<ComboboxSelected>>", update_visible_fields, True)
            update_visible_fields()

        add_vertical_separator(self.advanced_page)

        add_text_row(
            self.advanced_page,
            f"In case of serial communication errors, try different modes of sending commands to {self.get_firmware_name()} REPL",
            columnspan=6,
        )

        add_submit_mode_widgets(
            "", raw_paste_comment="fastest", paste_comment="next to try", raw_comment="slowest"
        )

        if self.allow_webrepl:
            add_vertical_separator(self.advanced_page)

            add_text_row(
                self.advanced_page,
                f"WebREPL connection may require different submit mode",
                columnspan=6,
            )

            add_submit_mode_widgets(
                "webrepl_",
                raw_paste_comment="probably doesn't work",
                paste_comment="try with blocks of 255 bytes",
                raw_comment="may require long delays",
            )

    def _keep_refreshing_ports(self, first_time=False):
        ports_by_desc_before = self._ports_by_desc.copy()
        self._refresh_ports(first_time=first_time)
        if (
            not self._port_desc_variable.get()
            and self._ports_by_desc != ports_by_desc_before
            and not first_time
        ):
            new_descs = self._ports_by_desc.keys() - ports_by_desc_before.keys()
            if len(new_descs) == 1:
                self._port_desc_variable.set(new_descs.pop())

        self._port_polling_after_id = self.after(500, self._keep_refreshing_ports)

    def _refresh_ports(self, first_time=False):
        old_port_desc = self._port_desc_variable.get()
        ports = list_serial_ports(max_cache_age=0, skip_logging=True)
        self._ports_by_desc = {get_serial_port_label(p): p for p in ports}
        self._port_names_by_desc = {get_serial_port_label(p): p.device for p in ports}
        self._port_names_by_desc["< " + tr("Try to detect port automatically") + " >"] = "auto"

        if self.allow_webrepl:
            self._port_names_by_desc[WEBREPL_OPTION_DESC] = WEBREPL_PORT_VALUE

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
        port_descriptions = [
            key for key, _ in sorted(self._port_names_by_desc.items(), key=port_order)
        ]
        self._port_combo["values"] = port_descriptions

        # update selection after first update
        if self._port_desc_variable.get() == "" and first_time:
            self._port_desc_variable.set(self.get_stored_port_desc())

        new_port_desc = self._port_desc_variable.get()
        if new_port_desc != "" and new_port_desc not in self._port_names_by_desc:
            logger.info(
                "Description %r not in %r anymore", new_port_desc, list(self._ports_by_desc.keys())
            )
            self._port_desc_variable.set("")

        new_port_desc = self._port_desc_variable.get()
        if new_port_desc != old_port_desc:
            if new_port_desc != "":
                logger.info("Changing port from %r to %r", old_port_desc, new_port_desc)
            self._port_desc_variable.set(new_port_desc)
            self._on_change_port()

    def _get_flasher_link_title(self) -> str:
        return tr("Install or update %s") % self.get_firmware_name()

    def _handle_python_installer_link(self, kind: str):
        new_port = self._open_flashing_dialog(kind)
        if new_port:
            # Try to select the new port
            self._refresh_ports()
            for desc, name in self._port_names_by_desc.items():
                if name == new_port:
                    self._port_desc_variable.set(desc)
                    break
        self._has_opened_python_flasher = True

    def _get_intro_text(self):
        return (
            tr("Connect your device to the computer and select corresponding port below")
            + "\n"
            + tr("If you can't find it, you may need to install proper USB driver first.")
        )

    def _get_serial_frame(self):
        if self._serial_frame is not None:
            return self._serial_frame

        self._serial_frame = TreeFrame(
            self.connection_page, columns=("attribute", "value"), height=5, show_scrollbar=False
        )
        tree = self._serial_frame.tree

        tree.column("attribute", width=ems_to_pixels(10), anchor="w", stretch=False)
        tree.column("value", width=ems_to_pixels(30), anchor="w", stretch=True)
        tree.heading("attribute", text=tr("Attribute"), anchor="w")
        tree.heading("value", text=tr("Value"), anchor="w")

        tree["show"] = ""
        return self._serial_frame

    def _update_serial_frame(self):
        tree_frame = self._get_serial_frame()
        tree_frame.clear()

        port = self.get_selected_port()
        if port is None:
            return

        tree = tree_frame.tree
        if port.vid and port.pid:
            vidhex = hex(port.vid)[2:].upper().rjust(4, "0")
            pidhex = hex(port.pid)[2:].upper().rjust(4, "0")
            vidpid = f"{vidhex}:{pidhex}"
        else:
            vidpid = f"{port.vid}:{port.pid}"

        atts = {
            "Manufacturer:": port.manufacturer,
            "Product:": port.product,
            "VID/PID:": vidpid,
            "Serial number:": port.serial_number,
            "Interface:": port.interface,
        }
        for key, value in atts.items():
            node_id = tree.insert("", "end")
            tree.set(node_id, "attribute", key)
            tree.set(node_id, "value", str(value or ""))

    def _get_webrepl_frame(self):
        if self._webrepl_frame is not None:
            return self._webrepl_frame

        self._webrepl_frame = ttk.Frame(self.connection_page)

        instructions = (
            "If your device supports WebREPL, first connect via serial, make sure WebREPL is enabled\n"
            + "(import webrepl_setup) and connect your computer and device to the same network"
        )
        instr_label = ttk.Label(self._webrepl_frame, text=instructions)
        instr_label.grid(row=0, column=0, sticky="nw", pady=(10, 0), columnspan=2)

        self._webrepl_url_var = create_string_var(
            get_workbench().get_option(self.backend_name + ".webrepl_url")
        )
        url_label = ttk.Label(self._webrepl_frame, text="URL (eg. %s)" % DEFAULT_WEBREPL_URL)
        url_label.grid(row=1, column=0, sticky="nw", pady=(15, 0))
        url_entry = ttk.Entry(self._webrepl_frame, textvariable=self._webrepl_url_var, width=30)
        url_entry.grid(row=2, column=0, sticky="nw")

        self._webrepl_password_var = create_string_var(
            get_workbench().get_option(self.backend_name + ".webrepl_password")
        )
        pw_label = ttk.Label(self._webrepl_frame, text=tr("Password"))
        pw_label.grid(row=1, column=1, sticky="nw", pady=(10, 0), padx=(10, 0))
        pw_entry = ttk.Entry(self._webrepl_frame, textvariable=self._webrepl_password_var, width=15)
        pw_entry.grid(row=2, column=1, sticky="nw", padx=(10, 0))

        return self._webrepl_frame

    def get_stored_port_desc(self):
        name = get_workbench().get_option(self.backend_name + ".port")
        for desc in self._port_names_by_desc:
            if self._port_names_by_desc[desc] == name:
                return desc

        return ""

    def get_selected_port_name(self):
        port_desc = self._port_desc_variable.get()
        if not port_desc:
            return None
        return self._port_names_by_desc[port_desc]

    def get_selected_port(self):
        port_desc = self._port_desc_variable.get()
        if not port_desc or port_desc not in self._ports_by_desc:
            return None
        return self._ports_by_desc[port_desc]

    def _connection_is_modified(self):
        return (
            self._port_desc_variable.modified
            or self.webrepl_selected()
            and self._webrepl_password_var.modified
            or self.webrepl_selected()
            and self._webrepl_url_var.modified
        )

    def webrepl_selected(self):
        return self.get_selected_port_name() == WEBREPL_PORT_VALUE

    def should_restart(self, changed_options: List[str]):
        return self._connection_is_modified() or self._has_opened_python_flasher

    def apply(self, changed_options: List[str]):
        if not self._connection_is_modified():
            return

        else:
            port_name = self.get_selected_port_name()
            get_workbench().set_option(self.backend_name + ".port", port_name)
            if self.webrepl_selected():
                if not self._webrepl_url_var.get().lower().startswith("ws://"):
                    messagebox.showerror(
                        "Bad URL", "WebREPL URL should start with ws://", parent=self
                    )
                    return False

                get_workbench().set_option(
                    self.backend_name + ".webrepl_url", self._webrepl_url_var.get()
                )
                get_workbench().set_option(
                    self.backend_name + ".webrepl_password", self._webrepl_password_var.get()
                )

    def destroy(self):
        if self._port_polling_after_id is not None:
            self.after_cancel(self._port_polling_after_id)
            self._port_polling_after_id = None

        super().destroy()

    def _on_change_port(self, *args):
        if self._port_desc_variable.get() == WEBREPL_OPTION_DESC:
            self._get_webrepl_frame().grid(row=6, column=0, columnspan=2, sticky="nwe")
            if self._serial_frame and self._serial_frame.winfo_ismapped():
                self._serial_frame.grid_forget()
        else:
            self._get_serial_frame().grid(
                row=6, column=0, columnspan=2, sticky="nwe", pady=(ems_to_pixels(1), 0)
            )
            self._update_serial_frame()
            if self._webrepl_frame and self._webrepl_frame.winfo_ismapped():
                self._webrepl_frame.grid_forget()

    def may_have_rtc(self):
        return True

    def _get_intro_url(self) -> Optional[str]:
        return None

    def get_flashing_dialog_kinds(self) -> List[str]:
        return []

    def _open_flashing_dialog(self, kind: str) -> Optional[str]:
        raise NotImplementedError()

    def get_firmware_name(self) -> str:
        return "MicroPython"

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
        self._target_executable = get_workbench().get_option("LocalMicroPython.executable")
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

    def can_install_packages_from_files(self) -> bool:
        return True


class LocalMicroPythonConfigPage(TabbedBackendDetailsConfigurationPage):

    def __init__(self, master):
        super().__init__(master)
        self.executable_page = self.create_and_add_empty_page(tr("Executable"))

        add_option_entry(
            self.executable_page, "LocalMicroPython.executable", tr("Interpreter"), width=30
        )

    def should_restart(self, changed_options: List[str]):
        return "LocalMicroPython.executable" in changed_options


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

    def can_install_packages_from_files(self) -> bool:
        return False


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

    desc = desc.replace("\x00", "").strip()

    return f"{desc} @ {p.device}"


def list_serial_ports(max_cache_age: float = 0.5, skip_logging: bool = False):
    global _PORTS_CACHE, _PORTS_CACHE_TIME

    cur_time = time.time()
    if cur_time - _PORTS_CACHE_TIME > max_cache_age:
        _PORTS_CACHE = _list_serial_ports_uncached(skip_logging=skip_logging)
        _PORTS_CACHE_TIME = cur_time

    return _PORTS_CACHE


def _list_serial_ports_uncached(skip_logging: bool = False):
    if not skip_logging:
        logger.info("Listing serial ports")
    # serial.tools.list_ports.comports() can be too slow
    # because os.path.islink can be too slow (https://github.com/pyserial/pyserial/pull/303)
    # Workarond: temporally patch os.path.islink
    old_islink = os.path.islink
    try:
        if sys.platform == "win32":
            os.path.islink = lambda _: False

        from serial.tools.list_ports import comports

        irrelevant = ["/dev/cu.Bluetooth-Incoming-Port", "/dev/cu.iPhone-WirelessiAP"]
        result = []
        unfiltered_result = comports()
        for p in unfiltered_result:
            if p.device not in irrelevant:
                result.append(p)

        return result
    finally:
        os.path.islink = old_islink
        if not skip_logging:
            logger.info("Done listing serial ports")


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
    # https://github.com/espressif/usb-pids
    return {
        (0x1A86, 0x7523),  # CH340 (HL-340?)
        (0x1A86, 0x5523),  # CH341
        (0x1A86, 0x55D4),  # CH9102F, seen at Adafruit Feather ESP32 V2, M5 stamp C3
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
    submit_mode="raw_paste",
    write_block_size=256,
    write_block_delay=0.01,
    webrepl_submit_mode="paste",
    webrepl_write_block_size=255,
    webrepl_write_block_delay=0.5,
    dtr=True,
    rts=True,
):
    if bare_metal:
        get_workbench().set_default(name + ".port", "auto")
        get_workbench().set_default(name + ".webrepl_url", DEFAULT_WEBREPL_URL)
        get_workbench().set_default(name + ".webrepl_password", "")
        get_workbench().set_default(name + ".submit_mode", submit_mode)
        get_workbench().set_default(name + ".write_block_size", write_block_size)
        get_workbench().set_default(name + ".write_block_delay", write_block_delay)
        get_workbench().set_default(name + ".webrepl_submit_mode", webrepl_submit_mode)
        get_workbench().set_default(name + ".webrepl_write_block_size", webrepl_write_block_size)
        get_workbench().set_default(name + ".webrepl_write_block_delay", webrepl_write_block_delay)
        get_workbench().set_default(name + ".dtr", dtr)
        get_workbench().set_default(name + ".rts", rts)
        get_workbench().set_default(name + ".interrupt_on_connect", True)
        get_workbench().set_default(name + ".restart_interpreter_before_run", True)
        get_workbench().set_default(name + ".populate_argv", False)

        if sync_time is None:
            sync_time = True
    else:
        if sync_time is None:
            sync_time = False

    get_workbench().set_default(name + ".sync_time", sync_time)
    get_workbench().set_default(name + ".local_rtc", local_rtc)
    get_workbench().set_default(name + ".validate_time", validate_time)
    get_workbench().add_backend(name, proxy_class, description, config_page, sort_key=sort_key)
