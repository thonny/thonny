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
        info["columns"] = value.columns.tolist()
        info["index"] = value.index.tolist() # TODO: convert to strings
        info["values"] = value.values.tolist() # TODO: convert to strings
        info["row_count"] = len(value)
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
    
        

def load_plugin(_vm):
    global vm
    vm = _vm
    vm.add_command("dataexplore", handle_dataexplore)    
    vm.add_command("de", handle_dataexplore)
    vm.add_command("delite", handle_delite)
    vm.add_value_tweaker(tweak_pandas_value)
    vm.add_value_tweaker(tweak_numpy_value)
    vm.add_object_info_tweaker(_check_add_dataframe_info)
    vm.add_object_info_tweaker(_check_add_matplotlib_info)
    