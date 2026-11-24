"""Helpers for backends that communicate with another system."""

import io
import os.path
import pathlib
import stat
import sys
from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, BinaryIO, Callable, Dict, Iterable, List, Optional, Tuple

from thonny.common import (
    INTERNAL_ERROR_STATUS_CODE,
    PROCESS_ACK,
    ImmediateCommand,
    InlineResponse,
    execute_with_frontend_sys_path,
    universal_dirname,
)

NEW_DIR_MODE = 0o755

logger = getLogger(__name__)


class UploadDownloadMixin(ABC):
    """Backend, which runs on a local process and talks to a nonlocal system,
    and therefore is able to upload/download"""

    def _cmd_download(self, cmd):
        errors = self._transfer_files_and_dirs(
            cmd.items, self._ensure_local_directory, self._download_file, cmd, pathlib.Path
        )
        return {"errors": errors}

    def _cmd_upload(self, cmd):
        def upload_file_wrapper(source_path, target_path, callback):
            self._upload_file(
                source_path, target_path, callback, cmd["make_shebang_scripts_executable"]
            )

        errors = self._transfer_files_and_dirs(
            cmd.items,
            self._ensure_remote_directory,
            upload_file_wrapper,
            cmd,
            pathlib.PurePosixPath,
        )
        return {"errors": errors}

    def _cmd_read_file(self, cmd):
        def callback(completed, total):
            self._report_progress(cmd, cmd["path"], completed, total)

        with io.BytesIO() as fp:
            self._read_file(cmd["path"], fp, callback)
            fp.seek(0)
            content_bytes = fp.read()

        return {"content_bytes": content_bytes, "path": cmd["path"]}

    def _cmd_write_file(self, cmd):
        def callback(completed, total):
            self._report_progress(cmd, cmd["path"], completed, total)

        with io.BytesIO() as fp:
            fp.write(cmd["content_bytes"])
            fp.seek(0)
            self._write_file(
                fp,
                cmd["path"],
                file_size=len(cmd["content_bytes"]),
                callback=callback,
                make_shebang_scripts_executable=cmd["make_shebang_scripts_executable"],
            )

        return InlineResponse(
            command_name="write_file", path=cmd["path"], editor_id=cmd.get("editor_id")
        )

    def _supports_directories(self) -> bool:
        return True

    def _transfer_files_and_dirs(
        self,
        items: Iterable[Dict],
        ensure_dir_fun: Callable[[str], None],
        transfer_file_fun: Callable,
        cmd,
        target_path_class,
    ) -> List[str]:
        total_cost = 0
        for item in items:
            if item["kind"] == "file":
                total_cost += item["size_bytes"] + self._get_file_fixed_cost()
            else:
                total_cost += self._get_dir_transfer_cost()

        completed_cost = 0
        errors = []

        ensured_dirs = set()

        def ensure_dir(path):
            if path in ensured_dirs:
                return
            ensure_dir_fun(path)
            ensured_dirs.add(path)

        for item in sorted(items, key=lambda x: x["source_path"]):
            self._report_progress(cmd, "Starting", completed_cost, total_cost)

            def copy_bytes_notifier(completed_bytes, total_bytes):
                completed = completed_cost + completed_bytes
                desc = str(round(completed / total_cost * 100)) + "%"

                self._report_progress(cmd, desc, completed, total_cost)

            try:
                if item["kind"] == "dir":
                    ensure_dir(item["target_path"])
                    completed_cost += self._get_dir_transfer_cost()
                else:
                    if self._supports_directories():
                        ensure_dir(self._get_parent_directory(item["target_path"]))
                    print("%s (%d bytes)" % (item["source_path"], item["size_bytes"]))
                    transfer_file_fun(item["source_path"], item["target_path"], copy_bytes_notifier)
                    completed_cost += self._get_file_fixed_cost() + item["size_bytes"]
            except OSError as e:
                logger.exception("OSError during upload")
                errors.append(
                    "Could not copy %s to %s: %s"
                    % (item["source_path"], item["target_path"], str(e))
                )

        return errors

    def _download_file(self, source_path, target_path, callback):
        with open(target_path, "bw") as target_fp:
            self._read_file(source_path, target_fp, callback)

    def _upload_file(
        self, source_path, target_path, callback, make_shebang_scripts_executable: bool
    ):
        with open(source_path, "br") as source_fp:
            self._write_file(
                source_fp,
                target_path,
                os.path.getsize(source_path),
                callback,
                make_shebang_scripts_executable,
            )

    def _get_dir_transfer_cost(self):
        # Validating and maybe creating a directory is taken to be equal to copying this number of bytes
        return 1000

    def _get_file_fixed_cost(self):
        # Creating or overwriting a file is taken to be equal to copying this number of bytes
        return 100

    def _get_parent_directory(self, path: str):
        return universal_dirname(path)

    def _ensure_local_directory(self, path: str) -> None:
        os.makedirs(path, NEW_DIR_MODE, exist_ok=True)

    def _ensure_remote_directory(self, path: str) -> None:
        # assuming remote system is Posix
        ensure_posix_directory(path, self._get_stat_mode_for_upload, self._mkdir_for_upload)

    @abstractmethod
    def _get_stat_mode_for_upload(self, path: str) -> Optional[int]:
        """returns None if path doesn't exist"""

    @abstractmethod
    def _mkdir_for_upload(self, path: str) -> None: ...

    @abstractmethod
    def _write_file(
        self,
        source_fp: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
        make_shebang_scripts_executable: bool,
    ) -> None: ...

    @abstractmethod
    def _read_file(
        self, source_path: str, target_fp: BinaryIO, callback: Callable[[int, int], None]
    ) -> None: ...

    @abstractmethod
    def _report_internal_exception(self, msg: str) -> None: ...

    @abstractmethod
    def _report_progress(
        self, cmd, description: Optional[str], value: float, maximum: float
    ) -> None: ...

    def _read_file_return_bytes(self, source_path: str) -> bytes:
        def callback(x, y):
            pass

        with io.BytesIO() as fp:
            self._read_file(source_path, fp, callback)
            fp.seek(0)
            return fp.read()


