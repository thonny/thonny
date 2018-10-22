import sys
import runpy

if sys.executable.endswith("thonny.exe"):
    sys.executable = sys.executable[:-len("thonny.exe")] + "pythonw.exe"

from thonny import launch

try:
    runpy.run_module("thonny.customize", run_name="__main__")
except ImportError:
    pass


launch()
