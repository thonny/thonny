# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
        
        self.columns = {}
        self.colframe = None
        self._last_globals = {}
        self.df_expr = None
        self.plt_info = None
    
    
    def _init_plotting(self):
        plotframe = ttk.Frame(self)
        plotframe.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        innerpad=5
        
        default_font = tk.font.nametofont("TkDefaultFont")
        bold_font = default_font.copy()
        bold_font.configure(weight="bold", size=int(default_font.cget("size")*1.5)) # need to explicitly copy size, because Tk 8.6 on certain Ubuntus use bigger font in copies
        
        def title(text, row):
            label = tk.Label(plotframe, text=text, anchor="w", font=bold_font)
            label.grid(row=row, column=0, sticky="w")
        
        def channel(name, row, column, caption=None):
            if caption == None:
                caption = name
            label = ttk.Label(plotframe, text=caption, anchor="w")
            label.grid(row=row, column=column, sticky="nsew", pady=(2, 0), padx=innerpad)
            
            tray = ChannelTray(plotframe)
            tray.grid(row=row+1, column=column, sticky="nsew", pady=(0, 2), padx=innerpad)
            self.channel_trays[name] = tray
            
            return tray
        
        #title("Plot", 0)
        self.channel_trays = {}
        
        channel("x", 1, 0, "x-axis")
        channel("y", 1, 1, "y-axis")
        channel("color", 1, 2)
        
        ttk.Label(plotframe, text="kind", anchor="w").grid(row=1, column=3, sticky="nsew")
        kind_combo = ttk.Combobox(plotframe,
                              exportselection=False,
                              state='readonly', 
                              values=["auto", "point", "bar", "line"],
                              width=5)
        kind_combo.grid(row=2, column=3, sticky="nsew", pady=(0, 2))
        
        #channel("row", 3, 0)
        #channel("column", 3, 1)
        
        plotframe.columnconfigure(0, weight=1)
        plotframe.columnconfigure(1, weight=1)
        plotframe.columnconfigure(2, weight=1)
        plotframe.columnconfigure(3, weight=0)
        
        
        
    
    def _init_plotting_old(self):        
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
            
        buttons = ["individual", "count", "summary", "distribution"]
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
        create_title("Unique", 4)
        create_title("Nulls", 5)
        create_title("Min", 6)
        create_title("Max", 7)
        #create_title("...", 8)
        
        def create_checkbutton(row, col, column_name):
            var = tk.BooleanVar(self.colframe, value=False)
            var.column_name = column_name
            self.colframe.checkbutton_vars[col].append(var)
            cb = ttk.Checkbutton(self.colframe, text="", takefocus=False,
                                variable=var, onvalue=True, offvalue=False)
            cb.grid(row=row, column=col, sticky="nsew", pady=(0,1))
        
                
        def sort_expr_template(name, ascending, sort_as_str):
            expr = "{df}"
            #expr += ".dropna(subset=['{column}'])"
            if sort_as_str:
                expr += ".astype(str)"
            expr += (".sort_values('%s', ascending=" % name) + str(ascending) + ") ?"
            return expr
        
        self.columns = {}
        for i, col_info in enumerate(info["columns"]):
            row = i+1
            name = col_info["name"]
            self.columns[name] = col_info
            #create_checkbutton(row, 0, name)
            #create_checkbutton(row, 1, name)
            
            #self.create_label(row, 2, name, name, anchor="nw", justify="left",
            #             on_click=self.get_name_click_handler(name, col_info))
            name_widget = SourceFieldWidget(self.colframe, self, name)
            name_widget.grid(row=row, column=2, sticky="nsew")
            
            
            self.create_label(row, 3, col_info["count"], hide_zero=True)
            self.create_label(row, 4, col_info["unique"], hide_zero=True,
                              code_template="{df}['%s'].value_counts() ?" % name)
            self.create_label(row, 5, info["row_count"] - col_info["count"], hide_zero=True)
            self.create_label(row, 6, col_info["min"],
                         code_template=sort_expr_template(name, True, col_info["sort_as_str"]))
            self.create_label(row, 7, col_info["max"],
                         code_template=sort_expr_template(name, False, col_info["sort_as_str"]))
            
            
        self.after_idle(lambda: self.after(100, self.colcontainer.update_scrollbars))
        
        
        #for combo in [self.x_combo, self.y_combo, self.hue_combo,
        #              self.weight_combo, self.row_combo, self.col_combo]:
        #    combo.configure(values=list(self.columns.keys()))
    
    def create_label(self, row, col, value, hide_zero=False, wraplength=100,
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
            link.bind("<1>", lambda e: self.send_command_to_shell(code_template), True)
    
    
    def send_command_to_shell(self, expr_template):
        # TODO: check that df_name is really variable name
        # TODO: check that runner state is suitable
        # TODO: empty line for multiline code
        expr = expr_template.format(df=self.df_name).strip() + "\n"
        get_workbench().show_view("ShellView").submit_python_code(expr)

    def _handle_globals_event(self, event):
        self._last_globals = event.globals
    
    def _request_plt_info(self, event=None):
        # update info about whether matplotlib.pyplot has been imported
        get_runner().send_command(InlineCommand(command="get_plt_info"))
    
    def _update_plt_info(self, msg):
        self.plt_info = msg 
    
    def add_field_for_plotting(self, field_name):
        field = UsedFieldWidget(self, self, field_name)
        old_field = self.channel_trays["x"].accept_field(field)
        # TODO: temp
        if old_field is not None:
            old_field.destroy()
         
    
    def clear_trays(self):
        for name in self.channel_trays:
            self.channel_trays[name].clear()
                
    
    def plot(self):
        def get_channel_info(name):
            tray = self.channel_trays[name]
            if tray.field is None:
                return None
            else:
                result = self.columns[tray.field.name].copy()
                result["function"] = tray.field.function
                return result
        
        x = get_channel_info("x")
        y = get_channel_info("y")
        color = get_channel_info("color")
        
        # TODO: 
        kind = "bar"
        if kind == "auto":
            "TODO: choose most suitable kind"
        
        try:
            template = self._histogram(x)
            self.send_command_to_shell(template)
            
        except BadChannelsError as e:
            messagebox.showerror("Bad channels", str(e))
        
    
    def _histogram(self, field_info):
        if math.isnan(field_info["mean"]):
            base_code = "{df}['%s'].value_counts().sort_index().plot.bar(ax=dfe_ax, sort_columns=True) ?" % field_info["name"]
        else:
            base_code = "{df}['%s'].hist(ax=dfe_ax, bins='auto') ?" % field_info["name"]
            
        template = ""
        if self.plt_info is None:
            plt = "plt"
            template = "import matplotlib.pyplot as plt\n"
        else:
            if not self.plt_info.imported:
                template = "import matplotlib.pyplot as " + self.plt_info["name"] + "\n"
            plt = self.plt_info.name
        
        if getattr(self.plt_info, "dfe_fig_exists", False):
            template += plt + ".close(dfe_fig) # avoid wasting memory\n"
            
        template += "dfe_fig, dfe_ax = " + plt +".subplots(tight_layout=True)\n"
        template += "dfe_ax.set(xlabel='"+field_info["name"]+"', ylabel='count')\n"
        template += base_code
        return template
    
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


class FieldWidget(tk.Frame):
    def __init__(self, master, dfe, field_name, include_menu, action_label = " × "):
        self.background = "LightGray"
        self.action_label = action_label
        self.name = field_name
        self.dfe = dfe
        
        tk.Frame.__init__(self, master, background=self.background)
        
        if include_menu:
            menu_button = tk.Label(self, text=" ▾ ", background=self.background) # ▼ ▾ 
            menu_button.grid(row=0, column=0, sticky="nsw")
            menu_button.bind("<Enter>", self.section_enter, True)
            menu_button.bind("<Leave>", self.section_leave, True)
            menu_button.bind("<1>", self.menu_press, True)
        
        name_label = tk.Label(self, text=field_name, 
                              background=self.background, cursor="fleur",
                              wraplength=100, anchor="w")
        name_label.bind("<Enter>", self.section_enter, True)
        name_label.bind("<Leave>", self.section_leave, True)
        name_label.grid(row=0, column=1, sticky="nsew")
        
        action_button = tk.Label(self, text=action_label, background=self.background) # ×
        action_button.grid(row=0, column=2, sticky="nse")
        action_button.bind("<Enter>", self.section_enter, True)
        action_button.bind("<Leave>", self.section_leave, True)
        action_button.bind("<1>", self.action_click, True)
        action_button.bind("<Double-Button-1>", self.action_double_click, True)
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
    
    def section_enter(self, event):
        event.widget["background"] = "DarkGray"
        event.widget["foreground"] = "White"
        
    def section_leave(self, event):
        event.widget["background"] = self.background
        event.widget["foreground"] = "black"
    
    def action_click(self, event):
        print("action")
    
    def action_double_click(self, event):
        print("action double")
    
    def menu_press(self, event):
        print("menu")

class SourceFieldWidget(FieldWidget):
    def __init__(self, master, dfe, field_name):
        FieldWidget.__init__(self, master, dfe, field_name, False, " + ")
    
    def action_click(self, event):
        self.dfe.add_field_for_plotting(self.name)
        self.dfe.plot()

    def action_double_click(self, event):
        print("dbcl")
        self.dfe.clear_trays()
        self.dfe.add_field_for_plotting(self.name)
        self.dfe.plot()

class UsedFieldWidget(FieldWidget):
    def __init__(self, master, dfe, field_name):
        FieldWidget.__init__(self, master, dfe, field_name, True, " × ")
        self.function = None 
    
    def action_click(self, event):
        self.destroy()


class ChannelTray(tk.Frame):
    def __init__(self, master):
        self.field = None
        tk.Frame.__init__(self, master, background="pink")
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
    
    def clear(self):
        if self.field is not None:
            self.field.destroy()
            self.field = None
    
    def accept_field(self, field):
        old_field = self.field
        field.grid(row=0, column=0, in_=self)
        self.field = field
        
        return old_field

class BadChannelsError(RuntimeError):
    pass

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
