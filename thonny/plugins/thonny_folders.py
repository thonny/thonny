# -*- coding: utf-8 -*-
"""Adds commands for opening certain Thonny folders"""

from thonny import get_thonny_user_dir, get_workbench
from tkinter.messagebox import askyesno
from thonny.languages import tr
from thonny.ui_utils import open_path_in_system_file_manager


def load_plugin() -> None:
    def cmd_open_data_dir():
        quit_data_dir = askyesno(
            title= tr("Thonny Closure"),
            message= tr("Do you want to close Thonny before enterring the data folder? This is useful if you want to manually edit the configuration files. "),
            parent= get_workbench()
        )
        open_path_in_system_file_manager(get_thonny_user_dir())
        if quit_data_dir:
            get_workbench().quit()

    def cmd_open_program_dir():
        open_path_in_system_file_manager(get_workbench().get_package_dir())

    get_workbench().add_command(
        "open_program_dir",
        "tools",
        tr("Open Thonny program folder..."),
        cmd_open_program_dir,
        group=110,
    )
    get_workbench().add_command(
        "open_data_dir", "tools", tr("Open Thonny data folder..."), cmd_open_data_dir, group=110
    )
