# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from ui_utils import TreeFrame
from misc_utils import running_on_windows, get_res_path, is_hidden_or_system_file,\
    get_win_drives
import os

_dummy_node_text = "..."
    
class BrowseNotebook(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master)
        self.files_frame = FileBrowser(self)
        self.modules_frame = ModulesFrame(self)
        
        self.add(self.files_frame, text="Files")
        self.add(self.modules_frame, text="Modules")
        
        
        
class FileBrowser(TreeFrame):
    
    def __init__(self, master):
        TreeFrame.__init__(self, master, 
                           ["#0", "kind", "path"], 
                           displaycolumns=(0,))
        #print(self.get_toplevel_items())
        self.tree['show'] = ('tree',)
        
        self.hor_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.tree.config(xscrollcommand=self.hor_scrollbar.set)
        self.hor_scrollbar['command'] = self.tree.xview
        self.hor_scrollbar.grid(row=1, column=0, sticky="nsew")
        
        self.folder_icon = tk.PhotoImage(file=get_res_path("folder.gif"))
        self.python_file_icon = tk.PhotoImage(file=get_res_path("python_file.gif"))
        self.text_file_icon = tk.PhotoImage(file=get_res_path("text_file.gif"))
        self.generic_file_icon = tk.PhotoImage(file=get_res_path("generic_file.gif"))
        self.hard_drive_icon = tk.PhotoImage(file=get_res_path("hard_drive2.gif"))
        
        self.tree.column('#0', width=500, anchor=tk.W)
        
        # set-up root node
        self.tree.set("", "kind", "root")
        self.tree.set("", "path", "")
        self.refresh_tree()
        
        #self.open_path(r"C:\workspaces\python_stuff\thonny\src")
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)
    
    
    def on_open_node(self, event):
        node_id = self.tree.focus()
        if node_id:
            self.refresh_tree(node_id, True)
    
    def open_path(self, path, see=True):
        
        # unfortunately os.path.split splits from the wrong end (for this case)
        def split(path):
            head, tail = os.path.split(path)
            if head == "" and tail == "":
                return []
            elif head == path or tail == path:
                return [path]
            elif head == "":
                return [tail]
            elif tail == "":
                return split(head)
            else:
                return split(head) + [tail]
        
        parts = split(path)
        current_node_id = ""
        current_path = ""
        
        while parts != []:
            current_path = os.path.join(current_path, parts.pop(0))
            
            for child_id in self.tree.get_children(current_node_id):
                child_path = self.tree.set(child_id, "path")
                if child_path == current_path:
                    self.tree.item(child_id, open=True)
                    self.refresh_tree(child_id)
                    current_node_id = child_id
                    break
        
        if see:
            self.tree.see(current_node_id)    
                
    
    def populate_tree(self):
        for path in self.get_toplevel_items():
            self.show_item(path, path, "", 2)
    
    def refresh_tree(self, node_id="", opening=None):
        path = self.tree.set(node_id, "path")
        #print("REFRESH", path)
        
        if os.path.isfile(path):
            self.tree.set_children(node_id)
            self.tree.item(node_id, open=False)
        else:
            # either root or directory
            if node_id == "" or self.tree.item(node_id, "open") or opening == True:
                fs_children_names = self.listdir(path)
                tree_children_ids = self.tree.get_children(node_id) 
                
                # recollect children
                children = {}
                
                # first the ones, which are present already in tree
                for child_id in tree_children_ids:
                    name = self.tree.item(child_id, "text")
                    if name in fs_children_names:
                        children[name] = child_id
                
                # add missing children
                for name in fs_children_names:
                    if name not in children:
                        children[name] = self.tree.insert(node_id, "end")
                        self.tree.set(children[name], "path", os.path.join(path, name))
                        
                
                def file_order(name):
                    # items in a folder should be ordered so that 
                    # folders come first and names are ordered case insensitively
                    return (os.path.isfile(os.path.join(path, name)),
                            name.upper())
                
                # update tree
                ids_sorted_by_name = list(map(lambda key: children[key],
                                              sorted(children.keys(), key=file_order)))
                self.tree.set_children(node_id, *ids_sorted_by_name)
                
                for child_id in ids_sorted_by_name:
                    self.update_node_format(child_id)
                    self.refresh_tree(child_id)
                
            else:
                # closed dir
                # Don't fetch children yet, but ensure that expand button is visible
                children_ids = self.tree.get_children(node_id)
                if len(children_ids) == 0:
                    self.tree.insert(node_id, "end", text=_dummy_node_text) 
    
    def update_node_format(self, node_id):
        assert node_id != ""
        
        path = self.tree.set(node_id, "path")
        
        
        if os.path.isdir(path):
            if path.endswith(":") or path.endswith(":\\"):
                img = self.hard_drive_icon
            else:
                img = self.folder_icon
            
        else:
            if path.lower().endswith(".py"):
                img = self.python_file_icon
            elif path.lower().endswith(".txt") or path.lower().endswith(".csv"):
                img = self.text_file_icon
            else:
                img = self.generic_file_icon
            
        # compute caption 
        text = os.path.basename(path)
        if text == "": # in case of drive roots 
            text = path
            
        self.tree.item(node_id, text=" " + text, image=img)
        self.tree.set(node_id, "path", path)
    
    def listdir(self, path="", include_hidden_files=False):
        
        if path == "" and running_on_windows():
            result = get_win_drives()
        else:
            result = [x for x in os.listdir(path) 
                        if include_hidden_files 
                            or not is_hidden_or_system_file(os.path.join(path, x))]
            
            if path == "" and not running_on_windows():
                result = ["/" + x for x in result]
            
        return sorted(result, key=str.upper)
    

class ModulesFrame(ttk.Frame):
    pass