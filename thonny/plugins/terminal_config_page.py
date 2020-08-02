from tkinter import ttk

from thonny import get_workbench
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr
from thonny.misc_utils import running_on_mac_os


class TerminalConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        runscript_label = ttk.Label(self, text=tr("Running current script in terminal") + ":")
        runscript_label.grid(row=0, column=0, sticky="w")

        self.add_checkbox(
            "run.run_in_terminal_python_repl",
            tr("Present Python REPL after program ends"),
            row=1,
            padx=(12, 0),
        )

        self.add_checkbox(
            "run.run_in_terminal_keep_open",
            tr("Keep terminal window open after Python process ends"),
            row=2,
            padx=(12, 0),
        )

        exit_remark = " "
        if running_on_mac_os():
            exit_remark = tr(
                "NB! Automatic closing needs to be enabled in Terminal's settings\n"
                + "(Profiles → Shell → When the shell exits)"
            )
        remark_label = ttk.Label(self, text=exit_remark)
        remark_label.grid(row=3, column=0, sticky="w", padx=(12, 0), pady=(0, 10))


def load_plugin():
    get_workbench().add_configuration_page(
        "terminal", tr("Terminal"), TerminalConfigurationPage, 60
    )
