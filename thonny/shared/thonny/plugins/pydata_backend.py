"""
import io
import sys
import numpy as np
import datetime

app = None
vm = None

def handle_delite(cmd):
    import tkinter as tk
    from tkinter import ttk
    root = tk.Tk()
    frame = ttk.Frame(root)
    frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    from pandastable import Table
    #assuming parent is the frame in which you want to place the table
    pt = Table(frame)
    pt.show()
    
    root.mainloop()


def handle_dfe(cmd):
    if not cmd.args_str:
        return {"show_dfe" : True}
    
    import pandas as pd
    df_expr = cmd.args_str
    # TODO: if expr is not variable then create a variable
    df = eval(df_expr, vm.get_main_module().__dict__)
    desc = df.describe(include="all").round(pd.options.display.precision)
    
    def get_att(column, attname, try_int=False):
        if attname in desc.index:
            val = desc.at[attname, column]
            if (try_int and not np.isnan(val) and val == int(val) 
                and "int" in df[column].dtype.name):
                return int(val)
            else:
                return val
        else:
            return None
    
    def shorten(s):
        if len(s) > 10:
            return s[:7] + '…'
        else:
            return s
    
    def format_ts(ts):
        if ts.time() == datetime.time(0):
            return str(ts)[:10]
        else:
            return str(ts)[:10] + '…'
    
    cols = []
    for column in desc:
        sort_as_str = False
        
        if "first" in desc.index and not pd.isnull(desc.at["first", column]):
            min_ = format_ts(desc.at["first", column])
            max_ = format_ts(desc.at["last", column])
        elif "min" in desc.index and not pd.isnull(desc.at["min", column]):
            min_ = get_att(column, "min", True)
            max_ = get_att(column, "max", True)
        #elif df[column].dtype == np.dtype('<M8[ns]'):
        #    min_ = get_att(column, "first", True)
        #    max_ = get_att(column, "last", True)
        else:
            dropna = df[column].dropna()
            try:
                
                min_ = shorten(str(dropna.min()))
                max_ = shorten(str(dropna.max()))
            except TypeError:
                # Must contain mixed datatypes
                sort_as_str = True
                min_ = shorten(dropna.astype(str).min())
                max_ = shorten(dropna.astype(str).max())
        
        unique = get_att(column, "unique", True)
        if np.isnan(unique):
            unique = df[column].nunique()
            
        cols.append({
            'name' : column,
            'count' : int(get_att(column, "count")),
            'unique' : unique,
            #'top' : str(get_att(column, "top")),
            'mean' : get_att(column, "mean"),
            'std' : get_att(column, "std"),
            'min' : min_,
            '50%' : get_att(column, "50%", True),
            'max' : max_,
            'sort_as_str' : sort_as_str
        })
  
    return {"show_dfe" : True,
            "dataframe_info" : {"row_count" : len(df),
                                "columns" : cols,
                                "df_name" : df_expr}
            }

def handle_get_plt_info(cmd):
    # gets the variable name for matplotlib.pyplot 
    # and whether it is imported 
    from types import ModuleType
    
    globs = vm.get_main_module().__dict__
    for name in globs:
        if isinstance(globs[name], ModuleType) and globs[name].__name__ == 'matplotlib.pyplot':
            plt_name = name
            imported = True
            break
    else:
        recommended_name = "plt"
        while recommended_name in globs:
            recommended_name += "_"
        
        plt_name = recommended_name
        imported = False
    
    return {"message_type" : "PltInfo",
            "name" : plt_name,
            "imported" : imported,
            "dfe_fig_exists" : "dfe_fig" in globs}


def handle_dataexplore(cmd):
    from pandastable.app import DataExplore  # @UnresolvedImport
    import tkinter as tk
    global app
    
    if cmd.args_str:
        df = eval(cmd.args_str, vm.get_main_module().__dict__)
    else:
        df = None
    
    
    def create_app():
        global app
        app = DataExplore()
        #app.newProject(df=df)
        
    if app is None:
        create_app()
    else:
        try:
            app.state()
        except tk.TclError:
            create_app()
    
    # Show dataexplore window
    _bring_up(app.main)
    #app.bring_to_foreground()
    
    # load data
    if df is not None:
        #app.load_dataframe(df, cmd.args_str, select=True)
        app.load_dataframe(df, cmd.args_str)
    
    # Bring up correct tab
    ind = app.nb.index('end')-1
    s = app.nb.tabs()[ind]
    app.nb.select(s)
    

def tweak_numpy_value(value, record):
    if isinstance(value, np.ndarray):  # @UndefinedVariable
        record["description"] = ("NumPy " + value.dtype.name + " array [" 
                                 + " x ".join(map(str, value.shape))
                                 + "]")

def tweak_pandas_value(value, record):
    # "weak" import pandas, because user script maybe uses only numpy
    pd = sys.modules.get("pandas")
    if pd is None:
        return
    
    if isinstance(value, pd.DataFrame):
        shape = value.shape
        record["description"] = ("pandas " + type(value).__name__ 
                                 + " [" + str(shape[0]) + " rows x "
                                 + str(shape[1]) + " columns]")
    elif isinstance(value, pd.Series):
        record["description"] = ("pandas " + type(value).__name__ +  
                                  " [Name: %s, Length: %d, dtype: %s]" 
                                   % (value.name, value.shape[0], value.dtype.name))

def _check_add_dataframe_info(value, info, cmd):
    pd = sys.modules.get("pandas")
    if pd is None:
        return
    
    if isinstance(value, pd.DataFrame):
        info.update(_export_dataframe(value, num_rows=pd.options.display.max_rows))
        info["is_DataFrame"] = True
        
        import pandas as pd  # @UnresolvedImport
        info["float_format"] = pd.options.display.float_format 

def _check_add_matplotlib_info(value, info, cmd):
    if (type(value).__name__ == "Figure"
        and type(value).__module__ == "matplotlib.figure"):
        fig = value
    elif ("matplotlib" in type(value).__module__
          and hasattr(value, "get_figure")):
        fig = value.get_figure()
    else:
        return
    # TODO: test with ion/ioff
    
    frame_width = getattr(cmd, "frame_width", None)
    frame_height = getattr(cmd, "frame_height", None)
    if frame_width is not None and frame_height is not None:
        frame_ratio = frame_width / frame_height
        fig_ratio = fig.get_figwidth() / fig.get_figheight()
        if frame_ratio > fig_ratio:
            # image size should depend on height
            dpi = frame_height / fig.get_figheight()
        else:
            dpi = frame_width / fig.get_figwidth()
    else:
        dpi = None
    
    
    #import matplotlib.pyplot as plt
    fp = io.BytesIO()
    fig.savefig(fp, format="png", dpi=dpi)
    
    import base64
    info["image_data"] = base64.b64encode(fp.getvalue())
    fp.close() 

def _bring_up(window):
    # copied from thonny.workbench.Workbench
    # Looks like at least on Windows all following is required for the window to get focus
    # (deiconify, ..., iconify, deiconify)
    window.deiconify()
    window.attributes('-topmost', True)
    window.after_idle(window.attributes, '-topmost', False)
    window.lift()
    
    "_""
    import platform
    if platform.system() != "Linux":
        # http://stackoverflow.com/a/13867710/261181
        self.iconify()
        self.deiconify()
    "_""

def _export_dataframe(df, num_rows="all", all_columns=False):
    import pandas as pd
    
    # TODO: pd.options.display.max_rows and max_columns
    # TODO: take both beginning and end
    if num_rows == "all":
        subframe = df
    else:
        subframe = df.head(num_rows)
        
    return {
        "columns" : df.columns.tolist(),
        "index" : subframe.index.astype(str).tolist(),
        "values" : subframe.round(pd.options.display.precision).astype(str).values.tolist(), 
        "row_count" : len(df)
    }
        

def load_plugin(_vm):
    global vm
    vm = _vm
    vm.add_command("get_plt_info", handle_get_plt_info)    
    vm.add_command("dataexplore", handle_dataexplore)    
    vm.add_command("de", handle_dataexplore)
    vm.add_command("delite", handle_delite)
    vm.add_command("dfe", handle_dfe)
    vm.add_value_tweaker(tweak_pandas_value)
    vm.add_value_tweaker(tweak_numpy_value)
    vm.add_object_info_tweaker(_check_add_dataframe_info)
    vm.add_object_info_tweaker(_check_add_matplotlib_info)
"""