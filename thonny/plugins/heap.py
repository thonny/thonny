# -*- coding: utf-8 -*-

import tkinter as tk

from thonny.memory import MemoryFrame, format_object_id, MAX_REPR_LENGTH_IN_GRID,\
    parse_object_id
from thonny.misc_utils import shorten_repr
from thonny.common import ActionResponse
from thonny.globals import get_workbench

class HeapView(MemoryFrame):
    def __init__(self, master):
        MemoryFrame.__init__(self, master, ("id", "value"))
        
        self.tree.column('id', width=100, anchor=tk.W, stretch=False)
        self.tree.column('value', width=150, anchor=tk.W, stretch=True)
        
        self.tree.heading('id', text='ID', anchor=tk.W)
        self.tree.heading('value', text='Value', anchor=tk.W) 

    def _update_data(self, data):
        self._clear_tree()
        for value_id in sorted(data.keys()):
            node_id = self.tree.insert("", "end")
            self.tree.set(node_id, "id", format_object_id(value_id))
            self.tree.set(node_id, "value", shorten_repr(data[value_id].repr, MAX_REPR_LENGTH_IN_GRID))
            

    def on_select(self, event):
        iid = self.tree.focus()
        if iid != '':
            object_id = parse_object_id(self.tree.item(iid)['values'][0])
            get_workbench().event_generate("ObjectSelect", object_id=object_id)
            
    def handle_vm_message(self, msg):
        if self.winfo_ismapped():
            if hasattr(msg, "heap"):
                self._update_data(msg.heap)
            elif isinstance(msg, ActionResponse):
                """
                # ask for updated heap
                vm_proxy.send_command(InlineCommand(command="get_heap"))
                """
                
def load_plugin():
    get_workbench().add_view(HeapView, "Heap", "e")