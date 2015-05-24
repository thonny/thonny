# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.messagebox
import os.path
import codecs
import ast
import traceback
from configparser import ConfigParser


PREFS_FILE = os.path.expanduser(os.path.join("~", ".thonny", "preferences.ini"))

defaults = {
    "general" : {
        "advanced_debugging" : False,
        "values_in_heap" : False,
        "cwd" : os.path.expanduser("~"),
        "show_double_underscore_names" : False,
        "language" : "en",
        "open_files" : "",
        "last_browser_folder": ""
    },
    "debugging" : {
        "detailed_steps" : False,
        "expand_call_functions" : False,
    },
    "view" : {
        "code_font_size"    : None,
        "code_font_family"  : None,
    },
    "run" : {
        "auto_cd"      : True,
    },
    "layout" : {
        "zoomed" : False,
        "top"       : 15,
        "left"      : 150,
        "width"     : 700,
        "height"    : 650,
        "browser_visible" : False, 
        "memory_visible"  : False,
        "inspector_visible"  : False,
        "outline_visible"  : False,
        "browser_width"   : 200,
        "center_width"    : 650,
        "memory_width"    : 200,
        "shell_height"    : 200,
    },
    "experimental" : {
        "find_feature_enabled"      : True,
        "autocomplete_feature_enabled"      : True,
        "outline_feature_enabled"      : True,
        "refactor_rename_feature_enabled"   : True,
        "comment_toggle_enabled"   : True,
    },    
}


class ThonnyConfigParser(ConfigParser):
    def __init__(self):
        ConfigParser.__init__(self)
        self.filename = PREFS_FILE
        if os.path.exists(self.filename):
            with codecs.open(self.filename, 'r', "UTF-8") as fp: 
                self.readfp(fp)

        #print(prefs_filename, self.sections())
    
    def __getitem__(self, descriptor):
        section, option = _parse_descriptor(descriptor)
        try:
            val = self.get(section, option)
            try:
                return ast.literal_eval(val)
            except:
                return val
        except:
            return defaults[section][option]

    def __setitem__(self, descriptor, value):
        section, option = _parse_descriptor(descriptor)
        if not self.has_section(section):
            self.add_section(section)
        
        if isinstance(value, str):
            self.set(section, option, value)
        else:
            self.set(section, option, repr(value))
            
    def save(self):
        with codecs.open(self.filename, 'w', "UTF-8") as fp: 
            self.write(fp)
        

def _parse_descriptor(descriptor):
    if "." in descriptor:
        return descriptor.split(".", 1)
    else:
        return "general", descriptor 


class ThonnyTkVars():
    def __init__(self):
        self._vars = {}
    
    def __getitem__(self, descriptor):
        section, option = _parse_descriptor(descriptor)
        key = section + "." + option
        
        if not key in self._vars:
            default = defaults[section][option]
            if isinstance(default, bool):
                var = tk.BooleanVar(value=prefs[descriptor])
            elif isinstance(default, int):
                var = tk.IntVar(value=prefs[descriptor])
            elif isinstance(default, str):
                var = tk.StringVar(value=prefs[descriptor])
            else:
                raise KeyError("Can't create Tk Var for " + descriptor)
            
            self._vars[key] = var
            
            # make it update prefs
            def _update_prefs(*args):
                prefs[descriptor] = var.get()
                 
            var.trace_variable("w", _update_prefs)
        
        return self._vars[key]

try:
    prefs = ThonnyConfigParser()
    prefs_vars = ThonnyTkVars()
except:
    tkinter.messagebox.showerror("Error reading configuration. Use Ctrl+C to copy",
                                traceback.format_exc())
    raise




