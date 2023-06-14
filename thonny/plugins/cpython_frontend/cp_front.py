import os.path
import subprocess
import sys
import textwrap
import tkinter as tk
import traceback
from logging import getLogger
from tkinter import messagebox, ttk
from typing import Any, Dict

import thonny
from thonny import get_runner, get_shell, get_workbench, running, ui_utils
from thonny.common import (
    InlineCommand,
    InlineResponse,
    ToplevelCommand,
    get_base_executable,
    is_private_python,
    is_virtual_executable,
    normpath_with_actual_case,
)
from thonny.languages import tr
from thonny.misc_utils import running_on_mac_os, running_on_windows
from thonny.plugins.backend_config_page import BackendDetailsConfigPage
from thonny.running import WINDOWS_EXE, SubprocessProxy, get_front_interpreter_for_subprocess
from thonny.terminal import run_in_terminal
from thonny.ui_utils import askdirectory, askopenfilename, create_string_var

logger = getLogger(__name__)


class LocalCPythonProxy(SubprocessProxy):
    def __init__(self, clean: bool) -> None:
        logger.info("Creating LocalCPythonProxy")
        executable = get_workbench().get_option("LocalCPython.executable")
        self._expecting_response_for_gui_update = False
        super().__init__(clean, executable)
        try:
            self._send_msg(ToplevelCommand("get_environment_info"))
        except Exception:
            get_shell().report_exception()

    def _get_initial_cwd(self):
        return get_workbench().get_local_cwd()

    def _get_launch_cwd(self):
        # use a directory which doesn't contain misleading modules
        empty_dir = os.path.join(thonny.THONNY_USER_DIR, "leave_this_empty")
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
        cmd = [self._mgmt_executable]
        if interactive:
            cmd.append("-i")
        cmd.append(os.path.basename(script_path))
        cmd.extend(args)

        run_in_terminal(cmd, os.path.dirname(script_path), keep_open=keep_open)

    def get_pip_gui_class(self):
        from thonny.plugins.cpython_frontend.cp_pip_gui import LocalCPythonPipDialog

        return LocalCPythonPipDialog

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
    def get_switcher_entries(cls):
        confs = sorted(
            cls.get_last_configurations(), key=lambda conf: conf[f"{cls.backend_name}.executable"]
        )
        default_exe = get_default_cpython_executable_for_backend()
        default_conf = cls._get_switcher_conf_for_executable(default_exe)
        if default_conf not in confs:
            confs.insert(0, default_conf)

        return [
            (conf, cls.get_switcher_configuration_label(conf))
            for conf in confs
            if os.path.exists(conf[f"{cls.backend_name}.executable"])
        ]

    def open_custom_system_shell(self) -> None:
        raise NotImplementedError()

    @classmethod
    def is_valid_configuration(cls, conf: Dict[str, Any]) -> bool:
        return os.path.exists(conf[f"{cls.backend_name}.executable"])


