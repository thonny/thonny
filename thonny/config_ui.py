import tkinter as tk
from tkinter import ttk
from thonny.globals import get_workbench


class ConfigurationDialog(tk.Toplevel):
    def __init__(self, master, page_records):
        tk.Toplevel.__init__(self, master)
        width = 400
        height = 400
        left = max(int(get_workbench().winfo_x() + get_workbench().winfo_width()/2 - width/2), 0)
        top = max(int(get_workbench().winfo_y() + get_workbench().winfo_height()/2 - height/2), 0)
        self.geometry("%dx%d+%d+%d" % (width, height, left, top))
        self.title("Thonny options")
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self) # otherwise there is wrong color background with clam
        main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        self._notebook = ttk.Notebook(main_frame)
        self._notebook.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW, padx=10, pady=10)
        
        self._ok_button = ttk.Button(main_frame, text="OK", command=self._ok, default="active")
        self._cancel_button = ttk.Button(main_frame, text="Cancel", command=self._cancel)
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
    
    def add_checkbox(self, flag_name, description, row=None, pady=0, columnspan=1):
        variable = get_workbench().get_variable(flag_name)
        checkbox = ttk.Checkbutton(self, text=description, variable=variable)
        checkbox.grid(row=row, column=0, sticky=tk.W, pady=pady, columnspan=columnspan)
                
    def apply(self):
        """Apply method should return False, when page contains invalid
        input and configuration dialog should not be closed."""
        pass
        