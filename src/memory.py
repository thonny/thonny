# -*- coding: utf-8 -*-
from __future__ import print_function, division 
from ui_utils import TreeFrame, TextFrame
from config import prefs
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
        if hasattr(msg, "heap"):
            self._update_data(msg.heap)
    

class ObjectInfoFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="white")
        
        # set up scrolling with canvas
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        canvas = tk.Canvas(self, bg="white", bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=canvas.yview)
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # now the actual content
        self.inner_frame = tk.Frame(canvas, bg="white")
        self.inner_frame.grid(sticky=tk.NSEW, padx=10, pady=15)
        
        self.id_entry = self._add_info(0, "id", "823234235")
        self.repr_entry = self._add_info(1, "repr", "[234, 345, 324, 33333]")
        self.type_entry = self._add_info(2, "type", "<class 'list'>")
        self.type_entry.config(cursor="hand2", fg="dark blue")
        self.type_entry.bind("<Button-1>", self.goto_type)
    
    def _add_block(self, row, caption, widget):
        label = ttk.Label(self.inner_frame, bg="white", text=caption)
        label.grid(row=row, column=0, columnspan=2, sticky=tk.NEW)
        
        widget.grid(row=row, column=0, columnspan=2, sticky=tk.NEW)
        
    
    def goto_type(self, event):
        # TODO:
        print("Goto type", event)
    
    def _add_info(self, row, caption, value):
        label = ttk.Label(self.inner_frame, text=caption + ":  ",
                         background="white",
                         justify=tk.LEFT)
        label.grid(row=row, column=0, sticky=tk.NW)
        
        if isinstance(value, str):
            text = value
            value = tk.Entry(self.inner_frame,
                             background="white",
                             bd=0,
                             readonlybackground="white",
                             )
            value.insert(0, text)
            value.config(state="readonly")
            value.grid(row=row, column=1, sticky=tk.NW, pady=2)
        else:
            value.grid(row=row, column=1, sticky=tk.NW)
        
        return value
                            
        
class ObjectInfoFrameOld(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        """
        self.font = tk_font.nametofont("TkTextFont")
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        self.text = tk.Text(self, font=self.font,
                            borderwidth=0,
                            yscrollcommand=self.scrollbar.set,
                            padx=4,
                            insertwidth=2)
        self.text.grid(row=0, column=0, sticky=tk.NSEW)
        self.text.insert("1.0", "len(...)\nlen(object) -> integer\nReturn the number of items of a sequence or mapping.")
        self.scrollbar['command'] = self.text.yview
        top_frame = tk.Frame(self, background="white")
        top_frame.grid(row=0, column=0, sticky=tk.NSEW)
        label = tk.Label(top_frame, text="type: list\nrepr: [234, 345, 324, 33333]\nid: 12349973",
                         background="white",
                         justify=tk.LEFT)
        label.grid(row=0, column=0)
        
        varf = VariablesFrame(self)
        #self.text.window_create("end", window=vars)
        varf.grid(row=1, column=0, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        """
        
        bbg = tk.Frame(self, bg="white")
        bbg.grid(sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        bg = tk.Frame(bbg, bg="white")
        bg.grid(sticky=tk.NSEW, padx=10, pady=10)
        bbg.columnconfigure(0, weight=1)
        bbg.rowconfigure(0, weight=1)
        
        def add_item(caption, value, row):
            label = tk.Label(bg, text=caption + ": ",
                             background="white",
                             justify=tk.LEFT)
            if isinstance(value, str):
                value = tk.Label(bg, text=value,
                                 background="white",
                                 justify=tk.LEFT)
            
            label.grid(row=row, column=0, sticky=tk.NW)
            value.grid(row=row, column=1, sticky=tk.NW)
            
        
        add_item("id", "12349973", 0)  
        add_item("repr", "[234, 345, 324, 33333]", 1)  
        add_item("type", "list", 2)  
        #add_item("doc", 'acos(x)\n\nReturn the arc cosine (measured in radians) of x.', 3)
        #content = VariablesFrame(bg)
        #content.config(borderwidth=1)
        #add_item("content", content, 4)
        #add_item("attributes", "", 4)
        
        attlabel = tk.Label(bg, text="Attributes",
                             background="white",
                             justify=tk.LEFT)
        attlabel.grid(row=4, columnspan=2, sticky=tk.NSEW)
        
        varf = TreeFrame(bg, ("Attribute", "Value"), show_scrollbar=False)
        varf.config(borderwidth=1)
        varf.grid(row=5, columnspan=2, sticky=tk.NSEW)
        bg.columnconfigure(1, weight=1)
        bg.rowconfigure(5, weight=1)
        
        


