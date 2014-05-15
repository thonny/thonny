# -*- coding: utf-8 -*-
from __future__ import print_function, division 
from ui_utils import TreeFrame, TextFrame, update_entry_text, ScrollableFrame
from config import prefs
from codeview import CodeView
from common import ToplevelResponse, ActionResponse, InlineCommand
import vm_proxy
try:
    import tkinter as tk
    from tkinter import ttk
    import tkinter.font as tk_font
except ImportError:
    import Tkinter as tk
    import ttk 
    import tkFont as tk_font


def format_object_id(object_id):
    return "@" + str(object_id)

class MemoryFrame(TreeFrame):
    def __init__(self, master, columns):
        TreeFrame.__init__(self, master, columns)
    
    def stop_debugging(self):
        self._clear_tree()
        
    def change_font_size(self, delta):
        pass
    
        
class VariablesFrame(MemoryFrame):
    def __init__(self, master):
        MemoryFrame.__init__(self, master, ('name', 'id', 'value'))
    
        self.tree.column('name', width=90, anchor=tk.W, stretch=False)
        self.tree.column('id', width=150, anchor=tk.W, stretch=False)
        self.tree.column('value', width=150, anchor=tk.W, stretch=True)
        
        self.tree.heading('name', text='Name', anchor=tk.W) 
        self.tree.heading('id', text='Id', anchor=tk.W)
        self.tree.heading('value', text='Value', anchor=tk.W)
        
        self.update_memory_model()
        #self.tree.tag_configure("item", font=ui_utils.TREE_FONT)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select, "+")

    def show_object(self, event):
        print("show object", event)

    def update_memory_model(self):
        if prefs["values_in_heap"]:
            self.tree.configure(displaycolumns=("name", "id"))
        else:
            self.tree.configure(displaycolumns=("name", "value"))

    def update_variables(self, variables):
        self._clear_tree()
        
        if variables:
            for name in sorted(variables.keys()):
                
                if not name.startswith("__"): # TODO: consult prefs
                    node_id = self.tree.insert("", "end", tags="item")
                    self.tree.set(node_id, "name", name)
                    self.tree.set(node_id, "id", format_object_id(variables[name].id))
                    self.tree.set(node_id, "value", variables[name].short_repr)
    
    def on_select(self, event):
        iid = self.tree.focus()
        if iid != '':
            object_id = int(self.tree.item(iid)['values'][1].strip("@"))
            self.event_generate("<<ObjectSelect>>", serial=object_id)
            
        
class GlobalsFrame(VariablesFrame):
    def __init__(self, master):
        VariablesFrame.__init__(self, master)

    def handle_vm_message(self, event):
        if hasattr(event, "globals"):
            # TODO: handle other modules as well
            self.update_variables(event.globals["__main__"])
    
    def show_module(self, module_name, frame_id=None):
        "TODO:"
    

class LocalsFrame(VariablesFrame):   
    def handle_vm_message(self, event):
        pass

    def show_frame(self, frame):
        "TODO:"
    

class HeapFrame(MemoryFrame):
    def __init__(self, master):
        MemoryFrame.__init__(self, master, ("id", "value"))
        
        self.tree.column('id', width=100, anchor=tk.W, stretch=False)
        self.tree.column('value', width=150, anchor=tk.W, stretch=True)
        
        self.tree.heading('id', text='Id', anchor=tk.W)
        self.tree.heading('value', text='Description', anchor=tk.W) 

    def _update_data(self, data):
        self._clear_tree()
        for value_id in sorted(data.keys()):
            node_id = self.tree.insert("", "end")
            self.tree.set(node_id, "id", format_object_id(value_id))
            self.tree.set(node_id, "value", data[value_id].short_repr)
            

    def handle_vm_message(self, msg):
        if self.winfo_ismapped():
            if hasattr(msg, "heap"):
                self._update_data(msg.heap)
            elif isinstance(msg, ActionResponse):
                # ask for updated heap
                vm_proxy.send_command(InlineCommand(command="get_heap"))
                
    

class ObjectInspectorFrame(ScrollableFrame):
    def __init__(self, master):
        
        ScrollableFrame.__init__(self, master)
        
        self.object_id = None
        
        self.grid_frame = tk.Frame(self.interior, bg="white") 
        self.grid_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(10,0), pady=15)
        self.grid_frame.columnconfigure(1, weight=1)
        
        def _add_main_attribute(row, caption):
            label = ttk.Label(self.grid_frame, text=caption + ":  ",
                             background="white",
                             justify=tk.LEFT)
            label.grid(row=row, column=0, sticky=tk.NW)
            
            value = tk.Entry(self.grid_frame,
                             background="white",
                             bd=0,
                             readonlybackground="white",
                             state="readonly"
                             )
            value.grid(row=row, column=1, sticky=tk.NSEW, pady=2)
            
            return value
        
        self.id_entry   = _add_main_attribute(0, "id")
        self.repr_entry = _add_main_attribute(1, "repr")
        self.type_entry = _add_main_attribute(2, "type")
        self.type_entry.config(cursor="hand2", fg="dark blue")
        self.type_entry.bind("<Button-1>", self.goto_type)
        
        self.bind_all("<<ObjectSelect>>", self.show_object)
        
    
    def show_object(self, event):
        object_id = event.serial
        
        if self.winfo_ismapped() and self.object_id != object_id:
            self.object_id = object_id
            update_entry_text(self.id_entry, str(object_id))
            self.update_info(None)
            
            # ask for object info
            vm_proxy.send_command(InlineCommand(command="get_object_info", object_id=object_id))
    
    def handle_vm_message(self, msg):
        if self.winfo_ismapped():
            if hasattr(msg, "object_info") and msg.object_info["id"] == self.object_id:
                self.update_info(msg.object_info)
            elif isinstance(msg, ActionResponse) and self.object_id != None:
                # ask for updated heap
                vm_proxy.send_command(InlineCommand(command="get_object_info", object_id=self.object_id))
                
                    
    def update_info(self, object_info):
        if object_info == None:
            update_entry_text(self.repr_entry, "")
            update_entry_text(self.type_entry, "")
        else:
            update_entry_text(self.repr_entry, object_info["repr"])
            update_entry_text(self.type_entry, object_info["type"])
         
    def goto_type(self, event):
        # TODO:
        print("Goto type", event)
    
    
    
    def _add_block_label(self, row, caption):
        label = tk.Label(self, bg="white", text=caption)
        label.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=(10,0))
            
        
