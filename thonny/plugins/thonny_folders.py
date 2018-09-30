# -*- coding: utf-8 -*-
"""Adds commands for opening certain Thonny folders"""

from thonny import THONNY_USER_DIR, get_workbench
from thonny.ui_utils import open_path_in_system_file_manager


def load_plugin() -> None:
    def cmd_open_data_dir():
        open_path_in_system_file_manager(THONNY_USER_DIR)

    def cmd_open_program_dir():
        open_path_in_system_file_manager(get_workbench().get_package_dir())

    get_workbench().add_command(
        "open_program_dir",
        "tools",
        "Open Thonny program folder...",
        cmd_open_program_dir,
        group=110,
    )
    get_workbench().add_command(
        "open_data_dir",
        "tools",
        "Open Thonny data folder...",
        cmd_open_data_dir,
        group=110,
    )
