from thonny.config_ui import ConfigurationPage
from thonny import get_workbench

class TerminalConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        self.add_checkbox(
            "run.run_in_terminal_repl",
            "Present REPL after program ends with 'Run → Run current script in terminal'",
        )


def load_plugin():
    get_workbench().add_configuration_page("Terminal", TerminalConfigurationPage)
    