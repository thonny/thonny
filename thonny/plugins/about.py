# -*- coding: utf-8 -*-

import datetime
import platform
import sys
import tkinter as tk
import tkinter.font
from logging import getLogger
from tkinter import ttk

import thonny
from thonny import get_workbench, ui_utils
from thonny.common import get_python_version_string
from thonny.languages import tr
from thonny.ui_utils import CommonDialog, CommonDialogEx, create_url_label, get_hyperlink_cursor

logger = getLogger(__name__)


class AboutDialog(CommonDialogEx):
    def __init__(self, master):
        super().__init__(master)

        self.title(tr("About Thonny"))
        self.resizable(height=tk.FALSE, width=tk.FALSE)

        default_heading_font = tkinter.font.nametofont("TkHeadingFont")
        heading_font = default_heading_font.copy()
        heading_font.configure(size=int(default_heading_font["size"] * 1.7), weight="bold")
        heading_label = ttk.Label(
            self.main_frame, text="Thonny " + thonny.get_version(), font=heading_font
        )
        heading_label.grid(pady=(self.get_large_padding(), self.get_small_padding()))

        url_label = create_url_label(self.main_frame, "https://thonny.org", justify=tk.CENTER)
        url_label.grid()

        if sys.platform == "linux":
            try:
                import distro  # distro don't need to be installed

                system_desc = distro.name(True)
            except ImportError:
                system_desc = "Linux"

            if "32" not in system_desc and "64" not in system_desc:
                system_desc += self.get_os_word_size_suffix()
        elif sys.platform == "darwin":
            mac_ver = platform.mac_ver()[0]
            mac_arch = platform.mac_ver()[2]
            system_desc = f"macOS {mac_ver} ({mac_arch})"
        else:
            release = platform.release()
            if sys.platform == "win32":
                # Win 10 and 11 both give 10 as release
                try:
                    build = int(platform.version().split(".")[2])
                    if release == "10" and build >= 22000:
                        release = "11"
                except Exception:
                    logger.exception("Could not determine Windows version")

            system_desc = platform.system() + " " + release + self.get_os_word_size_suffix()

        platform_label = ttk.Label(
            self.main_frame,
            justify=tk.CENTER,
            text=system_desc
            + "\n"
            + "Python "
            + get_python_version_string()
            + "\n"
            + "Tk "
            + ui_utils.get_tk_version_str(),
        )
        platform_label.grid(pady=self.get_medium_padding())

        credits_label = create_url_label(
            self.main_frame,
            "https://github.com/thonny/thonny/blob/master/CREDITS.rst",
            tr(
                "Made in\n"
                + "University of Tartu, Estonia,\n"
                + "with the help from\n"
                + "open-source community,\n"
                + "Raspberry Pi Foundation\n"
                + "and Cybernetica AS"
            ),
            justify=tk.CENTER,
        )
        credits_label.grid()

        default_font = tkinter.font.nametofont("TkDefaultFont")
        license_font = default_font.copy()
        license_font.configure(size=round(default_font["size"] * 0.7))
        license_label = ttk.Label(
            self.main_frame,
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
        license_label.grid(pady=self.get_medium_padding())

        ok_button = ttk.Button(
            self.main_frame, text=tr("OK"), command=self.on_close, default="active"
        )
        ok_button.grid(pady=(0, self.get_large_padding()))
        ok_button.focus_set()

        self.bind("<Return>", self.on_close, True)

    def get_os_word_size_suffix(self):
        if "32" in platform.machine() and "64" not in platform.machine():
            return " (32-bit)"
        else:
            return ""


def load_plugin() -> None:
    def open_about():
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
