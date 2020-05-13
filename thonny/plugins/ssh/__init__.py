import logging
import io
import os
import platform
import queue
import re
import subprocess
import sys
import textwrap
import threading
import time
import traceback
from queue import Queue
from textwrap import dedent
from time import sleep
from tkinter import ttk, messagebox
from thonny.ui_utils import askopenfilename, create_url_label
from typing import Optional

import thonny

from thonny import common, get_runner, get_shell, get_workbench, running, ui_utils
from thonny.common import (
    BackendEvent,
    InlineResponse,
    MessageFromBackend,
    ToplevelCommand,
    ToplevelResponse,
    InterruptCommand,
    EOFCommand,
    CommandToBackend,
)
from thonny.config_ui import ConfigurationPage
from thonny.misc_utils import find_volumes_by_name, TimeHelper
from thonny.plugins.backend_config_page import BackendDetailsConfigPage
from thonny.running import BackendProxy, SubprocessProxy
from thonny.ui_utils import SubprocessDialog, create_string_var, show_dialog
import collections
from threading import Thread
from logging import debug
import shlex


class SshProxy(SubprocessProxy):
    def __init__(self, clean):
        self._host = get_workbench().get_option("ssh.host")
        self._user = get_workbench().get_option("ssh.user")
        self._password = get_workbench().get_option("ssh.password")
        self._client = None
        self._proc = None
        self._starting = True

        super().__init__(clean, "/usr/bin/python3")

    def _get_launcher_with_args(self):
        return [self._get_remote_program_directory() + "/thonny/backend_launcher.py"]

    def _start_background_process(self, clean=None):
        # deque, because in one occasion I need to put messages back
        self._response_queue = collections.deque()

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
        Thread(target=self._connect_in_background, args=(cmd_line_str,), daemon=True).start()

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

        env = {
            "THONNY_USER_DIR": "~/.config/Thonny",
            "THONNY_FRONTEND_SYS_PATH": "[]",
        }

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

    def is_terminated(self):
        return not self._starting and not super().process_is_alive()

    def interrupt(self):
        # Don't interrupt local process, but direct it to device
        # self._send_msg(InterruptCommand())
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

    def _check_install_thonny_backend(self):
        import paramiko

        sftp = paramiko.SFTPClient.from_transport(self._client.get_transport())

        launch_dir = self._get_remote_program_directory()
        try:
            sftp.stat(launch_dir)
            # dir is present
            if not launch_dir.endswith("-dev"):
                # don't overwrite unless in dev mode
                return

        except IOError:
            sftp.mkdir(launch_dir)

        # copy backend_launcher next to thonny module so that thonny module will be in path
        # import thonny.backend_launcher
        # sftp.put(thonny.backend_launcher.__file__, launch_dir + "/launch.py")

        # other files go to thonny directory
        module_dir = launch_dir + "/thonny"
        try:
            sftp.stat(module_dir)
        except IOError:
            sftp.mkdir(module_dir)

        import thonny.backend_launcher
        import thonny.backend
        import thonny.common
        import thonny.ast_utils

        # create empty __init__.py
        # sftp.open(module_dir + "/__init__.py", "w").close()

        for module in [
            thonny,
            thonny.backend_launcher,
            thonny.backend,
            thonny.common,
            thonny.ast_utils,
        ]:
            local_path = module.__file__
            remote_path = module_dir + "/" + os.path.basename(local_path)
            sftp.put(local_path, remote_path)

        sftp.close()


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


class SshProxyConfigPage(BackendDetailsConfigPage):
    backend_name = None  # Will be overwritten on Workbench.add_backend

    def __init__(self, master):
        super().__init__(master)
        self._changed = False

        self._host_var = self._add_text_field("Host", "ssh.host", 1)
        self._user_var = self._add_text_field("Username", "ssh.user", 3)
        self._password_var = self._add_text_field("Password", "ssh.password", 5, show="•")

    def _add_text_field(self, label_text, variable_name, row, show=None):
        entry_label = ttk.Label(self, text=label_text)
        entry_label.grid(row=row, column=0, sticky="w")

        variable = create_string_var(get_workbench().get_option(variable_name), self._on_change)
        entry = ttk.Entry(self, textvariable=variable, show=show)
        entry.grid(row=row + 1, column=0, sticky="we")
        return variable

    def _on_change(self):
        print("detected change")
        self._changed = True

    def apply(self):
        get_workbench().set_option("ssh.host", self._host_var.get())
        get_workbench().set_option("ssh.user", self._user_var.get())
        get_workbench().set_option("ssh.password", self._password_var.get())

    def should_restart(self):
        return self._changed


def load_plugin():
    get_workbench().set_default("ssh.host", "raspberrypi.local")
    get_workbench().set_default("ssh.user", "pi")
    get_workbench().set_default("ssh.password", "raspberry")
    get_workbench().add_backend("SSHProxy", SshProxy, "SSH proxy", SshProxyConfigPage)
