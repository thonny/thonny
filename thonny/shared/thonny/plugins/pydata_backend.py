import io
import sys
import numpy as np

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
    df = eval(cmd.args_str, vm.get_main_module().__dict__)
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
    
    cols = []
    for column in desc:
        cols.append({
            'name' : column,
            'count' : int(get_att(column, "count")),
            'mean' : get_att(column, "mean"),
            'std' : get_att(column, "std"),
            'min' : get_att(column, "min", True),
            'median' : get_att(column, "50%", True),
            'max' : get_att(column, "max", True),
        })
  
    return {"show_dfe" : True,
            "dataframe_info" : {"row_count" : len(df),
                      "columns" : cols}
            }


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
        info.update(_export_dataframe(value))
        info["is_DataFrame"] = True
        
        import pandas as pd  # @UnresolvedImport
        info["float_format"] = pd.options.display.float_format 

def _check_add_matplotlib_info(value, info, cmd):
    if (type(value).__name__ == "Figure"
        and type(value).__module__ == "matplotlib.figure"):
        # TODO: test with ion/ioff
        
        frame_width = getattr(cmd, "frame_width", None)
        frame_height = getattr(cmd, "frame_height", None)
        if frame_width is not None and frame_height is not None:
            frame_ratio = frame_width / frame_height
            fig_ratio = value.get_figwidth() / value.get_figheight()
            if frame_ratio > fig_ratio:
                # image size should depend on height
                dpi = frame_height / value.get_figheight()
            else:
                dpi = frame_width / value.get_figwidth()
        else:
            dpi = None
        
        
        #import matplotlib.pyplot as plt
        fp = io.BytesIO()
        value.savefig(fp, format="png", dpi=dpi)
        
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
    
    """
    import platform
    if platform.system() != "Linux":
        # http://stackoverflow.com/a/13867710/261181
        self.iconify()
        self.deiconify()
    """

def _export_dataframe(df, all_rows=False, all_columns=False):
    import pandas as pd
    
    # TODO: pd.options.display.max_rows and max_columns
    return {
        "columns" : df.columns.tolist(),
        "index" : df.index.astype(str).tolist(),
        "values" : df.values.round(pd.options.display.precision).astype(str).tolist(), 
        "row_count" : len(df)
    }
        

def load_plugin(_vm):
    global vm
    vm = _vm
    vm.add_command("dataexplore", handle_dataexplore)    
    vm.add_command("de", handle_dataexplore)
    vm.add_command("delite", handle_delite)
    vm.add_command("dfe", handle_dfe)
    vm.add_value_tweaker(tweak_pandas_value)
    vm.add_value_tweaker(tweak_numpy_value)
    vm.add_object_info_tweaker(_check_add_dataframe_info)
    vm.add_object_info_tweaker(_check_add_matplotlib_info)
    