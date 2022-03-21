from thonny import get_workbench
from thonny.languages import tr
from thonny.plugins.micropython import (
    SshMicroPythonConfigPage,
    SshMicroPythonProxy,
    add_micropython_backend,
)


class EV3MicroPythonProxy(SshMicroPythonProxy):
    def _get_extra_launcher_args(self):
        return {"interpreter_launcher": ["brickrun", "-r", "--"]}


class EV3MicroPythonConfigPage(SshMicroPythonConfigPage):
    pass


def _load_plugin():
    add_micropython_backend(
        "EV3MicroPython",
        EV3MicroPythonProxy,
        "MicroPython (EV3)",
        EV3MicroPythonConfigPage,
        sort_key="23",
    )
    get_workbench().set_default("EV3MicroPython.executable", "pybricks-micropython")
    get_workbench().set_default("EV3MicroPython.cwd", None)
    get_workbench().set_default("EV3MicroPython.host", "")
    get_workbench().set_default("EV3MicroPython.user", "robot")
    get_workbench().set_default("EV3MicroPython.auth_method", "password")
