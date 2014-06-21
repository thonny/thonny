# -*- coding: utf-8 -*-
 
from ui_utils import TreeFrame, update_entry_text, ScrollableFrame,\
    generate_event, get_event_data, CALM_WHITE
from config import prefs
from common import ActionResponse, InlineCommand
import vm_proxy
import tkinter as tk
import tkinter.font as tk_font


def format_object_id(object_id):
    #return "@" + str(object_id)
    return hex(object_id).upper().replace("X", "x")

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
        
    def change_font_size(self, delta):
        pass
    
        
class VariablesFrame(MemoryFrame):
    def __init__(self, master):
        MemoryFrame.__init__(self, master, ('name', 'id', 'value'))
    
        self.tree.column('name', width=120, anchor=tk.W, stretch=False)
        self.tree.column('id', width=450, anchor=tk.W, stretch=True)
        self.tree.column('value', width=450, anchor=tk.W, stretch=True)
        
        self.tree.heading('name', text='Name', anchor=tk.W) 
        self.tree.heading('id', text='Id', anchor=tk.W)
        self.tree.heading('value', text='Value', anchor=tk.W)
        
        self.update_memory_model()
        #self.tree.tag_configure("item", font=ui_utils.TREE_FONT)
        

    def update_memory_model(self):
        if prefs["values_in_heap"]:
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
                
                if not name.startswith("__"): # TODO: consult prefs
                    node_id = self.tree.insert("", "end", tags="item")
                    self.tree.set(node_id, "name", name)
                    self.tree.set(node_id, "id", format_object_id(variables[name].id))
                    self.tree.set(node_id, "value", variables[name].short_repr)
    
    def on_select(self, event):
        iid = self.tree.focus()
        if iid != '':
            object_id = parse_object_id(self.tree.item(iid)['values'][1])
            # self.event_generate("<<ObjectSelect>>", serial=object_id)
            generate_event(self, "<<ObjectSelect>>", object_id)
            
        
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

class AttributesFrame(VariablesFrame):   
    def on_select(self, event):
        pass
    

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
            

    def on_select(self, event):
        iid = self.tree.focus()
        if iid != '':
            object_id = parse_object_id(self.tree.item(iid)['values'][0])
            #self.event_generate("<<ObjectSelect>>", serial=object_id)
            generate_event(self, "<<ObjectSelect>>", object_id)
            
    def handle_vm_message(self, msg):
        if self.winfo_ismapped():
            if hasattr(msg, "heap"):
                self._update_data(msg.heap)
            elif isinstance(msg, ActionResponse):
                """
                # ask for updated heap
                vm_proxy.send_command(InlineCommand(command="get_heap"))
                """
                
    

class ObjectInspectorFrame(ScrollableFrame):
    def __init__(self, master):
        
        ScrollableFrame.__init__(self, master)
        self.object_id = None
        self.object_info = None
        self.bind_all("<<ObjectSelect>>", self.show_object)
        
        self.grid_frame = tk.Frame(self.interior, bg=CALM_WHITE) 
        self.grid_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(10,0), pady=15)
        self.grid_frame.columnconfigure(1, weight=1)
        
        def _add_main_attribute(row, caption):
            label = tk.Label(self.grid_frame, text=caption + ":  ",
                             background=CALM_WHITE,
                             justify=tk.LEFT)
            label.grid(row=row, column=0, sticky=tk.NW)
            
            value = tk.Entry(self.grid_frame,
                             background=CALM_WHITE,
                             bd=0,
                             readonlybackground=CALM_WHITE,
                             highlightthickness = 0,
                             state="readonly"
                             )
            value.grid(row=row, column=1, sticky=tk.NSEW, pady=2)
            
            return value
        
        self.id_entry   = _add_main_attribute(0, "id")
        self.repr_entry = _add_main_attribute(1, "repr")
        self.type_entry = _add_main_attribute(2, "type")
        self.type_entry.config(cursor="hand2", fg="dark blue")
        self.type_entry.bind("<Button-1>", self.goto_type)
        
        self._add_block_label(4, "Attributes")
        self.attributes_frame = AttributesFrame(self.grid_frame)
        self.attributes_frame.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, padx=(0,10))
        self.attributes_frame.configure(border=1)
        self.attributes_frame.scrollbar.grid_remove()
        
        self.grid_frame.grid_remove()
        
    
    def show_object(self, event):
        print("SO", vars(event))
        object_id = get_event_data(event)
        
        if self.winfo_ismapped() and self.object_id != object_id:
            self.object_id = object_id
            update_entry_text(self.id_entry, format_object_id(object_id))
            self.update_info(None)
            self.request_object_info()
    
    def handle_vm_message(self, msg):
        print("MAS", msg)
        if self.winfo_ismapped():
            if hasattr(msg, "object_info") and msg.object_info["id"] == self.object_id:
                if hasattr(msg, "not_found") and msg.not_found:
                    self.object_id = None
                    self.update_info(None)
                else:
                    self.update_info(msg.object_info)
            elif (isinstance(msg, ActionResponse)
                  and not hasattr(msg, "error") 
                  and self.object_id != None):
                self.request_object_info()
                
                
    def request_object_info(self): 
        vm_proxy.send_command(InlineCommand(command="get_object_info",
                                            object_id=self.object_id,
                                            all_attributes=False)) # TODO: consult configuration
                    
    def update_info(self, object_info):
        self.object_info = object_info
        if object_info == None:
            update_entry_text(self.repr_entry, "")
            update_entry_text(self.type_entry, "")
            self.grid_frame.grid_remove()
        else:
            update_entry_text(self.repr_entry, object_info["repr"])
            update_entry_text(self.type_entry, object_info["type"])
            self.attributes_frame.tree.configure(height=len(object_info["attributes"]))
            self.attributes_frame.update_variables(object_info["attributes"])
            self._expose(None)
            if not self.grid_frame.winfo_ismapped():
                self.grid_frame.grid()
         
    def goto_type(self, event):
        if self.object_info != None:
            generate_event(self, "<<ObjectSelect>>", self.object_info["type_id"])
    
    
    
    def _add_block_label(self, row, caption):
        label = tk.Label(self.grid_frame, bg=CALM_WHITE, text=caption)
        label.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=(10,0))
            
    def update_memory_model(self):
        self.attributes_frame.update_memory_model()
        
