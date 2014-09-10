"""
import os.path
import sys

_user_copy_path = os.path.expanduser("~/.thonny/user_copy/thonny")
if os.path.exists(os.path.join(_user_copy_path, "main.py")):
    sys.path[0] = _user_copy_path
"""

try:
    # http://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7
    import ctypes
    #ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AivarAnnamaa.Thonny")
except:
    # TODO:
    pass


import main
main.Thonny().mainloop()    