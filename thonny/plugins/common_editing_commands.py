# -*- coding: utf-8 -*-
from thonny import get_workbench
from thonny.languages import tr
from thonny.ui_utils import select_sequence


def load_plugin() -> None:
    def create_edit_command_handler(virtual_event_sequence):
        def handler(event=None):
            widget = get_workbench().focus_get()
            if widget:
                return widget.event_generate(virtual_event_sequence)

            return None

        return handler

    get_workbench().add_command(
        "undo",
        "edit",
        tr("Undo"),
        create_edit_command_handler("<<Undo>>"),
        tester=None,  # TODO:
        default_sequence=select_sequence("<Control-z>", "<Command-z>"),
        extra_sequences=["<Control-Greek_zeta>"],
        skip_sequence_binding=True,
        group=10,
    )

    get_workbench().add_command(
        "redo",
        "edit",
        tr("Redo"),
        create_edit_command_handler("<<Redo>>"),
        tester=None,  # TODO:
        default_sequence=select_sequence("<Control-y>", "<Command-y>"),
        extra_sequences=[
            select_sequence("<Control-Shift-Z>", "<Command-Shift-Z>"),
            "<Control-Greek_upsilon>",
            "<Control-Shift-Greek_ZETA>",
        ],
        skip_sequence_binding=True,
        group=10,
    )

    get_workbench().add_command(
        "Cut",
        "edit",
        tr("Cut"),
        create_edit_command_handler("<<Cut>>"),
        tester=None,  # TODO:
        default_sequence=select_sequence("<Control-x>", "<Command-x>"),
        extra_sequences=["<Control-Greek_chi>"],
        skip_sequence_binding=True,
        group=20,
    )

    get_workbench().add_command(
        "Copy",
        "edit",
        tr("Copy"),
        create_edit_command_handler("<<Copy>>"),
        tester=None,  # TODO:
        default_sequence=select_sequence("<Control-c>", "<Command-c>"),
        extra_sequences=["<Control-Greek_psi>"],
        skip_sequence_binding=True,
        group=20,
    )

    get_workbench().add_command(
        "Paste",
        "edit",
        tr("Paste"),
        create_edit_command_handler("<<Paste>>"),
        tester=None,  # TODO:
        default_sequence=select_sequence("<Control-v>", "<Command-v>"),
        extra_sequences=["<Control-Greek_omega>"],
        skip_sequence_binding=True,
        group=20,
    )

    get_workbench().add_command(
        "SelectAll",
        "edit",
        tr("Select all"),
        create_edit_command_handler("<<SelectAll>>"),
        tester=None,  # TODO:
        default_sequence=select_sequence("<Control-a>", "<Command-a>"),
        extra_sequences=["<Control-Greek_alpha>"],
        skip_sequence_binding=True,
        group=20,
    )
