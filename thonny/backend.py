# -*- coding: utf-8 -*-

import _thread
import io
import logging
import os.path
import pathlib
import queue
import shlex
import stat
import sys
import threading
import time
import traceback
from abc import abstractmethod, ABC
from typing import BinaryIO, Callable, List, Dict, Optional, Iterable, Union, Any

from thonny.common import (
    BackendEvent,
    EOFCommand,
    InlineCommand,
    InlineResponse,
    InputSubmission,
    ToplevelCommand,
    ToplevelResponse,
    parse_message,
    serialize_message,
    ImmediateCommand,
    MessageFromBackend,
    CommandToBackend,
    universal_dirname,
)
from thonny.common import IGNORED_FILES_AND_DIRS  # TODO: try to get rid of this
from thonny.common import ConnectionClosedException

NEW_DIR_MODE = 0o755


logger = logging.getLogger(__name__)


class BaseBackend(ABC):
    """Methods for both MainBackend and forwarding backend"""

    def __init__(self):
        self._current_command = None
        self._incoming_message_queue = queue.Queue()  # populated by the reader thread
        self._interrupt_lock = threading.Lock()
        self._last_progress_reporting_time = 0
        self._init_command_reader()

    def _init_command_reader(self):
        # Don't use threading for creating a management thread, because I don't want them
        # to be affected by threading.settrace
        _thread.start_new_thread(self._read_incoming_messages, ())

    def mainloop(self):
        try:
            while self._should_keep_going():
                try:
                    try:
                        msg = self._fetch_next_incoming_message(timeout=0.01)
                    except queue.Empty:
                        self._perform_idle_tasks()
                    else:
                        if isinstance(msg, InputSubmission):
                            self._handle_user_input(msg)
                        elif isinstance(msg, EOFCommand):
                            self._handle_eof_command(msg)
                        else:
                            self._current_command = msg
                            self._handle_normal_command(msg)
                except KeyboardInterrupt:
                    self._send_output("KeyboardInterrupt", "stderr")  # CPython idle REPL does this
                    self.send_message(ToplevelResponse())
        except ConnectionClosedException:
            sys.exit(0)

    def _current_command_is_interrupted(self):
        return getattr(self._current_command, "interrupted", False)

    def _fetch_next_incoming_message(self, timeout=None):
        return self._incoming_message_queue.get(timeout=timeout)

    def _report_progress(
        self, cmd, description: Optional[str], value: float, maximum: float
    ) -> None:
        # Don't notify too often (unless it's the final notification)
        if value != maximum and time.time() - self._last_progress_reporting_time < 0.2:
            return

        self.send_message(
            BackendEvent(
                event_type="InlineProgress",
                command_id=cmd["id"],
                value=value,
                maximum=maximum,
                description=description,
            )
        )
        self._last_progress_reporting_time = time.time()

    def _report_current_action(self, cmd, description: str) -> None:
        self.send_message(
            BackendEvent(
                event_type="InlineProgress",
                command_id=cmd["id"],
                description=description,
            )
        )

    def _read_incoming_messages(self):
        # works in a separate thread
        while self._should_keep_going():
            if not self._read_one_incoming_message():
                break

    def _read_one_incoming_message(self):
        line = self._read_incoming_msg_line()
        if line == "":
            return False
        msg = parse_message(line)
        if isinstance(msg, ImmediateCommand):
            # This will be handled right away
            self._handle_immediate_command(msg)
        else:
            self._incoming_message_queue.put(msg)
        return True

    def _prepare_command_response(
        self, response: Union[MessageFromBackend, Dict, None], command: CommandToBackend
    ) -> MessageFromBackend:
        if response is None:
            response = {}

        if "id" in command and "command_id" not in response:
            response["command_id"] = command["id"]

        if isinstance(response, MessageFromBackend):
            if "command_name" not in response:
                response["command_name"] = command["name"]
            return response
        else:
            if isinstance(response, dict):
                args = response
            else:
                args = {}

            if isinstance(command, ToplevelCommand):
                return ToplevelResponse(command_name=command.name, **args)
            else:
                assert isinstance(command, InlineCommand)
                return InlineResponse(command_name=command.name, **args)

    def send_message(self, msg: MessageFromBackend) -> None:
        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()

    def _send_output(self, data, stream_name):
        if not data:
            return

        data = self._transform_output(data, stream_name)
        msg = BackendEvent(event_type="ProgramOutput", stream_name=stream_name, data=data)
        self.send_message(msg)

    def _transform_output(self, data, stream_name):
        return data

    def _read_incoming_msg_line(self) -> str:
        return sys.stdin.readline()

    def _perform_idle_tasks(self):
        """Executed when there is no commands in queue"""
        pass

    def _report_internal_exception(self, exception=None):
        logger.exception("PROBLEM WITH THONNY'S BACK-END", exc_info=exception)

    def _report_internal_error(self, message):
        print("PROBLEM WITH THONNY'S BACK-END:\n" + message + "\n", file=sys.stderr)

    @abstractmethod
    def _should_keep_going(self) -> bool:
        """Returns False when there is no point in processing more commands
        (eg. connection to the target process is lost or target process has exited)"""

    @abstractmethod
    def _handle_user_input(self, msg: InputSubmission) -> None:
        pass

    @abstractmethod
    def _handle_eof_command(self, msg: EOFCommand) -> None:
        pass

    @abstractmethod
    def _handle_normal_command(self, cmd: CommandToBackend) -> None:
        pass

    @abstractmethod
    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        """Command handler will be executed in command reading thread, right after receiving the command"""


