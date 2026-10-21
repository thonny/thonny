import os.path
import shutil
import subprocess
import sys
import typing
from logging import getLogger
from typing import Dict, Optional

from thonny import get_runner, get_workbench
from thonny.common import UserError
from thonny.lsp_proxy import LanguageServerProxy
from thonny.misc_utils import get_project_venv_interpreters
from thonny.running import create_frontend_python_process

logger = getLogger(__name__)


class BasedpyrightProxy(LanguageServerProxy):

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

        python_path = self._get_python_path_for_server()

        if python_path is not None:
            result["python"]["pythonPath"] = python_path

        if not proxy.interpreter_is_cpython_compatible() or not proxy.has_local_interpreter():
            # MicroPython stdlib and frozen modules have only stubs, so the modules won't have source
            result["basedpyright"]["analysis"]["diagnosticSeverityOverrides"][
                "reportMissingModuleSource"
            ] = "none"

        user_stubs_path = proxy.get_user_stubs_location()
        # do not blindly set stubPath to a folder not (directly) containing stubs,
        # as this would unnecessarily hide the typings folder from Basedpyright
        if self._folder_may_contain_stubs_beyond_typeshed(user_stubs_path):
            result["basedpyright"]["analysis"]["stubPath"] = user_stubs_path
        if os.path.isdir(os.path.join(user_stubs_path, "stdlib")):
            result["basedpyright"]["analysis"]["typeshedPaths"] = [user_stubs_path]

        logger.info("Using following basedpyright configuration: %r", result)
        return result

    def _create_server_process(self) -> subprocess.Popen[bytes]:
        server_path = shutil.which("basedpyright-langserver")
        if server_path is None:
            raise UserError("Can't find basedpyright-langserver")

        logger.info("basedpyright-langserver path: %r", server_path)

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
            logger.debug("Basedpyright env: %s=%r", key, env.get(key))

        return subprocess.Popen(
            [server_path, "--stdio"],
            executable=server_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags,
            startupinfo=startupinfo,
            universal_newlines=False,
            env=env,
        )

    def get_supported_language_ids(self) -> typing.Set[str]:
        return {"python"}


def load_plugin():
    get_workbench().add_language_server_proxy_class(BasedpyrightProxy)
