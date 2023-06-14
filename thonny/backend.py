# -*- coding: utf-8 -*-
import _thread
import io
import os.path
import pathlib
import queue
import stat
import sys
import threading
import time
import traceback
import warnings
from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, BinaryIO, Callable, Dict, Iterable, List, Optional, Tuple, Union

import thonny
from thonny import report_time
from thonny.common import (  # TODO: try to get rid of this
    IGNORED_FILES_AND_DIRS,
    PROCESS_ACK,
    BackendEvent,
    CommandToBackend,
    EOFCommand,
    ImmediateCommand,
    InlineCommand,
    InlineResponse,
    InputSubmission,
    MessageFromBackend,
    ToplevelCommand,
    ToplevelResponse,
    UserError,
    is_local_path,
    parse_message,
    read_one_incoming_message_str,
    serialize_message,
    try_load_modules_with_frontend_sys_path,
    universal_dirname,
)

NEW_DIR_MODE = 0o755


logger = getLogger(__name__)


class BaseBackend(ABC):
    """Methods for both MainBackend and forwarding backend"""

    def __init__(self):
        self._current_command = None
        self._incoming_message_queue = queue.Queue()  # populated by the reader thread
        self._interrupt_lock = threading.Lock()
        self._last_progress_reporting_time = 0
        self._last_sent_output = ""
        self._init_command_reader()

    def _init_command_reader(self):
        # NB! This approach is used only in MicroPython and SshCPython backend.
        # MainCPython backend uses main thread for reading commands
        # https://github.com/thonny/thonny/issues/1363
        threading.Thread(target=self._read_incoming_messages, daemon=True).start()

    def mainloop(self):
        report_time("Beginning of mainloop")

        try:
            while True:
                self._check_for_connection_error()
                try:
                    msg = self._fetch_next_incoming_message(timeout=0.01)
                except KeyboardInterrupt:
                    self._send_output(
                        "\nKeyboardInterrupt", "stderr"
                    )  # CPython idle REPL does this
                    self.send_message(ToplevelResponse())
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
            self._send_output("\nKeyboardInterrupt", "stderr")
            sys.exit(0)
        except ConnectionError as e:
            self.handle_connection_error(e)
        except Exception:
            # Error in Thonny's code
            logger.exception("mainloop error")
            self._report_internal_exception("mainloop error")

        logger.info("After mainloop")
        sys.exit(17)

    def handle_connection_error(self, error=None):
        logger.info("Handling connection error")
        message = "Connection lost"
        if error:
            message += " -- " + str(error)
        self._send_output("\n" + message + "\n", "stderr")
        self._send_output("\n" + "Use Stop/Restart to reconnect." + "\n", "stderr")
        sys.exit(1)

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
        while True:
            if not self._read_one_incoming_message():
                break

    def _read_one_incoming_message(self):
        msg_str = read_one_incoming_message_str(self._read_incoming_msg_line)
        if not msg_str:
            return False

        msg = parse_message(msg_str)
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
        self._last_sent_output = data
        self.send_message(msg)

    def _transform_output(self, data, stream_name):
        return data

    def _read_incoming_msg_line(self) -> str:
        return sys.stdin.readline()

    def _perform_idle_tasks(self):
        """Executed when there is no commands in queue"""
        pass

    def _report_internal_exception(self, msg: str) -> None:
        user_msg = "PROBLEM IN THONNY'S BACK-END: " + msg
        if sys.exc_info()[1]:
            err_msg = "\n".join(
                traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])
            ).strip()
            user_msg += f" ({err_msg})"

        user_msg += ".\nSee " + thonny.BACKEND_LOG_MARKER + " for more info."

        print(user_msg, file=sys.stderr)

    def _report_internal_warning(self, msg: str) -> None:
        user_msg = f"Warning: {msg}.\nSee backend.log for more info."
        print(user_msg, file=sys.stderr)

    @abstractmethod
    def _check_for_connection_error(self) -> None:
        ...

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
        self._command_handlers = {}
        self._jedi_is_loaded = False
        BaseBackend.__init__(self)

    def add_command(self, command_name, handler):
        """Handler should be 1-argument function taking command object.

        Handler may return None (in this case no response is sent to frontend)
        or a BackendResponse
        """
        self._command_handlers[command_name] = handler

    def send_message(self, msg: MessageFromBackend) -> None:
        super().send_message(msg)

        # take the time for pre-loading jedi after the first toplevel response
        if isinstance(msg, ToplevelResponse):
            self._check_load_jedi()

    def _handle_normal_command(self, cmd: CommandToBackend) -> None:
        assert isinstance(cmd, (ToplevelCommand, InlineCommand))
        logger.debug("Command: %r", cmd)

        if cmd.name in self._command_handlers:
            handler = self._command_handlers[cmd.name]
        else:
            handler = getattr(self, "_cmd_" + cmd.name, None)

        if handler is None:
            if isinstance(cmd, ToplevelCommand):
                self._send_output(f"Unknown command '{cmd.name}'", "stderr")
            response = {"error": "Unknown command: " + cmd.name}
        else:
            try:
                response = handler(cmd)
                # Exceptions must be caused by Thonny or plugins code, because the ones
                # from user code are caught at execution places
            except UserError as e:
                logger.info("UserError while handling %r", cmd.name, exc_info=True)
                if isinstance(cmd, ToplevelCommand):
                    print(str(e), file=sys.stderr)
                    response = {}
                else:
                    response = {"error": str(e)}
            except KeyboardInterrupt as e:
                if isinstance(cmd, ToplevelCommand):
                    print(str(e), file=sys.stderr)
                    response = {}
                else:
                    response = {"error": "Interrupted", "interrupted": True}
            except Exception as e:
                logger.exception("Exception while handling %r", cmd.name)
                self._report_internal_exception("Exception while handling %r" % cmd.name)
                sys.exit(1)

        if response is False:
            # Command doesn't want to send any response
            return

        real_response = self._prepare_command_response(response, cmd)
        self.send_message(real_response)

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

    def _cmd_shell_autocomplete(self, cmd):
        error = None
        try:
            from thonny import jedi_utils
        except ImportError:
            completions = []
            error = "Could not import jedi"
        else:
            import __main__

            with warnings.catch_warnings():
                completions = jedi_utils.get_interpreter_completions(
                    cmd.source, [__main__.__dict__], sys_path=self._get_sys_path_for_analysis()
                )

        return dict(
            source=cmd.source,
            completions=completions,
            error=error,
            row=cmd.row,
            column=cmd.column,
        )

    def _cmd_editor_autocomplete(self, cmd):
        logger.debug("Starting _cmd_editor_autocomplete")
        error = None
        try:
            from thonny import jedi_utils

            sys_path = self._get_sys_path_for_analysis()

            # add current dir for local files
            """
            if cmd.filename and is_local_path(cmd.filename):
                sys_path.insert(0, os.getcwd())
                logger.debug("editor autocomplete with %r", sys_path)
            """

            with warnings.catch_warnings():
                completions = jedi_utils.get_script_completions(
                    cmd.source,
                    cmd.row,
                    cmd.column,
                    cmd.filename,
                    sys_path=sys_path,
                )
        except ImportError:
            completions = []
            error = "Could not import jedi"

        return dict(
            source=cmd.source,
            row=cmd.row,
            column=cmd.column,
            filename=cmd.filename,
            completions=completions,
            error=error,
        )

    def _cmd_get_completion_details(self, cmd):
        # it is assumed this gets called after requesting editor or shell completions
        from thonny import jedi_utils

        return InlineResponse(
            "get_completion_details",
            full_name=cmd.full_name,
            details=jedi_utils.get_completion_details(cmd.full_name),
        )

    def _cmd_get_editor_calltip(self, cmd):
        from thonny import jedi_utils

        signatures = jedi_utils.get_script_signatures(
            cmd.source,
            cmd.row,
            cmd.column,
            cmd.filename,
            sys_path=self._get_sys_path_for_analysis(),
        )
        return InlineResponse(
            "get_editor_calltip",
            source=cmd.source,
            row=cmd.row,
            column=cmd.column,
            filename=cmd.filename,
            signatures=signatures,
        )

    def _cmd_get_shell_calltip(self, cmd):
        import __main__
        from thonny import jedi_utils

        signatures = jedi_utils.get_interpreter_signatures(
            cmd.source, [__main__.__dict__], sys_path=self._get_sys_path_for_analysis()
        )
        return InlineResponse(
            "get_shell_calltip",
            source=cmd.source,
            row=cmd.row,
            column=cmd.column,
            filename=cmd.filename,
            signatures=signatures,
        )

    def _cmd_highlight_occurrences(self, cmd):
        from thonny import jedi_utils

        refs = jedi_utils.get_references(
            cmd.source,
            cmd.row,
            cmd.column,
            cmd.filename,
            scope="file",
            sys_path=self._get_sys_path_for_analysis(),
        )

        return {"references": refs, "text_last_operation_time": cmd.text_last_operation_time}

    def _cmd_get_definitions(self, cmd):
        from thonny import jedi_utils

        defs = jedi_utils.get_definitions(
            cmd.source,
            cmd.row,
            cmd.column,
            filename=cmd.filename,
            sys_path=self._get_sys_path_for_analysis(),
        )
        return {"definitions": defs}

    def _cmd_get_active_distributions(self, cmd):
        raise NotImplementedError()

    def _cmd_install_distributions(self, cmd):
        raise NotImplementedError()

    def _cmd_uninstall_distributions(self, cmd):
        raise NotImplementedError()

    def _get_sys_path_for_analysis(self) -> Optional[List[str]]:
        return None

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
    def _get_dir_children_info(
        self, path: str, include_hidden: bool = False
    ) -> Optional[Dict[str, Dict]]:
        """For existing dirs returns Dict[child_short_name, Dict of its information].
        Returns None if path doesn't exist or is not a dir.
        """

    @abstractmethod
    def _get_sep(self) -> str:
        """Returns symbol for combining parent directory path and child name"""

    def _check_load_jedi(self) -> None:
        if self._jedi_is_loaded:
            return
        logger.info("Loading Jedi")

        report_time("Before loading Jedi")
        try_load_modules_with_frontend_sys_path(["jedi", "parso"])
        self._jedi_is_loaded = True
        report_time("After loading Jedi")


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
    def _mkdir_for_upload(self, path: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _write_file(
        self,
        source_fp: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
        make_shebang_scripts_executable: bool,
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
            from paramiko.client import AutoAddPolicy, SSHClient
        except ImportError:
            print(
                "\nThis back-end requires an extra package named 'paramiko'."
                " Install it from 'Tools => Manage plug-ins' or via your system package manager.",
                file=sys.stderr,
            )
            sys.exit(1)

        self._host = host
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

    def _connect(self):
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
        import shlex

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
        ack = stdout.readline().strip()
        if ack != PROCESS_ACK:
            raise RuntimeError(f"Got {ack!r} instead of expected {PROCESS_ACK!r}")
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


if __name__ == "__main__":
    # print(_closest_common_directory(["C:\\kala\\pala", "C:\\kala", "D:\\kuku"], pathlib.PureWindowsPath))
    print(_longest_common_path_prefix(["C:\\kala\\pala", "C:\\kala"], pathlib.PureWindowsPath))
    print(_longest_common_path_prefix(["C:\\kala\\pala"], pathlib.PureWindowsPath))
