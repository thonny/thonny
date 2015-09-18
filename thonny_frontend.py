import sys
import os.path
import traceback
import tkinter.messagebox
from logging import exception


if getattr(sys, 'frozen', False):
    # The application is frozen
    this_file = sys.executable
else:
    # The application is not frozen
    this_file = __file__


try:
    from thonny import workbench
    workbench.Workbench(os.path.abspath(os.path.join(this_file, os.pardir)))
except:
    exception("Internal error")
    tkinter.messagebox.showerror("Internal error", traceback.format_exc())
