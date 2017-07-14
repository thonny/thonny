# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from thonny.plugins.object_inspector2 import ContentInspector
from thonny.gridtable import ScrollableGridTable
from thonny.globals import get_workbench, get_runner
from thonny.ui_utils import VerticallyScrollableFrame, CALM_WHITE
import math
from thonny.shared.thonny.common import InlineCommand

class DataFrameExplorer(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        
        self.colcontainer = VerticallyScrollableFrame(self)
        self.colcontainer.grid(row=0, column=0, sticky="nsew")
        self.colcontainer.interior.columnconfigure(0, weight=1)
        self.colcontainer.interior.rowconfigure(0, weight=1)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._init_plotting()
    
        get_workbench().bind("ToplevelResult", self._request_plt_info, True)
        get_workbench().bind("PltInfo", self._update_plt_info, True)
        
        self.colframe = None
        self._last_globals = {}
        self.df_expr = None
        self.plt_info = None
    
    def _init_plotting(self):        
        compframe = ttk.Frame(self)
        compframe.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        innerpad=2
        
        def title(column, text):
            label = ttk.Label(compframe, text=text)
            label.grid(row=0, column=column, sticky="nsew", pady=2, padx=innerpad)
            return label
        
        
        title(0, "X-axis / Y-axis")
        title(1, "Hue / Weight")
        title(2, "Column / Row")
        
        def combo(row, column):
            cb = ttk.Combobox(compframe,
                              exportselection=False,
                              state='readonly')
            cb.grid(row=row, column=column, sticky="nsew", pady=innerpad, padx=innerpad)
            return cb
            
        self.x_combo = combo(1, 0)  
        self.y_combo = combo(2, 0)
          
        self.hue_combo = combo(1, 1)  
        self.weight_combo = combo(2, 1)  

        self.col_combo = combo(1, 2)  
        self.row_combo = combo(2, 2)  
        
        compframe.columnconfigure(0, weight=1)
        compframe.columnconfigure(1, weight=1)
        compframe.columnconfigure(2, weight=1)
        
        button_strip = ttk.Frame(self)
        button_strip.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0,10))
        
        def button(i, name):
            bt = ttk.Button(button_strip, text=name, command=lambda: self.plot(name))
            bt.grid(row=0, column=i, sticky="nsew", padx=2)
            button_strip.columnconfigure(i, weight=1)
            
        buttons = ["count", "mean", "quartiles", "corr", "line", "crosstab", "extra"]
        for i, name in enumerate(buttons):
            button(i, name)
        
    def load_dataframe(self, info):
        self.df_name = info["df_name"]
        
        if self.colframe is not None:
            self.colframe.grid_forget()
            self.colframe.destroy()
        
        self.colframe = tk.Frame(self.colcontainer.interior)
        self.colframe.grid(sticky="nsw")
        self.colframe.checkbutton_vars = ([], [])
        
        def create_title(text, col, colspan=1):
            label = tk.Label(self.colframe, text=text, anchor="n", justify="center")
            label.grid(row=0, column=col, columnspan=colspan, sticky="nsew")
            
        #create_title("Plot by", 0, 2)
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
        
                
        def sort_expr_template(ascending, sort_as_str):
            expr = "{df}"
            #expr += ".dropna(subset=['{column}'])"
            if sort_as_str:
                expr += ".astype(str)"
            expr += ".sort_values('{column}', ascending=" + str(ascending) + ") ?"
            return expr
        
        col_names = []
        for i, col_info in enumerate(info["columns"]):
            row = i+1
            name = col_info["name"]
            col_names.append(name)
            #create_checkbutton(row, 0, name)
            #create_checkbutton(row, 1, name)
            
            self.create_label(row, 2, name, name, anchor="nw", justify="left",
                         on_click=self.get_name_click_handler(name, col_info))
            
            self.create_label(row, 3, name, col_info["count"], hide_zero=True)
            self.create_label(row, 4, name, info["row_count"] - col_info["count"], hide_zero=True)
            self.create_label(row, 5, name, col_info["min"],
                         code_template=sort_expr_template(True, col_info["sort_as_str"]))
            self.create_label(row, 6, name, col_info["max"],
                         code_template=sort_expr_template(False, col_info["sort_as_str"]))
            
            if math.isnan(col_info["mean"]):
                if col_info["unique"] == col_info["count"]:
                    unique_text = "all unique"
                else:
                    unique_text = (str(col_info["unique"]) + " unique" 
                                   + ("s" if col_info["unique"] != 1 else ""))
                self.create_label(row, 7, name, unique_text, columnspan=5,
                             anchor="n", wraplength=None)
            else:
                self.create_label(row, 7, name, col_info["50%"])
                self.create_label(row, 8, name, col_info["mean"], wraplength=60)
                self.create_label(row, 9, name, col_info["std"], wraplength=60)
            
        self.after_idle(lambda: self.after(100, self.colcontainer.update_scrollbars))
        
        
        for combo in [self.x_combo, self.y_combo, self.hue_combo,
                      self.weight_combo, self.row_combo, self.col_combo]:
            combo.configure(values=col_names)
    
    def create_label(self, row, col, col_name, value, hide_zero=False, wraplength=100,
                     anchor="ne", justify="right", columnspan=1,
                     on_click=None, code_template=None):
        
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
        
        if on_click is not None:
            link.bind("<1>", on_click, True)
        elif code_template is not None:
            link.bind("<1>", lambda e: self.send_command_to_shell(code_template, col_name), True)
    
    def get_name_click_handler(self, name, col_info):
        if math.isnan(col_info["mean"]):
            base_code = "{df}['{column}'].value_counts().plot.barh(sort_columns=True) ?"
        else:
            base_code = "{df}['{column}'].hist(bins='auto') ?"
            
        def handle_name_click(event):
            template = ""
            if self.plt_info is None:
                plt = "plt"
                template = "import matplotlib.pyplot as plt\n"
            else:
                if not self.plt_info.imported:
                    template = "import matplotlib.pyplot as " + self.plt_info.name + "\n"
                plt = self.plt_info.name
                
            
            #template += plt + ".figure(tight_layout=True); "
            template += plt + ".cla(); "
            template += base_code
            
            self.send_command_to_shell(template, name)
            #self.send_command_to_shell(plt + ".tight_layout()")
        
        return handle_name_click
        
    
    def send_command_to_shell(self, expr_template, column_name):
        # TODO: check that df_name is really variable name
        # TODO: check that runner state is suitable
        expr = expr_template.format(df=self.df_name, column=column_name).strip() + "\n"
        get_workbench().show_view("ShellView").submit_python_code(expr)

    def _handle_globals_event(self, event):
        self._last_globals = event.globals
    
    def _request_plt_info(self, event=None):
        # update info about whether matplotlib.pyplot has been imported
        get_runner().send_command(InlineCommand(command="get_plt_info"))
    
    def _update_plt_info(self, msg):
        self.plt_info = msg 
    
    def plot(self, kind):
        print(kind)   
        

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
