# -*- coding: utf-8 -*-

import ast
import sys
import configparser
import datetime
import os.path
import tkinter as tk
from configparser import ConfigParser
from logging import exception
import shutil
from thonny import THONNY_USER_DIR, get_workbench
import traceback


def try_load_configuration(filename):
    try:
        return ConfigurationManager(filename)
    except configparser.Error:
        from tkinter import messagebox

        if os.path.exists(filename) and messagebox.askyesno(
            "Problem",
            "Thonny's configuration file can't be read. It may be corrupt.\n\n"
            + "Do you want to discard the file and open Thonny with default settings?",
            parent=get_workbench()
        ):
            os.replace(filename, filename + "_corrupt")
            # For some reasons Thonny styles are not loaded properly once messagebox has been shown before main window (At least Windows Py 3.5)
            raise SystemExit(
                "Configuration file has been discarded. Please restart Thonny!"
            )
        else:
            raise


class ConfigurationManager:
    def __init__(self, filename):
        self._ini = ConfigParser(interpolation=None)
        self._filename = filename
        self._defaults = {}
        self._variables = {}  # Tk variables

        if os.path.exists(self._filename):
            with open(self._filename, "r", encoding="UTF-8") as fp:
                self._ini.read_file(fp)
        else:
            # For migration to new conf directory
            # only if not in venv
            if not (
                hasattr(sys, "base_prefix")
                and sys.base_prefix != sys.prefix
                or hasattr(sys, "real_prefix")
                and getattr(sys, "real_prefix") != sys.prefix
            ):
                old_user_dir = os.path.join(os.path.expanduser("~"), ".thonny")
                old_config_file = os.path.join(old_user_dir, "configuration.ini")
                if os.path.exists(old_config_file):
                    with open(old_config_file, "r", encoding="UTF-8") as fp:
                        self._ini.read_file(fp)
                        self.set_option("run.backend_name", "SameAsFrontend")

                    # migrate user_logs
                    # (I know, it's not proper place for this code, but ...)
                    old_user_logs = os.path.join(old_user_dir, "user_logs")
                    new_user_logs = os.path.join(THONNY_USER_DIR, "user_logs")
                    if os.path.exists(old_user_logs) and not os.path.exists(
                        new_user_logs
                    ):
                        try:
                            shutil.copytree(old_user_logs, new_user_logs)
                        except Exception:
                            traceback.print_exc()

        if not self.get_option("general.configuration_creation_timestamp"):
            self.set_option(
                "general.configuration_creation_timestamp",
                datetime.datetime.now().isoformat(),
            )

        # print(prefs_filename, self.sections())

    def get_option(self, name, secondary_default=None):
        section, option = self._parse_name(name)
        name = section + "." + option

        # variable may have more recent value
        if name in self._variables:
            return self._variables[name].get()

        try:
            val = self._ini.get(section, option)
            if name in self._defaults and isinstance(self._defaults[name], str):
                return val
            try:
                return ast.literal_eval(val)
            except Exception:
                return val
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
        section, option = self._parse_name(name)
        name = section + "." + option
        self._defaults[name] = primary_default_value

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
                    "Can't create Tk Variable for "
                    + name
                    + ". Type is "
                    + str(type(value))
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
