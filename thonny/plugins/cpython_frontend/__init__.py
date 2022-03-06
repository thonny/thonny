from thonny import get_workbench
from thonny.languages import tr
from thonny.plugins.cpython_frontend.cp_front import (
    CustomCPythonConfigurationPage,
    CustomCPythonProxy,
    LocalCPythonProxy,
    PrivateVenvConfigurationPage,
    PrivateVenvCPythonProxy,
    SameAsFrontEndConfigurationPage,
    SameAsFrontendCPythonProxy,
)


def load_plugin():
    wb = get_workbench()
    wb.set_default("run.backend_name", "SameAsFrontend")
    wb.set_default("CustomInterpreter.used_paths", [])
    wb.set_default("CustomInterpreter.path", "")

    wb.add_backend(
        "SameAsFrontend",
        SameAsFrontendCPythonProxy,
        tr("The same interpreter which runs Thonny (default)"),
        SameAsFrontEndConfigurationPage,
        "01",
    )

    wb.add_backend(
        "CustomCPython",
        CustomCPythonProxy,
        tr("Alternative Python 3 interpreter or virtual environment"),
        CustomCPythonConfigurationPage,
        "02",
    )

    wb.add_backend(
        "PrivateVenv",
        PrivateVenvCPythonProxy,
        tr("A special virtual environment (deprecated)"),
        PrivateVenvConfigurationPage,
        "zz",
    )
