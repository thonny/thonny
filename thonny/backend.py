# -*- coding: utf-8 -*-
import queue
import sys
import threading
import time
import traceback
from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, Dict, List, Optional, Union

import thonny
from thonny import report_time
from thonny.common import (  # TODO: try to get rid of this
    INTERNAL_ERROR_STATUS_CODE,
    IGNORED_FILES_AND_DIRS,
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
    parse_message,
    read_one_incoming_message_str,
    serialize_message,
    UserError,
)

logger = getLogger(__name__)


class BaseBackend(ABC):
    """Methods for both MainBackend and forwarding backend"""

    def __init__(self):
        self._current_command = None
        self._current_command_interrupt_event = None
        self._incoming_message_queue = queue.Queue()  # populated by the reader thread
        self._interrupt_lock = threading.Lock()
        self._last_progress_reporting_time: float = 0
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
                        self._current_command_interrupt_event = threading.Event()
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
        self._send_output(
            "\n", "stderr"
        )  # in case we were at prompt or another line without newline
        self._send_output("\n" + message + "\n", "stderr")
        self._send_output(
            "\n" + "Click ☐ at the bottom of the window or use Stop/Restart to reconnect." + "\n",
            "stderr",
        )
        sys.exit(INTERNAL_ERROR_STATUS_CODE)

    def _current_command_is_interrupted(self):
        return (
            self._current_command_interrupt_event is not None
            and self._current_command_interrupt_event.is_set()
        )

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
    def _check_for_connection_error(self) -> None: ...

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
        BaseBackend.__init__(self)

    def add_command(self, command_name, handler):
        """Handler should be 1-argument function taking command object.

        Handler may return None (in this case no response is sent to frontend)
        or a BackendResponse
        """
        self._command_handlers[command_name] = handler

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
            except Exception:
                logger.exception("Exception while handling ex %r", cmd.name)
                self._report_internal_exception("Exception while handling %r" % cmd.name)
                sys.exit(INTERNAL_ERROR_STATUS_CODE)

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

    @abstractmethod
    def _cmd_get_active_distributions(self, cmd) -> Dict[str, Any]: ...

    @abstractmethod
    def _cmd_install_distributions(self, cmd) -> Dict[str, Any]: ...

    @abstractmethod
    def _cmd_uninstall_distributions(self, cmd) -> Dict[str, Any]: ...

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
        assert children_info is not None
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
