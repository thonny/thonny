import os

from thonny import get_runner
from thonny.common import normpath_with_actual_case
from thonny.plugins.cpython_frontend import CPythonProxy
from thonny.plugins.cpython_ssh import SshCPythonProxy
from thonny.plugins.pip_gui import BackendPipDialog


class CPythonBackendPipDialog(BackendPipDialog):
    def __init__(self, master):
        super().__init__(master)
        assert isinstance(self._backend_proxy, (CPythonProxy, SshCPythonProxy))

    def _is_read_only(self):
        # readonly if not in a virtual environment
        # and user site packages is disabled
        return (
            self._use_user_install()
            and not get_runner().get_backend_proxy().get_user_site_packages()
        )

    def _get_interpreter_description(self):
        return get_runner().get_local_executable()

    def _get_target_directory(self):
        if self._use_user_install():
            usp = self._backend_proxy.get_user_site_packages()
            if isinstance(self._backend_proxy, CPythonProxy):
                os.makedirs(usp, exist_ok=True)
                return normpath_with_actual_case(usp)
            else:
                return usp
        else:
            sp = self._backend_proxy.get_site_packages()
            if sp is None:
                return None
            return normpath_with_actual_case(sp)

    def _use_user_install(self):
        return not self._targets_virtual_environment()

    def _targets_virtual_environment(self):
        return get_runner().using_venv()
