# -*- coding: utf-8 -*-

import tkinter as tk

from thonny.memory import format_object_id, VariablesFrame, MemoryFrame,\
    MAX_REPR_LENGTH_IN_GRID
from thonny.misc_utils import shorten_repr
from thonny.ui_utils import ScrollableFrame, CALM_WHITE, update_entry_text
from thonny.tktextext import TextFrame
from thonny.common import InlineCommand
import ast
from thonny.globals import get_workbench, get_runner
from logging import exception



class AttributesFrame(VariablesFrame):
    def __init__(self, master):
        VariablesFrame.__init__(self, master)
        self.configure(border=1)
        self.vert_scrollbar.grid_remove()
       
    def on_select(self, event):
        pass
    
    def on_double_click(self, event):
        self.show_selected_object_info()
    


        
    

class ObjectInspector(ScrollableFrame):
    def __init__(self, master):
        
        ScrollableFrame.__init__(self, master)
        
        self.object_id = None
        self.object_info = None
        get_workbench().bind("ObjectSelect", self.show_object, True)
        
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
            if row > 0:
                value.grid(row=row, column=1, columnspan=3, 
                       sticky=tk.NSEW, pady=2)
            else:
                value.grid(row=row, column=1, sticky=tk.NSEW, pady=2)
            return value
        
        self.id_entry   = _add_main_attribute(0, "id")
        self.repr_entry = _add_main_attribute(1, "repr")
        self.type_entry = _add_main_attribute(2, "type")
        self.type_entry.config(cursor="hand2", fg="dark blue")
        self.type_entry.bind("<Button-1>", self.goto_type)
        
        self._add_block_label(5, "Attributes")
        self.attributes_frame = AttributesFrame(self.grid_frame)
        self.attributes_frame.grid(row=6, column=0, columnspan=4, sticky=tk.NSEW, padx=(0,10))
        
        self.grid_frame.grid_remove()
        
        # navigation 
        self.back_label = self.create_navigation_link(2, " << ", self.navigate_back)
        self.forward_label = self.create_navigation_link(3, " >> ", self.navigate_forward, (0,10))
        self.back_links = []
        self.forward_links = []
        
        # type-specific inspectors
        self.current_type_specific_inspector = None
        self.current_type_specific_label = None
        self.type_specific_inspectors = [ 
            FileHandleInspector(self.grid_frame),
            FunctionInspector(self.grid_frame),
            StringInspector(self.grid_frame),
            ElementsInspector(self.grid_frame),
            DictInspector(self.grid_frame),
        ]

        get_workbench().bind("ObjectInfo", self._handle_object_info_event, True)
        get_workbench().bind("DebuggerProgress", self._handle_progress_event, True)
        get_workbench().bind("ToplevelResult", self._handle_progress_event, True)


    
    def create_navigation_link(self, col, text, action, padx=0):
        link = tk.Label(self.grid_frame,
                        text=text,
                        background=CALM_WHITE,
                        foreground="blue",
                        cursor="hand2")
        link.grid(row=0, column=col, sticky=tk.NE, padx=padx)
        link.bind("<Button-1>", action)
        return link
    
    def navigate_back(self, event):
        if len(self.back_links) == 0:
            return
        
        self.forward_links.append(self.object_id)
        self._show_object_by_id(self.back_links.pop(), True)
    
    def navigate_forward(self, event):
        if len(self.forward_links) == 0:
            return
    
        self.back_links.append(self.object_id)
        self._show_object_by_id(self.forward_links.pop(), True)

    def show_object(self, event):
        self._show_object_by_id(event.object_id)
        
    def _show_object_by_id(self, object_id, via_navigation=False):
        
        if self.winfo_ismapped() and self.object_id != object_id:
            if not via_navigation and self.object_id is not None:
                if self.object_id in self.back_links:
                    self.back_links.remove(self.object_id)
                self.back_links.append(self.object_id)
                del self.forward_links[:]
                
            self.object_id = object_id
            update_entry_text(self.id_entry, format_object_id(object_id))
            self.set_object_info(None)
            self.request_object_info()
    
    def _handle_object_info_event(self, msg):
        if self.winfo_ismapped():
            if msg.info["id"] == self.object_id:
                if hasattr(msg, "not_found") and msg.not_found:
                    self.object_id = None
                    self.set_object_info(None)
                else:
                    self.set_object_info(msg.info)
    
    def _handle_progress_event(self, event):
        if self.object_id is not None:
            self.request_object_info()
                
                
    def request_object_info(self): 
        get_runner().send_command(InlineCommand("get_object_info",
                                            object_id=self.object_id,
                                            all_attributes=False)) 
                    
    def set_object_info(self, object_info):
        self.object_info = object_info
        if object_info is None:
            update_entry_text(self.repr_entry, "")
            update_entry_text(self.type_entry, "")
            self.grid_frame.grid_remove()
        else:
            update_entry_text(self.repr_entry, object_info["repr"])
            update_entry_text(self.type_entry, object_info["type"])
            self.attributes_frame.tree.configure(height=len(object_info["attributes"]))
            self.attributes_frame.update_variables(object_info["attributes"])
            self.update_type_specific_info(object_info)
                
            
            # update layout
            self._expose(None)
            if not self.grid_frame.winfo_ismapped():
                self.grid_frame.grid()
    
        if self.back_links == []:
            self.back_label.config(foreground="lightgray", cursor="arrow")
        else:
            self.back_label.config(foreground="blue", cursor="hand2")
    
        if self.forward_links == []:
            self.forward_label.config(foreground="lightgray", cursor="arrow")
        else:
            self.forward_label.config(foreground="blue", cursor="hand2")
    
    def update_type_specific_info(self, object_info):
        type_specific_inspector = None
        for insp in self.type_specific_inspectors:
            if insp.applies_to(object_info):
                type_specific_inspector = insp
                break
        
        if type_specific_inspector != self.current_type_specific_inspector:
            if self.current_type_specific_inspector is not None:
                self.current_type_specific_inspector.grid_remove() # TODO: or forget?
                self.current_type_specific_label.destroy()
                self.current_type_specific_inspector = None
                self.current_type_specific_label = None
                
            if type_specific_inspector is not None:
                self.current_type_specific_label = self._add_block_label (3, "")
                
                type_specific_inspector.grid(row=4, 
                                             column=0, 
                                             columnspan=4, 
                                             sticky=tk.NSEW,
                                             padx=(0,10))
                
            self.current_type_specific_inspector = type_specific_inspector
        
        if self.current_type_specific_inspector is not None:
            self.current_type_specific_inspector.set_object_info(object_info,
                                                             self.current_type_specific_label)
    
    def goto_type(self, event):
        if self.object_info is not None:
            get_workbench().event_generate("ObjectSelect", object_id=self.object_info["type_id"])
    
    
    
    def _add_block_label(self, row, caption):
        label = tk.Label(self.grid_frame, bg=CALM_WHITE, text=caption)
        label.grid(row=row, column=0, columnspan=4, sticky="nsew", pady=(20,0))
        return label
            

