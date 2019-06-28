from thonny.running import SubprocessProxy
from thonny.common import CommandToBackend
from typing import Optional
import logging
from thonny.plugins.micropython import MicroPythonConfigPage
import sys
from thonny import running


class NewMicroPythonProxy(SubprocessProxy):
    def __init__(self, clean):
        super().__init__(clean, running.get_frontend_python())

    def _get_launcher_path(self):
        import thonny.plugins.micropython.backend

        return thonny.plugins.micropython.backend.__file__

    def _clear_environment(self):
        self._close_backend()
        self._start_background_process()


class NewGenericConfPage(MicroPythonConfigPage):
    pass
