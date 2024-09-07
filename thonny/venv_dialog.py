import logging
import os.path
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from thonny import get_runner, get_workbench, ui_utils
from thonny.common import normpath_with_actual_case
from thonny.languages import tr
from thonny.misc_utils import inside_flatpak, running_on_windows
from thonny.ui_utils import MappingCombobox, askdirectory, askopenfilename, set_text_if_different
from thonny.workdlg import SubprocessDialog

logger = logging.getLogger(__name__)


class VenvDialog(SubprocessDialog):
    def __init__(self, master):
        self.created_executable: Optional[str] = None

        super().__init__(master, title=tr("Create new virtual environment"), autostart=False)

    def populate_main_frame(self):
        from thonny.plugins.cpython_frontend import LocalCPythonProxy
        from thonny.plugins.cpython_frontend.cp_front import find_local_cpython_executables

        epadx = self.get_large_padding()
        ipadx = self.get_small_padding()
        epady = epadx
        ipady = ipadx

        exes = find_local_cpython_executables()

        proxy = get_runner().get_backend_proxy()
        if isinstance(proxy, LocalCPythonProxy):
            current_base_cpython = proxy.get_base_executable()
        else:
            current_base_cpython = None

        logger.info("Current base executable: %r", current_base_cpython)

        if current_base_cpython is not None:
            if current_base_cpython in exes:
                exes.remove(current_base_cpython)
            exes.insert(0, current_base_cpython)

        browse_button_width = 2 if get_workbench().is_using_aqua_based_theme() else 3

        base_label = ttk.Label(self.main_frame, text=tr("Base interpreter"))
        base_label.grid(row=1, column=1, columnspan=2, sticky="w", padx=epadx, pady=(epady, 0))
        self._base_combo = MappingCombobox(
            self.main_frame, mapping={path: path for path in exes}, exportselection=False, width=30
        )
        if current_base_cpython is not None:
            self._base_combo.select_value(current_base_cpython)
        self._base_combo.grid(
            row=2, column=1, columnspan=2, sticky="we", padx=(epadx, ipadx), pady=(0, ipady)
        )
        self._base_browse_button = ttk.Button(
            self.main_frame,
            text="...",
            command=self._browse_base_interpreter,
            width=browse_button_width,
        )
        self._base_browse_button.grid(row=2, column=3, padx=(0, epadx), pady=(0, ipady))

        self._parent_label = ttk.Label(
            self.main_frame, text=tr("Parent folder of the new environment")
        )
        self._parent_label.grid(
            row=3, column=1, columnspan=2, sticky="w", padx=epadx, pady=(ipady, 0)
        )
        self._parent_combo = ttk.Combobox(self.main_frame, width=30)
        self._parent_combo.grid(
            row=4, column=1, columnspan=2, sticky="we", padx=(epadx, ipadx), pady=(0, ipady)
        )
        self._parent_browse_button = ttk.Button(
            self.main_frame,
            text="...",
            command=self._browse_parent_folder,
            width=browse_button_width,
        )
        self._parent_browse_button.grid(row=4, column=3, padx=(0, epadx), pady=(0, ipady))
        self._parent_combo.set(get_workbench().get_local_cwd())

        self._name_label = ttk.Label(self.main_frame, text=tr("Environment name"))
        self._name_label.grid(row=5, column=1, sticky="w", padx=(epadx, 0), pady=(ipady, 0))
        self._name_var = tk.StringVar(self, value="venv")
        self._name_entry = ttk.Entry(self.main_frame, width=12, textvariable=self._name_var)
        self._name_entry.grid(row=6, column=1, sticky="w", padx=(epadx, 0), pady=(0, ipady))

        self._new_exe_label = ttk.Label(
            self.main_frame, text=" " + tr("Path of the new Python executable")
        )
        self._new_exe_label.grid(
            row=5, column=2, columnspan=2, sticky="w", padx=(epadx, epadx), pady=(ipady, 0)
        )
        self._new_exe_var = tk.StringVar(self)
        self._new_exe_entry = ttk.Entry(
            self.main_frame, width=30, state="readonly", textvariable=self._new_exe_var
        )
        self._new_exe_entry.grid(
            row=6, column=2, columnspan=2, sticky="we", padx=(epadx, epadx), pady=(0, ipady)
        )

        self._base_packages_variable = tk.BooleanVar(value=False)
        self._base_packages_checkbox = ttk.Checkbutton(
            self.main_frame,
            text=tr("Include packages installed for the base interpreter"),
            variable=self._base_packages_variable,
        )
        self._base_packages_checkbox.grid(
            row=9, column=1, columnspan=2, sticky="w", padx=epadx, pady=(ipady, ipady)
        )

        self.main_frame.columnconfigure(2, weight=1)

    def get_instructions(self) -> Optional[str]:
        return (
            tr(
                "A virtual environment is basically a folder containing a special Python executable and a private set of packages,\n"
                "which are available only for the programs ran with this executable. You can create different virtual environments\n"
                "for running different programs and not worry whether the packages required by one are compatible with the others."
            )
            + "\n\n"
            + tr(
                "In order to save disk space, the folder does not contain a full Python installation, but is tied to an existing\n"
                "'base interpreter', which provides the base features, including the standard library modules and, optionally,\n"
                "shares the packages installed at the base level."
            )
            + "\n\n"
            + tr(
                "For maximum isolation and clarity, the professionals usually create a separate virtual environment for each project,\n"
                "often in a folder named 'venv' or '.venv' under the project folder."
            )
            + "\n\n"
            + tr(
                "Beginners may prefer a more universal virtual environment, which they can use for several projects.\n"
                "In such case it makes sense to create it above a specific project folder and name it e.g. 'my-school-venv'."
            )
            + "\n\n"
            + tr(
                "This dialog creates a new virtual environment by using the 'venv' module in the standard library. After creation,\n"
                "the new Python executable appears as an option in the interpreter menu."
            )
        )

    def get_ok_text(self):
        return tr("Create")

    def _browse_parent_folder(self):
        result = askdirectory(parent=self, initialdir=get_workbench().get_local_cwd())
        if result:
            self._parent_combo.set(result)

    def _browse_base_interpreter(self):
        initialdir = os.path.dirname(sys.executable)
        filetypes = [
            (tr("all files"), ".*"),
        ]
        if running_on_windows():
            filetypes.insert(
                0,
                (tr("Python interpreters"), "python.exe"),
            )

        filename = askopenfilename(parent=self, filetypes=filetypes, initialdir=initialdir)
        if not filename:
            return

        if filename.endswith("/activate"):
            filename = filename[: -len("activate")] + "python3"

        if filename:
            self._base_combo.set(filename)

    def is_ready_for_work(self):
        return self._name_var.get() and self._parent_combo.get() and self._base_combo.get()

    def start_subprocess(self):
        assert self.is_ready_for_work()
        assert os.path.isdir(self._parent_combo.get())
        target_dir = os.path.join(self._parent_combo.get(), self._name_var.get())
        cmd = [self._base_combo.get_selected_value(), "-I", "-m", "venv"]
        if self._base_packages_variable.get():
            cmd.append("--system-site-packages")
        if inside_flatpak():
            cmd.append("--without-pip")
        cmd.append(target_dir)

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )

        proc.cmd = cmd

        return proc

    def update_ui(self):
        super().update_ui()
        if self.state == "closed":
            return

        current_parent = self._parent_combo.get()
        current_name = self._name_var.get()

        if current_parent and current_name:
            if running_on_windows():
                suffix = "Scripts\\python.exe"
            else:
                suffix = "bin/python"

            new_exe = os.path.join(current_parent, current_name, suffix)
        else:
            new_exe = ""

        if new_exe != self._new_exe_var.get():
            self._new_exe_var.set(new_exe)

    def on_done(self, success):
        logger.info("Done with success=%r", success)
        if success:
            expected_exe = self._new_exe_var.get()
            if os.path.isfile(expected_exe):
                self.created_executable = expected_exe
            else:
                messagebox.showwarning(
                    parent=self,
                    title=tr("Warning"),
                    message=f"Could not find expected {expected_exe!r}",
                )

        super().on_done(success)


def create_new_virtual_environment(dialog_parent) -> Optional[str]:
    dlg = VenvDialog(dialog_parent)

    ui_utils.show_dialog(dlg)

    if dlg.created_executable is not None:
        if inside_flatpak():
            proc = subprocess.Popen(
                [dlg.created_executable, "-m", "ensurepip", "--default-pip", "--upgrade"],
                stdin=None,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            from thonny.workdlg import SubprocessDialog

            dlg = SubprocessDialog(
                dialog_parent,
                prepared_proc=proc,
                title=tr("Initializing virtual environment"),
                autostart=True,
            )
            ui_utils.show_dialog(dlg)

        return dlg.created_executable
    else:
        return None