class RemoteProcess:
    """Modelled after subprocess.Popen"""

    def __init__(self, client, channel, stdin, stdout, pid):
        self._client = client
        self._channel = channel
        self.stdin = stdin
        self.stdout = stdout
        self.pid = pid
        self.returncode = None

    def poll(self):
        if self._channel.exit_status_ready():
            self.returncode = self._channel.recv_exit_status()
            return self.returncode
        else:
            return None

    def wait(self):
        self.returncode = self._channel.recv_exit_status()
        return self.returncode

    def kill(self):
        _, stdout, _ = self._client.exec_command("kill -9 %s" % self.pid)
        # wait until completion
        stdout.channel.recv_exit_status()


class SshMixin(UploadDownloadMixin):
    def __init__(self, host, port, user, password, interpreter, cwd):
        # UploadDownloadMixin.__init__(self)
        execute_with_frontend_sys_path(self._try_load_paramiko)
        import paramiko
        from paramiko.client import SSHClient

        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._target_interpreter = interpreter
        self._cwd = cwd
        self._proc = None  # type: Optional[RemoteProcess]
        self._sftp = None  # type: Optional[paramiko.SFTPClient]
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        # TODO: does it get closed properly after process gets killed?
        self._connect()

    def _try_load_paramiko(self):
        try:
            import paramiko.client

            logger.debug("Could import %s", paramiko.client)
        except ImportError:
            logger.info("Could not import paramiko")
            print(
                "\nThis back-end requires an extra package named 'paramiko'."
                " Install it from 'Tools => Manage plug-ins' or via your system package manager.",
                file=sys.stderr,
            )
            sys.exit(INTERNAL_ERROR_STATUS_CODE)

    def _connect(self):
        from paramiko import SSHException

        try:
            self._client.connect(
                hostname=self._host,
                port=int(self._port) if self._port else 22,
                username=self._user,
                password=self._password,
                passphrase=self._password,
            )
        except (SSHException, OSError) as e:
            print(
                "\nCan't connect to '%s' with user '%s': %s" % (self._host, self._user, str(e)),
                file=sys.stderr,
            )
            print("Re-check your host, authentication method, password or keys.", file=sys.stderr)
            delete_stored_ssh_password()

            sys.exit(INTERNAL_ERROR_STATUS_CODE)

    def _create_remote_process(self, cmd_items: List[str], cwd: str, env: Dict) -> RemoteProcess:
        import shlex

        # Before running the main thing:
        # * print process id (so that we can kill it later)
        #   http://redes-privadas-virtuales.blogspot.com/2013/03/getting-hold-of-remote-pid-through.html
        # * change to desired directory
        #
        # About -onlcr: https://stackoverflow.com/q/35887380/261181
        # can't trust the env-argument of the exec_command, as the server may ignore it
        env_str = " ".join([f"env {key}={shlex.quote(value)}" for key, value in env.items()])
        cmd_line_str = (
            "echo $$ ; stty -echo ; stty -onlcr ; "
            + (" cd %s  2> /dev/null ;" % shlex.quote(cwd) if cwd else "")
            + (f" exec {env_str} " + " ".join(map(shlex.quote, cmd_items)))
        )
        logger.info("Starting remote process with following cmd line:\n%s", cmd_line_str)
        stdin, stdout, _ = self._client.exec_command(cmd_line_str, bufsize=0, get_pty=True)

        # stderr gets directed to stdout because of pty
        first_line = stdout.readline()
        second_line = stdout.readline()
        pid = first_line.strip()
        ack = second_line.strip()
        if ack != PROCESS_ACK:
            print(f"Got {ack!r} instead of expected {PROCESS_ACK!r}", file=sys.stderr)
            print("Whole output:", file=sys.stderr)
            print(first_line, end="", file=sys.stderr)
            print(second_line, end="", file=sys.stderr)
            while True:
                line = stdout.readline()
                if not line:
                    break
                print(line, end="", file=sys.stderr)
        channel = stdout.channel

        return RemoteProcess(self._client, channel, stdin, stdout, pid)

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        if cmd.name == "kill":
            self._kill()
        elif cmd.name == "interrupt":
            self._interrupt()
        else:
            raise RuntimeError("Unknown immediateCommand %s" % cmd.name)

    def _kill(self):
        if self._proc is None or self._proc.poll() is not None:
            return

        self._proc.kill()

    def _interrupt(self):
        pass

    def _get_sftp(self, fresh: bool):
        if fresh and self._sftp is not None:
            self._sftp.close()
            self._sftp = None

        if self._sftp is None:
            import paramiko

            # TODO: does it get closed properly after process gets killed?
            transport = self._client.get_transport()
            assert transport is not None
            self._sftp = paramiko.SFTPClient.from_transport(transport)

        return self._sftp

    def _read_file(
        self, source_path: str, target_fp: BinaryIO, callback: Callable[[int, int], None]
    ) -> None:
        self._perform_sftp_operation_with_retry(
            lambda sftp: sftp.getfo(source_path, target_fp, callback)
        )

    def _write_file(
        self,
        source_fp: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
        make_shebang_scripts_executable: bool,
    ) -> None:
        logger.info("Writing bytes to %r", target_path)
        if make_shebang_scripts_executable:
            source_fp, has_shebang = convert_newlines_if_has_shebang(source_fp)
        else:
            has_shebang = None

        self._perform_sftp_operation_with_retry(
            lambda sftp: sftp.putfo(source_fp, target_path, callback)
        )

        logger.debug(
            "make_shebang_scripts_executable: %r, has_shebang: %r",
            make_shebang_scripts_executable,
            has_shebang,
        )
        if make_shebang_scripts_executable and has_shebang:
            self._perform_sftp_operation_with_retry(lambda sftp: sftp.chmod(target_path, 0o755))

    def _perform_sftp_operation_with_retry(self, operation) -> Any:
        try:
            return operation(self._get_sftp(fresh=False))
        except OSError:
            # It looks like SFTPClient gets stale after a while.
            # Try again with fresh SFTPClient
            return operation(self._get_sftp(fresh=True))

    def _get_stat_mode_for_upload(self, path: str) -> Optional[int]:
        try:
            return self._perform_sftp_operation_with_retry(lambda sftp: sftp.stat(path).st_mode)
        except OSError:
            return None

    def _mkdir_for_upload(self, path: str) -> None:
        self._perform_sftp_operation_with_retry(lambda sftp: sftp.mkdir(path, NEW_DIR_MODE))


