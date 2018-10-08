import os.path
import subprocess
import tkinter as tk
from shutil import which
from tkinter import messagebox, ttk

from thonny import get_workbench, running, ui_utils
from thonny.common import normpath_with_actual_case
from thonny.misc_utils import running_on_mac_os, running_on_windows
from thonny.plugins.backend_config_page import BackendDetailsConfigPage
from thonny.running import WINDOWS_EXE
from thonny.ui_utils import (
    SubprocessDialog,
    askdirectory,
    askopenfilename,
    create_string_var,
)


class CustomCPythonConfigurationPage(BackendDetailsConfigPage):
    def __init__(self, master):
        super().__init__(master)

        self._configuration_variable = create_string_var(
            get_workbench().get_option("CustomInterpreter.path")
        )

        entry_label = ttk.Label(
            self, text="Which interpreter to use for running programs?"
        )
        entry_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        self._entry = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=self._configuration_variable,
            values=self._get_interpreters(),
        )

        self._entry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self._entry.state(["!disabled", "readonly"])

        another_label = ttk.Label(self, text="Your interpreter isn't in the list?")
        another_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        ttk.Style().configure("Centered.TButton", justify="center")
        self._select_button = ttk.Button(
            self,
            style="Centered.TButton",
            text="Locate another "
            + ("python.exe ..." if running_on_windows() else "python executable ...")
            + "\nNB! Thonny only supports Python 3.5 and later",
            command=self._select_executable,
        )

        self._select_button.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW)

        self._venv_button = ttk.Button(
            self,
            style="Centered.TButton",
            text="Create new virtual environment ...\n"
            + "(Select existing or create a new empty directory)",
            command=self._create_venv,
        )

        self._venv_button.grid(
            row=4, column=0, columnspan=2, sticky=tk.NSEW, pady=(5, 0)
        )

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def _select_executable(self):
        # TODO: get dir of current interpreter
        options = {"master": self}
        if running_on_windows():
            options["filetypes"] = [
                ("Python interpreters", "python.exe"),
                ("all files", ".*"),
            ]

        filename = askopenfilename(**options)

        if filename:
            self._configuration_variable.set(filename)

    def _create_venv(self):
        path = None
        while True:
            path = askdirectory(
                master=self,
                initialdir=path,
                title="Select empty directory for new virtual environment",
            )
            if not path:
                return

            if os.listdir(path):
                messagebox.showerror(
                    "Bad directory",
                    "Selected directory is not empty.\nSelect another or cancel.",
                    parent=get_workbench()
                )
            else:
                break
        assert os.path.isdir(path)
        path = normpath_with_actual_case(path)

        proc = subprocess.Popen(
            [running.get_frontend_python(), "-m", "venv", path],
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        dlg = SubprocessDialog(self, proc, "Creating virtual environment")
        ui_utils.show_dialog(dlg)

        if running_on_windows():
            exe_path = normpath_with_actual_case(
                os.path.join(path, "Scripts", "python.exe")
            )
        else:
            exe_path = os.path.join(path, "bin", "python3")

        if os.path.exists(exe_path):
            self._configuration_variable.set(exe_path)

    def _get_interpreters(self):
        result = set()

        if running_on_windows():
            # registry
            result.update(self._get_interpreters_from_windows_registry())

            for minor in [5, 6, 7, 8]:
                for dir_ in [
                    "C:\\Python3%d" % minor,
                    "C:\\Python3%d-32" % minor,
                    "C:\\Python3%d-64" % minor,
                    "C:\\Program Files\\Python 3.%d" % minor,
                    "C:\\Program Files\\Python 3.%d-64" % minor,
                    "C:\\Program Files (x86)\\Python 3.%d" % minor,
                    "C:\\Program Files (x86)\\Python 3.%d-32" % minor,
                ]:
                    path = os.path.join(dir_, WINDOWS_EXE)
                    if os.path.exists(path):
                        result.add(normpath_with_actual_case(path))

            # other locations
            for dir_ in ["C:\\Anaconda3", os.path.expanduser("~/Anaconda3")]:
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
                    "python3.5",
                    "python3.6",
                    "python3.7",
                    "python3.8",
                ]:
                    path = os.path.join(dir_, name)
                    if os.path.exists(path):
                        result.add(path)

        if running_on_mac_os():
            for version in ["3.5", "3.6", "3.7", "3.8"]:
                dir_ = os.path.join(
                    "/Library/Frameworks/Python.framework/Versions", version, "bin"
                )
                path = os.path.join(dir_, "python3")

                if os.path.exists(path):
                    result.add(path)

        for command in [
            "python3",
            "python3.5",
            "python3.5",
            "python3.6",
            "python3.7",
            "python3.8",
        ]:
            path = which(command)
            if path is not None and os.path.isabs(path):
                result.add(path)

        for path in get_workbench().get_option("CustomInterpreter.used_paths"):
            if os.path.exists(path):
                result.add(normpath_with_actual_case(path))

        return sorted(result)

    def _get_interpreters_from_windows_registry(self):
        # https://github.com/python/cpython/blob/master/Tools/msi/README.txt
        import winreg

        result = set()
        for key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for version in [
                "3.5",
                "3.5-32",
                "3.5-64",
                "3.6",
                "3.6-32",
                "3.6-64",
                "3.7",
                "3.7-32",
                "3.7-64",
                "3.8",
                "3.8-32",
                "3.8-64",
            ]:
                try:
                    for subkey in [
                        "SOFTWARE\\Python\\PythonCore\\" + version + "\\InstallPath",
                        "SOFTWARE\\Python\\PythonCore\\Wow6432Node\\"
                        + version
                        + "\\InstallPath",
                    ]:
                        dir_ = winreg.QueryValue(key, subkey)
                        if dir_:
                            path = os.path.join(dir_, WINDOWS_EXE)
                            if os.path.exists(path):
                                result.add(path)
                except Exception:
                    pass

        return result

    def should_restart(self):
        return self._configuration_variable.modified  # pylint: disable=no-member

    def apply(self):
        if not self.should_restart():
            return

        path = self._configuration_variable.get()
        if os.path.isfile(path):
            get_workbench().set_option("CustomInterpreter.path", path)
