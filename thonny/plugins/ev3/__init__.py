"""
/usr/bin/pybricks-repl content:
#!/bin/sh
brickrun -r -- pybricks-micropython -i -c 'from core import *'

using pybricks-micropython instead

"""

from thonny import get_workbench
from thonny.languages import tr
from thonny.plugins.micropython import (
    SshMicroPythonConfigPage,
    SshMicroPythonProxy,
    add_micropython_backend,
)


class EV3MicroPythonProxy(SshMicroPythonProxy):
    def _get_launcher_with_args(self):
        import thonny.plugins.ev3.ev3_back

        args = {
            "cwd": get_workbench().get_option(f"{self.backend_name}.cwd") or "",
            "interpreter": self._target_executable,
            "host": self._host,
            "user": self._user,
        }

        args.update(self._get_time_args())
        args.update(self._get_extra_launcher_args())

        cmd = [
            thonny.plugins.ev3.ev3_back.__file__,
            repr(args),
        ]
        return cmd

    def _get_extra_launcher_args(self):
        return {"interpreter_launcher": ["brickrun", "-r", "--"]}


class EV3MicroPythonConfigPage(SshMicroPythonConfigPage):
    pass


def load_plugin():
    add_micropython_backend(
        "EV3MicroPython",
        EV3MicroPythonProxy,
        "MicroPython (EV3)",
        EV3MicroPythonConfigPage,
        bare_metal=False,
        sort_key="23",
    )
    get_workbench().set_default("EV3MicroPython.executable", "pybricks-micropython")
    get_workbench().set_default("EV3MicroPython.make_uploaded_shebang_scripts_executable", True)
    get_workbench().set_default("EV3MicroPython.cwd", None)
    get_workbench().set_default("EV3MicroPython.host", "")
    get_workbench().set_default("EV3MicroPython.user", "robot")
    get_workbench().set_default("EV3MicroPython.auth_method", "password")
