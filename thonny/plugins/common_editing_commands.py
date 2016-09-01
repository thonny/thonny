# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from thonny.globals import get_workbench
from thonny.ui_utils import select_sequence

def load_plugin():
    def create_edit_command_handler(virtual_event_sequence):
        def handler(event=None):
            widget = get_workbench().focus_get()
            if widget:
                return widget.event_generate(virtual_event_sequence)
        
        return handler
    
    def select_all(event=None):
        # Tk 8.6 has <<SelectAll>> virtual event, but 8.5 doesn't
        widget = get_workbench().focus_get()
        if isinstance(widget, tk.Text):
            widget.tag_remove("sel","1.0","end")
            widget.tag_add("sel","1.0","end")
        elif isinstance(widget, ttk.Entry) or isinstance(widget, tk.Entry):
            widget.select_range(0, tk.END)
        
    
    get_workbench().add_command("undo", "edit", "Undo",
        create_edit_command_handler("<<Undo>>"),
        tester=None, # TODO:
        default_sequence=select_sequence("<Control-z>", "<Command-z>"),
        skip_sequence_binding=True,
        group=10)
    
    get_workbench().add_command("redo", "edit", "Redo",
        create_edit_command_handler("<<Redo>>"),
        tester=None, # TODO:
        default_sequence=select_sequence("<Control-y>", "<Command-y>"),
        skip_sequence_binding=True,
        group=10)
    
    # Ctrl+Shift+Z as alternative shortcut for redo
    get_workbench().bind_class("Text", select_sequence("<Control-Shift-Z>", "<Command-Shift-Z>"),
                               create_edit_command_handler("<<Redo>>"), True)
    
    
    get_workbench().add_command("Cut", "edit", "Cut",
        create_edit_command_handler("<<Cut>>"),
        tester=None, # TODO:
        default_sequence=select_sequence("<Control-x>", "<Command-x>"),
        skip_sequence_binding=True,
        group=20)
    
    get_workbench().add_command("Copy", "edit", "Copy",
        create_edit_command_handler("<<Copy>>"),
        tester=None, # TODO:
        default_sequence=select_sequence("<Control-c>", "<Command-c>"),
        skip_sequence_binding=True,
        group=20)
    
    get_workbench().add_command("Paste", "edit", "Paste",
        create_edit_command_handler("<<Paste>>"),
        tester=None, # TODO:
        default_sequence=select_sequence("<Control-v>", "<Command-v>"),
        skip_sequence_binding=True,
        group=20)
    
    get_workbench().add_command("SelectAll", "edit", "Select all",
        select_all,
        tester=None, # TODO:
        default_sequence=select_sequence("<Control-a>", "<Command-a>"),
        skip_sequence_binding=True,
        group=20)
    
