import collections
import os
import shlex
from logging import debug
from threading import Thread
from typing import Optional

import thonny
from thonny import get_runner, get_shell, get_workbench
from thonny.common import CommandToBackend, InlineCommand, ToplevelCommand
from thonny.plugins.backend_config_page import BaseSshProxyConfigPage
from thonny.running import SubprocessProxy


class SshProxy(SubprocessProxy):
    def __init__(self, clean):
        self._host = get_workbench().get_option("ssh.host")
        self._user = get_workbench().get_option("ssh.user")
        self._password = get_workbench().get_option("ssh.password")
        self._executable = get_workbench().get_option("ssh.executable")
        self._thread_commands = collections.deque()
        self._client = None
        self._sftp = None
        self._proc = None
        self._starting = True

        self._thread_commands.append(InlineCommand("connect"))
        super().__init__(clean, self._executable)
        Thread(target=self._process_thread_commands, daemon=True).start()

    def send_command(self, cmd: CommandToBackend) -> Optional[str]:
        if cmd.name in ["write_file", "read_file", "upload", "download"]:
            self._thread_commands.append(cmd)
        else:
            super().send_command(cmd)

    def _handle_local_commands(self):
        pass

    def _get_launcher_with_args(self):
        return [self._get_remote_program_directory() + "/thonny/backend_launcher.py"]

    def _process_thread_commands(self):
        while True:
            cmd = self._thread_commands.popleft()
            if cmd.name == "quit":
                return
            elif cmd.name == "connect":
                self._connect()
            elif cmd.name == "launch":
                self._execute_backend()

    def _connect(self):
        pass

    def _launch_backend(self):
        pass

    def _start_background_process(self, clean=None, extra_args=[]):
        self._response_queue = collections.deque()
        self._thread_commands = collections.deque()

        """
        # prepare environment
        env = get_environment_for_python_subprocess(self._executable)
        # variables controlling communication with the back-end process
        env["PYTHONIOENCODING"] = "utf-8"

        # because cmd line option -u won't reach child processes
        # see https://github.com/thonny/thonny/issues/808
        env["PYTHONUNBUFFERED"] = "1"

        # Let back-end know about plug-ins
        env["THONNY_USER_DIR"] = THONNY_USER_DIR
        env["THONNY_FRONTEND_SYS_PATH"] = repr(sys.path)

        env["THONNY_LANGUAGE"] = get_workbench().get_option("general.language")
        env["FRIENDLY_TRACEBACK_LEVEL"] = str(
            get_workbench().get_option("assistance.friendly_traceback_level")
        )

        if get_workbench().in_debug_mode():
            env["THONNY_DEBUG"] = "1"
        elif "THONNY_DEBUG" in env:
            del env["THONNY_DEBUG"]

        if not os.path.exists(self._executable):
            raise UserError(
                "Interpreter (%s) not found. Please recheck corresponding option!"
                % self._executable
            )
        """

        cmd_line = [
            self._executable,
            "-u",  # unbuffered IO
            "-B",  # don't write pyo/pyc files
            # (to avoid problems when using different Python versions without write permissions)
        ] + self._get_launcher_with_args()

        cmd_line_str = " ".join(map(shlex.quote, cmd_line))

        debug("Starting the backend: %s %s", cmd_line_str, get_workbench().get_local_cwd())

        # Don't remain waiting
        self._starting = True
        self._thread_commands.append(InlineCommand("launch", cmd_line=cmd_line_str))

    def _connect_in_background(self, cmd_line_str):
        try:
            from paramiko.client import SSHClient
        except ImportError:
            self._show_error(
                "SSH connection requires an extra package -- 'paramiko'.\n"
                + "You can install it via 'Tools => Manage plug-ins' or via system package manager."
            )
            return

        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.connect(hostname=self._host, username=self._user, password=self._password)

        self._check_install_thonny_backend()

        env = {"THONNY_USER_DIR": "~/.config/Thonny", "THONNY_FRONTEND_SYS_PATH": "[]"}

        stdin, stdout, stderr = self._client.exec_command(
            cmd_line_str, bufsize=0, timeout=None, get_pty=False, environment=env
        )
        self._proc = SshPopen(stdin, stdout, stderr)

        # setup asynchronous output listeners
        Thread(target=self._listen_stdout, args=(stdout,), daemon=True).start()
        Thread(target=self._listen_stderr, args=(stderr,), daemon=True).start()

        self._send_msg(ToplevelCommand("get_environment_info"))
        self._starting = False

    def _get_initial_cwd(self):
        return "~/"

    def _get_sftp(self):
        if self._sftp is None:
            import paramiko

            # TODO: does it get closed properly after process gets killed?
            self._sftp = paramiko.SFTPClient.from_transport(self._client.get_transport())

        return self._sftp

    def is_terminated(self):
        return not self._starting and not super().process_is_alive()

    def interrupt(self):
        # Don't interrupt local process, but direct it to device
        # self._send_msg(ImmediateCommand())
        self._proc.stdin.write("\x03")

    def fetch_next_message(self):
        msg = super().fetch_next_message()
        if msg and "welcome_text" in msg:
            msg["welcome_text"] += " (" + self._executable + " on " + self._host + ")"
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

    def destroy(self):
        super().destroy()
        self._client.close()

    def _get_remote_program_directory(self):
        return "/tmp/thonny-backend-" + thonny.get_version()


class SshPopen:
    """
    Wraps Channel streams to subprocess.Popen-like structure
    """

    def __init__(self, stdin, stdout, stderr):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = None

    def poll(self):
        if self.stdout.closed:
            self.returncode = self.stdout.channel.recv_exit_status()
            return self.returncode
        else:
            return None

    def kill(self):
        pass


class SshProxyConfigPage(BaseSshProxyConfigPage):
    backend_name = None  # Will be overwritten on Workbench.add_backend

    def __init__(self, master):
        super().__init__(master, "ssh")


def load_plugin():
    get_workbench().set_default("ssh.host", "raspberrypi.local")
    get_workbench().set_default("ssh.user", "pi")
    get_workbench().set_default("ssh.password", "raspberry")
    get_workbench().add_backend("SSHProxy", SshProxy, "SSH proxy", SshProxyConfigPage)
