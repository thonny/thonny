# -*- coding: utf-8 -*-

import tkinter as tk
import os.path
import ast
from configparser import ConfigParser

class ConfigurationManager:
    def __init__(self, filename):
        self._ini = ConfigParser()
        self._filename = filename
        self._defaults = {}
        self._variables = {} # Tk variables
        
        if os.path.exists(self._filename):
            with open(self._filename, 'r', encoding="UTF-8") as fp: 
                self._ini.readfp(fp)

        #print(prefs_filename, self.sections())
    
    def get_option(self, name):
        section, option = self._parse_name(name)
        name = section + "." + option
        
        # variable may have more recent value
        if name in self._variables:
            return self._variables[name].get()
            
        try:
            val = self._ini.get(section, option)
            try:
                return ast.literal_eval(val)
            except:
                return val
        except:
            if name not in self._defaults:
                raise KeyError("Option named '{}' doesn't exist".format(name)) 
            
            return self._defaults[name]
    
    def has_option(self, name):
        return name in self._defaults
    
    def set_option(self, name, value, save_now=True):
        section, option = self._parse_name(name)
        name = section + "." + option
        if not self._ini.has_section(section):
            self._ini.add_section(section)
        
        if isinstance(value, str):
            self._ini.set(section, option, value)
        else:
            self._ini.set(section, option, repr(value))
        
        # update variable
        if name in self._variables:
            self._variables[name].set(value)
        
        if save_now:
            self.save() 
    
    def add_option(self, name, default_value):
        section, option = self._parse_name(name)
        name = section + "." + option
        self._defaults[name] = default_value

    def get_variable(self, name):
        section, option = self._parse_name(name)
        name = section + "." + option
        
        if name in self._variables:
            return self._variables[name]
        else:
            value = self.get_option(name)
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
    
    def save(self):
        # save all tk variables
        for name in self._variables:
            self.set_option(name, self._variables[name].get(), save_now=False)
            
        # store
        if not os.path.exists(self._filename):
            os.makedirs(os.path.dirname(self._filename), mode=0o700, exist_ok=True)
        with open(self._filename, 'w', encoding="UTF-8") as fp: 
            self._ini.write(fp)
        

    def _parse_name(self, name):
        if "." in name:
            return name.split(".", 1)
        else:
            return "general", name 
