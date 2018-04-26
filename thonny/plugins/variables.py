# -*- coding: utf-8 -*-

from tkinter import ttk

from thonny.memory import VariablesFrame
from thonny import get_workbench, get_runner
from thonny.common import InlineCommand

class GlobalsView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        self.variables_frame = VariablesFrame(self)
        self.variables_frame.grid(row=1, column=0, sticky="nsew")
        
        self.error_label = ttk.Label(self, text="Error", anchor="center")
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        get_workbench().bind("Globals", self._handle_globals_event, True)
        get_workbench().bind("BackendRestart", lambda e=None: self.variables_frame._clear_tree(), True)
        get_workbench().bind("DebuggerProgress", self._request_globals, True)
        get_workbench().bind("ToplevelResult", self._request_globals, True)
        get_workbench().bind("InputRequest", self._request_globals, True)
    
    def before_show(self):
        self._request_globals(even_when_hidden=True)
    
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
    
    def _request_globals(self, event=None, even_when_hidden=False):
        if not getattr(self, "hidden", False) or even_when_hidden:
            # TODO: module_name
            get_runner().send_command(InlineCommand("get_globals", module_name="__main__"))
    

def load_plugin():
    get_workbench().add_view(GlobalsView, "Variables", "ne", default_position_key="AAA")