# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from thonny.plugins.object_inspector2 import ContentInspector
from thonny.gridtable import ScrollableGridTable
from thonny.globals import get_workbench
from thonny.ui_utils import VerticallyScrollableFrame, CALM_WHITE
import math

class DataFrameExplorer(VerticallyScrollableFrame):
    def __init__(self, master):
        
        VerticallyScrollableFrame.__init__(self, master)
        self.interior.columnconfigure(0, weight=1)
        self.interior.rowconfigure(0, weight=1)
        self.colframe = None
    
    def load_dataframe(self, info):
        print("Got info:", info)
        
        df_expr = info["df_expr"]
        
        if self.colframe is not None:
            self.colframe.grid_forget()
            self.colframe.destroy()
        
        self.colframe = tk.Frame(self.interior)
        self.colframe.grid(sticky="nsw")
        self.colframe.checkbutton_vars = ([], [])
        
        def create_title(text, col, colspan=1):
            label = tk.Label(self.colframe, text=text, anchor="n", justify="center")
            label.grid(row=0, column=col, columnspan=colspan, sticky="nsew")
            
        create_title("Plot by", 0, 2)
        create_title("Column name", 2)
        create_title("Count", 3)
        create_title("Nulls", 4)
        create_title("Min", 5)
        create_title("Max", 6)
        create_title("Med", 7)
        create_title("Mean", 8)
        create_title("Std", 9)
        #create_title("", 11) # Dummy allowing extra room for categorical info
        
        def create_checkbutton(row, col, column_name):
            var = tk.BooleanVar(self.colframe, value=False)
            var.column_name = column_name
            self.colframe.checkbutton_vars[col].append(var)
            cb = ttk.Checkbutton(self.colframe, text="", takefocus=False,
                                variable=var, onvalue=True, offvalue=False)
            cb.grid(row=row, column=col, sticky="nsew", pady=(0,1))
        
        def create_label(row, col, col_name, value, expr_template=None, hide_zero=False, wraplength=100,
                         anchor="ne", justify="right", columnspan=1):
            
            if (isinstance(value, float) and math.isnan(value) 
                or value == 0 and hide_zero):
                text = ""
            else:
                text = str(value)
             
            link = tk.Label(self.colframe,
                            wraplength=wraplength,
                            text=text,
                            background=CALM_WHITE, # if row % 2 == 0 else None,
                            anchor=anchor,
                            justify=justify,
                            foreground="blue",
                            cursor="hand2")
            link.grid(row=row, column=col, sticky="nsew", pady=(0,1), padx=(0,1),
                      columnspan=columnspan)
            
            if expr_template is not None:
                link.bind("<1>", 
                          lambda e: self.send_command_to_shell(expr_template, df_expr, col_name),
                          True)
        
        for i, col_info in enumerate(info["columns"]):
            row = i+1
            name = col_info["name"]
            create_checkbutton(row, 0, name)
            create_checkbutton(row, 1, name)
            create_label(row, 2, name, name, anchor="nw", justify="left",
                         expr_template="{df}['{column}'].dtype")
            create_label(row, 3, name, col_info["count"], hide_zero=True)
            create_label(row, 4, name, info["row_count"] - col_info["count"], hide_zero=True)
            create_label(row, 5, name, col_info["min"])
            create_label(row, 6, name, col_info["max"])
            if math.isnan(col_info["mean"]):
                if col_info["unique"] == col_info["count"]:
                    unique_text = "all unique"
                else:
                    unique_text = (str(col_info["unique"]) + " unique" 
                                   + ("s" if col_info["unique"] != 1 else ""))
                create_label(row, 7, name, unique_text, columnspan=5,
                             anchor="n", wraplength=None)
            else:
                create_label(row, 7, name, col_info["50%"])
                create_label(row, 8, name, col_info["mean"], wraplength=60)
                create_label(row, 9, name, col_info["std"], wraplength=60)
            
        self.after_idle(lambda: self.after(100, self.update_scrollbars))
        
    def send_command_to_shell(self, expr_template, df_name, column_name):
        # TODO: check that df_name is really variable name
        # TODO: check that runner state is suitable
        expr = expr_template.format(df=df_name, column=column_name).strip() + "\n"
        get_workbench().show_view("ShellView").submit_python_code(expr)

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

def listen_toplevel_results(event):
    if getattr(event, "show_dfe", False):
        view = get_workbench().show_view("DataFrameExplorer")
        info = getattr(event, "dataframe_info", None)
        if info is not None:
            view.load_dataframe(info)

def load_early_plugin():
    get_workbench().add_content_inspector(DataFrameInspector)


def load_plugin():
    get_workbench().add_view(DataFrameExplorer, "DataFrame explorer", "ne")
    get_workbench().bind("ToplevelResult", listen_toplevel_results, True)
