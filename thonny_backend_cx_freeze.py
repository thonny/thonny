# -*- coding: utf-8 -*-

# This file is used only in frozen backend

import sys
import os.path

# main directory may be present as '', but I want absolute path
main_dir = os.path.dirname(sys.executable)
if main_dir not in sys.path:
    sys.path.append(main_dir)

# for some reason cx_freeze includes executable as path item
if sys.executable in sys.path:
    sys.path.remove(sys.executable)

# for some reason cx_freeze includes non existant thonny_backend.zip as path item
backend_zip = os.path.join(main_dir, "thonny_backend.zip")
if backend_zip in sys.path:
    sys.path.remove(backend_zip)

from imp import load_dynamic            # @UnusedImport, otherwise this function is not available in frozen 3.5

import thonny_backend                   # @UnusedImport

