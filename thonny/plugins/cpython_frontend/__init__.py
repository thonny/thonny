from thonny import get_workbench
from thonny.languages import tr
from thonny.plugins.cpython_frontend.cp_front import (
    LocalCPythonConfigurationPage,
    LocalCPythonProxy,
    get_default_cpython_executable_for_backend,
)


def load_plugin():
    wb = get_workbench()
    wb.set_default("run.backend_name", "LocalCPython")
    wb.set_default("LocalCPython.last_executables", [])
    wb.set_default("LocalCPython.executable", get_default_cpython_executable_for_backend())

    if wb.get_option("run.backend_name") in ["PrivateVenv", "SameAsFrontend", "CustomCPython"]:
        # Removed in Thonny 4.0
        wb.set_option("run.backend_name", "LocalCPython")
        wb.set_option("LocalCPython.executable", get_default_cpython_executable_for_backend())

    wb.add_backend(
        "LocalCPython",
        LocalCPythonProxy,
        tr("Local Python 3"),
        LocalCPythonConfigurationPage,
        "02",
    )
