import glob
import os.path
import sys
import textwrap
import tkinter as tk
from logging import getLogger
from tkinter import ttk
from typing import Any, Dict, List, Optional, Tuple

import thonny
from thonny import get_runner, get_shell, get_workbench, ui_utils
from thonny.base_file_browser import (
    FILE_DIALOG_HEIGHT_EMS_OPTION,
    FILE_DIALOG_WIDTH_EMS_OPTION,
    LocalFileDialog,
)
from thonny.common import (
    InlineCommand,
    InlineResponse,
    ToplevelCommand,
    is_private_python,
    normpath_with_actual_case,
    running_in_virtual_environment,
    try_get_base_executable,
)
from thonny.languages import tr
from thonny.misc_utils import running_on_mac_os, running_on_windows
from thonny.plugins.backend_config_page import TabbedBackendDetailsConfigurationPage
from thonny.running import WINDOWS_EXE, SubprocessProxy
from thonny.terminal import run_in_terminal
from thonny.ui_utils import askopenfilename, create_string_var, ems_to_pixels

logger = getLogger(__name__)


class LocalCPythonProxy(SubprocessProxy):
    def __init__(self, clean: bool) -> None:
        logger.info("Creating LocalCPythonProxy")
        self._expecting_response_for_gui_update = False
        super().__init__(clean)
        try:
            self._send_msg(ToplevelCommand("get_environment_info"))
        except Exception:
            get_shell().report_exception()

    def compute_mgmt_executable(self):
        return get_workbench().get_option("LocalCPython.executable")

    def get_mgmt_executable_validation_error(self) -> Optional[str]:
        if not os.path.isfile(self._mgmt_executable):
            return f"Interpreter {self._mgmt_executable!r} not found.\nPlease select another!"

    def _get_initial_cwd(self):
        return get_workbench().get_local_cwd()

    def _get_launch_cwd(self):
        # use a directory which doesn't contain misleading modules
        empty_dir = os.path.join(thonny.get_thonny_user_dir(), "leave_this_empty")
        os.makedirs(empty_dir, exist_ok=True)
        return empty_dir

    def _get_launcher_with_args(self):
        launcher_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "cpython_backend", "cp_launcher.py"
        )
        return [
            launcher_file,
            self.get_cwd(),
            repr(
                {
                    "run.warn_module_shadowing": get_workbench().get_option(
                        "run.warn_module_shadowing"
                    )
                }
            ),
        ]

    def can_be_isolated(self) -> bool:
        # Can't run in isolated mode as it would hide user site-packages
        return False

    def _store_state_info(self, msg):
        super()._store_state_info(msg)

        if "gui_is_active" in msg:
            self._update_gui_updating(msg)

    def _prepare_clean_launch(self):
        self._close_backend()
        self._start_background_process()

    def _close_backend(self):
        self._cancel_gui_update_loop()
        super()._close_backend()

    def get_target_executable(self):
        return self._mgmt_executable

    def get_executable(self):
        return self._reported_executable

    def get_base_executable(self) -> Optional[str]:
        return self._reported_base_executable

    def _update_gui_updating(self, msg):
        """Enables running Tkinter or Qt programs which doesn't call mainloop.

        When mainloop is omitted, then program can be interacted with
        from the shell after it runs to the end.

        Each ToplevelResponse is supposed to tell, whether gui is active
        and needs updating.
        """
        if "gui_is_active" not in msg:
            return

        if msg["gui_is_active"] and self._gui_update_loop_id is None:
            # Start updating
            logger.info("Starting GUI update loop")
            self._loop_gui_update(True)
        elif not msg["gui_is_active"] and self._gui_update_loop_id is not None:
            logger.info("Cancelling GUI update loop")
            self._cancel_gui_update_loop()

    def _loop_gui_update(self, force=False):
        if force or get_runner().is_waiting_toplevel_command():
            # Don't send command if response for the last one hasn't arrived yet
            if not self._expecting_response_for_gui_update:
                try:
                    self.send_command(InlineCommand("process_gui_events"))
                    self._expecting_response_for_gui_update = True
                except OSError:
                    # the backend process may have been closed already
                    # https://github.com/thonny/thonny/issues/966
                    logger.exception("Could not send process_gui_events")

        self._gui_update_loop_id = get_workbench().after(50, self._loop_gui_update)

    def _cancel_gui_update_loop(self):
        if self._gui_update_loop_id is not None:
            try:
                get_workbench().after_cancel(self._gui_update_loop_id)
            finally:
                self._gui_update_loop_id = None

    def interrupt(self):
        import signal

        if self._proc is not None and self._proc.poll() is None:
            if running_on_windows():
                try:
                    os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # pylint: disable=no-member
                except Exception:
                    logger.exception("Could not interrupt backend process")
            else:
                self._proc.send_signal(signal.SIGINT)

    def run_script_in_terminal(self, script_path, args, interactive, keep_open):
        cmd = [self._mgmt_executable] + self.get_mgmt_executable_special_switches()
        if interactive:
            cmd.append("-i")
        cmd.append(os.path.basename(script_path))
        cmd.extend(args)

        run_in_terminal(cmd, os.path.dirname(script_path), keep_open=keep_open)

    def can_run_remote_files(self):
        return False

    def can_run_local_files(self):
        return True

    def fetch_next_message(self):
        while True:
            msg = super().fetch_next_message()
            if isinstance(msg, InlineResponse) and msg.command_name == "process_gui_events":
                # Only wanted to know that the command was processed
                # Don't pass upstream
                self._expecting_response_for_gui_update = False
            else:
                break

        return msg

    def has_local_interpreter(self):
        return True

    def interpreter_is_cpython_compatible(self) -> bool:
        return True

    def can_debug(self) -> bool:
        return True

    def can_run_in_terminal(self) -> bool:
        return True

    @classmethod
    def _get_switcher_conf_for_executable(cls, executable):
        return {"run.backend_name": cls.backend_name, f"{cls.backend_name}.executable": executable}

    def get_current_switcher_configuration(self):
        return self._get_switcher_conf_for_executable(
            get_workbench().get_option(f"{self.backend_name}.executable")
        )

    @classmethod
    def get_switcher_configuration_label(cls, conf: Dict[str, Any]) -> str:
        exe = conf[f"{cls.backend_name}.executable"]
        if is_private_python(exe) and exe == get_default_cpython_executable_for_backend():
            exe_label = tr("Thonny's Python")
        else:
            exe_label = exe
        # •✶♦▸
        return cls.backend_description + "  •  " + exe_label

    @classmethod
    def get_switcher_entries(cls) -> List[Tuple[Dict[str, Any], str, str]]:
        confs = sorted(
            cls.get_last_configurations(), key=lambda conf: conf[f"{cls.backend_name}.executable"]
        )
        default_exe = get_default_cpython_executable_for_backend()
        default_conf = cls._get_switcher_conf_for_executable(default_exe)
        if default_conf not in confs:
            confs.insert(0, default_conf)

        return [
            (conf, cls.get_switcher_configuration_label(conf), "localhost")
            for conf in confs
            if os.path.exists(conf[f"{cls.backend_name}.executable"])
        ]

    def open_custom_system_shell(self) -> None:
        raise NotImplementedError()

    @classmethod
    def is_valid_configuration(cls, conf: Dict[str, Any]) -> bool:
        return os.path.exists(conf[f"{cls.backend_name}.executable"])

    def can_install_packages_from_files(self) -> bool:
        return True

    def _prefer_user_install(self):
        return not (
            self._in_venv
            or thonny.is_portable()
            and is_private_python(self.get_target_executable())
        )

    def get_packages_target_dir_with_comment(self):
        if self.is_externally_managed():
            return None, self.get_externally_managed_message()

        if self._prefer_user_install():
            usp = self.get_user_site_packages()
            os.makedirs(usp, exist_ok=True)
            return normpath_with_actual_case(usp), "user site-packages"
        else:
            sp = self.get_site_packages()
            if sp is None:
                return None, "could not find target directory"
            return normpath_with_actual_case(sp), "site-packages"

    def normalize_target_path(self, path: str) -> str:
        return normpath_with_actual_case(path)


