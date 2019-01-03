from tkinter import ttk
from thonny.config_ui import ConfigurationPage
from thonny import get_workbench

class TerminalConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        runscript_label = ttk.Label(self, text="Running current script in terminal:")
        runscript_label.grid(row=0, column=0, sticky="w")
        
        self.add_checkbox(
            "run.run_in_terminal_python_repl",
            "Present Python REPL after program ends",
            row=1,
            padx=(12,0)
        )
        
        self.add_checkbox(
            "run.run_in_terminal_keep_open",
            "Keep terminal window open after Python process ends",
            row=2,
            pady=(0,10),
            padx=(12,0)
        )


def load_plugin():
    get_workbench().add_configuration_page("Terminal", TerminalConfigurationPage)
    