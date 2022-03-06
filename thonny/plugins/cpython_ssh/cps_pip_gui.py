from thonny import get_runner
from thonny.plugins.cpython_frontend.cp_pip_gui import CPythonPipDialog
from thonny.plugins.cpython_ssh import SshCPythonProxy


class SshCPythonPipDialog(CPythonPipDialog):
    def _installer_runs_locally(self):
        return False

    def _get_interpreter_description(self):

        proxy = get_runner().get_backend_proxy()
        assert isinstance(proxy, SshCPythonProxy)
        return f"{proxy.get_target_executable()} @ {proxy.get_host()}"
