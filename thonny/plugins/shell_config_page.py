import logging
import tkinter as tk
from tkinter import font as tk_font
from tkinter import ttk

from thonny import get_workbench, get_shell
from thonny.config_ui import ConfigurationPage
from thonny.ui_utils import create_string_var, EnhancedTextWithLogging
from thonny.codeview import CodeView
from thonny.shell import ShellView


class ShellConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)

        max_lines_var = get_workbench().get_variable("shell.max_lines")
        max_lines_label = ttk.Label(
            self,
            text=_(
                "Maximum number of lines to keep.\n"
                + "NB! Large values may cause poor performance!"
            ),
        )
        max_lines_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        max_lines_combo = ttk.Combobox(
            self,
            width=9,
            exportselection=False,
            textvariable=max_lines_var,
            state="readonly",
            values=[100, 500, 1000, 5000, 10000, 50000, 100000],
        )
        max_lines_combo.grid(row=0, column=2, sticky="w", padx=10)

        squeeze_var = get_workbench().get_variable("shell.squeeze_threshold")
        squeeze_label = ttk.Label(
            self, text="Maximum length of line fragments before squeezing"
        )
        squeeze_label.grid(row=2, column=0, columnspan=2, sticky="w")
        squeeze_combo = ttk.Combobox(
            self,
            width=9,
            exportselection=False,
            textvariable=squeeze_var,
            state="readonly",
            values=[500, 1000, 1500, 2000, 3000, 4000, 5000, 10000],
        )
        squeeze_combo.grid(row=2, column=2, sticky="w", padx=10, pady=10)

        # ==================================================
        self._original_family = get_workbench().get_option("view.io_font_family")
        self._original_size = get_workbench().get_option("view.io_font_size")

        self._family_variable = create_string_var(
            self._original_family, modification_listener=self._update_appearance
        )

        self._size_variable = create_string_var(
            self._original_size, modification_listener=self._update_appearance
        )

        ttk.Label(self, text="Shell font").grid(
            row=5, column=0, sticky="w", pady=(10, 0)
        )
        self._family_combo = ttk.Combobox(
            self,
            exportselection=False,
            state="readonly",
            height=15,
            textvariable=self._family_variable,
            values=self._get_families_to_show(),
        )
        self._family_combo.grid(row=6, column=0, sticky="w", padx=(0, 10))

        ttk.Label(self, text="Size").grid(row=5, column=1, sticky="w", pady=(10, 0))
        self._size_combo = ttk.Combobox(
            self,
            width=4,
            exportselection=False,
            textvariable=self._size_variable,
            state="readonly",
            height=15,
            values=[str(x) for x in range(3, 73)],
        )
        self._size_combo.grid(row=6, column=1, sticky="w")

        self._text_preview = ttk.Label(
            self, text="Shell text preview", font="IOFont", background="white"
        )
        self._text_preview.grid(
            row=7, column=1, sticky="w", pady=(30, 30), columnspan=4
        )

        (
            ttk.Label(
                self, text="NB! Some style elements change only after restarting Thonny"
            ).grid(row=9, column=0, columnspan=3, sticky="w", pady=(0, 5))
        )

    def apply(self):
        return

    def cancel(self):
        if getattr(self._family_variable, "modified") or getattr(
            self._size_variable, "modified"
        ):
            get_workbench().set_option("view.io_font_size", self._original_size)
            get_workbench().set_option("view.io_font_family", self._original_family)
            get_workbench().reload_themes()
            get_workbench().update_fonts()

    def _update_appearance(self):
        get_workbench().set_option("view.io_font_size", int(self._size_variable.get()))
        get_workbench().set_option("view.io_font_family", self._family_variable.get())
        get_workbench().update_fonts()
        self._text_preview.configure(font="IOFont")
        pass

    def _get_families_to_show(self):
        # In Linux, families may contain duplicates (actually different fonts get same names)
        return sorted(set(filter(lambda name: name[0].isalpha(), tk_font.families())))


def load_plugin() -> None:
    get_workbench().add_configuration_page(_("Shell"), ShellConfigurationPage)
