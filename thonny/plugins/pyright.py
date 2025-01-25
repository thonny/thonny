import os.path
import shutil
import subprocess
import sys
import typing
from logging import getLogger
from typing import Dict

from thonny import get_runner, get_workbench
from thonny.common import UserError
from thonny.lsp_proxy import LanguageServerProxy
from thonny.misc_utils import get_project_venv_interpreters

logger = getLogger(__name__)


class PyrightProxy(LanguageServerProxy):

    def get_settings(self) -> Dict:
        proxy = get_runner().get_backend_proxy()
        if proxy is None:
            return {}

        result = {
            "python": {},
            "basedpyright": {
                "analysis": {
                    "diagnosticMode": "openFilesOnly",
                    "diagnosticSeverityOverrides": {},
                    "logLevel": "Information",  # "Error", "Warning", "Information", "Trace"
                }
            },
        }

        project_path = get_workbench().get_local_project_path()
        logger.info("Detected project path: %s", project_path)
        if project_path is not None:
            base_path = project_path
        else:
            base_path = get_workbench().get_local_cwd()

        typings_path = os.path.join(base_path, "typings")

        if (
            proxy.interpreter_is_cpython_compatible()
            and proxy.has_local_interpreter()
            and proxy.get_target_executable()
        ):
            result["python"]["pythonPath"] = proxy.get_target_executable()
        elif project_path is not None:
            # may have a dev-venv in project directory
            venv_interpreters = get_project_venv_interpreters(project_path)
            if venv_interpreters:
                result["python"]["pythonPath"] = venv_interpreters[0]

        if not proxy.interpreter_is_cpython_compatible() or not proxy.has_local_interpreter():
            # MicroPython stdlib and frozen modules have only stubs, so the modules won't have source
            result["basedpyright"]["analysis"]["diagnosticSeverityOverrides"][
                "reportMissingModuleSource"
            ] = "none"

        if proxy.get_typeshed_path():
            result["basedpyright"]["analysis"]["typeshedPaths"] = [proxy.get_typeshed_path()]

        return result

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

        env = {
            key: os.environ[key]
            for key in os.environ
            if not key.startswith("PYTHON") and key != "VIRTUAL_ENV"
        }
        for key in env:
            logger.info("Pyright env: %s=%r", key, env.get(key))

        return subprocess.Popen(
            [node_path, langserv_js, "--stdio"],
            executable=node_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags,
            startupinfo=startupinfo,
            universal_newlines=False,
            env=env,
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

    def get_supported_language_ids(self) -> typing.Set[str]:
        return {"python"}


def load_plugin():
    get_workbench().add_language_server_proxy_class(PyrightProxy)
