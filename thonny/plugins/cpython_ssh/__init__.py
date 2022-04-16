from thonny import get_workbench
from thonny.languages import tr
from thonny.plugins.cpython_ssh.cps_front import SshCPythonProxy, SshProxyConfigPage


def load_plugin():
    get_workbench().set_default("SshCPython.host", "")
    get_workbench().set_default("SshCPython.user", "")
    get_workbench().set_default("SshCPython.auth_method", "password")
    get_workbench().set_default("SshCPython.executable", "python3")
    get_workbench().set_default("SshCPython.cwd", "~")
    get_workbench().set_default("SshCPython.last_executables", [])
    get_workbench().set_default("SshCPython.make_uploaded_shebang_scripts_executable", True)
    get_workbench().add_backend(
        "SshCPython",
        SshCPythonProxy,
        tr("Remote Python 3 (SSH)"),
        SshProxyConfigPage,
        sort_key="15",
    )
