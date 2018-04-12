import tkinter as tk
import os.path
from tkinter import filedialog
from tkinter import ttk

from thonny.config_ui import ConfigurationPage
from thonny import get_workbench
from thonny.ui_utils import create_string_var
from thonny.misc_utils import running_on_windows, running_on_mac_os
from shutil import which
from thonny.running import WINDOWS_EXE
from thonny.plugins.backend_config_page import BackendDetailsConfigPage

class CustomCPythonConfigurationPage(BackendDetailsConfigPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        
        self._configuration_variable = create_string_var(
            get_workbench().get_option("CustomInterpreter.path"))
        
        entry_label = ttk.Label(self, text="Which interpreter to use for running programs?")
        entry_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self._entry = ttk.Combobox(self,
                              exportselection=False,
                              textvariable=self._configuration_variable,
                              values=self._get_interpreters())
        
        self._entry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self._entry.state(['!disabled', 'readonly'])
        
        another_label = ttk.Label(self, text="Your interpreter isn't in the list?")
        another_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10,0))
        self._select_button = ttk.Button(self,
                                         text="Locate another executable "
                                         + ("(python.exe) ..." if running_on_windows() else "(python3) ...")
                                         + "\nNB! Thonny only supports Python 3.4 and later",
                                         command=self._select_executable)
        
        self._select_button.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
    
    def _select_executable(self):
        if running_on_windows():
            options = {"filetypes" : [('Exe-files', '.exe'), ('all files', '.*')]}
        else:
            options = {}

        # TODO: get dir of current interpreter
            
        filename = filedialog.askopenfilename(**options)
        
        if filename:
            self._configuration_variable.set(filename)
    
    
    def _get_interpreters(self):
        result = set()
        
        if running_on_windows():
            # registry
            result.update(self._get_interpreters_from_windows_registry())
            
            # Common locations
            for dir_ in ["C:\\Python34",
                         "C:\\Python35",
                         "C:\\Program Files\\Python 3.5",
                         "C:\\Program Files (x86)\\Python 3.5",
                         "C:\\Python36",
                         "C:\\Program Files\\Python 3.6",
                         "C:\\Program Files (x86)\\Python 3.6",
                         ]:
                path = os.path.join(dir_, WINDOWS_EXE)
                if os.path.exists(path):
                    result.add(os.path.realpath(path))  
        
        else:
            # Common unix locations
            dirs = ["/bin", "/usr/bin", "/usr/local/bin",
                    os.path.expanduser("~/.local/bin")]
            for dir_ in dirs:
                # if the dir_ is just a link to another dir_, skip it
                # (not to show items twice)
                # for example on Fedora /bin -> usr/bin
                realpath = os.path.realpath(dir_)
                if realpath != dir_ and realpath in dirs:
                    continue
                for name in ["python3", "python3.4", "python3.5", "python3.6"]:
                    path = os.path.join(dir_, name)
                    if os.path.exists(path):
                        result.add(path)  
        
        if running_on_mac_os():
            for version in ["3.4", "3.5", "3.6"]:
                dir_ = os.path.join("/Library/Frameworks/Python.framework/Versions",
                                    version, "bin")
                path = os.path.join(dir_, "python3")
                
                if os.path.exists(path):
                    result.add(path)
        
        for command in ["pythonw", "python3", "python3.4", "python3.5", "python3.6"]:
            path = which(command)
            if path is not None and os.path.isabs(path):
                result.add(path)
        
        for path in get_workbench().get_option("CustomInterpreter.used_paths"):
            if os.path.exists(path):
                result.add(os.path.realpath(path))
        
        return sorted(result)
    
    def _get_interpreters_from_windows_registry(self):
        import winreg
        result = set()
        for key in [winreg.HKEY_LOCAL_MACHINE,
                    winreg.HKEY_CURRENT_USER]:
            for version in ["3.4",
                            "3.5", "3.5-32", "3.5-64",
                            "3.6", "3.6-32", "3.6-64"]:
                try:
                    for subkey in [
                        'SOFTWARE\\Python\\PythonCore\\' + version + '\\InstallPath',
                        'SOFTWARE\\Python\\PythonCore\\Wow6432Node\\' + version + '\\InstallPath'
                                 ]:
                        dir_ = winreg.QueryValue(key, subkey)
                        if dir_:
                            path = os.path.join(dir_, WINDOWS_EXE)
                            if os.path.exists(path):
                                result.add(path)
                except:
                    pass
        
        return result
    
    def should_restart(self):
        return self._configuration_variable.modified
        
    def apply(self):
        if not self.should_restart():
            return
        
        configuration = self._configuration_variable.get()
        get_workbench().set_option("CustomInterpreter.path", configuration)
