import logging
import tkinter as tk
from tkinter import ttk

from thonny import get_workbench
from thonny.config_ui import ConfigurationPage


class ShellConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)

        soft_max_chars_var = get_workbench().get_variable(
            "shell.soft_max_chars"
        )
        label = ttk.Label(
            self,
            text=_("Preferred size of output history (scroll buffer) in characters.\n"
                   + "This does not constrain last block, which is always shown in full.\n"
                   + "NB! Larger values may cause poor performance!"),
        )
        label.grid(row=20, column=0, sticky=tk.W)
        self._line_length_combo = ttk.Combobox(
            self,
            width=9,
            exportselection=False,
            textvariable=soft_max_chars_var,
            state="readonly",
            values=[1000, 5000, 10000, 50000, 100000, 500000, 1000000],
        )
        self._line_length_combo.grid(row=20, column=1, sticky=tk.W, padx=10)

        self.columnconfigure(1, weight=1)

def load_plugin() -> None:
    get_workbench().add_configuration_page(_("Shell"), ShellConfigurationPage)
