import tkinter as tk
from tkinter import ttk
from thonny.globals import get_workbench


class ConfigurationDialog(tk.Toplevel):
    def __init__(self, master, page_records):
        tk.Toplevel.__init__(self, master)
        self.geometry("400x400+400+100")
        self.title("Thonny options")
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._notebook = ttk.Notebook(self)
        self._notebook.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW, padx=10, pady=10)
        
        self._ok_button = ttk.Button(self, text="OK", command=self._ok, default="active")
        self._cancel_button = ttk.Button(self, text="Cancel", command=self._cancel)
        self._ok_button.grid(row=1, column=1, padx=(0,11), pady=(0,10))
        self._cancel_button.grid(row=1, column=2, padx=(0,11), pady=(0,10))
        
        self._pages = {}
        for title in sorted(page_records):
            page_class = page_records[title]
            spacer = ttk.Frame(self)
            spacer.rowconfigure(0, weight=1)
            spacer.columnconfigure(0, weight=1)
            page = page_class(spacer)
            self._pages[title] = page
            page.grid(sticky=tk.NSEW, pady=10, padx=15)
            self._notebook.add(spacer, text=title)
        
        self.bind("<Return>", self._ok, True)
        self.bind("<Escape>", self._cancel, True)
    
    def _ok(self, event=None):
        for title in sorted(self._pages):
            try:
                page = self._pages[title]
                if page.apply() == False:
                    return
            except:
                get_workbench().report_exception("Error when applying options in " + title)
             
        self.destroy()
    
    def _cancel(self, event=None):
        self.destroy()

class ConfigurationPage(ttk.Frame):
    """This is an example dummy implementation of a configuration page.
    
    It's not required that configuration pages inherit from this class
    (can be any widget), but the class must have constructor with single parameter
    for getting the master."""
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
    
    def apply(self):
        """Apply method should return False, when page contains invalid
        input and configuration dialog should not be closed."""
        pass
        