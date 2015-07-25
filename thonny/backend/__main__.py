# -*- coding: utf-8 -*-
"""
This file is run by VMProxy

(Why separate file for launching? I want to have clean global scope 
in toplevel __main__ module (because that's where user scripts run), but backend's global scope 
is far from clean. 
I could also do python -c "from backend import VM: VM().mainloop()", but looks like this 
gives relative __file__-s on imported modules.) 
"""

import sys
import logging
import os.path

# Tweak the path

# It is assumed that backend is run with
#     python3 /absolute/path/to/thonny/thonny/backend
# We don't assume that path contains
#             /absolute/path/to/thonny
# therefore we add it to path, because that's the base for thonny package
main_dir = os.path.normpath(os.path.join(__file__, os.pardir, os.pardir))
if main_dir not in sys.path:
    sys.path.insert(0, main_dir)

from thonny.backend import VM

# set up logging
logger = logging.getLogger("thonny.backend")

file_handler = logging.FileHandler(os.path.expanduser(os.path.join("~",".thonny","backend.log")), encoding="UTF-8");
file_handler.setLevel(logging.WARNING);
logger.addHandler(file_handler)

# TODO: sending log records to original stdout could be better (reading from stderr may introduce sync problems)
stream_handler = logging.StreamHandler(stream=sys.stderr)
logger.addHandler(stream_handler)

# create and run VM
VM(main_dir).mainloop()