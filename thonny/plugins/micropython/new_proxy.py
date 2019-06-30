from thonny.running import SubprocessProxy
from thonny.common import CommandToBackend, InterruptCommand
from typing import Optional
import logging
from thonny.plugins.micropython import MicroPythonConfigPage
import sys
from thonny import running, get_runner


class NewMicroPythonProxy(SubprocessProxy):
    def __init__(self, clean):
        super().__init__(clean, running.get_frontend_python())

    def _get_launcher_path(self):
        import thonny.plugins.micropython.backend

        return thonny.plugins.micropython.backend.__file__

    def interrupt(self):
        self._send_msg(InterruptCommand())
        """
        if self._proc is not None and self._proc.poll() is None:
            if running_on_windows():
                try:
                    os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # @UndefinedVariable
                except Exception:
                    logging.exception("Could not interrupt backend process")
            else:
                self._proc.send_signal(signal.SIGINT)
        """

    def _clear_environment(self):
        "TODO:"

    def has_own_filesystem(self):
        return self._proc is not None

    def uses_local_filesystem(self):
        return False

    def can_do_file_operations(self):
        return self._proc is not None and get_runner().is_waiting_toplevel_command()

    def is_connected(self):
        return self._proc is not None

    def is_functional(self):
        return self.is_connected()


class NewGenericConfPage(MicroPythonConfigPage):
    pass
