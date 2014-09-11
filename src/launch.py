"""
import os.path
import sys

_user_copy_path = os.path.expanduser("~/.thonny/user_copy/thonny")
if os.path.exists(os.path.join(_user_copy_path, "main.py")):
    sys.path[0] = _user_copy_path
"""

import main
main.Thonny().mainloop()    