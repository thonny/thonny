import platform

from thonny import get_workbench
from thonny.languages import tr
from thonny.plugins.micropython.mp_front import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
    GenericBareMetalMicroPythonConfigPage,
    GenericBareMetalMicroPythonProxy,
    LocalMicroPythonConfigPage,
    LocalMicroPythonProxy,
    MicroPythonProxy,
    SshMicroPythonConfigPage,
    SshMicroPythonProxy,
    add_micropython_backend,
    list_serial_ports,
)


def load_plugin():
    add_micropython_backend(
        "GenericMicroPython",
        GenericBareMetalMicroPythonProxy,
        tr("MicroPython (generic)"),
        GenericBareMetalMicroPythonConfigPage,
        sort_key="49",
    )

    get_workbench().set_default("serial.last_backend_per_vid_pid", {})

    if platform.system() in ("Linux", "Darwin"):
        add_micropython_backend(
            "LocalMicroPython",
            LocalMicroPythonProxy,
            tr("MicroPython (local)"),
            LocalMicroPythonConfigPage,
            bare_metal=False,
            local_rtc=False,
            sort_key="21",
        )
        get_workbench().set_default("LocalMicroPython.executable", "micropython")

    add_micropython_backend(
        "SshMicroPython",
        SshMicroPythonProxy,
        tr("MicroPython (SSH)"),
        SshMicroPythonConfigPage,
        bare_metal=False,
        local_rtc=False,
        sort_key="22",
    )
    get_workbench().set_default("SshMicroPython.executable", "micropython")
    get_workbench().set_default("SshMicroPython.cwd", None)
    get_workbench().set_default("SshMicroPython.host", "")
    get_workbench().set_default("SshMicroPython.user", "")
    get_workbench().set_default("SshMicroPython.auth_method", "password")
    get_workbench().set_default("SshMicroPython.make_uploaded_shebang_scripts_executable", True)

    get_workbench().set_default("esptool.show_advanced_options", False)
