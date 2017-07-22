# -*- coding: utf-8 -*-

from thonny.memory import VariablesFrame
from thonny.globals import get_workbench, get_runner
from thonny.common import InlineCommand

class GlobalsView(VariablesFrame):
    def __init__(self, master):
        VariablesFrame.__init__(self, master)
        
        get_workbench().bind("Globals", self._handle_globals_event, True)
        get_workbench().bind("BackendRestart", lambda e=None: self._clear_tree(), True)
        get_workbench().bind("DebuggerProgress", self._request_globals, True)
        get_workbench().bind("ToplevelResult", self._request_globals, True)
    
    def before_show(self):
        self._request_globals(even_when_hidden=True)
    
    def _handle_globals_event(self, event):
        # TODO: handle other modules as well
        self.update_variables(event.globals)
    
    def _request_globals(self, event=None, even_when_hidden=False):
        if not getattr(self, "hidden", False) or even_when_hidden:
            # TODO: module_name
            get_runner().send_command(InlineCommand("get_globals", module_name="__main__"))
    

def load_plugin():
    get_workbench().add_view(GlobalsView, "Variables", "ne")