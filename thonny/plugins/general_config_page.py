import tkinter as tk
from tkinter import ttk

from thonny.config_ui import ConfigurationPage
from thonny.globals import get_workbench


class GeneralConfigurationPage(ConfigurationPage):
    
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        
        self._single_instance_var = get_workbench().get_variable("general.single_instance")
        
        self._single_instance_checkbox = ttk.Checkbutton(self,
                                                         text="Allow only single Thonny instance"
                                                            + "\n(close and reopen Thonny after changing this)", 
                                                      variable=self._single_instance_var)
        self._single_instance_checkbox.grid(row=0, column=0, sticky=tk.W)
        self.columnconfigure(0, weight=1)

            
    

def load_plugin():
    get_workbench().add_configuration_page("General", GeneralConfigurationPage)
