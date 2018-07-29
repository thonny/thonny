# -*- coding: utf-8 -*-

from tkinter import ttk

from thonny.memory import VariablesFrame
from thonny import get_workbench
import warnings

class VariablesView(VariablesFrame):
    # TODO: Indicate invalid state when program or debug command is running more than a second
    def __init__(self, master):
        super().__init__(master)
        
        ttk.Style().configure("Centered.TButton", justify="center")
        self.home_button = ttk.Button(self.tree, style="Centered.TButton", 
                                      text="Back to\ncurrent frame",
                                      width=15)
        #self.home_button.place(relx=1, x=-5, y=5, anchor="ne")
        
        get_workbench().bind("BackendRestart", self._handle_backend_restart, True)
        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)
        get_workbench().bind("get_frame_info_response", self._handle_frame_info_event, True)
    
    def _handle_backend_restart(self, event):
        self._clear_tree()
    
    def _handle_toplevel_response(self, event):
        self.show_globals(event["globals"], "__main__")
    
    def show_globals(self, globals_, module_name):
        # TODO: update only if something has changed
        self.update_variables(globals_)
        if module_name == "__main__":
            self._set_tab_caption("Variables")
        else:
            self._set_tab_caption("Variables (%s)" % module_name)
    
    def show_frame_variables(self, locals_, globals_, freevars, frame_name):
        # TODO: update only if something has changed
        actual_locals = {}
        nonlocals = {}
        for name in locals_:
            if name in freevars:
                nonlocals[name] = locals_[name]
            else:
                actual_locals[name] = locals_[name]
                
        groups = [("LOCALS", actual_locals), 
                  ("GLOBALS", globals_)]
        if nonlocals:
            groups.insert(1, ("NONLOCALS", nonlocals))
        
        self.update_variables(groups)
        self._set_tab_caption("Variables (%s)" % frame_name)
        
    def _handle_frame_info_event(self, frame_info):
        # caused by clicking on a stacktrace
        warnings.warn("What to do with non-existent frames?")
        #print("FRAI", event)
        if frame_info.get("error"):
            self.update_variables(None)
            # TODO: show error
            self._set_tab_caption("Variables")
        else:
            frame_name = "TODO:"
            self.show_frame_variables(frame_info["locals"],
                                      frame_info["globals"],
                                      frame_info["freevars"],
                                      frame_name) 
    
    def _set_tab_caption(self, text):    
        self.home_widget.master.tab(self.home_widget, text=text)
    
    

def load_plugin() -> None:
    get_workbench().add_view(VariablesView, "Variables", "e", default_position_key="AAA")