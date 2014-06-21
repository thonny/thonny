# -*- coding: utf-8 -*-

from configparser import ConfigParser
import tkinter as tk
import os.path
import codecs
import ast


PREFS_FILE = os.path.expanduser(os.path.join("~", ".thonny", "preferences.ini"))

defaults = {
    "general" : {
        "advanced_debugging" : False,
        "values_in_heap" : False,
        "friendly_values" : True,
        "cwd" : os.path.expanduser("~"),
        "language" : "en"
    },
    "debugging" : {
        "detailed_steps" : False,
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
        "browser_width"   : 200,
        "center_width"    : 650,
        "memory_width"    : 200,
        "shell_height"    : 200,
    }    
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
        if not os.path.exists(os.path.dirname(self.filename)):
            os.makedirs(os.path.dirname(self.filename), 0o600)
            
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
 
prefs = ThonnyConfigParser()
prefs_vars = ThonnyTkVars()




if __name__ == "__main__":
    print(repr(prefs["UI.font_size"]),
          repr(prefs["UI.heap_visible"]),
          repr(prefs["UI.some_crap"]))
    prefs["kola.pola"] = True
