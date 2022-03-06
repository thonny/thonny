import shutil
from tkinter import messagebox
from typing import Optional

from thonny import get_runner, get_shell, get_workbench
from thonny.common import ImmediateCommand, ToplevelCommand
from thonny.languages import tr
from thonny.plugins.backend_config_page import BaseSshProxyConfigPage, get_ssh_password
from thonny.running import SubprocessProxy


class SshCPythonProxy(SubprocessProxy):
    def __init__(self, clean):
        self._host = get_workbench().get_option("ssh.host")
        self._user = get_workbench().get_option("ssh.user")
        self._target_executable = get_workbench().get_option("ssh.executable")

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
        return [
            "-m",
            "thonny.plugins.cpython_ssh.cps_back",
            repr(
                {
                    "host": self._host,
                    "user": self._user,
                    "password": get_ssh_password("ssh"),
                    "interpreter": self._target_executable,
                    "cwd": self._get_initial_cwd(),
                }
            ),
        ]

    def _connect(self):
        pass

    def _get_initial_cwd(self):
        return get_workbench().get_option("ssh.cwd")

    def _publish_cwd(self, cwd):
        get_workbench().set_option("ssh.cwd", cwd)

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

    @classmethod
    def should_show_in_switcher(cls):
        # Show when the executable, user and host are configured
        return (
            get_workbench().get_option("ssh.host")
            and get_workbench().get_option("ssh.user")
            and get_workbench().get_option("ssh.executable")
        )

    @classmethod
    def get_switcher_entries(cls):
        if cls.should_show_in_switcher():
            return [(cls.get_current_switcher_configuration(), cls.backend_description)]
        else:
            return []

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


class SshProxyConfigPage(BaseSshProxyConfigPage):
    backend_name = None  # Will be overwritten on Workbench.add_backend

    def __init__(self, master):
        super().__init__(master, "ssh")
