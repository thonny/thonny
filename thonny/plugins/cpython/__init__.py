import logging
import os.path
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import thonny
from thonny import get_workbench, get_runner, ui_utils, THONNY_USER_DIR, running
from thonny.common import (
    ToplevelCommand,
    InlineCommand,
    is_same_path,
    normpath_with_actual_case,
    get_python_version_string,
)
from thonny.languages import tr
from thonny.misc_utils import running_on_windows, running_on_mac_os, running_on_linux
from thonny.plugins.backend_config_page import BackendDetailsConfigPage
from thonny.running import (
    SubprocessProxy,
    create_frontend_python_process,
    get_interpreter_for_subprocess,
    is_bundled_python,
    WINDOWS_EXE,
)
from thonny.terminal import run_in_terminal
from thonny.ui_utils import askdirectory, askopenfilename, create_string_var

logger = logging.getLogger(__name__)


class CPythonProxy(SubprocessProxy):
    "abstract class"

    def __init__(self, clean: bool, executable: str) -> None:
        super().__init__(clean, executable)
        self._send_msg(ToplevelCommand("get_environment_info"))

    def _get_initial_cwd(self):
        return get_workbench().get_local_cwd()

    def _get_launch_cwd(self):
        # launch in the directory containing thonny package, so that other interpreters can import it as well
        return os.path.dirname(os.path.dirname(thonny.__file__))

    def _get_launcher_with_args(self):
        return ["-m", "thonny.plugins.cpython", self.get_cwd()]

    def _store_state_info(self, msg):
        super()._store_state_info(msg)

        if "gui_is_active" in msg:
            self._update_gui_updating(msg)

    def _clear_environment(self):
        self._close_backend()
        self._start_background_process()

    def _close_backend(self):
        self._cancel_gui_update_loop()
        super()._close_backend()

    def get_local_executable(self):
        return self._executable

    def _update_gui_updating(self, msg):
        """Enables running Tkinter or Qt programs which doesn't call mainloop.

        When mainloop is omitted, then program can be interacted with
        from the shell after it runs to the end.

        Each ToplevelResponse is supposed to tell, whether gui is active
        and needs updating.
        """
        if not "gui_is_active" in msg:
            return

        if msg["gui_is_active"] and self._gui_update_loop_id is None:
            # Start updating
            self._loop_gui_update(True)
        elif not msg["gui_is_active"] and self._gui_update_loop_id is not None:
            self._cancel_gui_update_loop()

    def _loop_gui_update(self, force=False):
        if force or get_runner().is_waiting_toplevel_command():
            try:
                self.send_command(InlineCommand("process_gui_events"))
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
                    logging.exception("Could not interrupt backend process")
            else:
                self._proc.send_signal(signal.SIGINT)

    def run_script_in_terminal(self, script_path, args, interactive, keep_open):
        cmd = [self._executable]
        if interactive:
            cmd.append("-i")
        cmd.append(os.path.basename(script_path))
        cmd.extend(args)

        run_in_terminal(cmd, os.path.dirname(script_path), keep_open=keep_open)

    def get_supported_features(self):
        return {"run", "debug", "run_in_terminal", "pip_gui", "system_shell"}

    def get_pip_gui_class(self):
        from thonny.plugins.pip_gui import CPythonBackendPipDialog

        return CPythonBackendPipDialog

    def can_run_remote_files(self):
        return False

    def can_run_local_files(self):
        return True


