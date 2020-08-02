"""Intermediate process for communicating with the remote Python via SSH"""
import os.path
import sys
from threading import Thread

import thonny
from thonny.backend import (
    SshBackend,
    BaseBackend,
    interrupt_local_process,
    RemoteProcess,
    ensure_posix_directory,
)
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
            [self._remote_interpreter, "-m", "thonny.plugins.cpython"],
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
            pass

        ensure_posix_directory(launch_dir + "/thonny/plugins/cpython", sftp.stat, sftp.mkdir)

        import thonny.ast_utils
        import thonny.backend
        import thonny.common
        import thonny.plugins.cpython.backend

        local_context = os.path.dirname(os.path.dirname(thonny.__file__))
        for module in [
            thonny,
            thonny.common,
            thonny.ast_utils,
            thonny.backend,
            thonny.plugins.cpython.backend,
        ]:
            local_path = module.__file__
            local_suffix = module.__file__[len(local_context) :]
            remote_path = launch_dir + local_suffix.replace("\\", "/")
            sftp.put(local_path, remote_path)

        sftp.close()
