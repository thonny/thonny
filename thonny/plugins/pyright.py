import os.path
import shutil
import subprocess
import sys
from logging import getLogger

from thonny import get_workbench
from thonny.common import UserError
from thonny.lsp_proxy import LanguageServerProxy

logger = getLogger(__name__)


class PyrightProxy(LanguageServerProxy):

    def _create_server_process(self) -> subprocess.Popen[bytes]:
        node_path = self._get_node_path()
        basedpyright_dir = os.path.join(
            os.path.dirname(__file__), "..", "vendored_libs", "basedpyright"
        )
        langserv_js = os.path.join(basedpyright_dir, "langserver.index.js")
        logger.info("Node path: %r", node_path)
        logger.info("Pyright launcher: %r", langserv_js)

        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        else:
            startupinfo = None
            creationflags = 0

        return subprocess.Popen(
            [node_path, langserv_js, "--stdio"],
            executable=node_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags,
            startupinfo=startupinfo,
            universal_newlines=False,
        )

    def _get_node_path(self) -> str:
        bin_dir = os.path.dirname(sys.executable)
        if os.name == "nt":
            exe_name = "node.exe"
        else:
            exe_name = "node"

        preferred_node_path = os.path.join(bin_dir, exe_name)
        if os.path.isfile(preferred_node_path):
            return preferred_node_path

        node_in_path = shutil.which(exe_name)
        if node_in_path is None:
            raise UserError(
                f"Can't find {exe_name}. In order to make code completion and analysis work, "
                f"{exe_name} needs to be copied to {bin_dir} or Node.js needs to be installed globally"
            )

        return node_in_path


def load_plugin():
    get_workbench().add_language_server_proxy("Pyright", PyrightProxy)
