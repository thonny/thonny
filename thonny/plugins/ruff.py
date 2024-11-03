import subprocess
from typing import List

from thonny import get_workbench
from thonny.lsp_proxy import LanguageServerProxy
from thonny.running import create_frontend_python_process


class RuffProxy(LanguageServerProxy):

    def _create_server_process(self) -> subprocess.Popen[bytes]:
        return create_frontend_python_process(
            ["-m", "ruff", "server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=False,
        )


def load_plugin():
    get_workbench().add_language_server_proxy("Ruff", RuffProxy)