def ensure_posix_directory(
    path: str, stat_mode_fun: Callable[[str], Optional[int]], mkdir_fun: Callable[[str], None]
) -> None:
    assert path.startswith("/")
    if path == "/":
        return

    for step in list(reversed(list(map(str, pathlib.PurePosixPath(path).parents)))) + [path]:
        if step != "/":
            mode = stat_mode_fun(step)
            if mode is None:
                mkdir_fun(step)
            elif not stat.S_ISDIR(mode):
                raise AssertionError("'%s' is file, not a directory" % step)


def interrupt_local_process() -> None:
    """Meant to be executed from a background thread"""
    import signal

    if hasattr(signal, "raise_signal"):
        # Python 3.8 and later
        signal.raise_signal(signal.SIGINT)
    elif sys.platform == "win32":
        # https://stackoverflow.com/a/51122690/261181
        import ctypes

        ucrtbase = ctypes.CDLL("ucrtbase")
        c_raise = ucrtbase["raise"]
        c_raise(signal.SIGINT)
    else:
        # Does not give KeyboardInterrupt in Windows
        os.kill(os.getpid(), signal.SIGINT)


def get_ssh_password_file_path():
    from thonny import get_thonny_user_dir

    return os.path.join(get_thonny_user_dir(), "ssh_password")


def delete_stored_ssh_password():
    if os.path.exists(get_ssh_password_file_path()):
        # invalidate stored password
        os.remove(get_ssh_password_file_path())


def convert_newlines_if_has_shebang(fp: BinaryIO) -> Tuple[BinaryIO, bool]:
    if fp.read(3) == b"#!/":
        fp.seek(0)
        new_fp = io.BytesIO()
        new_fp.write(fp.read().replace(b"\r\n", b"\n"))
        fp.close()
        new_fp.seek(0)
        return new_fp, True
    else:
        fp.seek(0)
        return fp, False
