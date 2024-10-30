import subprocess
from typing import List

from thonny import get_workbench
from thonny.lsp_proxy import LanguageServerProxy
from thonny.running import create_frontend_python_process


class PyrightProxy(LanguageServerProxy):

    def _start_server(self) -> None:
        self._proc = create_frontend_python_process(
            ["-m", "basedpyright-langserver", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


def load_plugin():
    get_workbench().add_language_server_proxy("Pyright", PyrightProxy)