class MainBackend(BaseBackend, ABC):
    """Backend which does not forward to another backend"""

    def __init__(self):
        BaseBackend.__init__(self)

    def _cmd_get_dirs_children_info(self, cmd):
        """Provides information about immediate children of paths opened in a file browser"""
        data = {
            path: self._get_filtered_dir_children_info(path, cmd["include_hidden"])
            for path in cmd["paths"]
        }
        return {"node_id": cmd["node_id"], "dir_separator": self._get_sep(), "data": data}

    def _cmd_prepare_upload(self, cmd):
        """Returns info about items to be overwritten or merged by cmd.paths"""
        return {"existing_items": self._get_paths_info(cmd.target_paths, recurse=False)}

    def _cmd_prepare_download(self, cmd):
        assert "id" in cmd
        """Returns info about all items under and including cmd.paths"""
        return {"all_items": self._get_paths_info(cmd.source_paths, recurse=True)}

    def _get_paths_info(self, paths: List[str], recurse: bool) -> Dict[str, Dict]:
        result = {}

        for path in paths:
            info = self._get_path_info(path)
            if info is not None:
                info["anchor"] = path
                result[path] = info

            if recurse and info is not None and info["kind"] == "dir":
                desc_infos = self._get_dir_descendants_info(path)
                for key in desc_infos:
                    desc_infos[key]["anchor"] = path
                result.update(desc_infos)

        return result

    def _get_dir_descendants_info(self, path: str, include_hidden: bool = False) -> Dict[str, Dict]:
        """Assumes path is dir. Dict is keyed by full path"""
        result = {}
        children_info = self._get_filtered_dir_children_info(path, include_hidden)
        for child_name, child_info in children_info.items():
            full_child_path = path + self._get_sep() + child_name
            result[full_child_path] = child_info
            if child_info["kind"] == "dir":
                result.update(self._get_dir_descendants_info(full_child_path))

        return result

    def _get_filtered_dir_children_info(
        self, path: str, include_hidden: bool = False
    ) -> Optional[Dict[str, Dict]]:
        children = self._get_dir_children_info(path, include_hidden)
        if children is None:
            return None

        return {name: children[name] for name in children if name not in IGNORED_FILES_AND_DIRS}

    @abstractmethod
    def _get_path_info(self, path: str) -> Optional[Dict]:
        """Returns information about this path or None if it doesn't exist"""

    @abstractmethod
    def _get_dir_children_info(self, path: str) -> Optional[Dict[str, Dict]]:
        """For existing dirs returns Dict[child_short_name, Dict of its information].
        Returns None if path doesn't exist or is not a dir.
        """

    @abstractmethod
    def _get_sep(self) -> str:
        """Returns symbol for combining parent directory path and child name"""


