from thonny import launch

import runpy
try:
    runpy.run_module("thonny.customize", run_name="__main__")
except ImportError:
    pass


launch()