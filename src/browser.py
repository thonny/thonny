# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from ui_utils import TreeFrame
from misc_utils import running_on_windows, get_res_path
import os
    
class BrowseNotebook(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master)
        self.files_frame = FileBrowser(self)
        self.modules_frame = ModulesFrame(self)
        
        self.add(self.files_frame, text="Files")
        self.add(self.modules_frame, text="Modules")
        
        
        
    """
    def create_content_widget(self, master, scrollbar):
#        return tk.Text(master, borderwidth=0, 
#                       yscrollcommand=scrollbar.set,
#                       width=15)
        box = tk.Listbox(master, borderwidth=0, highlightthickness=0,
                         yscrollcommand=scrollbar.set)
        box.insert(0, "essa", "tessa", "kossa")
        return box
    """

class FileBrowser(TreeFrame):
    
    def __init__(self, master):
        TreeFrame.__init__(self, master, ["#0"], displaycolumns=(0,))
        #print(self.get_toplevel_items())
        self.tree['show'] = ('tree')
        
        self.hor_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.tree.config(xscrollcommand=self.hor_scrollbar.set)
        self.hor_scrollbar['command'] = self.tree.xview
        self.hor_scrollbar.grid(row=1, column=0, sticky="nsew")
        
        self.folder_icon = tk.PhotoImage(file=get_res_path("folder.gif"))
        self.python_file_icon = tk.PhotoImage(file=get_res_path("python_file.gif"))
        self.text_file_icon = tk.PhotoImage(file=get_res_path("text_file.gif"))
        self.generic_file_icon = tk.PhotoImage(file=get_res_path("generic_file.gif"))
        
        #self.populate_tree()
    
    
    def populate_tree(self):
        for path in self.get_toplevel_items():
            self.show_item(path, path, "", 2)
    
    def show_item(self, name, path, parent_id, levels_left):
        if os.path.isdir(path):
            img = self.folder_icon
        elif path.lower().endswith(".py"):
            img = self.python_file_icon
        elif path.lower().endswith(".txt") or path.lower().endswith(".csv"):
            img = self.text_file_icon
        else:
            img = self.generic_file_icon
            
        node_id = self.tree.insert(parent_id, "end",
                                   text=" " + name,
                                   open=False,
                                   image=img)
        
        try:
            if os.path.isdir(path) and levels_left > 0:
                for name in os.listdir(path):
                    child_path = os.path.join(path, name)
                    self.show_item(name, child_path, node_id, levels_left-1)
        except:
            pass
        
    
    def get_toplevel_items(self):
        if running_on_windows():
            return self.get_win_drives()
        else:
            result = []
            for item in os.listdir("/"):
                result.append("/" + item)
            return sorted(result)
    
    def get_win_drives(self):
        # http://stackoverflow.com/a/2288225/261181
        # http://msdn.microsoft.com/en-us/library/windows/desktop/aa364939%28v=vs.85%29.aspx
        import string
        from ctypes import windll
        
        all_drive_types = ['DRIVE_UNKNOWN', 
                           'DRIVE_NO_ROOT_DIR',
                           'DRIVE_REMOVABLE',
                           'DRIVE_FIXED',
                           'DRIVE_REMOTE',
                           'DRIVE_CDROM',
                           'DRIVE_RAMDISK']
        
        required_drive_types = ['DRIVE_REMOVABLE',
                                'DRIVE_FIXED',
                                'DRIVE_REMOTE',
                                #'DRIVE_CDROM',
                                'DRIVE_RAMDISK']
    
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()  # @UndefinedVariable
        for letter in string.ascii_uppercase:
            drive_type = all_drive_types[windll.kernel32.GetDriveTypeW("%s:\\" % letter)]  # @UndefinedVariable
            if bitmask & 1 and drive_type in required_drive_types:
                drives.append(letter + ":\\")
            bitmask >>= 1
    
        return drives

class ModulesFrame(ttk.Frame):
    pass