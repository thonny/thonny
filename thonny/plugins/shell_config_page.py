import logging
import tkinter as tk
from tkinter import ttk

from thonny import get_workbench
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr


class ShellConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        self.columnconfigure(1, weight=1)

        self.add_checkbox(
            "shell.tty_mode",
            tr("Terminal emulation")
            + " ("
            + tr("supports basic ANSI-colors and styles")
            + ", \\a, \\r, \\b)",
            10,
            0,
            columnspan=2,
            pady=(0, 10),
        )

        max_lines_var = get_workbench().get_variable("shell.max_lines")
        max_lines_label = ttk.Label(
            self,
            text=tr(
                tr("Maximum number of lines to keep.")
                + "\n"
                + tr("NB! Large values may cause poor performance!")
            ),
        )
        max_lines_label.grid(row=20, column=0, sticky=tk.W)
        max_lines_combo = ttk.Combobox(
            self,
            width=9,
            exportselection=False,
            textvariable=max_lines_var,
            state="readonly",
            values=[100, 500, 1000, 5000, 10000, 50000, 100000],
        )
        max_lines_combo.grid(row=20, column=1, sticky=tk.W, padx=10)

        squeeze_var = get_workbench().get_variable("shell.squeeze_threshold")
        squeeze_label = ttk.Label(
            self, text=tr("Maximum length of line fragments before squeezing")
        )
        squeeze_label.grid(row=22, column=0, sticky="w")
        squeeze_combo = ttk.Combobox(
            self,
            width=9,
            exportselection=False,
            textvariable=squeeze_var,
            state="readonly",
            values=[500, 1000, 1500, 2000, 3000, 4000, 5000, 10000],
        )
        squeeze_combo.grid(row=22, column=1, sticky=tk.W, padx=10, pady=10)

        self.add_checkbox(
            "shell.auto_inspect_values",
            tr("Open evaluated values in Object inspector"),
            30,
            0,
            columnspan=2,
            pady=(0, 10),
        )


def load_plugin() -> None:
    get_workbench().add_configuration_page("shell", tr("Shell"), ShellConfigurationPage, 70)
