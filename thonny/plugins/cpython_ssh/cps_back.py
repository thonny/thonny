"""Intermediate process for communicating with the remote Python via SSH"""

import ast
import os.path
import sys
import threading
from logging import getLogger
from threading import Thread
from typing import Any, Dict

# make sure thonny folder is in sys.path (relevant in dev)
thonny_container = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if thonny_container not in sys.path:
    sys.path.insert(0, thonny_container)


import thonny
from thonny.backend import (
    BaseBackend,
    RemoteProcess,
    SshMixin,
    ensure_posix_directory,
    interrupt_local_process,
)
from thonny.common import (
    PROCESS_ACK,
    CommandToBackend,
    EOFCommand,
    ImmediateCommand,
    InputSubmission,
    MessageFromBackend,
    serialize_message,
)

logger = getLogger("thonny.plugins.cpython_ssh.cps_back")


class SshCPythonBackend(BaseBackend, SshMixin):
    def __init__(self, host, user, interpreter, cwd, main_backend_options: Dict[str, Any]):
        logger.info("Starting mediator for %s @ %s", user, host)
        self._main_backend_options = main_backend_options
        password = sys.stdin.readline().strip("\r\n")
        SshMixin.__init__(self, host, user, password, interpreter, cwd)
        self._upload_main_backend()
        self._proc = self._start_main_backend()
        self._main_backend_is_fresh = True

        self._response_lock = threading.Lock()
        self._start_response_forwarder()
        BaseBackend.__init__(self)

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        self._forward_incoming_command(msg)

    def _handle_user_input(self, msg: InputSubmission) -> None:
        self._forward_incoming_command(msg)

    def _handle_normal_command(self, cmd: CommandToBackend) -> None:
        if cmd.name[0].isupper():
            if "expected_cwd" in cmd:
                self._cwd = cmd["expected_cwd"]
            self._restart_main_backend()

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
            self._forward_incoming_command(cmd)

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        SshMixin._handle_immediate_command(self, cmd)
        # It is possible that there is a command being executed both in the local and remote process,
        # interrupt them both
        with self._interrupt_lock:
            # TODO: interrupt local process only if it's going on
            # otherwise the whole backend comes down
            # interrupt_local_process()
            self._proc.stdin.write("\x03")

    def send_message(self, msg: MessageFromBackend) -> None:
        with self._response_lock:
            super().send_message(msg)

    def _forward_incoming_command(self, msg):
        msg_str = serialize_message(msg, 1024)

        for line in msg_str.splitlines(keepends=True):
            self._proc.stdin.write(line)
            self._proc.stdin.flush()

        self._proc.stdin.write("\n")

    def _start_response_forwarder(self):
        logger.info("Starting response forwarder")
        self._response_forwarder = Thread(target=self._forward_main_responses, daemon=True)
        self._response_forwarder.start()

    def _forward_main_responses(self):
        while True:
            try:
                self._check_for_connection_error()
            except ConnectionError:
                logger.info("Breaking forwarding loop because of connection error")
                break

            line = self._proc.stdout.readline()
            if self._main_backend_is_fresh and self._looks_like_echo(line):
                # In the beginning the backend may echo commands sent to it (perhaps this echo-avoiding trick
                # takes time). Don't forward those lines.
                logger.info("Skipping forwarding %r", line)
                continue

            if not line:
                logger.info("Breaking forwarding loop")
                break
            with self._response_lock:
                sys.stdout.write(line)
                sys.stdout.flush()
                self._main_backend_is_fresh = False

        logger.info("Completed _forward_main_responses")

    def _looks_like_echo(self, line):
        return line.startswith("^B")

    def _check_for_connection_error(self) -> None:
        if self._proc is None or self._proc.poll() is not None:
            raise ConnectionAbortedError()

    def _start_main_backend(self) -> RemoteProcess:
        env = {"THONNY_USER_DIR": "~/.config/Thonny", "THONNY_FRONTEND_SYS_PATH": "[]"}
        self._main_backend_is_fresh = True

        cp_launcher_file = (
            self._get_remote_program_directory()
            + "/"
            + "thonny/plugins/cpython_backend/cp_launcher.py"
        )
        args = [
            self._target_interpreter,
            cp_launcher_file,
            self._cwd,
            repr(self._main_backend_options),
        ]
        logger.info("Starting remote process: %r", args)
        return self._create_remote_process(
            args,
            cwd=self._get_remote_program_directory(),
            env=env,
        )

    def _restart_main_backend(self):
        self._proc.kill()
        self._proc = None
        self._response_forwarder.join()
        self._proc = self._start_main_backend()
        self._start_response_forwarder()

    def _get_remote_program_directory(self):
        return f"/tmp/thonny-backend-{thonny.get_version()}-{self._user}"

    def _upload_main_backend(self):
        logger.info("Uploading main backend")
        import thonny

        launch_dir = self._get_remote_program_directory()
        if self._get_stat_mode_for_upload(launch_dir) and not thonny.get_version().endswith("-dev"):
            # don't overwrite unless in dev mode
            return

        ensure_posix_directory(
            launch_dir + "/thonny/plugins/cpython_backend",
            self._get_stat_mode_for_upload,
            self._mkdir_for_upload,
        )

        import thonny.ast_utils
        import thonny.backend
        import thonny.jedi_utils
        import thonny.plugins.cpython_backend.cp_back

        # Don't want to import cp_back_launcher and cp_tracers

        local_context = os.path.dirname(os.path.dirname(thonny.__file__))
        for local_path in [
            thonny.__file__,
            thonny.common.__file__,
            thonny.ast_utils.__file__,
            thonny.jedi_utils.__file__,
            thonny.backend.__file__,
            thonny.plugins.cpython_backend.__file__,
            thonny.plugins.cpython_backend.cp_back.__file__,
            thonny.plugins.cpython_backend.cp_back.__file__.replace("cp_back.py", "cp_launcher.py"),
            thonny.plugins.cpython_backend.cp_back.__file__.replace("cp_back.py", "cp_tracers.py"),
        ]:
            local_suffix = local_path[len(local_context) :]
            remote_path = launch_dir + local_suffix.replace("\\", "/")
            logger.info("Uploading %s => %s", local_path, remote_path)
            self._perform_sftp_operation_with_retry(lambda sftp: sftp.put(local_path, remote_path))


if __name__ == "__main__":
    thonny.configure_backend_logging()
    print(PROCESS_ACK)
    args = ast.literal_eval(sys.argv[1])
    backend = SshCPythonBackend(**args)
    backend.mainloop()
