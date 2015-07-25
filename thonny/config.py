# -*- coding: utf-8 -*-

import tkinter as tk
import json
import os.path


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


class ConfigurationManager:
    def __init__(self, filename):
        self._filename = filename 
        self._preferences = {}
        self._variables = {} # for storing respective Tk control variables
        self._defaults = {}
        
        if os.path.exists(self._filename):
            with open(self._filename, encoding="UTF-8") as fp: 
                self._preferences = json.load(fp)
                

    def __getitem__(self, name):
        if name in self._variables:
            return self._variables[name].get()
        elif name in self._variables:
            return self._preferences[name]
        else:
            return self._defaults[name]

    def __setitem__(self, name, value):
        self._preferences[name] = value
        if name in self._variables:
            self._variables[name].set(value)
    
    def get_variable(self, name):
        if name in self._variables:
            return self._variables[name]
        else:
            value = self[name]
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
            elif isinstance(value, int):
                var = tk.IntVar(value=value)
            elif isinstance(value, str):
                var = tk.StringVar(value=value)
            else:
                raise KeyError("Can't create Tk Variable for " + name)
            self._variables[name] = var
            return var
    
    def _save(self):
        # save all tk variables
        for name in self._variables:
            self._preferences[name] = self._variables[name].get()
            
        
        with open(self._filename, 'w', encoding="UTF-8") as fp: 
            json.dump(self._preferences, fp)
        

