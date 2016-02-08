import tkinter as tk
from tkinter import font as tk_font 
from tkinter import ttk

from thonny.config_ui import ConfigurationPage
from thonny.globals import get_workbench
from thonny.ui_utils import create_string_var
import textwrap


class EditorConfigurationPage(ConfigurationPage):
    
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        
        self._line_numbers_var = get_workbench().get_variable("view.show_line_numbers")
        self._line_length_var = get_workbench().get_variable("view.recommended_line_length")
        self._family_variable = create_string_var(
            get_workbench().get_option("view.editor_font_family"),
            modification_listener=self._update_preview_font)
        self._size_variable = create_string_var(
            get_workbench().get_option("view.editor_font_size"),
            modification_listener=self._update_preview_font)
        
        
        # Line numbers
        self._line_numbers_checkbox = ttk.Checkbutton(self, text="Show line numbers", 
                                                      variable=self._line_numbers_var)
        self._line_numbers_checkbox.grid(row=0, column=0, sticky=tk.W)
        
        # Linge length recommender
        ttk.Label(self, text="Recommended maximum line length\n(Set to 0 to turn off margin line)").grid(row=1, column=0, sticky=tk.W)
        self._line_length_combo = ttk.Combobox(self, width=4,
                                        exportselection=False,
                                        textvariable=self._line_length_var,
                                        state='readonly',
                                        values=[0,60,70,80,90,100,110,120])
        self._line_length_combo.grid(row=2, column=0, sticky=tk.W)
        
                
        ttk.Label(self, text="Editor font").grid(row=10, column=0, sticky="w")
        
        self._family_combo = ttk.Combobox(self,
                                          exportselection=False,
                                          state='readonly',
                                          textvariable=self._family_variable,
                                          values=self._get_families_to_show())
        self._family_combo.grid(row=11, column=0, sticky=tk.NSEW, padx=(0,10))
        
        ttk.Label(self, text="Size").grid(row=10, column=1, sticky="w")
        self._size_combo = ttk.Combobox(self, width=4,
                                        exportselection=False,
                                        textvariable=self._size_variable,
                                        state='readonly',
                                        values=[str(x) for x in range(3,73)])
        
        self._size_combo.grid(row=11, column=1)
        
        
        ttk.Label(self, text="Preview").grid(row=12, column=0, sticky="w", pady=(10,0))
        self._preview_font = tk_font.Font()
        self._preview_text = tk.Text(self,
                                height=10,
                                borderwidth=1,
                                font=self._preview_font,
                                wrap=tk.WORD)
        self._preview_text.insert("1.0", textwrap.dedent("""
            The quick brown fox jumps over the lazy dog
            
            ABCDEFGHIJKLMNOPQRSTUVWXYZ
            abcdefghijklmnopqrstuvwxyz
            
            1234567890
            @$%()[]{}/\_-+
            "Hello " + 'world!'""").strip())
        self._preview_text.grid(row=13, column=0, columnspan=2, sticky=tk.NSEW, pady=(0,5))
        
            
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self._update_preview_font()
    
    def apply(self):
        if (not self._family_variable.modified
            and not self._size_variable.modified):
            return
        
        get_workbench().set_option("view.editor_font_size", int(self._size_variable.get()))
        get_workbench().set_option("view.editor_font_family", self._family_variable.get())
        get_workbench().update_fonts()
    
    def _update_preview_font(self):
        self._preview_font.configure(family=self._family_variable.get(),
                                     size=int(self._size_variable.get()))
    
    def _get_families_to_show(self):
        return sorted(filter(
            lambda name : name[0].isalpha(),          
            tk_font.families()
        ))

def load_plugin():
    get_workbench().add_configuration_page("Editor", EditorConfigurationPage)
