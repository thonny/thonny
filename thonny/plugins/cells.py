# -*- coding: utf-8 -*-

import re
from thonny.globals import get_workbench
from thonny.codeview import PythonText
from thonny import ui_utils

cell_regex = re.compile("(^|\n)(# ?%%|##)[^\n]*", re.MULTILINE)  # @UndefinedVariable


def update_editor_cells(event):
    text = event.widget
    
    if not getattr(text, "cell_tags_configured", False):
        text.tag_configure("CURRENT_CELL", 
                           borderwidth=1, relief="groove",
                           #background="#f3ffed"
                           background="LightYellow"
                           )
        text.tag_configure("CELL_HEADER", 
                           font=get_workbench().get_font("BoldEditorFont"),
                           foreground="#665843",
                           #background="Gray"
                           #underline=True
                           )
        text.cell_tags_configured = True
    
    text.tag_remove("CURRENT_CELL", "0.1", "end")
    text.tag_remove("CELL_HEADER", "0.1", "end")
    source = text.get("1.0", "end")
    cells = []
    prev_marker = 0
    for match in cell_regex.finditer(source):
        if match.start() == 0:
            this_marker = match.start()
        else:
            this_marker = match.start() + 1
        
        cell_start_index = text.index("1.0+%dc" % prev_marker)
        header_end_index = text.index("1.0+%dc" % match.end())
        cell_end_index = text.index("1.0+%dc" % this_marker)
        text.tag_add("CELL_HEADER", cell_end_index, header_end_index)
        cells.append((cell_start_index, cell_end_index)) 
        
        prev_marker = this_marker
    
    if prev_marker != 0:
        cells.append((text.index("1.0+%dc" % prev_marker), "end"))
        
    if text.index("insert").endswith(".0"):
        # normal insertion cursor is not well visible when 
        # in the left edge of the cell box 
        text["insertwidth"] = 3 
    else:
        text["insertwidth"] = 2
        

    for start_index, end_index in cells:
        if (text.compare(start_index, "<=", "insert")
            and text.compare(end_index, ">", "insert")):
            text.tag_add("CURRENT_CELL", start_index, end_index)
            break


def _patch_perform_return():
    original_perform_return = PythonText.perform_return

    def _patched_perform_return(self, event):
        text = event.widget
        ranges = text.tag_ranges("CURRENT_CELL")
        
        if (len(ranges) == 2 
            and (ui_utils.shift_is_pressed(event.state)
                 or ui_utils.control_is_pressed(event.state))):
            
            code = text.get(ranges[0], ranges[1]).strip()
            lines = code.splitlines()
            
            # remove starting comments
            while len(lines) > 0 and lines[0].strip().startswith("#"):
                lines = lines[1:]
            
            # remove starting empty lines
            while len(lines) > 0 and lines[0].strip() == "":
                lines = lines[1:]
            
            # remove trailing empty lines
            while len(lines) > 0 and lines[-1].strip() == "":
                lines = lines[:-1]
            
            if len(lines) > 0:
                code = "\n".join(lines) + "\n"
                shell = get_workbench().show_view("ShellView", False)
                shell.submit_python_code(code)
            
            if ui_utils.shift_is_pressed(event.state):
                # advance to next cell
                text.mark_set("insert", ranges[1])
            
            return "break"
        else:
            return original_perform_return(self, event)
    
    PythonText.perform_return = _patched_perform_return

def dummy(event=None):
    "This is dummy method"


def run_selection(event=None):
    print("run_selection")

def run_enabled():
    return True

def load_early_plugin():
    wb = get_workbench() 
    wb.bind_class("CodeViewText", "<<CursorMove>>", update_editor_cells, True)
    wb.bind_class("CodeViewText", "<<TextChange>>", update_editor_cells, True)

def load_plugin():
    wb = get_workbench() 
    
    _patch_perform_return()
    
    wb.add_command('run_cell', "run", 'Run cell',
            handler=dummy, # actual handler is in the patch
            default_sequence="<Control-Return>",
            tester=run_enabled,
            group=11)
    
    wb.add_command('run_cell_and_advance', "run", 'Run cell and advance',
            handler=dummy, # actual handler is in the patch
            default_sequence="<Shift-Return>",
            tester=run_enabled,
            group=11)
    
    wb.add_command('run_selection', "run", 'Run selection or current line',
            handler=run_selection,
            default_sequence="<F9>",
            tester=run_enabled,
            group=11)
