import tkinter as tk
import os.path
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

from thonny.config_ui import ConfigurationPage
from thonny.globals import get_workbench
from thonny.ui_utils import create_string_var
from thonny.misc_utils import running_on_windows, running_on_mac_os
import sys
from shutil import which


class InterpreterConfigurationPage(ConfigurationPage):
    
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        
        self._interpreter_variable = create_string_var(
            get_workbench().get_option("run.interpreter"))
        
        entry_label = ttk.Label(self, text="Which Python to use for running programs?")
        entry_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self._entry = ttk.Combobox(self,
                              exportselection=False,
                              textvariable=self._interpreter_variable,
                              values=self._get_interpreters())
        
        self._entry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        
        self._clear_button = ttk.Button(self,
                                        text="Clear to use\n"
                                        + ("built-in Python" if getattr(sys, 'frozen', False) else "same as GUI"),
                                        command=lambda: self._interpreter_variable.set(""))
        
        self._select_button = ttk.Button(self,
                                         text="Select executable\n"
                                         + ("(pythonw.exe) ..." if running_on_windows() else "(python3) ..."),
                                         command=self._select_executable)
        
        self._clear_button.grid(row=2, column=0, sticky=tk.EW, pady=10)
        self._select_button.grid(row=2, column=1, sticky=tk.EW, pady=10, padx=(10,0))
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
    
    def _select_executable(self):
        filetypes = [('all files', '.*')]
        if running_on_windows():
            filetypes.insert(0, ('Exe-files', '.exe'))
            
        filename = filedialog.askopenfilename(
            filetypes = filetypes, 
            # TODO: get dir of current interpreter
            #initialdir = get_workbench().get_option("run.working_directory")
            )
        
        if filename:
            self._interpreter_variable.set(os.path.realpath(filename))
    
    def _get_interpreters(self):
        result = set()
        
        if running_on_windows():
            # registry
            result.update(self._get_interpreters_from_windows_registry())
            
            # Common locations
            for dir_ in ["C:\\Python36", "C:\\Python35", "C:\\Python34",
                         "C:\\Python33", "C:\\Python32", "C:\\Python27",
                         "C:\\Program Files\\Python 3.5",
                         "C:\\Program Files (x86)\\Python 3.5",
                         "C:\\Program Files\\Python 3.6",
                         "C:\\Program Files (x86)\\Python 3.6",
                         ]:
                path = os.path.join(dir_, "pythonw.exe")
                if os.path.exists(path):
                    result.add(os.path.realpath(path))  
        
        else:
            # Common unix locations
            for dir_ in ["/bin", "/usr/bin", "/usr/local/bin",
                         os.path.expanduser("~/.local/bin")]:
                for name in ["python", "python3", "python2.7", "python3.2", "python3.3",
                             "python3.4", "python3.5", "python3.6"]:
                    path = os.path.join(dir_, name)
                    if os.path.exists(path):
                        result.add(path)  
        
        if running_on_mac_os():
            for version in ["2.7", "3.2", "3.3", "3.4", "3.5", "3.6"]:
                dir_ = os.path.join("/Library/Frameworks/Python.framework/Versions",
                                    version, "bin")
                if version.startswith("2"):
                    path = os.path.join(dir_, "python")
                else:
                    path = os.path.join(dir_, "python3")
                
                if os.path.exists(path):
                    result.add(path)
        
        
        for command in ["python", "python3", "python3.5", "python3.4", 
                        "python3.3", "python3.2", "python2.7", "python3.6"]:
            path = which(command)
            if path is not None:
                result.add(path)
        
        current_interpreter = get_workbench().get_option("run.interpreter") 
        if current_interpreter and os.path.exists(current_interpreter):
            result.add(os.path.realpath(current_interpreter))
        
        for path in get_workbench().get_option("run.used_interpreters"):
            if os.path.exists(path):
                result.add(os.path.realpath(path))
        
        return sorted(result)
    
    
    def _get_interpreters_from_windows_registry(self):
        import winreg
        result = set()
        for key in [winreg.HKEY_LOCAL_MACHINE,
                    winreg.HKEY_CURRENT_USER]:
            for version in ["2.7", "3.2", "3.3", "3.4",
                            "3.5", "3.5-32", "3.5-64",
                            "3.6", "3.6-32", "3.6-64"]:
                try:
                    for subkey in [
                        'SOFTWARE\\Python\\PythonCore\\' + version + '\\InstallPath',
                        'SOFTWARE\\Python\\PythonCore\\Wow6432Node\\' + version + '\\InstallPath'
                                 ]:
                        dir_ = winreg.QueryValue(key, subkey)
                        if dir_:
                            path = os.path.join(dir_, "pythonw.exe")
                            if os.path.exists(path):
                                result.add(path)
                except:
                    pass
        
        return result
    
    def apply(self):
        if not self._interpreter_variable.modified:
            return
        
        interpreter = self._interpreter_variable.get()
        get_workbench().set_option("run.interpreter", interpreter)
        
        used_interpreters = get_workbench().get_option("run.used_interpreters")
        if interpreter not in used_interpreters:
            used_interpreters.append(interpreter)
        get_workbench().set_option("run.used_interpreters", used_interpreters)
        
        messagebox.showinfo(None, "New interpreter will be selected at next Run/Debug/Reset")
        
    

def load_plugin():
    get_workbench().add_option("run.used_interpreters", [])
    get_workbench().add_configuration_page("Interpreter", InterpreterConfigurationPage)
