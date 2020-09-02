"""Intermediate process for communicating with the remote Python via SSH"""
import os.path
import sys
import threading
from threading import Thread

import thonny
from thonny.backend import (
    SshMixin,
    BaseBackend,
    interrupt_local_process,
    RemoteProcess,
    ensure_posix_directory,
)
from thonny.common import (
    serialize_message,
    ImmediateCommand,
    EOFCommand,
    InputSubmission,
    CommandToBackend,
    MessageFromBackend,
)


class SshCPythonBackend(BaseBackend, SshMixin):
    def __init__(self, host, user, password, interpreter, cwd):
        SshMixin.__init__(self, host, user, password, interpreter, cwd)
        self._upload_main_backend()
        self._proc = self._start_main_backend()

        self._response_lock = threading.Lock()
        Thread(target=self._forward_main_responses, daemon=True).start()
        BaseBackend.__init__(self)

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        self._forward_incoming_message(msg)

    def _handle_user_input(self, msg: InputSubmission) -> None:
        self._forward_incoming_message(msg)

    def _handle_normal_command(self, cmd: CommandToBackend) -> None:
        handler = getattr(self, "_cmd_" + cmd.name, None)
        if handler is not None:
            # SFTP methods defined in SshMixin
            try:
                response = handler(cmd)
            except Exception as e:
                response = {"error": str(e)}  # TODO:

            self.send_message(self._prepare_command_response(response, cmd))
        else:
            # other methods running in the remote process
            self._forward_incoming_message(cmd)

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        SshMixin._handle_immediate_command(self, cmd)
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
        launch_dir = self._get_remote_program_directory()
        if self._get_stat_mode_for_upload(launch_dir) and not launch_dir.endswith("-dev"):
            # don't overwrite unless in dev mode
            return

        ensure_posix_directory(
            launch_dir + "/thonny/plugins/cpython",
            self._get_stat_mode_for_upload,
            self._mkdir_for_upload,
        )

        import thonny.ast_utils
        import thonny.backend
        import thonny.common
        import thonny.plugins.cpython.cpython_backend

        local_context = os.path.dirname(os.path.dirname(thonny.__file__))
        for local_path in [
            thonny.__file__,
            thonny.common.__file__,
            thonny.ast_utils.__file__,
            thonny.backend.__file__,
            thonny.plugins.cpython.cpython_backend.__file__,
            thonny.plugins.cpython.__file__.replace("__init__", "__main__"),
        ]:
            local_suffix = local_path[len(local_context) :]
            remote_path = launch_dir + local_suffix.replace("\\", "/")
            self._perform_sftp_operation_with_retry(lambda sftp: sftp.put(local_path, remote_path))

        def create_empty_cpython_init(sftp):
            with sftp.open(thonny.plugins.cpython.__file__, "w") as fp:
                fp.close(self._perform_sftp_operation_with_retry(create_empty_cpython_init))
