from thonny import get_workbench
from thonny.config_ui import ConfigurationPage, add_option_checkbox, add_option_combobox
from thonny.languages import tr


class ShellConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        self.columnconfigure(1, weight=1)

        add_option_checkbox(
            self,
            "shell.clear_for_new_process",
            tr("Clear Shell before starting new process (Run, Debug, Stop/Restart, ...)"),
        )

        add_option_checkbox(
            self,
            "shell.tty_mode",
            tr("Terminal emulation")
            + " ("
            + tr("supports basic ANSI-colors and styles")
            + ", \\a, \\r, \\b)",
        )

        add_option_combobox(
            self,
            "shell.max_lines",
            tr("Maximum number of lines to keep.")
            + "\n"
            + tr("NB! Large values may cause poor performance!"),
            choices=[100, 500, 1000, 5000, 10000, 50000, 100000],
        )

        add_option_combobox(
            self,
            "shell.squeeze_threshold",
            tr("Maximum length of line fragments before squeezing"),
            choices=[500, 1000, 1500, 2000, 3000, 4000, 5000, 10000],
        )

        add_option_checkbox(
            self,
            "shell.auto_inspect_values",
            tr("Open evaluated values in Object inspector"),
        )


def load_plugin() -> None:
    get_workbench().add_configuration_page("shell", tr("Shell"), ShellConfigurationPage, 70)
