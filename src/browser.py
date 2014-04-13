# -*- coding: utf-8 -*-
from __future__ import print_function, division 
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk 
    
class BrowseNotebook(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master)
        self.files_frame = FilesFrame(self)
        self.modules_frame = ModulesFrame(self)
        
        tv = ttk.Treeview(self, columns=('Essa', 'Tessa'))
        tv.heading('#0', text='Name', anchor=tk.W)
        tv.heading('Essa', text='Essa', anchor=tk.W)
        tv.heading('Tessa', text='Tessa', anchor=tk.W)
        
        #self.add(self.files_frame, text="Files")
        self.add(tv, text="Files")
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

class FilesFrame(ttk.Frame):
    pass

class ModulesFrame(ttk.Frame):
    pass