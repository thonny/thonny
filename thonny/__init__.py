import traceback
import tkinter.messagebox
from logging import exception

def launch():
    try:
        from thonny import workbench
        workbench.Workbench()
        return 0
    except:
        exception("Internal error")
        tkinter.messagebox.showerror("Internal error", traceback.format_exc())
        return -1
