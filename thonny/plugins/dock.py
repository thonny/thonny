import tkinter as tk
from tkinter import ttk
import os
from thonny import get_workbench

class DockView(tk.Frame):
    def __init__(self, master=None, **kw):
        tk.Frame.__init__(self, master=master)
        self._dock = None
        self._create_new_dock()
        
        # need new dock for each new embedding 
        get_workbench().bind("StartingCPythonBackend", self._create_new_dock, True)
    
    def _create_new_dock(self, event=None):
        if self._dock is not None:
            #self._dock.pack_forget()
            self._dock.destroy()
        
        #self._dock = tk.Frame(self)
        #self._dock.pack(fill="both", expand=1)
        #self.update_idletasks()
        #self._dock.grid(row=0, column=0, sticky="nsew")
        #self.rowconfigure(0, weight=1)
        #self.columnconfigure(0, weight=1)
        
        os.environ["THONNY_DOCK_ID"] = hex(self.winfo_id())


def load_plugin():
    get_workbench().add_view(DockView, "Dock", "se")
    