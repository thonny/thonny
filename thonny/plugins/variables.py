# -*- coding: utf-8 -*-

from thonny.memory import VariablesFrame
from thonny.globals import get_workbench

class GlobalsView(VariablesFrame):
    def __init__(self, master):
        VariablesFrame.__init__(self, master)
        
        get_workbench().bind("DebuggerResponse", self._update)
        get_workbench().bind("ToplevelResponse", self._update)
        get_workbench().bind("InputRequest", self._update)

    def _update(self, event):
        # TODO: request globals itself?
        msg = event.msg
        if hasattr(msg, "globals"):
            # TODO: handle other modules as well
            self.update_variables(event.globals["__main__"])
    

def load_plugin():
    get_workbench().add_view(GlobalsView, "Variables", "ne")