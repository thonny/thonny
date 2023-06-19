import os.path
import shutil
from tkinter import messagebox
from typing import Any, Dict, Optional

from thonny import get_runner, get_shell, get_workbench
from thonny.common import ImmediateCommand, ToplevelCommand
from thonny.plugins.backend_config_page import BaseSshProxyConfigPage, get_ssh_password
from thonny.running import SubprocessProxy


class SshCPythonProxy(SubprocessProxy):
    def __init__(self, clean):
        self._host = get_workbench().get_option("SshCPython.host")
        self._user = get_workbench().get_option("SshCPython.user")
        self._target_executable = get_workbench().get_option("SshCPython.executable")

        super().__init__(clean)
        self._send_msg(ToplevelCommand("get_environment_info"))

    def get_target_executable(self) -> Optional[str]:
        return self._target_executable

    def get_host(self) -> str:
        return self._host

    def can_run_in_terminal(self) -> bool:
        return False

    def can_debug(self) -> bool:
        return True

    def _get_launcher_with_args(self):
        launcher_file = os.path.join(os.path.dirname(__file__), "cps_back.py")
        return [
            launcher_file,
            repr(
                {
                    "host": self._host,
                    "user": self._user,
                    "interpreter": self._target_executable,
                    "cwd": self._get_initial_cwd(),
                    "main_backend_options": {
                        "run.warn_module_shadowing": get_workbench().get_option(
                            "run.warn_module_shadowing"
                        )
                    },
                }
            ),
        ]

    def _send_initial_input(self) -> None:
        assert self._proc is not None
        self._proc.stdin.write((get_ssh_password("SshCPython") or "") + "\n")
        self._proc.stdin.flush()

    def _connect(self):
        pass

    def _get_initial_cwd(self):
        return get_workbench().get_option("SshCPython.cwd")

    def _publish_cwd(self, cwd):
        get_workbench().set_option("SshCPython.cwd", cwd)

    def interrupt(self):
        # Don't interrupt local process, but direct it to device
        self._send_msg(ImmediateCommand("interrupt"))

    def fetch_next_message(self):
        msg = super().fetch_next_message()
        if msg and "welcome_text" in msg:
            assert hasattr(self, "_reported_executable")
            msg["welcome_text"] += " (" + self._reported_executable + " on " + self._host + ")"
        return msg

    def supports_remote_files(self):
        return self._proc is not None

    def uses_local_filesystem(self):
        return False

    def ready_for_remote_file_operations(self):
        return self._proc is not None and get_runner().is_waiting_toplevel_command()

    def supports_remote_directories(self):
        return self._cwd is not None and self._cwd != ""

    def supports_trash(self):
        return False

    def is_connected(self):
        return self._proc is not None

    def _show_error(self, text):
        get_shell().print_error("\n" + text + "\n")

    def disconnect(self):
        self.destroy()

    def get_node_label(self):
        return self._host

    def get_exe_dirs(self):
        return []

    def destroy(self, for_restart: bool = False):
        try:
            self.send_command(ImmediateCommand("kill"))
        except BrokenPipeError:
            pass
        except OSError:
            pass
        super().destroy()

    def can_run_remote_files(self):
        return True

    def can_run_local_files(self):
        return False

    def get_full_label(self):
        return f"{self._reported_executable or self.get_target_executable()} @ {self.get_host()}"

    def get_current_switcher_configuration(self) -> Dict[str, Any]:
        return {
            "run.backend_name": self.backend_name,
            f"{self.backend_name}.executable": get_workbench().get_option(
                f"{self.backend_name}.executable"
            ),
            f"{self.backend_name}.host": get_workbench().get_option(f"{self.backend_name}.host"),
            f"{self.backend_name}.user": get_workbench().get_option(f"{self.backend_name}.user"),
        }

    @classmethod
    def get_switcher_configuration_label(cls, conf: Dict[str, Any]) -> str:
        user = conf[f"{cls.backend_name}.user"]
        host = conf[f"{cls.backend_name}.host"]
        executable = conf[f"{cls.backend_name}.executable"]
        return f"{cls.backend_description}  •  {user} @ {host} : {executable}"

    @classmethod
    def get_switcher_entries(cls):
        confs = sorted(cls.get_last_configurations(), key=cls.get_switcher_configuration_label)
        return [(conf, cls.get_switcher_configuration_label(conf)) for conf in confs]

    def get_pip_gui_class(self):
        from thonny.plugins.cpython_ssh.cps_pip_gui import SshCPythonPipDialog

        return SshCPythonPipDialog

    def has_custom_system_shell(self):
        return True

    def open_custom_system_shell(self):
        if not shutil.which("ssh"):
            messagebox.showerror(
                "Command not found", "Command 'ssh' not found", master=get_workbench()
            )
            return

        from thonny import terminal

        userhost = "%s@%s" % (self._user, self._host)
        terminal.run_in_terminal(
            ["ssh", userhost], cwd=get_workbench().get_local_cwd(), keep_open=False, title=userhost
        )

    def has_local_interpreter(self):
        return False

    @classmethod
    def is_valid_configuration(cls, conf: Dict[str, Any]) -> bool:
        return True


class SshProxyConfigPage(BaseSshProxyConfigPage):
    pass
