"""Intermediate process for communicating with the remote Python via SSH"""
import os.path
import sys
from threading import Thread

import thonny
from thonny.backend import SshBackend, BaseBackend, interrupt_local_process, RemoteProcess
from thonny.common import parse_message, serialize_message, InlineCommand, ImmediateCommand


class CPythonSshBackend(BaseBackend, SshBackend):
    def __init__(self, host, user, password, remote_interpreter):
        BaseBackend.__init__(self)
        SshBackend.__init__(self, host, user, password, remote_interpreter)
        self._upload_main_backend()
        self._proc = self._start_main_backend()
        Thread(target=self._forward_main_responses, daemon=True).start()

    def _handle_incoming_message(self, msg) -> None:
        handler = getattr(self, "_cmd_" + msg.name, None)
        if handler is not None:
            # SFTP methods defined in SshBackend
            try:
                response = handler(msg)
            except Exception as e:
                response = {"error": str(e)}  # TODO:

            self.send_message(self._prepare_response(response))
        else:
            # other methods running in the remote process
            self._proc.write(serialize_message(msg) + "\n")

    def _forward_main_responses(self):
        while self._should_keep_going():
            line = self._proc.stdout.readline()
            sys.stdout.write(line)

    def _should_keep_going(self) -> bool:
        return self._proc.alive()  # TODO:

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        SshBackend._handle_immediate_command(self, cmd)
        # It is possible that there is a command being executed both in the local and remote process,
        # interrupt them both
        with self._interrupt_lock.acquire():
            interrupt_local_process()
            self._proc.stdin.write("\x03")

    def _start_main_backend(self) -> RemoteProcess:
        env = {"THONNY_USER_DIR": "~/.config/Thonny", "THONNY_FRONTEND_SYS_PATH": "[]"}
        return self._create_remote_process(
            [
                self._remote_interpreter,
                self._get_remote_program_directory() + "/thonny/backend_launcher.py",
            ],
            cwd=self._get_remote_program_directory(),
            env=env,
        )

    def _get_remote_program_directory(self):
        return "/tmp/thonny-backend-" + thonny.get_version()

    def _upload_main_backend(self):
        sftp = self._get_sftp()

        launch_dir = self._get_remote_program_directory()
        try:
            sftp.stat(launch_dir)
            # dir is present
            if not launch_dir.endswith("-dev"):
                # don't overwrite unless in dev mode
                return
        except IOError:
            sftp.mkdir(launch_dir)

        # other files go to thonny directory
        module_dir = launch_dir + "/thonny"
        try:
            sftp.stat(module_dir)
        except IOError:
            sftp.mkdir(module_dir)

        import thonny.backend_launcher
        import thonny.ast_utils
        import thonny.backend
        import thonny.common

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
