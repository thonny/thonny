from thonny import get_workbench
from thonny.config_ui import ConfigurationPage, add_option_checkbox, add_text_row
from thonny.languages import tr
from thonny.misc_utils import running_on_mac_os


class TerminalConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        add_text_row(self, tr("Running current script in terminal") + ":")

        add_option_checkbox(
            self,
            "run.run_in_terminal_python_repl",
            tr("Present Python REPL after program ends"),
        )

        add_option_checkbox(
            self,
            "run.run_in_terminal_keep_open",
            tr("Keep terminal window open after Python process ends"),
        )

        if running_on_mac_os():
            add_text_row(
                self,
                tr(
                    "NB! Automatic closing needs to be enabled in Terminal's settings\n"
                    + "(Profiles → Shell → When the shell exits)"
                ),
            )


def load_plugin():
    get_workbench().add_configuration_page(
        "terminal", tr("Terminal"), TerminalConfigurationPage, 60
    )