class LocalCPythonConfigurationPage(BackendDetailsConfigPage):
    def __init__(self, master):
        super().__init__(master)

        self._configuration_variable = create_string_var(
            get_workbench().get_option("LocalCPython.executable")
        )

        entry_label = ttk.Label(self, text=tr("Python executable"))
        entry_label.grid(row=0, column=1, columnspan=2, sticky=tk.W)

        self._entry = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=self._configuration_variable,
            values=_get_interpreters(),
        )
        self._entry.state(["!disabled", "readonly"])

        self._entry.grid(row=1, column=1, sticky=tk.NSEW)

        self._select_button = ttk.Button(
            self,
            text="...",
            width=3,
            command=self._select_executable,
        )
        self._select_button.grid(row=1, column=2, sticky="e", padx=(10, 0))
        self.columnconfigure(1, weight=1)

        extra_text = tr("NB! Thonny only supports Python %s and later") % "3.8"
        if running_on_mac_os():
            extra_text += "\n\n" + tr(
                "NB! File selection button may not work properly when selecting executables\n"
                + "from a virtual environment. In this case choose the 'activate' script instead\n"
                + "of the interpreter (or enter the path directly to the box)!"
            )
        extra_label = ttk.Label(self, text=extra_text)
        extra_label.grid(row=2, column=1, columnspan=2, pady=10, sticky="w")

        venv_text = tr(
            "You can activate an existing virtual environment also"
            + " via the right-click context menu in the file navagation"
            + " when selecting a virtual environment folder,"
            + " or the 'pyveng.cfg' file inside."
        )
        venv_text = "\n".join(textwrap.wrap(venv_text, 80))

        venv_label = ttk.Label(self, text=venv_text)
        venv_label.grid(row=3, column=1, columnspan=2, pady=10, sticky="w")

        last_row = ttk.Frame(self)
        last_row.grid(row=100, sticky="swe", column=1, columnspan=2)
        self.rowconfigure(100, weight=1)
        last_row.columnconfigure(1, weight=1)
        new_venv_link = ui_utils.create_action_label(
            last_row,
            "New virtual environment",
            self._create_venv,
        )
        new_venv_link.grid(row=0, column=1, sticky="e", pady=10)

        # self.columnconfigure(1, weight=1)

    def _select_executable(self):
        # TODO: get dir of current interpreter
        options = {"parent": self.winfo_toplevel()}
        if running_on_windows():
            options["filetypes"] = [
                (tr("Python interpreters"), "python.exe"),
                (tr("all files"), ".*"),
            ]

        filename = askopenfilename(**options)
        if not filename:
            return

        if filename.endswith("/activate"):
            filename = filename[: -len("activate")] + "python3"

        if filename:
            self._configuration_variable.set(filename)

    def _create_venv(self, event=None):
        if not _check_venv_installed(self):
            return

        messagebox.showinfo(
            "Creating new virtual environment",
            "After clicking 'OK' you need to choose an empty directory, "
            "which will be the root of your new virtual environment.",
            parent=self,
        )
        path = None
        while True:
            path = askdirectory(
                parent=self.winfo_toplevel(),
                initialdir=path,
                title=tr("Select empty directory for new virtual environment"),
            )
            if not path:
                return

            if os.listdir(path):
                messagebox.showerror(
                    tr("Bad directory"),
                    tr("Selected directory is not empty.\nSelect another or cancel."),
                    master=self,
                )
            else:
                break
        assert os.path.isdir(path)
        path = normpath_with_actual_case(path)

        proc = subprocess.Popen(
            [running.get_front_interpreter_for_subprocess(), "-m", "venv", path],
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        from thonny.workdlg import SubprocessDialog

        dlg = SubprocessDialog(self, proc, tr("Creating virtual environment"), autostart=True)
        ui_utils.show_dialog(dlg)

        if running_on_windows():
            exe_path = normpath_with_actual_case(os.path.join(path, "Scripts", "python.exe"))
        else:
            exe_path = os.path.join(path, "bin", "python3")

        if os.path.exists(exe_path):
            self._configuration_variable.set(exe_path)

    def should_restart(self):
        return self._configuration_variable.modified

    def apply(self):
        if not self.should_restart():
            return

        path = self._configuration_variable.get()
        if os.path.isfile(path):
            get_workbench().set_option("LocalCPython.executable", path)


def _get_interpreters():
    result = set()

    if running_on_windows():
        # registry
        result.update(_get_interpreters_from_windows_registry())

        for minor in [8, 9, 10, 11, 12]:
            for dir_ in [
                "C:\\Python3%d" % minor,
                "C:\\Python3%d-32" % minor,
                "C:\\Python3%d-64" % minor,
                "C:\\Program Files\\Python 3.%d" % minor,
                "C:\\Program Files\\Python 3.%d-64" % minor,
                "C:\\Program Files (x86)\\Python 3.%d" % minor,
                "C:\\Program Files (x86)\\Python 3.%d-32" % minor,
                "C:\\Program Files (x86)\\Python 3.%d-32" % minor,
                os.path.expanduser(r"~\AppData\Local\Programs\Python\Python3%d" % minor),
                os.path.expanduser(r"~\AppData\Local\Programs\Python\Python3%d-32" % minor),
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
        for dir_ in dirs:
            # if the dir_ is just a link to another dir_, skip it
            # (not to show items twice)
            # for example on Fedora /bin -> usr/bin
            if not os.path.exists(dir_):
                continue

            apath = normpath_with_actual_case(dir_)
            if apath != dir_ and apath in dirs:
                continue
            for name in [
                "python3",
                "python3.8",
                "python3.9",
                "python3.10",
                "python3.11",
                "python3.12",
            ]:
                path = os.path.join(dir_, name)
                if os.path.exists(path):
                    result.add(path)

    if running_on_mac_os():
        for version in ["3.8", "3.9", "3.10", "3.11", "3.12"]:
            dir_ = os.path.join("/Library/Frameworks/Python.framework/Versions", version, "bin")
            path = os.path.join(dir_, "python3")

            if os.path.exists(path):
                result.add(path)

    from shutil import which

    for command in ["python3", "python3.8", "python3.9", "python3.10", "python3.11", "python3.12"]:
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


def get_default_cpython_executable_for_backend() -> str:
    if is_private_python(sys.executable) and is_virtual_executable(sys.executable):
        # Private venv. Make an exception and use base Python for default backend.
        default_path = get_base_executable()
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
        for version in [
            "3.8",
            "3.8-32",
            "3.8-64",
            "3.9",
            "3.9-32",
            "3.9-64",
            "3.10",
            "3.10-32",
            "3.10-64",
        ]:
            for subkey in [
                "SOFTWARE\\Python\\PythonCore\\" + version + "\\InstallPath",
                "SOFTWARE\\Python\\PythonCore\\Wow6432Node\\" + version + "\\InstallPath",
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


def _check_venv_installed(parent):
    try:
        import venv

        return True
    except ImportError:
        messagebox.showerror("Error", "Package 'venv' is not available.", parent=parent)
        return False
