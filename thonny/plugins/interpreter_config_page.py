import tkinter as tk
import os.path
from tkinter import filedialog
from tkinter import ttk

from thonny.config_ui import ConfigurationPage
from thonny.globals import get_workbench, get_runner
from thonny.ui_utils import create_string_var
from thonny.misc_utils import running_on_windows
from thonny.running import parse_configuration


class InterpreterConfigurationPage(ConfigurationPage):
    
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        
        self._configuration_variable = create_string_var(
            get_workbench().get_option("run.backend_configuration"))
        
        entry_label = ttk.Label(self, text="Which interpreter to use for running programs?")
        entry_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self._entry = ttk.Combobox(self,
                              exportselection=False,
                              textvariable=self._configuration_variable,
                              values=self._get_configurations())
        
        self._entry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self._entry.state(['!disabled', 'readonly'])
        
        another_label = ttk.Label(self, text="Your interpreter isn't in the list?")
        another_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10,0))
        self._select_button = ttk.Button(self,
                                         text="Locate another executable "
                                         + ("(python.exe) ..." if running_on_windows() else "(python3) ...")
                                         + "\nNB! Thonny only supports Python 3.4 and later",
                                         command=self._select_executable)
        
        self._select_button.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
    
    def _get_configurations(self):
        result = []
        
        backends = get_workbench().get_backends()
        for backend_name in sorted(backends.keys()):
            backend_class = backends[backend_name]
            for configuration_option in backend_class.get_configuration_options():
                if configuration_option is None or configuration_option == "":
                    result.append(backend_name)
                else:
                    result.append("%s (%s)" % (backend_name, configuration_option))
        
        return result
    
    def _select_executable(self):
        if running_on_windows():
            options = {"filetypes" : [('Exe-files', '.exe'), ('all files', '.*')]}
        else:
            options = {}

        # TODO: get dir of current interpreter
            
        filename = filedialog.askopenfilename(**options)
        
        if filename:
            self._configuration_variable.set("Python (%s)" % os.path.realpath(filename))
    
    
    def apply(self):
        if not self._configuration_variable.modified:
            return
        
        configuration = self._configuration_variable.get()
        get_workbench().set_option("run.backend_configuration", configuration)
        
        get_runner().reset_backend()
        
    

def load_plugin():
    get_workbench().add_configuration_page("Interpreter", InterpreterConfigurationPage)
