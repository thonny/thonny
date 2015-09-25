import tkinter as tk
from tkinter import font as tk_font 
from tkinter import ttk

from thonny.config_ui import ConfigurationPage
from thonny.globals import get_workbench
from tkinter.messagebox import showerror


class FontConfigurationPage(ConfigurationPage):
    
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        
        self._family_variable = self.get_string_var(
            get_workbench().get_option("view.editor_font_family"))
        
        self._size_variable = self.get_string_var(
            get_workbench().get_option("view.editor_font_size"))
        
        ttk.Label(self, text="Editor font family").grid(row=0, column=0, sticky="w")
        
        self._family_combo = ttk.Combobox(self,
                                          exportselection=False,
                                          state='readonly',
                                          textvariable=self._family_variable,
                                          values=self._get_families_to_show())
        self._family_combo.grid(row=1, column=0, sticky=tk.NSEW, padx=(0,10))
        
        ttk.Label(self, text="Size").grid(row=0, column=1, sticky="w")
        self._size_entry = ttk.Entry(self, width=4, exportselection=False,
                                     textvariable=self._size_variable)
        
        self._size_entry.grid(row=1, column=1)    
        self.columnconfigure(0, weight=1)
    
    def apply(self):
        min_font_size = 3
        max_font_size = 99
        
        try:
            size = int(self._size_variable.get())
            assert min_font_size <= size <= max_font_size
            
            get_workbench().set_option("view.editor_font_size", size)
            get_workbench().set_option("view.editor_font_family", self._family_variable.get())
            get_workbench().update_fonts()
            
            return True
        except:
            showerror("Error", "Font size must be integer between %d and %d" 
                      % (min_font_size, max_font_size))
            self._size_entry.focus_set()
            return False
    
    
    def _get_families_to_show(self):
        return sorted(filter(
            lambda name : name[0].isalpha(),          
            tk_font.families()
        ))

def load_plugin():
    get_workbench().add_configuration_page("Fonts", FontConfigurationPage)