class UploadDownloadMixin(ABC):
    """Backend, which runs on a local process and talks to a nonlocal system,
    and therefore is able to upload/download"""

    def _cmd_download(self, cmd):
        errors = self._transfer_files_and_dirs(
            cmd.items, self._ensure_local_directory, self._download_file, cmd, pathlib.Path
        )
        return {"errors": errors}

    def _cmd_upload(self, cmd):
        errors = self._transfer_files_and_dirs(
            cmd.items,
            self._ensure_remote_directory,
            self._upload_file,
            cmd,
            pathlib.PurePosixPath,
        )
        return {"errors": errors}

    def _cmd_read_file(self, cmd):
        def callback(completed, total):
            self._report_progress(cmd, cmd["path"], completed, total)

        try:
            with io.BytesIO() as fp:
                self._read_file(cmd["path"], fp, callback)
                fp.seek(0)
                content_bytes = fp.read()

            error = None
        except Exception as e:
            self._report_internal_exception()
            error = str(e)
            content_bytes = None

        return {"content_bytes": content_bytes, "path": cmd["path"], "error": error}

    def _cmd_write_file(self, cmd):
        def callback(completed, total):
            self._report_progress(cmd, cmd["path"], completed, total)

        try:
            with io.BytesIO() as fp:
                fp.write(cmd["content_bytes"])
                fp.seek(0)
                self._write_file(fp, cmd["path"], len(cmd["content_bytes"]), callback)

            error = None
        except Exception as e:
            self._report_internal_exception()
            error = str(e)

        return InlineResponse(
            command_name="write_file", path=cmd["path"], editor_id=cmd.get("editor_id"), error=error
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
                total_cost += item["size"] + self._get_file_fixed_cost()
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
                    print("%s (%d bytes)" % (item["source_path"], item["size"]))
                    transfer_file_fun(item["source_path"], item["target_path"], copy_bytes_notifier)
                    completed_cost += self._get_file_fixed_cost() + item["size"]
            except OSError as e:
                errors.append(
                    "Could not copy %s to %s: %s"
                    % (item["source_path"], item["target_path"], str(e))
                )

        return errors

    def _download_file(self, source_path, target_path, callback):
        with open(target_path, "bw") as target_fp:
            self._read_file(source_path, target_fp, callback)

    def _upload_file(self, source_path, target_path, callback):
        with open(source_path, "br") as source_fp:
            self._write_file(
                source_fp,
                target_path,
                os.path.getsize(source_path),
                callback,
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
        "returns None if path doesn't exist"

    @abstractmethod
    def _mkdir_for_upload(self, path: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _write_file(
        self,
        source_fp: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _read_file(
        self, source_path: str, target_fp: BinaryIO, callback: Callable[[int, int], None]
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _report_internal_exception(self):
        raise NotImplementedError()

    @abstractmethod
    def _report_progress(
        self, cmd, description: Optional[str], value: float, maximum: float
    ) -> None:
        raise NotImplementedError()


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
    def __init__(self, host, user, password, interpreter, cwd):
        # UploadDownloadMixin.__init__(self)
        try:
            import paramiko
            from paramiko.client import SSHClient, AutoAddPolicy
        except ImportError:
            print(
                "\nThis back-end requires an extra package named 'paramiko'."
                " Install it from 'Tools => Manage plug-ins' or via your system package manager.",
                file=sys.stderr,
            )
            sys.exit()

        self._host = host
        self._user = user
        self._password = password
        self._remote_interpreter = interpreter
        self._cwd = cwd
        self._proc = None  # type: Optional[RemoteProcess]
        self._sftp = None  # type: Optional[paramiko.SFTPClient]
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        # TODO: does it get closed properly after process gets killed?
        self._connect()

    def _connect(self):
        from paramiko.ssh_exception import AuthenticationException
        import socket

        from paramiko import SSHException

        try:
            self._client.connect(
                hostname=self._host,
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

            sys.exit(1)

    def _create_remote_process(self, cmd_items: List[str], cwd: str, env: Dict) -> RemoteProcess:
        # Before running the main thing:
        # * print process id (so that we can kill it later)
        #   http://redes-privadas-virtuales.blogspot.com/2013/03/getting-hold-of-remote-pid-through.html
        # * change to desired directory
        #
        # About -onlcr: https://stackoverflow.com/q/35887380/261181
        cmd_line_str = (
            "echo $$ ; stty -echo ; stty -onlcr ; "
            + (" cd %s  2> /dev/null ;" % shlex.quote(cwd) if cwd else "")
            + (" exec " + " ".join(map(shlex.quote, cmd_items)))
        )
        stdin, stdout, _ = self._client.exec_command(
            cmd_line_str, bufsize=0, get_pty=True, environment=env
        )

        # stderr gets directed to stdout because of pty
        pid = stdout.readline().strip()
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
            self._sftp = paramiko.SFTPClient.from_transport(self._client.get_transport())

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
    ) -> None:
        self._perform_sftp_operation_with_retry(
            lambda sftp: sftp.putfo(source_fp, target_path, callback)
        )

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
        except OSError as e:
            return None

    def _mkdir_for_upload(self, path: str) -> None:
        self._perform_sftp_operation_with_retry(lambda sftp: sftp.mkdir(path, NEW_DIR_MODE))


def _longest_common_path_prefix(str_paths, path_class):
    assert str_paths

    if len(str_paths) == 1:
        return str_paths[0]

    list_of_parts = []
    for str_path in str_paths:
        list_of_parts.append(path_class(str_path).parts)

    first = list_of_parts[0]
    rest = list_of_parts[1:]

    i = 0
    while i < len(first):
        item_i = first[i]
        if not all([len(x) > i and x[i] == item_i for x in rest]):
            break
        else:
            i += 1

    if i == 0:
        return ""

    result = path_class(first[0])
    for j in range(1, i):
        result = result.joinpath(first[j])

    return str(result)


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
    from thonny import THONNY_USER_DIR

    return os.path.join(THONNY_USER_DIR, "ssh_password")


def delete_stored_ssh_password():
    if os.path.exists(get_ssh_password_file_path()):
        # invalidate stored password
        os.remove(get_ssh_password_file_path())


if __name__ == "__main__":
    # print(_closest_common_directory(["C:\\kala\\pala", "C:\\kala", "D:\\kuku"], pathlib.PureWindowsPath))
    print(_longest_common_path_prefix(["C:\\kala\\pala", "C:\\kala"], pathlib.PureWindowsPath))
    print(_longest_common_path_prefix(["C:\\kala\\pala"], pathlib.PureWindowsPath))
