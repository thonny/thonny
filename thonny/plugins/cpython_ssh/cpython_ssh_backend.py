"""Intermediate process for communicating with the remote Python via SSH"""
import os.path
import sys
import threading
from threading import Thread

import thonny
from thonny.backend import (
    SshBackend,
    BaseBackend,
    interrupt_local_process,
    RemoteProcess,
    ensure_posix_directory,
)
from thonny.common import (
    parse_message,
    serialize_message,
    InlineCommand,
    ImmediateCommand,
    EOFCommand,
    InputSubmission,
    CommandToBackend,
    MessageFromBackend,
)


class CPythonSshBackend(SshBackend):
    def __init__(self, host, user, password, interpreter, cwd):
        self._response_lock = threading.Lock()
        BaseBackend.__init__(self)
        SshBackend.__init__(self, host, user, password, interpreter, cwd)
        self._proc = self._start_main_backend()
        Thread(target=self._forward_main_responses, daemon=True).start()
        self._upload_main_backend()
        print("doneupback")

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        self._forward_incoming_message(msg)

    def _handle_user_input(self, msg: InputSubmission) -> None:
        self._forward_incoming_message(msg)

    def _handle_normal_command(self, cmd: CommandToBackend) -> None:
        handler = getattr(self, "_cmd_" + cmd.name, None)
        if handler is not None:
            # SFTP methods defined in SshBackend
            try:
                response = handler(cmd)
            except Exception as e:
                response = {"error": str(e)}  # TODO:

            self.send_message(self._prepare_command_response(response, cmd))
        else:
            # other methods running in the remote process
            self._forward_incoming_message(cmd)

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        SshBackend._handle_immediate_command(self, cmd)
        # It is possible that there is a command being executed both in the local and remote process,
        # interrupt them both
        with self._interrupt_lock:
            interrupt_local_process()
            self._proc.stdin.write("\x03")

    def send_message(self, msg: MessageFromBackend) -> None:
        with self._response_lock:
            super().send_message(msg)

    def _forward_incoming_message(self, msg):
        self._proc.stdin.write(serialize_message(msg) + "\n")

    def _forward_main_responses(self):
        while self._should_keep_going():
            line = self._proc.stdout.readline()
            if not line:
                break
            with self._response_lock:
                sys.stdout.write(line)
                sys.stdout.flush()

    def _should_keep_going(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def _start_main_backend(self) -> RemoteProcess:
        env = {"THONNY_USER_DIR": "~/.config/Thonny", "THONNY_FRONTEND_SYS_PATH": "[]"}
        return self._create_remote_process(
            [self._remote_interpreter, "-m", "thonny.plugins.cpython", self._cwd],
            cwd=self._get_remote_program_directory(),
            env=env,
        )

    def _get_remote_program_directory(self):
        return "/tmp/thonny-backend-" + thonny.get_version()

    def _upload_main_backend(self):
        sftp = self._get_sftp(fresh=True)

        launch_dir = self._get_remote_program_directory()
        try:
            sftp.stat(launch_dir)
        except IOError:
            pass
        else:
            # dir is present
            if not launch_dir.endswith("-dev"):
                # don't overwrite unless in dev mode
                return

        ensure_posix_directory(
            launch_dir + "/thonny/plugins/cpython", self._get_stat_mode_for_upload, sftp.mkdir
        )

        import thonny.ast_utils
        import thonny.backend
        import thonny.common
        import thonny.plugins.cpython.backend

        local_context = os.path.dirname(os.path.dirname(thonny.__file__))
        for local_path in [
            thonny.__file__,
            thonny.common.__file__,
            thonny.ast_utils.__file__,
            thonny.backend.__file__,
            thonny.plugins.cpython.backend.__file__,
            thonny.plugins.cpython.__file__.replace("__init__", "__main__"),
        ]:
            local_suffix = local_path[len(local_context) :]
            remote_path = launch_dir + local_suffix.replace("\\", "/")
            sftp.put(local_path, remote_path)

        sftp.close()
