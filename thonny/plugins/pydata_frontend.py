# -*- coding: utf-8 -*-

import re
import tkinter as tk
from thonny.plugins.object_inspector2 import ContentInspector
from thonny.gridtable import ScrollableGridTable
from thonny.globals import get_workbench

cell_regex = re.compile("\n(# ?%%|##)[^\n]*", re.MULTILINE)  # @UndefinedVariable

class DataFrameInspector(ContentInspector, tk.Frame):
    def __init__(self, master):
        ContentInspector.__init__(self, master)
        tk.Frame.__init__(self, master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.table = None
        self.columns = None
        self.index = None
        self.values = None
    
    def set_object_info(self, object_info):
        if self.table is not None and self.columns != object_info["columns"]:
            self.table.grid_forget()
            self.table.destroy()
            self.table = None
        
        data = []
        self.columns = object_info["columns"]
        index = object_info["index"]
        values = object_info["values"]
        assert len(values) == len(index)
        for i in range(len(values)):
            data.append([index[i]] + values[i])
        
        headers = [""] + self.columns 
        
        if self.table is None:
            self.table = ScrollableGridTable(self, [headers],
                                             object_info["row_count"], 0, 1)
            
            self.table.grid(row=0, column=0, sticky="nsew")
        
        self.table.grid_table.set_data(data)
    
    def applies_to(self, object_info):
        return object_info.get("is_DataFrame", False)

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

def load_early_plugin():
    wb = get_workbench() 
    wb.add_content_inspector(DataFrameInspector)
    wb.bind_class("CodeViewText", "<<CursorMove>>", update_editor_cells, True)
    wb.bind_class("CodeViewText", "<<TextChange>>", update_editor_cells, True)
