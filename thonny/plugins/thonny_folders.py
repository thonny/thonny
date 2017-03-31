# -*- coding: utf-8 -*-
"""Adds commands for opening certain Thonny folders"""

import os.path
from thonny.misc_utils import running_on_mac_os, running_on_linux,\
    running_on_windows
import subprocess
from thonny.globals import get_workbench
from thonny import THONNY_USER_DIR

def open_path_in_system_file_manager(path):
    if running_on_mac_os():
        # http://stackoverflow.com/a/3520693/261181
        # -R doesn't allow showing hidden folders
        subprocess.Popen(["open", path])
    elif running_on_linux():
        subprocess.Popen(["xdg-open", path])
    else:
        assert running_on_windows()
        subprocess.Popen(["explorer", path])




def load_plugin():
    def cmd_open_data_dir():
        open_path_in_system_file_manager(THONNY_USER_DIR)
        
    def cmd_open_program_dir():
        open_path_in_system_file_manager(get_workbench().get_package_dir())
        
    get_workbench().add_command("open_program_dir", "tools", "Open Thonny program folder...",
                                cmd_open_program_dir, group=110)
    get_workbench().add_command("open_data_dir", "tools", "Open Thonny data folder...",
                                cmd_open_data_dir, group=110)
    