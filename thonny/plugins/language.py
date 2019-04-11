import tkinter as tk
from tkinter import ttk

from thonny import get_workbench
from thonny.config_ui import ConfigurationPage


class GeneralConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        self._language_var = get_workbench().get_variable("general.language")
        self._language_label = ttk.Label(self, text="Language")
        self._language_label.grid(
            row=7, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0)
        )
        languages = ["English", "Francais"]
        self._language_combo = ttk.Combobox(
            self,
            width=7,
            exportselection=False,
            textvariable=self._language_var,
            state="readonly",
            height=15,
            values=languages,
        )
        self._language_combo.grid(row=7, column=1, sticky=tk.W, pady=(10, 0))

        self.columnconfigure(1, weight=1)


def load_plugin() -> None:
    get_workbench().add_configuration_page("Language", GeneralConfigurationPage)
