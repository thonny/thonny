# -*- coding: utf-8 -*-
"""
This file is run by VMProxy

(Why separate file for launching? I want to have clean global scope 
in toplevel __main__ module (because that's where user scripts run), but backend's global scope 
is far from clean. 
I could also do python -c "from backend import VM: VM().mainloop()", but looks like this 
gives relative __file__-s on imported modules.) 
"""

if __name__ == "__main__":
    # imports required by backend itself
    import sys
    import logging
    import os.path
    
    # remove script dir from path
    sys.path.pop(0)
    
    # import thonny relative to this script (not from current interpreter path)
    import importlib.util
    spec = importlib.util.spec_from_file_location (
        "thonny", 
        os.path.join(os.path.dirname(__file__), "__init__.py")
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["thonny"] = module
    spec.loader.exec_module(module)
    
    THONNY_USER_DIR = os.environ["THONNY_USER_DIR"]
    # set up logging
    logger = logging.getLogger()
    logFormatter = logging.Formatter('%(levelname)s: %(message)s')
    file_handler = logging.FileHandler(os.path.join(THONNY_USER_DIR,"backend.log"), 
                                       encoding="UTF-8",
                                       mode="w");
    file_handler.setFormatter(logFormatter)
    file_handler.setLevel(logging.INFO);
    logger.addHandler(file_handler)
    
    # TODO: sending log records to original stdout could be better (reading from stderr may introduce sync problems)
    stream_handler = logging.StreamHandler(stream=sys.stderr)
    stream_handler.setLevel(logging.INFO);
    stream_handler.setFormatter(logFormatter)
    logger.addHandler(stream_handler)
    
    logger.setLevel(logging.INFO)
    
    import faulthandler
    fault_out = open(os.path.join(THONNY_USER_DIR, "backend_faults.log"), mode="w")
    faulthandler.enable(fault_out)    
    
    # Disable blurry scaling in Windows
    if os.name == "nt":
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()    

    from thonny.backend import VM  # @UnresolvedImport
    VM().mainloop()
    
