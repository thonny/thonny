# -*- coding: utf-8 -*-

import tkinter as tk
from thonny.plugins.object_inspector2 import ContentInspector
from thonny.gridtable import ScrollableGridTable
from thonny.globals import get_workbench


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
        
        """
        data_row_count = 50
        column_count = 16
        
        header_row = []
        for i in range(column_count):
            header_row.append("Hdr " + str(i) )
        ScrollableGridTable.__init__(self, master, [header_row], 50, 0, 1)
        
        data_rows = {}
        for r in range(data_row_count):
            row = []
            for i in range(column_count):
                row.append("D" + str(r) + ":" + str(i))
            data_rows[r] = row
        self.grid_table.set_data_rows(data_rows)
        """
        print("Done creatino")
    
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

def load_early_plugin():
    get_workbench().add_content_inspector(DataFrameInspector)
