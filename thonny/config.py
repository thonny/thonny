# -*- coding: utf-8 -*-

import ast
import configparser
import datetime
import os.path
import sys
import tkinter as tk
from configparser import ConfigParser
from logging import exception, getLogger

from thonny import THONNY_USER_DIR

logger = getLogger(__name__)

_manager_cache = {}


def try_load_configuration(filename):
    if filename in _manager_cache:
        return _manager_cache[filename]

    try:
        # use cache so Workbench doesn't create duplicate manager
        # when FirstRunWindow already created one
        mgr = ConfigurationManager(filename)
    except configparser.Error as e:
        new_path = filename + ".corrupt"
        os.replace(filename, new_path)
        mgr = ConfigurationManager(filename, error_reading_existing_file=e)

    _manager_cache[filename] = mgr
    return mgr


class ConfigurationManager:
    def __init__(self, filename, error_reading_existing_file=None):
        self._ini = ConfigParser(interpolation=None)
        self.error_reading_existing_file = error_reading_existing_file
        self._filename = filename
        self._defaults = {}
        self._defaults_overrides_str = {}
        self._variables = {}  # Tk variables

        if os.path.exists(self._filename):
            with open(self._filename, "r", encoding="UTF-8") as fp:
                self._ini.read_file(fp)

        if not self.get_option("general.configuration_creation_timestamp"):
            self.set_option(
                "general.configuration_creation_timestamp", datetime.datetime.now().isoformat()
            )

        # print(prefs_filename, self.sections())
        self._init_default_overrides()

    def _init_default_overrides(self):
        overrides_path = os.path.join(os.path.dirname(__file__), "defaults.ini")
        if not os.path.isfile(overrides_path):
            return

        defparser = configparser.ConfigParser()
        defparser.read(overrides_path, "utf-8")
        for section in defparser.sections():
            for key in defparser[section]:
                # leave parsing until base default value is known
                self._defaults_overrides_str[section + "." + key] = defparser[section][key]

    def get_option(self, name, secondary_default=None):
        section, option = self._parse_name(name)
        name = section + "." + option

        # variable may have more recent value
        if name in self._variables:
            return self._variables[name].get()

        try:
            val = self._ini.get(section, option)

            # if option's data type is str (inferred from the default value)
            # then don't try to parse anything (unless it's None)
            if val == "None":
                return None
            elif isinstance(self._defaults.get(name), str):
                return val
            else:
                return self._parse_value(val)
        except Exception:
            if name in self._defaults:
                return self._defaults[name]
            else:
                return secondary_default

    def has_option(self, name):
        return name in self._defaults

    def set_option(self, name, value):
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

    def set_default(self, name, primary_default_value):
        # normalize name
        section, option = self._parse_name(name)
        name = section + "." + option
        self._defaults[name] = primary_default_value

        if name in self._defaults_overrides_str:
            if isinstance(primary_default_value, str):
                value = self._defaults_overrides_str[name]
            else:
                value = self._parse_value(self._defaults_overrides_str[name])
        else:
            value = primary_default_value

        self._defaults[name] = value

    def get_variable(self, name: str) -> tk.Variable:
        section, option = self._parse_name(name)
        name = section + "." + option

        if name in self._variables:
            return self._variables[name]
        else:
            value = self.get_option(name)
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)  # type: tk.Variable
            elif isinstance(value, int):
                var = tk.IntVar(value=value)
            elif isinstance(value, str):
                var = tk.StringVar(value=value)
            elif isinstance(value, float):
                var = tk.StringVar(value=value)
            else:
                raise KeyError(
                    "Can't create Tk Variable for " + name + ". Type is " + str(type(value))
                )
            self._variables[name] = var
            return var

    def save(self):
        # save all tk variables
        for name in self._variables:
            self.set_option(name, self._variables[name].get())

        # store
        if not os.path.exists(self._filename):
            os.makedirs(os.path.dirname(self._filename), mode=0o700, exist_ok=True)

        # Normal saving occasionally creates corrupted file:
        # https://bitbucket.org/plas/thonny/issues/167/configuration-file-occasionally-gets
        # Now I'm saving the configuration to a temp file
        # and if the save is successful, I replace configuration file with it
        temp_filename = self._filename + ".temp"
        with open(temp_filename, "w", encoding="UTF-8") as fp:
            self._ini.write(fp)

        try:
            ConfigurationManager(temp_filename)
            # temp file was created successfully
            os.chmod(temp_filename, 0o600)
            os.replace(temp_filename, self._filename)
            os.chmod(self._filename, 0o600)
        except Exception:
            exception("Could not save configuration file. Reverting to previous file.")

    def _parse_name(self, name):
        if "." in name:
            return name.split(".", 1)
        else:
            return "general", name

    def _parse_value(self, value):
        try:
            return ast.literal_eval(value)
        except Exception:
            return value
