import tkinter as tk
from tkinter import ttk

from thonny.config_ui import ConfigurationPage
from thonny.globals import get_workbench


class EditorConfigurationPage(ConfigurationPage):
    
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        
        self._line_numbers_var = get_workbench().get_variable("view.show_line_numbers")
        self._line_length_var = get_workbench().get_variable("view.recommended_line_length")
        
        
        self._line_numbers_checkbox = ttk.Checkbutton(self, text="Show line numbers", 
                                                      variable=self._line_numbers_var)
        self._line_numbers_checkbox.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(self, text="Recommended maximum line length\n(Set to 0 to turn off margin line)").grid(row=1, column=0, sticky=tk.W)
        self._line_length_combo = ttk.Combobox(self, width=4,
                                        exportselection=False,
                                        textvariable=self._line_length_var,
                                        state='readonly',
                                        values=[0,60,70,80,90,100,110,120])
        self._line_length_combo.grid(row=1, column=1, sticky=tk.E)
        self.columnconfigure(0, weight=1)
        
                

def load_plugin():
    get_workbench().add_configuration_page("Editor", EditorConfigurationPage)