class PrivateVenvCPythonProxy(CPythonProxy):
    def __init__(self, clean):
        self._prepare_private_venv()
        super().__init__(clean, get_private_venv_executable())

    def _prepare_private_venv(self):
        path = get_private_venv_path()
        if os.path.isdir(path) and os.path.isfile(os.path.join(path, "pyvenv.cfg")):
            self._check_upgrade_private_venv(path)
        else:
            self._create_private_venv(
                path, "Please wait!\nThonny prepares its virtual environment."
            )

    def _check_upgrade_private_venv(self, path):
        # If home is wrong then regenerate
        # If only micro version is different, then upgrade
        info = _get_venv_info(path)

        if not is_same_path(info["home"], os.path.dirname(sys.executable)):
            self._create_private_venv(
                path,
                "Thonny's virtual environment was created for another interpreter.\n"
                + "Regenerating the virtual environment for current interpreter.\n"
                + "(You may need to reinstall your 3rd party packages)\n"
                + "Please wait!.",
                clear=True,
            )
        else:
            venv_version = tuple(map(int, info["version"].split(".")))
            sys_version = sys.version_info[:3]
            assert venv_version[0] == sys_version[0]
            assert venv_version[1] == sys_version[1]

            if venv_version[2] != sys_version[2]:
                self._create_private_venv(
                    path, "Please wait!\nUpgrading Thonny's virtual environment.", upgrade=True
                )

    def _create_private_venv(self, path, description, clear=False, upgrade=False):
        if not _check_venv_installed(self):
            return
        # Don't include system site packages
        # This way all students will have similar configuration
        # independently of system Python (if Thonny is used with system Python)

        # NB! Cant run venv.create directly, because in Windows bundle
        # it tries to link venv to thonny.exe.
        # Need to run it via proper python
        args = ["-m", "venv"]
        if clear:
            args.append("--clear")
        if upgrade:
            args.append("--upgrade")

        try:
            import ensurepip
        except ImportError:
            args.append("--without-pip")

        args.append(path)

        proc = create_frontend_python_process(args)

        from thonny.workdlg import SubprocessDialog

        dlg = SubprocessDialog(
            get_workbench(),
            proc,
            "Preparing the backend",
            long_description=description,
            autostart=True,
        )
        try:
            ui_utils.show_dialog(dlg)
        except Exception:
            # if using --without-pip the dialog may close very quickly
            # and for some reason wait_window would give error then
            logging.exception("Problem with waiting for venv creation dialog")
        get_workbench().become_active_window()  # Otherwise focus may get stuck somewhere

        bindir = os.path.dirname(get_private_venv_executable())
        # create private env marker
        marker_path = os.path.join(bindir, "is_private")
        with open(marker_path, mode="w") as fp:
            fp.write("# This file marks Thonny-private venv")

        # Create recommended pip conf to get rid of list deprecation warning
        # https://github.com/pypa/pip/issues/4058
        pip_conf = "pip.ini" if running_on_windows() else "pip.conf"
        with open(os.path.join(path, pip_conf), mode="w") as fp:
            fp.write("[list]\nformat = columns")

        assert os.path.isdir(path)

    @classmethod
    def get_switcher_entries(cls):
        return []


class SameAsFrontendCPythonProxy(CPythonProxy):
    def __init__(self, clean):
        super().__init__(clean, get_interpreter_for_subprocess())

    def fetch_next_message(self):
        msg = super().fetch_next_message()
        if msg and "welcome_text" in msg:
            if is_bundled_python(self._executable):
                msg["welcome_text"] += " (bundled)"
            else:
                msg["welcome_text"] += " (" + self._executable + ")"
        return msg

    def get_clean_description(self):
        return "Python " + get_python_version_string()


class CustomCPythonProxy(CPythonProxy):
    def __init__(self, clean):
        executable = get_workbench().get_option("CustomInterpreter.path")

        # Remember the usage of this non-default interpreter
        used_interpreters = get_workbench().get_option("CustomInterpreter.used_paths")
        if executable not in used_interpreters:
            used_interpreters.append(executable)
        get_workbench().set_option("CustomInterpreter.used_paths", used_interpreters)

        super().__init__(clean, get_interpreter_for_subprocess(executable))

    def fetch_next_message(self):
        msg = super().fetch_next_message()
        if msg and "welcome_text" in msg:
            msg["welcome_text"] += " (" + self._executable + ")"
        return msg

    def get_clean_description(self):
        desc = get_workbench().get_option("CustomInterpreter.path")
        if not desc:
            desc = sys.executable

        return desc

    @classmethod
    def _get_switcher_entry_for_executable(cls, executable):
        return (
            {"run.backend_name": cls.backend_name, "CustomInterpreter.path": executable},
            executable,
        )

    @classmethod
    def get_current_switcher_configuration(cls):
        return cls._get_switcher_entry_for_executable(
            get_workbench().get_option("CustomInterpreter.path")
        )[0]

    @classmethod
    def get_switcher_entries(cls):
        return [
            cls._get_switcher_entry_for_executable(executable)
            for executable in _get_interpreters()
            if os.path.exists(executable)
        ]


def get_private_venv_path():
    if is_bundled_python(sys.executable.lower()):
        prefix = "BundledPython"
    else:
        prefix = "Python"
    return os.path.join(
        THONNY_USER_DIR, prefix + "%d%d" % (sys.version_info[0], sys.version_info[1])
    )


def get_private_venv_executable():
    venv_path = get_private_venv_path()

    if running_on_windows():
        exe = os.path.join(venv_path, "Scripts", WINDOWS_EXE)
    else:
        exe = os.path.join(venv_path, "bin", "python3")

    return exe


def _get_venv_info(venv_path):
    cfg_path = os.path.join(venv_path, "pyvenv.cfg")
    result = {}

    with open(cfg_path, encoding="UTF-8") as fp:
        for line in fp:
            if "=" in line:
                key, val = line.split("=", maxsplit=1)
                result[key.strip()] = val.strip()

    return result


class SameAsFrontEndConfigurationPage(BackendDetailsConfigPage):
    def __init__(self, master):
        super().__init__(master)
        label = ttk.Label(self, text=get_interpreter_for_subprocess())
        label.grid()

    def should_restart(self):
        return False


