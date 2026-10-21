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


class TyProxy(LanguageServerProxy):

    def get_settings(self) -> Dict:
        proxy = get_runner().get_backend_proxy()
        if proxy is None:
            return {}

        result = {
            "python": {},
            "ty": {"diagnosticMode": "openFilesOnly", "environment": {}},
        }

        python_path = self._get_python_path_for_server()
        if python_path is not None:
            result["ty"]["environment"]["python"] = python_path

        user_stubs_path = proxy.get_user_stubs_location()
        if self._folder_may_contain_stubs_beyond_typeshed(user_stubs_path):
            result["ty"]["environment"]["extra-paths"] = [user_stubs_path]
        if os.path.isdir(os.path.join(user_stubs_path, "stdlib")):
            result["ty"]["environment"]["typeshed"] = [user_stubs_path]

        # TODO: find out the root
        #result["ty"]["environment"]["root"] = [user_stubs_path]

        logger.info("Using following ty configuration: %r", result)
        return result


    def _create_server_process(self) -> subprocess.Popen[bytes]:
        ty_path = shutil.which("ty")
        logger.info("Ty path: %r", ty_path)

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
            logger.debug("Ty env: %s=%r", key, env.get(key))

        return subprocess.Popen(
            [ty_path, "server"],
            executable=ty_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags,
            startupinfo=startupinfo,
            text=False,
            env=env,
        )

    def get_supported_language_ids(self) -> typing.Set[str]:
        return {"python"}


def _load_plugin():
    get_workbench().add_language_server_proxy_class(TyProxy)
