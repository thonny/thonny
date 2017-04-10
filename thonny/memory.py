# -*- coding: utf-8 -*-
 
import tkinter as tk
import tkinter.font as tk_font

from thonny.ui_utils import TreeFrame
from thonny.misc_utils import shorten_repr
from thonny.globals import get_workbench

MAX_REPR_LENGTH_IN_GRID = 100

def format_object_id(object_id):
    # this format aligns with how Python shows memory addresses
    if object_id is None:
        return None
    else:
        return "0x" + hex(object_id)[2:].upper() #.rjust(8,'0')

def parse_object_id(object_id_repr):
    return int(object_id_repr, base=16)

class MemoryFrame(TreeFrame):
    def __init__(self, master, columns):
        TreeFrame.__init__(self, master, columns)
        
        font = tk_font.nametofont("TkDefaultFont").copy()
        font.configure(underline=True)
        self.tree.tag_configure("hovered", font=font)
    
    def stop_debugging(self):
        self._clear_tree()
        
    def show_selected_object_info(self):
        iid = self.tree.focus()
        if iid != '':
            # NB! Assuming id is second column!
            id_str = self.tree.item(iid)['values'][1]
            if id_str in ["", None, "None"]:
                return
            
            object_id = parse_object_id(id_str)
            get_workbench().event_generate("ObjectSelect", object_id=object_id)
    
    
        
class VariablesFrame(MemoryFrame):
    def __init__(self, master):
        MemoryFrame.__init__(self, master, ('name', 'id', 'value'))
    
        self.tree.column('name', width=120, anchor=tk.W, stretch=False)
        self.tree.column('id', width=450, anchor=tk.W, stretch=True)
        self.tree.column('value', width=450, anchor=tk.W, stretch=True)
        
        self.tree.heading('name', text='Name', anchor=tk.W) 
        self.tree.heading('id', text='Value ID', anchor=tk.W)
        self.tree.heading('value', text='Value', anchor=tk.W)
        
        get_workbench().bind("ShowView", self._update_memory_model, True)
        get_workbench().bind("HideView", self._update_memory_model, True)
        self._update_memory_model()
        #self.tree.tag_configure("item", font=ui_utils.TREE_FONT)
        
    def destroy(self):
        MemoryFrame.destroy(self)
        get_workbench().unbind("ShowView", self._update_memory_model)
        get_workbench().unbind("HideView", self._update_memory_model)

    def _update_memory_model(self, event=None):
        if get_workbench().in_heap_mode():
            self.tree.configure(displaycolumns=("name", "id"))
            #self.tree.columnconfigure(1, weight=1, width=400)
            #self.tree.columnconfigure(2, weight=0)
        else:
            self.tree.configure(displaycolumns=("name", "value"))
            #self.tree.columnconfigure(1, weight=0)
            #self.tree.columnconfigure(2, weight=1, width=400)

    def update_variables(self, variables):
        self._clear_tree()
        
        if variables:
            for name in sorted(variables.keys()):
                
                if not name.startswith("__"):
                    node_id = self.tree.insert("", "end", tags="item")
                    self.tree.set(node_id, "name", name)
                    if isinstance(variables[name], dict):
                        repr_str = variables[name]["repr"]
                        id_str = variables[name]["id"]
                    else:
                        repr_str = variables[name]
                        id_str = None
                        
                    self.tree.set(node_id, "id", format_object_id(id_str))
                    self.tree.set(node_id, "value", shorten_repr(repr_str, MAX_REPR_LENGTH_IN_GRID))
    
    
    def on_select(self, event):
        self.show_selected_object_info()
        

