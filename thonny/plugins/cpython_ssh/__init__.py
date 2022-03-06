from thonny import get_workbench
from thonny.languages import tr
from thonny.plugins.cpython_ssh.cps_front import SshCPythonProxy, SshProxyConfigPage


def load_plugin():
    get_workbench().set_default("ssh.host", "")
    get_workbench().set_default("ssh.user", "")
    get_workbench().set_default("ssh.auth_method", "password")
    get_workbench().set_default("ssh.executable", "python3")
    get_workbench().set_default("ssh.cwd", "~")
    get_workbench().add_backend(
        "SSHProxy", SshCPythonProxy, tr("Remote Python 3 (SSH)"), SshProxyConfigPage, sort_key="15"
    )
