# -*- coding: utf-8 -*-

from thonny.memory import VariablesFrame

class GlobalsView(VariablesFrame):
    def __init__(self, master, workbench):
        VariablesFrame.__init__(self, master, workbench)

    def handle_vm_message(self, event):
        if hasattr(event, "globals"):
            # TODO: handle other modules as well
            self.update_variables(event.globals["__main__"])
    
    def show_module(self, module_name, frame_id=None):
        "TODO:"
    

def load_plugin(workbench):
    workbench.add_view(GlobalsView, "Variables", "ne")