class TypeSpecificInspector:
    def __init__(self, master):
        pass
    
    def set_object_info(self, object_info, label):
        pass
    
    def applies_to(self, object_info):
        return False
    
class FileHandleInspector(TextFrame, TypeSpecificInspector):
    
    def __init__(self, master):
        TypeSpecificInspector.__init__(self, master)
        TextFrame.__init__(self, master, read_only=True)
        self.cache = {} # stores file contents for handle id-s
        self.config(borderwidth=1)
        self.text.configure(background="white")
        self.text.tag_configure("read", foreground="lightgray")
    
    def applies_to(self, object_info):
        return ("file_content" in object_info
                or "file_error" in object_info)
    
    def set_object_info(self, object_info, label):
        
        if "file_content" not in object_info:
            exception("File error: " + object_info["file_error"])
            return
        
        assert "file_content" in object_info
        content = object_info["file_content"]
        line_count_sep = len(content.split("\n"))
        line_count_term = len(content.splitlines())
        char_count = len(content)
        self.text.configure(height=min(line_count_sep, 10))
        self.text.set_content(content)
        
        assert "file_tell" in object_info
        # f.tell() gives num of bytes read (minus some magic with linebreaks)
        
        file_bytes = content.encode(encoding=object_info["file_encoding"])
        bytes_read = file_bytes[0:object_info["file_tell"]]
        read_content = bytes_read.decode(encoding=object_info["file_encoding"])
        read_char_count = len(read_content)
        read_line_count_term = (len(content.splitlines())
                                - len(content[read_char_count:].splitlines()))
        
        pos_index = "1.0+" + str(read_char_count) + "c"
        self.text.tag_add("read", "1.0", pos_index)
        self.text.see(pos_index)
        
        label.configure(text="Read %d/%d %s, %d/%d %s" 
                        % (read_char_count,
                           char_count,
                           "symbol" if char_count == 1 else "symbols",  
                           read_line_count_term,
                           line_count_term,
                           "line" if line_count_term == 1 else "lines"))
            
            
            
class FunctionInspector(TextFrame, TypeSpecificInspector):
    
    def __init__(self, master):
        TypeSpecificInspector.__init__(self, master)
        TextFrame.__init__(self, master, read_only=True)
        self.config(borderwidth=1)
        self.text.configure(background="white")

    def applies_to(self, object_info):
        return "source" in object_info
    
    def set_object_info(self, object_info, label):
        line_count = len(object_info["source"].split("\n"))
        self.text.configure(height=min(line_count, 15))
        self.text.set_content(object_info["source"])
        label.configure(text="Code")
                
            
class StringInspector(TextFrame, TypeSpecificInspector):
    
    def __init__(self, master):
        TypeSpecificInspector.__init__(self, master)
        TextFrame.__init__(self, master, read_only=True)
        self.config(borderwidth=1)
        self.text.configure(background="white")

    def applies_to(self, object_info):
        return object_info["type"] == repr(str)
    
    def set_object_info(self, object_info, label):
        # TODO: don't show too big string
        content = ast.literal_eval(object_info["repr"])
        line_count_sep = len(content.split("\n"))
        line_count_term = len(content.splitlines())
        self.text.configure(height=min(line_count_sep, 10))
        self.text.set_content(content)
        label.configure(text="%d %s, %d %s" 
                        % (len(content),
                           "symbol" if len(content) == 1 else "symbols",
                           line_count_term, 
                           "line" if line_count_term == 1 else "lines"))
        

