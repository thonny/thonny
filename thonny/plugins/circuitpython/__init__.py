from thonny.languages import tr
from thonny.plugins.circuitpython.cirpy_front import CircuitPythonConfigPage, CircuitPythonProxy
from thonny.plugins.micropython import add_micropython_backend


def load_plugin():
    add_micropython_backend(
        "CircuitPython",
        CircuitPythonProxy,
        tr("CircuitPython (generic)"),
        CircuitPythonConfigPage,
        sort_key="50",
    )
