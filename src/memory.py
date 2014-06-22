# -*- coding: utf-8 -*-
 
from ui_utils import TreeFrame, update_entry_text, ScrollableFrame,\
    generate_event, get_event_data, CALM_WHITE, TextFrame
from config import prefs
from common import ActionResponse, InlineCommand
import vm_proxy
import tkinter as tk
import tkinter.font as tk_font
import ast


def format_object_id(object_id):
    # this format aligns with how Python shows memory addresses
    return "0x" + hex(object_id)[2:].rjust(8,'0').upper()

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

    def show_selected_object_info(self):
        iid = self.tree.focus()
        if iid != '':
            # NB! Assuming id is second column!
            object_id = parse_object_id(self.tree.item(iid)['values'][1])
            generate_event(self, "<<ObjectSelect>>", object_id)
    
    
        
class VariablesFrame(MemoryFrame):
    def __init__(self, master):
        MemoryFrame.__init__(self, master, ('name', 'id', 'value'))
    
        self.tree.column('name', width=120, anchor=tk.W, stretch=False)
        self.tree.column('id', width=450, anchor=tk.W, stretch=True)
        self.tree.column('value', width=450, anchor=tk.W, stretch=True)
        
        self.tree.heading('name', text='Name', anchor=tk.W) 
        self.tree.heading('id', text='Value ID', anchor=tk.W)
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
                
                if (not name.startswith("__")
                    or prefs["show_double_underscore_names"]):
                    node_id = self.tree.insert("", "end", tags="item")
                    self.tree.set(node_id, "name", name)
                    self.tree.set(node_id, "id", format_object_id(variables[name].id))
                    self.tree.set(node_id, "value", variables[name].short_repr)
    
    def on_select(self, event):
        self.show_selected_object_info()
        
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
    def __init__(self, master):
        VariablesFrame.__init__(self, master)
        self.configure(border=1)
        self.vert_scrollbar.grid_remove()
       
    def on_select(self, event):
        pass
    
    def on_double_click(self, event):
        self.show_selected_object_info()
    

class HeapFrame(MemoryFrame):
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
                

        

class ObjectInspector(ScrollableFrame):
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
        object_id = get_event_data(event)
        self._show_object_by_id(object_id)
        
    def _show_object_by_id(self, object_id, via_navigation=False):
        
        if self.winfo_ismapped() and self.object_id != object_id:
            if not via_navigation and self.object_id != None:
                if self.object_id in self.back_links:
                    self.back_links.remove(self.object_id)
                self.back_links.append(self.object_id)
                self.forward_links.clear()
                
            self.object_id = object_id
            update_entry_text(self.id_entry, format_object_id(object_id))
            self.set_object_info(None)
            self.request_object_info()
    
    def handle_vm_message(self, msg):
        if self.winfo_ismapped():
            if hasattr(msg, "object_info") and msg.object_info["id"] == self.object_id:
                if hasattr(msg, "not_found") and msg.not_found:
                    self.object_id = None
                    self.set_object_info(None)
                else:
                    self.set_object_info(msg.object_info)
            elif (isinstance(msg, ActionResponse)
                  and not hasattr(msg, "error") 
                  and self.object_id != None):
                self.request_object_info()
                
                
    def request_object_info(self): 
        vm_proxy.send_command(InlineCommand(command="get_object_info",
                                            object_id=self.object_id,
                                            all_attributes=prefs["show_double_underscore_names"])) 
                    
    def set_object_info(self, object_info):
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
            if self.current_type_specific_inspector != None:
                self.current_type_specific_inspector.grid_remove() # TODO: or forget?
                self.current_type_specific_label.destroy()
                self.current_type_specific_inspector = None
                self.current_type_specific_label = None
                
            if type_specific_inspector != None:
                self.current_type_specific_label = self._add_block_label (3, "")
                
                type_specific_inspector.grid(row=4, 
                                             column=0, 
                                             columnspan=4, 
                                             sticky=tk.NSEW,
                                             padx=(0,10))
                
            self.current_type_specific_inspector = type_specific_inspector
        
        if self.current_type_specific_inspector != None:
            self.current_type_specific_inspector.set_object_info(object_info,
                                                             self.current_type_specific_label)
    
    def goto_type(self, event):
        if self.object_info != None:
            generate_event(self, "<<ObjectSelect>>", self.object_info["type_id"])
    
    
    
    def _add_block_label(self, row, caption):
        label = tk.Label(self.grid_frame, bg=CALM_WHITE, text=caption)
        label.grid(row=row, column=0, columnspan=4, sticky="nsew", pady=(20,0))
        return label
            
    def update_memory_model(self):
        self.attributes_frame.update_memory_model()
        if self.current_type_specific_inspector != None:
            self.current_type_specific_inspector.update_memory_model()