class ElementsInspector(MemoryFrame, TypeSpecificInspector):
    def __init__(self, master):
        TypeSpecificInspector.__init__(self, master)
        MemoryFrame.__init__(self, master, ('index', 'id', 'value'))
        self.configure(border=1)
        
        #self.vert_scrollbar.grid_remove()
        self.tree.column('index', width=40, anchor=tk.W, stretch=False)
        self.tree.column('id', width=750, anchor=tk.W, stretch=True)
        self.tree.column('value', width=750, anchor=tk.W, stretch=True)
        
        self.tree.heading('index', text='Index', anchor=tk.W) 
        self.tree.heading('id', text='Value ID', anchor=tk.W)
        self.tree.heading('value', text='Value', anchor=tk.W)
    
        self.elements_have_indices = None
        self.update_memory_model()

        get_workbench().bind("ShowView", self.update_memory_model, True)
        get_workbench().bind("HideView", self.update_memory_model, True)
        
        
    def update_memory_model(self, event=None):
        self._update_columns()
        
    def _update_columns(self):
        if get_workbench().in_heap_mode():
            if self.elements_have_indices:
                self.tree.configure(displaycolumns=("index", "id"))
            else:
                self.tree.configure(displaycolumns=("id",))
        else:
            if self.elements_have_indices:
                self.tree.configure(displaycolumns=("index", "value"))
            else:
                self.tree.configure(displaycolumns=("value"))

    def applies_to(self, object_info):
        return "elements" in object_info
    
    def on_select(self, event):
        pass
    
    def on_double_click(self, event):
        self.show_selected_object_info()
    
    def set_object_info(self, object_info, label):
        assert "elements" in object_info
        
        self.elements_have_indices = object_info["type"] in (repr(tuple), repr(list))
        self._update_columns()
        
        self._clear_tree()
        index = 0
        # TODO: don't show too big number of elements
        for element in object_info["elements"]:
            node_id = self.tree.insert("", "end")
            if self.elements_have_indices:
                self.tree.set(node_id, "index", index)
            else:
                self.tree.set(node_id, "index", "")
                
            self.tree.set(node_id, "id", format_object_id(element["id"]))
            self.tree.set(node_id, "value", shorten_repr(element["repr"], MAX_REPR_LENGTH_IN_GRID))
            index += 1

        count = len(object_info["elements"])
        self.tree.config(height=min(count,10))
        
        
        label.configure (
            text=("%d element" if count == 1 else "%d elements") % count
        ) 
        

class DictInspector(MemoryFrame, TypeSpecificInspector):
    def __init__(self, master):
        TypeSpecificInspector.__init__(self, master)
        MemoryFrame.__init__(self, master, ('key_id', 'id', 'key', 'value'))
        self.configure(border=1)
        #self.vert_scrollbar.grid_remove()
        self.tree.column('key_id', width=100, anchor=tk.W, stretch=False)
        self.tree.column('key', width=100, anchor=tk.W, stretch=False)
        self.tree.column('id', width=750, anchor=tk.W, stretch=True)
        self.tree.column('value', width=750, anchor=tk.W, stretch=True)
        
        self.tree.heading('key_id', text='Key ID', anchor=tk.W) 
        self.tree.heading('key', text='Key', anchor=tk.W) 
        self.tree.heading('id', text='Value ID', anchor=tk.W)
        self.tree.heading('value', text='Value', anchor=tk.W)
    
        self.update_memory_model()
        
    def update_memory_model(self, event=None):
        if get_workbench().in_heap_mode():
            self.tree.configure(displaycolumns=("key_id", "id"))
        else:
            self.tree.configure(displaycolumns=("key", "value"))

    def applies_to(self, object_info):
        return "entries" in object_info

    def on_select(self, event):
        pass
    
    def on_double_click(self, event):
        # NB! this selects value
        self.show_selected_object_info()

    def set_object_info(self, object_info, label):
        assert "entries" in object_info
        
        self._clear_tree()
        # TODO: don't show too big number of elements
        for key, value in object_info["entries"]:
            node_id = self.tree.insert("", "end")
            self.tree.set(node_id, "key_id", format_object_id(key["id"]))
            self.tree.set(node_id, "key", shorten_repr(key["repr"], MAX_REPR_LENGTH_IN_GRID))
            self.tree.set(node_id, "id", format_object_id(value["id"]))
            self.tree.set(node_id, "value", shorten_repr(value["repr"], MAX_REPR_LENGTH_IN_GRID))

        count = len(object_info["entries"])
        self.tree.config(height=min(count,10))
        
        label.configure (
            text=("%d entry" if count == 1 else "%d entries") % count
        ) 
        
        self.update_memory_model()

def load_plugin():
    get_workbench().add_view(ObjectInspector, "Object inspector", "se")