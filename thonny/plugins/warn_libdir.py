# -*- coding: utf-8 -*-

import os

import tkinter as tk
import tkinter.font
from tkinter import ttk

import thonny
from thonny import get_workbench, ui_utils
from thonny.misc_utils import get_python_version_string
from thonny.ui_utils import CommonDialog

py_cwd = ""


class Warn_LibDirDialog(CommonDialog):
    def __init__(self, master):
        super().__init__(master)

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.title(_("Warning"))
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self._ok)

        global py_cwd
        notice = (
            "Current working directory is set to "
            + py_cwd
            + ", which\n"
            + " is detected to be a library directory. It is recommended to run Thonny\n"
            + " from a different directory in order to avoid unnecessary consequences."
        )

        platform_label = ttk.Label(main_frame, justify=tk.CENTER, text=notice,)
        platform_label.grid(pady=20)

        ok_button = ttk.Button(main_frame, text="OK", command=self._ok, default="active")
        ok_button.grid(pady=(0, 15))
        ok_button.focus_set()

        self.bind("<Return>", self._ok, True)
        self.bind("<Escape>", self._ok, True)

    def _ok(self, event=None):
        self.destroy()


def load_plugin() -> None:
    global py_cwd
    py_cwd = os.getcwd()
    if py_cwd.find("site-packages") == -1 and py_cwd.find("dist-packages") == -1:
        pass  # everything safe
    else:
        ui_utils.show_dialog(Warn_LibDirDialog(get_workbench()))
