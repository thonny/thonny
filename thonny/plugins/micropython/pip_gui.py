import subprocess

from thonny import running
from thonny.plugins.pip_gui import PipDialog


class MicroPythonPipDialog(PipDialog):
    def _create_pip_process(self, args, stderr=subprocess.STDOUT):
        assert len(args) == 2
        assert args[0] == "install"

        return self._create_python_process(
            ["-m", "thonny.plugins.micropython.micropip"] + args, stderr=stderr
        )

    def _create_python_process(self, args, stderr):
        proc = running.create_frontend_python_process(args, stderr=stderr)
        return proc, proc.cmd
