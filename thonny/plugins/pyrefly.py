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


class PyreflyProxy(LanguageServerProxy):

    def get_settings(self) -> Dict:
        proxy = get_runner().get_backend_proxy()
        if proxy is None:
            return {}

        # https://pyrefly.org/en/docs/IDE/#customization
        result = {
            "pythonPath" : "...",
            "python": {"defaultInterpreterPath" : "..."},
            "pyrefly": {"typeCheckingMode": "default",
                        "diagnosticMode" : "openFilesOnly",
                        "trace" : {"server" : "verbose"}},
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
            result["pyrefly"]["analysis"]["diagnosticSeverityOverrides"][
                "reportMissingModuleSource"
            ] = "none"

        user_stubs_path = proxy.get_user_stubs_location()
        # do not blindly set stubPath to a folder not (directly) containing stubs,
        # as this would unnecessarily hide the typings folder from Pyrefly
        if self._folder_may_contain_stubs_beyond_typeshed(user_stubs_path):
            result["pyrefly"]["analysis"]["stubPath"] = user_stubs_path
        if os.path.isdir(os.path.join(user_stubs_path, "stdlib")):
            result["pyrefly"]["analysis"]["typeshedPaths"] = [user_stubs_path]

        logger.info("Using following pyrefly configuration: %r", result)
        return result

    def _create_server_process(self) -> subprocess.Popen[bytes]:
        pyrefly_path = shutil.which("pyrefly")
        logger.info("Pyrefly path: %r", pyrefly_path)

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
            logger.debug("Pyrefly env: %s=%r", key, env.get(key))

        return subprocess.Popen(
            [pyrefly_path, "lsp"],
            executable=pyrefly_path,
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
    get_workbench().add_language_server_proxy_class(PyreflyProxy)
