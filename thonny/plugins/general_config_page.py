import tkinter as tk
from tkinter import ttk

from thonny import get_workbench
from thonny.config_ui import ConfigurationPage


class GeneralConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)

        self.add_checkbox(
            "general.single_instance",
            "Allow only single Thonny instance",
            row=1,
            columnspan=2,
        )
        self.add_checkbox(
            "general.debug_mode",
            "Debug mode (provides more detailed logs)",
            row=3,
            columnspan=2,
        )
        self.add_checkbox(
            "file.reopen_all_files",
            "Reopen all files from previous session",
            row=4,
            columnspan=2,
        )
        self.add_checkbox(
            "general.disable_notification_sound",
            "Disable notification sound",
            row=5,
            columnspan=2,
        )

        ttk.Label(self, text="UI mode").grid(row=6, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.add_combobox(
            "general.ui_mode",
            ["simple", "regular", "expert"],
            row=6,
            column=1,
            pady=(10, 0)
        )

        self._scaling_var = get_workbench().get_variable("general.scaling")
        self._scaling_label = ttk.Label(self, text="UI scaling factor")
        self._scaling_label.grid(
            row=7, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0)
        )
        scalings = sorted({0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0})
        self._scaling_combo = ttk.Combobox(
            self,
            width=7,
            exportselection=False,
            textvariable=self._scaling_var,
            state="readonly",
            height=15,
            values=["default"] + scalings,
        )
        self._scaling_combo.grid(row=7, column=1, sticky=tk.W, pady=(10, 0))

        reopen_label = ttk.Label(
            self,
            text="NB! Restart Thonny after changing these options"
            + "\nin order to see the full effect",
            font="BoldTkDefaultFont",
        )
        reopen_label.grid(row=9, column=0, sticky=tk.W, pady=20, columnspan=2)

        self.columnconfigure(1, weight=1)


def load_plugin() -> None:
    get_workbench().add_configuration_page("General", GeneralConfigurationPage)
