# -*- coding: utf-8 -*-
from __future__ import print_function, division 
from ui_utils import TreeFrame, TextFrame
from config import prefs
from codeview import CodeView
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
    

class ObjectInspectorFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="white")
        
        # set up scrolling with canvas
        # http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(self, bg="white", bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        #self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        #vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.interior = tk.Frame(self.canvas, bg="white")
        self.interior.columnconfigure(0, weight=1)
        self.interior.rowconfigure(0, weight=1)
        self.interior_id = self.canvas.create_window(0,0, 
                                                    window=self.interior, 
                                                    anchor=tk.NW)
        self.bind('<Configure>', self._configure_interior, "+")
        self.bind('<Expose>', self._expose, "+")
#         def _configure_canvas(event):
#             if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
#                 # update the inner frame's width to fill the canvas
#                 self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())
        
        self.info_views = {}
        self.generic_view = ObjectInfoView(self.interior)
        self.current_view = self.generic_view
        
        self.show_object(1234)
        self.show_object("1234")
        #self._configure_interior(None)
    
    def _expose(self, event):
        self.update_idletasks()
        self._configure_interior(event)
    
    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.canvas.winfo_width() , self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if (self.interior.winfo_reqwidth() != self.canvas.winfo_width()
            and self.canvas.winfo_width() > 10):
            # update the interior's width to fit canvas
            #print("CAWI", self.canvas.winfo_width())
            self.canvas.itemconfigure(self.interior_id,
                                      width=self.canvas.winfo_width())
                
    def get_info_view(self, obj):
        type_code = str(type(obj))
        
        if not type_code in self.info_views:
            if type_code == "<class 'str'>":
                view = StringInfoView(self.interior)
            else:
                view = self.generic_view
            self.info_views[type_code] = view
        
        return self.info_views[type_code]
    
    def show_object(self, obj):
        view = self.get_info_view(obj)
        if view != self.current_view:
            self.current_view.grid_forget()
            view.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=15)
            self.current_view = view
         
            
        

class ObjectInfoView(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="white")
        self.columnconfigure(1, weight=1)
        self.id_entry = self._add_info(0, "id", "823234235")
        self.repr_entry = self._add_info(1, "repr", "[234, 345, 324, 33333]")
        self.type_entry = self._add_info(2, "type", "<class 'list'>")
        self.type_entry.config(cursor="hand2", fg="dark blue")
        self.type_entry.bind("<Button-1>", self.goto_type)
        
        # reserve intermediate rows for subclasses
        
        # row 10 for attributes
        self.attributes_tree = ttk.Button(self, text="ATT tree")
        self._add_block(10, "Attributes", self.attributes_tree)
         
    
    def goto_type(self, event):
        # TODO:
        print("Goto type", event)
    
    def _add_info(self, row, caption, value):
        label = ttk.Label(self, text=caption + ":  ",
                         background="white",
                         justify=tk.LEFT)
        label.grid(row=row, column=0, sticky=tk.NW)
        
        if isinstance(value, str):
            text = value
            value = tk.Entry(self,
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

    def _add_block(self, row, caption, widget):
        label = tk.Label(self, bg="white", text=caption)
        label.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=(10,0))
        
        widget.grid(row=row+1, column=0, columnspan=2, sticky="nsew")
        
    
class StringInfoView(ObjectInfoView):
    def __init__(self, master):
        ObjectInfoView.__init__(self, master)
        self.text = CodeView(self, auto_vert_scroll=True,
                             height=1)
        self.text.config(border=1)  
        self.text.set_coloring(False)       
        #self.attributes_tree = ttk.Button(self, text="Text ")
        self._add_block(4, "Content", self.text)
                                    
        
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
        
        