class LocalCPythonConfigurationPage(TabbedBackendDetailsConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        self.executable_page = self.create_and_add_empty_page(tr("Executable"))

        self._exe_variable = get_workbench().get_variable("LocalCPython.executable")

        entry_label = ttk.Label(self.executable_page, text=tr("Python executable"))
        entry_label.grid(row=0, column=1, columnspan=2, sticky=tk.W)

        self._exe_combo = ttk.Combobox(
            self.executable_page,
            exportselection=False,
            textvariable=self._exe_variable,
            values=find_local_cpython_executables(),
        )
        self._exe_combo.state(["!disabled", "readonly"])

        self._exe_combo.grid(row=1, column=1, sticky=tk.NSEW)

        self._select_button = ttk.Button(
            self.executable_page,
            text="...",
            width=3,
            command=self._select_executable,
        )
        self._select_button.grid(row=1, column=2, sticky="e", padx=(10, 0))
        self.executable_page.columnconfigure(1, weight=1)

        extra_text = tr("NB! Thonny only supports Python %s and later") % "3.9"
        extra_label = ttk.Label(self.executable_page, text=extra_text)
        extra_label.grid(row=2, column=1, columnspan=2, pady=10, sticky="w")

        file_browser_hint = ttk.Label(
            self.executable_page,
            text=tr(
                "Note that you can select an existing virtual environment also via "
                "right-click menu in Thonny's file browser."
            ),
        )
        file_browser_hint.grid(row=3, column=1, columnspan=2, pady=10, sticky="w")

        last_row = ttk.Frame(self.executable_page)
        last_row.grid(row=100, sticky="swe", column=1, columnspan=2)
        self.executable_page.rowconfigure(100, weight=1)
        last_row.columnconfigure(1, weight=1)
        new_venv_link = ui_utils.create_action_label(
            last_row,
            tr("New virtual environment"),
            self._create_venv,
        )
        new_venv_link.grid(row=0, column=1, sticky="e", pady=10)

        # self.columnconfigure(1, weight=1)

    def _select_executable(self):
        initialdir = get_workbench().get_local_cwd()
        # TODO: get dir of current interpreter
        options = {"parent": self.winfo_toplevel()}
        if running_on_windows():
            options["filetypes"] = [
                (tr("Python interpreters"), "python.exe"),
                (tr("all files"), ".*"),
            ]

        if running_on_mac_os():
            dlg = MacOsInterpreterDialog(self, "open", initialdir)
            ui_utils.show_dialog(
                dlg,
                self,
                width=ems_to_pixels(get_workbench().get_option(FILE_DIALOG_WIDTH_EMS_OPTION)),
                height=ems_to_pixels(get_workbench().get_option(FILE_DIALOG_HEIGHT_EMS_OPTION)),
            )
            filename = dlg.result
        else:
            filename = askopenfilename(**options)

        if not filename:
            return

        if filename.endswith("/activate"):
            filename = filename[: -len("activate")] + "python3"

        if filename:
            self._exe_variable.set(filename)

    def _create_venv(self, event=None):
        from thonny.venv_dialog import create_new_virtual_environment

        created_exe = create_new_virtual_environment(self)
        logger.info("created_exe=%r", created_exe)
        if created_exe is not None:
            self._exe_combo.configure(values=[created_exe] + find_local_cpython_executables())
            self._exe_variable.set(created_exe)

    def should_restart(self, changed_options: List[str]):
        return "LocalCPython.executable" in changed_options

    def get_new_machine_id(self) -> str:
        return "localhost"


def get_default_cpython_executable_for_backend() -> str:
    if is_private_python(sys.executable) and running_in_virtual_environment():
        # Private venv. Make an exception and use base Python for default backend.
        default_path = try_get_base_executable(sys.executable)
        if default_path is None:
            logger.warning("Could not find base executable of %s", sys.executable)
            default_path = sys.executable
    else:
        default_path = sys.executable.replace("pythonw.exe", "python.exe")

    # In macOS bundle the path may have ..-s
    default_path = os.path.normpath(default_path)

    """ # Too confusing:
    if running_on_mac_os():
        # try to generalize so that the path can survive Python upgrade
        ver = "{}.{}".format(*sys.version_info)
        ver_fragment = f"/Versions/{ver}/bin/"
        if ver_fragment in default_path:
            generalized = default_path.replace(ver_fragment, "/Versions/Current/bin/")
            if os.path.exists(generalized):
                return generalized
    """
    return default_path


def _get_interpreters_from_windows_registry():
    # https://github.com/python/cpython/blob/master/Tools/msi/README.txt
    # https://www.python.org/dev/peps/pep-0514/#installpath
    import winreg

    result = set()
    for key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for version in thonny.SUPPORTED_VERSIONS:
            for suffix in ["", "-32", "-64"]:
                variant = version + suffix
                for subkey in [
                    "SOFTWARE\\Python\\PythonCore\\" + variant + "\\InstallPath",
                    "SOFTWARE\\Python\\PythonCore\\Wow6432Node\\" + variant + "\\InstallPath",
                ]:
                    try:
                        dir_ = winreg.QueryValue(key, subkey)
                        if dir_:
                            path = os.path.join(dir_, WINDOWS_EXE)
                            if os.path.exists(path):
                                result.add(path)
                    except Exception:
                        pass

    return result


class MacOsInterpreterDialog(LocalFileDialog):
    def get_title(self):
        return tr("Select Python executable")

    def get_favorites(self) -> List[str]:
        result = super().get_favorites()
        for extra in [
            "/Library/Frameworks/Python.framework/Versions",
            "/usr/bin",
            "/opt/homebrew/bin",
        ]:
            if os.path.isdir(extra) and extra not in result:
                result.append(extra)

        return result


def find_local_cpython_executables():
    result = set()

    if running_on_windows():
        # registry
        result.update(_get_interpreters_from_windows_registry())

        for version in thonny.SUPPORTED_VERSIONS:
            no_dot = version.replace(".", "")
            for dir_ in [
                "C:\\Python%s" % no_dot,
                "C:\\Python%s-32" % no_dot,
                "C:\\Python%s-64" % no_dot,
                "C:\\Program Files\\Python %s" % version,
                "C:\\Program Files\\Python %s-64" % version,
                "C:\\Program Files (x86)\\Python %s" % version,
                "C:\\Program Files (x86)\\Python %s-32" % version,
                "C:\\Program Files (x86)\\Python %s-32" % version,
                os.path.expanduser(r"~\AppData\Local\Programs\Python\Python%s" % no_dot),
                os.path.expanduser(r"~\AppData\Local\Programs\Python\Python%s-32" % no_dot),
            ]:
                path = os.path.join(dir_, WINDOWS_EXE)
                if os.path.exists(path):
                    result.add(normpath_with_actual_case(path))

        # other locations
        for dir_ in [
            "C:\\Anaconda3",
            "C:\\ProgramData\\Anaconda3",
            os.path.expanduser("~\\Anaconda3"),
        ]:
            path = os.path.join(dir_, WINDOWS_EXE)
            if os.path.exists(path):
                result.add(normpath_with_actual_case(path))

    else:
        # Common unix locations
        dirs = [
            "/bin",
            "/usr/bin",
            "/usr/local/bin",
            os.path.expanduser("~/.local/bin"),
            os.path.expanduser("~/anaconda3/bin"),
        ]

        workon_home = os.environ.get("WORKON_HOME", os.path.expanduser("~/.virtualenvs"))
        virtualenvwrapper = os.path.join(workon_home, "*/bin")
        dirs += glob.glob(virtualenvwrapper)

        for dir_ in dirs:
            # if the dir_ is just a link to another dir_, skip it
            # (not to show items twice)
            # for example on Fedora /bin -> usr/bin
            if not os.path.exists(dir_):
                continue

            apath = normpath_with_actual_case(dir_)
            if apath != dir_ and apath in dirs:
                continue
            for version in ["3"] + thonny.SUPPORTED_VERSIONS:
                name = "python" + version
                path = os.path.join(dir_, name)
                if os.path.exists(path):
                    result.add(path)

    if running_on_mac_os():
        for version in thonny.SUPPORTED_VERSIONS:
            path = os.path.join(
                "/Library/Frameworks/Python.framework/Versions", version, "bin", "python" + version
            )

            if os.path.exists(path):
                result.add(path)

    from shutil import which

    for version in thonny.SUPPORTED_VERSIONS:
        command = "python" + version
        path = which(command)
        if path is not None and os.path.isabs(path):
            result.add(path)

    for conf in get_workbench().get_option(f"LocalCPython.last_configurations"):
        path = conf["LocalCPython.executable"]
        if os.path.exists(path):
            result.add(normpath_with_actual_case(path))

    # TODO: remove softlinked duplicates?

    sorted_result = sorted(result)

    # bundled python
    default_path = get_default_cpython_executable_for_backend()
    if is_private_python(default_path):
        sorted_result.insert(0, default_path)

    return sorted_result
