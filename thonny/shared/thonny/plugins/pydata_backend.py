import io
import sys
import logging

app = None
vm = None


def handle_dataexplore(command_line):
    from thonny.common import parse_shell_command
    from pandastable.app import DataExplore
    import tkinter as tk
    global app
    command, args = parse_shell_command(command_line, False)
    
    if app is None:
        app = DataExplore()
    else:
        try:
            app.state()
        except tk.TclError:
            app = DataExplore()
        
    
    if len(args) == 1 and args[0].strip() != "":
        expr = args[0].strip()
        df = eval(expr, vm.get_main_module().__dict__)
        app.load_dataframe(df, expr)

def tweak_value(value, record):
    # "weak" import pandas, because user script maybe uses only numpy
    pd = sys.modules.get("pandas")
    if pd is None:
        return
    
    if isinstance(value, pd.DataFrame):
        shape = value.shape
        record["description"] = (type(value).__name__ 
                                 + " [" + str(shape[0]) + " rows x "
                                 + str(shape[1]) + " columns]")
    elif isinstance(value, pd.Series):
        record["description"] = ("Series [Name: %s, Length: %d, dtype: %s]" 
                                 % (value.name, value.shape[0], value.dtype.name))

def _check_add_dataframe_info(value, info, cmd):
    if (type(value).__name__ == "DataFrame"
        and type(value).__module__ == "pandas.core.frame"):
        info["columns"] = value.columns.tolist()
        info["index"] = value.index.tolist()
        info["values"] = value.values.tolist()
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

        

def load_plugin(vm):
    vm.add_magic_command("dataexplore", handle_dataexplore)    
    vm.add_magic_command("de", handle_dataexplore)
    vm.add_value_tweaker(tweak_value)
    vm.add_object_info_tweaker(_check_add_dataframe_info)
    vm.add_object_info_tweaker(_check_add_matplotlib_info)
    