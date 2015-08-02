import sys
import os.path
import traceback
import tkinter
import logging


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# Tweak the path
# First remove the current folder from path
if sys.argv[0] in sys.path: 
    sys.path.remove(sys.argv[0]) # ../thonny/thonny


# It is assumed that Thonny is run with
#     python3 /absolute/path/to/thonny/thonny
# We don't assume that path contains
#             /absolute/path/to/thonny
# therefore we add it to path, because that's the base for thonny package
installation_dir = os.path.normpath(os.path.join(__file__, os.pardir, os.pardir))
if installation_dir not in sys.path:
    sys.path.insert(0, installation_dir)




# Run
try:
    from thonny import workbench
    workbench.Workbench(installation_dir).mainloop()
except:
    traceback.print_exc()
    tkinter.messagebox.showerror("Internal error. Use Ctrl+C to copy error message",
                            traceback.format_exc())
