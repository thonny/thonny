# -*- coding: utf-8 -*-

from tkinter import ttk

from thonny.memory import VariablesFrame
from thonny import get_workbench, get_runner
from thonny.common import InlineCommand
from thonny.ui_utils import create_string_var

class GlobalsView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        get_workbench().set_default("view.globals_module_selector", False)
        
        self._module_name_variable = create_string_var("__main__",
            modification_listener=self._request_globals)
        self.module_name_combo = ttk.Combobox(self,
                                        exportselection=False,
                                        textvariable=self._module_name_variable,
                                        state='readonly',
                                        height=20,
                                        values=[])
        
        if (get_workbench().get_option("view.globals_module_selector")
            and get_workbench().get_mode() != "simple"
            or self._module_name_variable.get() != "__main__"):
            self.module_name_combo.grid(row=0, column=0, sticky="nsew")
        
        self.variables_frame = VariablesFrame(self)
        self.variables_frame.grid(row=1, column=0, sticky="nsew")
        
        self.error_label = ttk.Label(self, text="Error", anchor="center")
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        get_workbench().bind("Globals", self._handle_globals_event, True)
        get_workbench().bind("BackendRestart", lambda e=None: self.variables_frame._clear_tree(), True)
        get_workbench().bind("DebuggerProgress", self._handle_progress, True)
        get_workbench().bind("ToplevelResult", self._handle_progress, True)
        get_workbench().bind("InputRequest", self._handle_progress, True)
    
    def before_show(self):
        self._handle_progress(even_when_hidden=True)
    
    def _handle_globals_event(self, event):
        # TODO: handle other modules as well
        error = getattr(event, "error", None)
        if error:
            self.error_label.configure(text=error)
            if self.variables_frame.winfo_ismapped():
                self.variables_frame.grid_remove()
            if not self.error_label.winfo_ismapped():
                self.error_label.grid(row=1, column=0, sticky="nsew")
        else:
            self.variables_frame.update_variables(event.globals)
            if self.error_label.winfo_ismapped():
                self.error_label.grid_remove()
            if not self.variables_frame.winfo_ismapped():
                self.variables_frame.grid(row=1, column=0, sticky="nsew")
    
    def _handle_progress(self, event=None, even_when_hidden=False):
        if not getattr(self, "hidden", False) or even_when_hidden:
            self._update_modules_list(event)
            self._request_globals()
    
    def _request_globals(self, event=None):    
            # TODO: module_name
            get_runner().send_command(InlineCommand("get_globals", 
                                                    module_name=self._module_name_variable.get()))
    
    def _update_modules_list(self, event):
        if not hasattr(event, "loaded_modules"):
            return
        else:
            self.module_name_combo.configure(values=sorted(event.loaded_modules))
    

def load_plugin():
    get_workbench().add_view(GlobalsView, "Variables", "ne", default_position_key="AAA")