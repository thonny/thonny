# -*- coding: utf-8 -*-
"""
This file is run by VMProxy

(I could run also backend.py directly, but I want to have clean global scope 
in __main__ module (because that's where user scripts run), but backend's global scope 
is far from clean. 
I could also do python -c "from backend import VM: VM().mainloop()", but looks like this 
gives relative __file__-s on imported modules.) 
"""

from backend import VM
VM().mainloop()