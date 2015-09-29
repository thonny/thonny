import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

from thonny.config_ui import ConfigurationPage
from thonny.globals import get_workbench
from thonny.ui_utils import create_string_var
from backend_private.thonny.misc_utils import running_on_windows


class InterpreterConfigurationPage(ConfigurationPage):
    
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        
        self._interpreter_variable = create_string_var(
            get_workbench().get_option("run.interpreter"))
        
        ttk.Label(self, text="Interpreter").grid(row=0, column=0, sticky="w")
        
        self._entry = ttk.Entry(self,
                              exportselection=False,
                              textvariable=self._interpreter_variable)
        
        self._entry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        
        self._select_button = ttk.Button(self, text="Select python executable ...",
                                         command=self._select_executable)
        self._clear_button = ttk.Button(self, text="Use default",
                                        command=lambda: self._interpreter_variable.set(""))
        
        self._select_button.grid(row=2, column=0, sticky=tk.EW, pady=10)
        self._clear_button.grid(row=2, column=1, sticky=tk.E, pady=10, padx=(10,0))
        
        self.columnconfigure(0, weight=1)
    
    def _select_executable(self):
        filetypes = [('all files', '.*')]
        if running_on_windows():
            filetypes.insert(0, ('Exe-files', '.exe'))
            
        filename = filedialog.askopenfilename(
            filetypes = filetypes, 
            # TODO: get dir of current interpreter
            #initialdir = get_workbench().get_option("run.working_directory")
            )
        
        if filename:
            self._interpreter_variable.set(filename)
    
    def apply(self):
        if not self._interpreter_variable.modified:
            return
        
        get_workbench().set_option("run.interpreter", self._interpreter_variable.get())
        
    

def load_plugin():
    get_workbench().add_configuration_page("Interpreter", InterpreterConfigurationPage)