class TypeSpecificInspector:
    def update_memory_model(self):
        pass
    
    def set_object_info(self, object_info, label):
        pass
    
    def applies_to(self, object_info):
        return False
    
class FileHandleInspector(TextFrame, TypeSpecificInspector):
    
    def __init__(self, master):
        TextFrame.__init__(self, master, readonly=True)
        self.cache = {} # stores file contents for handle id-s
        self.config(borderwidth=1)
        self.text.configure(background="white")
        self.text.tag_configure("read", foreground="lightgray")
    
    def applies_to(self, object_info):
        return ("file_content" in object_info
                or "file_error" in object_info)
    
    def set_object_info(self, object_info, label):
        
        assert "file_content" in object_info
        content = object_info["file_content"]
        line_count_sep = len(content.split("\n"))
        line_count_term = len(content.splitlines())
        char_count = len(content)
        self.text.configure(height=min(line_count_sep, 10))
        self.set_content(content)
        
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
        TextFrame.__init__(self, master, readonly=True)
        self.config(borderwidth=1)
        self.text.configure(background="white")

    def applies_to(self, object_info):
        return "source" in object_info
    
    def set_object_info(self, object_info, label):
        line_count = len(object_info["source"].split("\n"))
        self.text.configure(height=min(line_count, 15))
        self.set_content(object_info["source"])
        label.configure(text="Code")
                
            
class StringInspector(TextFrame, TypeSpecificInspector):
    
    def __init__(self, master):
        TextFrame.__init__(self, master, readonly=True)
        self.config(borderwidth=1)
        self.text.configure(background="white")

    def applies_to(self, object_info):
        return object_info["type"] == repr(str)
    
    def set_object_info(self, object_info, label):
        content = ast.literal_eval(object_info["repr"])
        line_count_sep = len(content.split("\n"))
        line_count_term = len(content.splitlines())
        self.text.configure(height=min(line_count_sep, 10))
        self.set_content(content)
        label.configure(text="%d %s, %d %s" 
                        % (len(content),
                           "symbol" if len(content) == 1 else "symbols",
                           line_count_term, 
                           "line" if line_count_term == 1 else "lines"))
        

class ElementsInspector(MemoryFrame, TypeSpecificInspector):
    def __init__(self, master):
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
        
        
    def update_memory_model(self):
        self._update_columns()
        
    def _update_columns(self):
        if prefs["values_in_heap"]:
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
        for element in object_info["elements"]:
            node_id = self.tree.insert("", "end")
            if self.elements_have_indices:
                self.tree.set(node_id, "index", index)
            else:
                self.tree.set(node_id, "index", "")
                
            self.tree.set(node_id, "id", format_object_id(element.id))
            self.tree.set(node_id, "value", element.short_repr)
            index += 1

        count = len(object_info["elements"])
        self.tree.config(height=min(count,10))
        
        
        label.configure (
            text=("%d element" if count == 1 else "%d elements") % count
        ) 
        

class DictInspector(MemoryFrame, TypeSpecificInspector):
    def __init__(self, master):
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
        
    def update_memory_model(self):
        if prefs["values_in_heap"]:
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
        for key, value in object_info["entries"]:
            node_id = self.tree.insert("", "end")
            self.tree.set(node_id, "key_id", format_object_id(key.id))
            self.tree.set(node_id, "key", key.short_repr)
            self.tree.set(node_id, "id", format_object_id(value.id))
            self.tree.set(node_id, "value", value.short_repr)

        count = len(object_info["entries"])
        self.tree.config(height=min(count,10))
        
        label.configure (
            text=("%d entry" if count == 1 else "%d entries") % count
        ) 
        
        self.update_memory_model()
    