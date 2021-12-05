# -*- coding: utf-8 -*-

import datetime
import platform
import sys
import tkinter as tk
import tkinter.font
from tkinter import ttk

import thonny
from thonny import get_workbench, ui_utils
from thonny.common import get_python_version_string
from thonny.languages import tr
from thonny.ui_utils import CommonDialog, get_hyperlink_cursor


class AboutDialog(CommonDialog):
    def __init__(self, master):
        import webbrowser

        super().__init__(master)

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.title(tr("About Thonny"))
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self._ok)

        # bg_frame = ttk.Frame(self) # gives proper color in aqua
        # bg_frame.grid()

        heading_font = tkinter.font.nametofont("TkHeadingFont").copy()
        heading_font.configure(size=19, weight="bold")
        heading_label = ttk.Label(
            main_frame, text="Thonny " + thonny.get_version(), font=heading_font
        )
        heading_label.grid()

        url = "https://thonny.org"
        url_font = tkinter.font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1)
        url_label = ttk.Label(
            main_frame, text=url, style="Url.TLabel", cursor=get_hyperlink_cursor(), font=url_font
        )
        url_label.grid()
        url_label.bind("<Button-1>", lambda _: webbrowser.open(url))

        if sys.platform == "linux":
            try:
                import distro  # distro don't need to be installed

                system_desc = distro.name(True)
            except ImportError:
                system_desc = "Linux"

            if "32" not in system_desc and "64" not in system_desc:
                system_desc += " " + self.get_os_word_size_guess()
        else:
            system_desc = (
                platform.system() + " " + platform.release() + " " + self.get_os_word_size_guess()
            )

        platform_label = ttk.Label(
            main_frame,
            justify=tk.CENTER,
            text=system_desc
            + "\n"
            + "Python "
            + get_python_version_string(maxsize=sys.maxsize)
            + "\n"
            + "Tk "
            + ui_utils.get_tk_version_str(),
        )
        platform_label.grid(pady=20)

        credits_label = ttk.Label(
            main_frame,
            text=tr(
                "Made in\n"
                + "University of Tartu, Estonia,\n"
                + "with the help from\n"
                + "open-source community,\n"
                + "Raspberry Pi Foundation\n"
                + "and Cybernetica AS"
            ),
            style="Url.TLabel",
            cursor=get_hyperlink_cursor(),
            font=url_font,
            justify="center",
        )
        credits_label.grid()
        credits_label.bind(
            "<Button-1>",
            lambda _: webbrowser.open("https://github.com/thonny/thonny/blob/master/CREDITS.rst"),
        )

        license_font = tkinter.font.nametofont("TkDefaultFont").copy()
        license_font.configure(size=7)
        license_label = ttk.Label(
            main_frame,
            text="Copyright (©) "
            + str(datetime.datetime.now().year)
            + " Aivar Annamaa\n"
            + tr(
                "This program comes with\n"
                + "ABSOLUTELY NO WARRANTY!\n"
                + "It is free software, and you are welcome to\n"
                + "redistribute it under certain conditions, see\n"
                + "https://opensource.org/licenses/MIT\n"
                + "for details"
            ),
            justify=tk.CENTER,
            font=license_font,
        )
        license_label.grid(pady=20)

        ok_button = ttk.Button(main_frame, text=tr("OK"), command=self._ok, default="active")
        ok_button.grid(pady=(0, 15))
        ok_button.focus_set()

        self.bind("<Return>", self._ok, True)
        self.bind("<Escape>", self._ok, True)

    def _ok(self, event=None):
        self.destroy()

    def get_os_word_size_guess(self):
        if "32" in platform.machine() and "64" not in platform.machine():
            return "(32-bit)"
        elif "64" in platform.machine() and "32" not in platform.machine():
            return "(64-bit)"
        else:
            return ""


def load_plugin() -> None:
    def open_about(*args):
        ui_utils.show_dialog(AboutDialog(get_workbench()))

    def open_url(url):
        import webbrowser

        # webbrowser.open returns bool, but add_command expects None
        webbrowser.open(url)

    get_workbench().add_command(
        "changelog",
        "help",
        tr("Version history"),
        lambda: open_url("https://github.com/thonny/thonny/blob/master/CHANGELOG.rst"),
        group=60,
    )
    get_workbench().add_command(
        "issues",
        "help",
        tr("Report problems"),
        lambda: open_url("https://github.com/thonny/thonny/issues"),
        group=60,
    )
    get_workbench().add_command("about", "help", tr("About Thonny"), open_about, group=61)

    # For Mac
    get_workbench().createcommand("tkAboutDialog", open_about)
