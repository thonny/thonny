# -*- coding: utf-8 -*-

from thonny.memory import VariablesFrame
from thonny.globals import get_workbench, get_runner
from thonny.common import InlineCommand
from logging import debug

class GlobalsView(VariablesFrame):
    def __init__(self, master):
        VariablesFrame.__init__(self, master)
        
        get_workbench().bind("Globals", self._handle_globals_event, True)
        get_workbench().bind("DebuggerProgress", self._handle_progress_event, True)
        get_workbench().bind("ToplevelResult", self._handle_progress_event, True)

    def _handle_globals_event(self, event):
        # TODO: handle other modules as well
        self.update_variables(event.globals)

    def _handle_progress_event(self, event):
        if self.winfo_ismapped():
            # TODO: update itself also when it becomes visible
            # TODO: module_name
            get_runner().send_command(InlineCommand("get_globals", module_name="__main__"))
    

def _load_plugin():
    get_workbench().add_view(GlobalsView, "Variables", "ne")