class PrivateVenvConfigurationPage(BackendDetailsConfigPage):
    def __init__(self, master):
        super().__init__(master)
        text = (
            tr("This virtual environment is automatically maintained by Thonny.\n")
            + tr("Location: ")
            + get_private_venv_path()
        )

        label = ttk.Label(self, text=text)
        label.grid()

    def should_restart(self):
        return False


class CustomCPythonConfigurationPage(BackendDetailsConfigPage):
    def __init__(self, master):
        super().__init__(master)

        self._configuration_variable = create_string_var(
            get_workbench().get_option("CustomInterpreter.path")
        )

        entry_label = ttk.Label(self, text=tr("Python executable"))
        entry_label.grid(row=0, column=1, columnspan=2, sticky=tk.W)

        self._entry = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=self._configuration_variable,
            values=_get_interpreters(),
        )

        self._entry.grid(row=1, column=1, sticky=tk.NSEW)

        self._select_button = ttk.Button(
            self,
            text="...",
            width=3,
            command=self._select_executable,
        )
        self._select_button.grid(row=1, column=2, sticky="e", padx=(10, 0))
        self.columnconfigure(1, weight=1)

        extra_text = tr("NB! Thonny only supports Python 3.5 and later")
        if running_on_mac_os():
            extra_text += "\n\n" + tr(
                "NB! File selection button may not work properly when selecting executables\n"
                + "from a virtual environment. In this case choose the 'activate' script instead\n"
                + "of the interpreter (or enter the path directly to the box)!"
            )
        extra_label = ttk.Label(self, text=extra_text)
        extra_label.grid(row=2, column=1, columnspan=2, pady=10, sticky="w")

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
            [running.get_interpreter_for_subprocess(), "-m", "venv", path],
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
            get_workbench().set_option("CustomInterpreter.path", path)


def _get_interpreters():
    result = set()

    if running_on_windows():
        # registry
        result.update(_get_interpreters_from_windows_registry())

        for minor in [6, 7, 8, 9, 10]:
            for dir_ in [
                "C:\\Python3%d" % minor,
                "C:\\Python3%d-32" % minor,
                "C:\\Python3%d-64" % minor,
                "C:\\Program Files\\Python 3.%d" % minor,
                "C:\\Program Files\\Python 3.%d-64" % minor,
                "C:\\Program Files (x86)\\Python 3.%d" % minor,
                "C:\\Program Files (x86)\\Python 3.%d-32" % minor,
                "C:\\Program Files (x86)\\Python 3.%d-32" % minor,
                os.path.expanduser("~\\AppData\Local\Programs\Python\Python3%d" % minor),
                os.path.expanduser("~\\AppData\Local\Programs\Python\Python3%d-32" % minor),
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
            for name in ["python3", "python3.5", "python3.6", "python3.7", "python3.8"]:
                path = os.path.join(dir_, name)
                if os.path.exists(path):
                    result.add(path)

    if running_on_mac_os():
        for version in ["3.6", "3.7", "3.8", "3.9"]:
            dir_ = os.path.join("/Library/Frameworks/Python.framework/Versions", version, "bin")
            path = os.path.join(dir_, "python3")

            if os.path.exists(path):
                result.add(path)

    from shutil import which

    for command in ["python3", "python3.6", "python3.7", "python3.8", "python3.9"]:
        path = which(command)
        if path is not None and os.path.isabs(path):
            result.add(path)

    for path in get_workbench().get_option("CustomInterpreter.used_paths"):
        if os.path.exists(path):
            result.add(normpath_with_actual_case(path))

    return sorted(result)


def _get_interpreters_from_windows_registry():
    # https://github.com/python/cpython/blob/master/Tools/msi/README.txt
    # https://www.python.org/dev/peps/pep-0514/#installpath
    import winreg

    result = set()
    for key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for version in [
            "3.6",
            "3.6-32",
            "3.6-64",
            "3.7",
            "3.7-32",
            "3.7-64",
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


def load_plugin():
    wb = get_workbench()
    wb.set_default("run.backend_name", "SameAsFrontend")
    wb.set_default("CustomInterpreter.used_paths", [])
    wb.set_default("CustomInterpreter.path", "")

    wb.add_backend(
        "SameAsFrontend",
        SameAsFrontendCPythonProxy,
        tr("The same interpreter which runs Thonny (default)"),
        SameAsFrontEndConfigurationPage,
        "01",
    )

    wb.add_backend(
        "CustomCPython",
        CustomCPythonProxy,
        tr("Alternative Python 3 interpreter or virtual environment"),
        CustomCPythonConfigurationPage,
        "02",
    )

    wb.add_backend(
        "PrivateVenv",
        PrivateVenvCPythonProxy,
        tr("A special virtual environment (deprecated)"),
        PrivateVenvConfigurationPage,
        "zz",
    )
