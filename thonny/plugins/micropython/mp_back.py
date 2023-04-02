"""
MP 1.12

>>> #import uos
>>> dir(uos)
['__class__', '__name__', 'remove', 'VfsFat', 'VfsLfs2', 'chdir', 'dupterm', 'dupterm_notify', 
'getcwd', 'ilistdir', 'listdir', 'mkdir', 'mount', 'rename', 'rmdir', 'stat', 'statvfs', 'umount', 
'uname', 'urandom']
>>> import sys
>>> dir(sys)
['__class__', '__name__', 'argv', 'byteorder', 'exit', 'implementation', 'maxsize', 'modules', 
'path', 'platform', 'print_exception', 'stderr', 'stdin', 'stdout', 'version', 'version_info']

micro:bit (1.9.2)

>>> import os
>>> dir(os)
['__name__', 'remove', 'listdir', 'size', 'uname']
>>> import sys
>>> dir(sys)
['__name__', 'version', 'version_info', 'implementation', 'platform', 'byteorder', 'exit', 
'print_exception']

CP 5.0
>>> dir(os)
['__class__', '__name__', 'chdir', 'getcwd', 'listdir', 'mkdir', 'remove', 'rename', 'rmdir', 'sep',
'stat', 'statvfs', 'sync', 'uname', 'unlink', 'urandom']
>>> import sys
>>> dir(sys)
['__class__', '__name__', 'argv', 'byteorder', 'exit', 'implementation', 'maxsize', 'modules', 
'path', 'platform', 'print_exception', 'stderr', 'stdin', 'stdout', 'version', 'version_info']


"""

import ast
import datetime
import io
import os
import re
import sys
import textwrap
import threading
import time
import traceback
from abc import ABC, abstractmethod
from logging import getLogger
from queue import Empty, Queue
from textwrap import dedent
from threading import Lock
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

from serial import SerialTimeoutException

from thonny import BACKEND_LOG_MARKER, get_backend_log_file, report_time
from thonny.backend import MainBackend
from thonny.common import (
    OBJECT_LINK_END,
    OBJECT_LINK_START,
    BackendEvent,
    CommandToBackend,
    CompletionInfo,
    DistInfo,
    EOFCommand,
    ImmediateCommand,
    InlineCommand,
    InlineResponse,
    InputSubmission,
    MessageFromBackend,
    Record,
    ToplevelCommand,
    ToplevelResponse,
    UserError,
    ValueInfo,
    parse_message,
    serialize_message,
)
from thonny.plugins.micropython.connection import MicroPythonConnection

ENCODING = "utf-8"

# Commands
RAW_MODE_CMD = b"\x01"
NORMAL_MODE_CMD = b"\x02"
INTERRUPT_CMD = b"\x03"
SOFT_REBOOT_CMD = b"\x04"

# Output tokens
VALUE_REPR_START = b"<repr>"
VALUE_REPR_END = b"</repr>"
EOT = b"\x04"
MGMT_VALUE_START = b"<thonny>"
MGMT_VALUE_END = b"</thonny>"

# How many seconds to wait for something that should appear quickly.
# In other words -- how long to wait with reporting a protocol error
# (hoping that the required piece is still coming)
WAIT_OR_CRASH_TIMEOUT = 5

SECONDS_IN_YEAR = 60 * 60 * 24 * 365

Y2000_EPOCH_OFFSET = 946684800

STAT_KIND_INDEX = 0
STAT_SIZE_INDEX = 6
STAT_MTIME_INDEX = 8

PASTE_MODE_CMD = b"\x05"
PASTE_MODE_LINE_PREFIX = b"=== "


logger = getLogger(__name__)


class MicroPythonBackend(MainBackend, ABC):
    def __init__(self, clean, args):
        # Make pipkin available
        sys.path.insert(
            0,
            os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "vendored_libs")),
        )
        logger.info("Initializing MicroPythonBackend of type %s", type(self).__name__)
        self._connection: MicroPythonConnection
        self._args = args
        self._last_interrupt_time = None
        self._local_cwd = None
        self._cwd = args.get("cwd")
        self._progress_times = {}
        self._welcome_text = None
        self._sys_path = None
        self._epoch_year = None
        self._builtin_modules = []
        self._number_of_interrupts_sent = 0

        MainBackend.__init__(self)
        try:
            report_time("before prepare")
            self._process_until_initial_prompt(
                interrupt=args.get("interrupt_on_connect", False) or clean, clean=clean
            )
            if self._welcome_text is None:
                self._welcome_text = self._fetch_welcome_text()
                report_time("got welcome")

            # Get rid of the welcome text which was printed while searching for prompt
            self.send_message(
                BackendEvent(event_type="HideTrailingOutput", text=self._welcome_text)
            )

            self._prepare_after_soft_reboot(clean)

            if not self._builtin_modules:
                self._builtin_modules = self._fetch_builtin_modules()
                logger.debug("Built-in modules: %s", self._builtin_modules)

            self._prepare_rtc()
            self._send_ready_message()
            report_time("sent ready")
            self.mainloop()
        except ConnectionError as e:
            self.handle_connection_error(e)
        except Exception:
            logger.exception("Exception in MicroPython main method")
            self._report_internal_exception("Internal error")

    def _prepare_after_soft_reboot(self, clean=False):
        report_time("bef preparing helpers")
        logger.info("Preparing helpers")
        script = self._get_helper_code()
        logger.debug("Helper code:\n%s", script)
        self._check_perform_just_in_case_gc()
        self._execute_without_output(script)
        # self._execute_without_output(
        #     dedent(
        #         """
        #     for key in __thonny_helper.builtins.dir(__thonny_helper.builtins):
        #         if not key.startswith("__"):
        #             __thonny_helper.builtins.globals()[key] = None
        #     """
        #     ).strip()
        # )
        report_time("prepared helpers")

        self._update_cwd()
        report_time("got cwd")
        self._sys_path = self._fetch_sys_path()

        report_time("prepared")
        self._check_perform_just_in_case_gc()
        logger.info("Prepared")

    def _prepare_rtc(self):
        if self._epoch_year is None:
            self._epoch_year = self._fetch_epoch_year()

        self._check_sync_time()
        if self._args.get("validate_time"):
            self._validate_time()

    def _check_perform_just_in_case_gc(self):
        if self._using_microbit_micropython():
            # May fail to allocate memory without this
            self._perform_gc()

    def _check_sync_time(self):
        if self._args.get("sync_time"):
            self._sync_time()

    def _perform_gc(self):
        logger.debug("Performing gc")
        self._execute_without_output(
            dedent(
                """
            import gc as __thonny_gc
            __thonny_gc.collect()
            del __thonny_gc
        """
            )
        )

    def _check_prepare(self):
        pass  # overridden in bare metal

    def _get_helper_code(self):
        # Can't import functions into class context:
        # https://github.com/micropython/micropython/issues/6198
        return (
            dedent(
                """
            class __thonny_helper:
                import builtins
                try:
                    import uos as os
                except builtins.ImportError:
                    import os
                import sys
                last_non_none_repl_value = None
                
                # for object inspector
                inspector_values = builtins.dict()
                @builtins.classmethod
                def print_repl_value(cls, obj):
                    if obj is not None:
                        cls.builtins.print({start_marker!r} % cls.builtins.id(obj), cls.builtins.repr(obj), {end_marker!r}, sep='')
                        cls.last_non_none_repl_value = obj
                
                @builtins.classmethod
                def print_mgmt_value(cls, obj):
                    cls.builtins.print({mgmt_start!r}, cls.builtins.repr(obj), {mgmt_end!r}, sep='', end='')
                    
                @builtins.classmethod
                def repr(cls, obj):
                    try:
                        s = cls.builtins.repr(obj)
                        if cls.builtins.len(s) > 50:
                            s = s[:50] + "..."
                        return s
                    except cls.builtins.Exception as e:
                        return "<could not serialize: " + __thonny_helper.builtins.str(e) + ">"
                    
                @builtins.classmethod
                def listdir(cls, x):
                    if cls.builtins.hasattr(cls.os, "listdir"):
                        return cls.os.listdir(x)
                    else:
                        return [rec[0] for rec in cls.os.ilistdir(x) if rec[0] not in ('.', '..')]
            """
            ).format(
                start_marker=OBJECT_LINK_START,
                end_marker=OBJECT_LINK_END,
                mgmt_start=MGMT_VALUE_START.decode(ENCODING),
                mgmt_end=MGMT_VALUE_END.decode(ENCODING),
            )
            + "\n"
        ).lstrip()

    def get_connection(self) -> MicroPythonConnection:
        raise NotImplementedError()

    def _sync_time(self):
        raise NotImplementedError()

    def _get_time_for_rtc(self):
        if self._args["local_rtc"]:
            return datetime.datetime.now().timetuple()
        else:
            return datetime.datetime.now(tz=datetime.timezone.utc).timetuple()

    def _validate_time(self):
        this_computer = self._get_time_for_rtc()
        remote = self._get_utc_timetuple_from_device()
        if isinstance(remote, tuple):
            # tweak the format if required
            remote = remote[:8]
            while len(remote) < 8:
                remote += (0,)
            remote += (-1,)  # unknown DST
            diff = int(time.mktime(this_computer) - time.mktime(remote))
            if abs(diff) > 10:
                print("WARNING: Device's real-time clock seems to be off by %s seconds" % diff)
        else:
            assert isinstance(remote, str)
            print("WARNING: Could not validate time: " + remote)

    def _get_utc_timetuple_from_device(self) -> Union[tuple, str]:
        raise NotImplementedError()

    def _resolve_unknown_epoch(self) -> int:
        raise NotImplementedError()

    def _get_actual_time_tuple_on_device(self):
        raise NotImplementedError()

    def _process_until_initial_prompt(self, interrupt: bool, clean: bool) -> None:
        raise NotImplementedError()

    def _perform_idle_tasks(self):
        self._forward_unexpected_output()

    def _handle_user_input(self, msg: InputSubmission) -> None:
        self._submit_input(msg.data)

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        raise NotImplementedError()

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        if cmd["name"] == "interrupt":
            self._interrupt()

    def _interrupt(self):
        # don't interrupt while command or input is being written
        with self._interrupt_lock:
            if self._current_command:
                self._current_command.interrupted = True
            logger.info("Sending interrupt")
            self._write(INTERRUPT_CMD)
            logger.info("Done sending interrupt")
            self._number_of_interrupts_sent += 1
            self._last_interrupt_time = time.time()

    def _handle_normal_command(self, cmd: CommandToBackend) -> None:
        logger.debug("Handling normal command '%s' in micropython backend ", cmd.name)
        report_time("before " + cmd.name)

        if "local_cwd" in cmd:
            self._local_cwd = cmd["local_cwd"]
            if os.path.isdir(self._local_cwd):
                os.chdir(self._local_cwd)

        super()._handle_normal_command(cmd)

        self._check_perform_just_in_case_gc()
        report_time("after " + cmd.name)

    def _check_for_connection_error(self) -> None:
        self.get_connection().check_for_error()

    def _using_microbit_micropython(self):
        if not self._welcome_text:
            return None

        # Don't confuse MicroPython and CircuitPython
        return "micro:bit" in self._welcome_text.lower() and "MicroPython" in self._welcome_text

    def _connected_to_pyboard(self):
        if not self._welcome_text:
            return None

        return "pyb" in self._welcome_text.lower() or "pyb" in self._builtin_modules

    def _connected_to_circuitpython(self):
        if not self._welcome_text:
            return None

        return "circuitpython" in self._welcome_text.lower()

    def _get_interpreter_kind(self):
        return "CircuitPython" if self._connected_to_circuitpython() else "MicroPython"

    def _connected_to_pycom(self):
        if not self._welcome_text:
            return None

        return "pycom" in self._welcome_text.lower()

    def _fetch_welcome_text(self) -> str:
        raise NotImplementedError()

    def _fetch_builtin_modules(self):
        raise NotImplementedError()

    def _fetch_sys_path(self):
        if not self._supports_directories():
            return []
        else:
            return self._evaluate("__thonny_helper.sys.path")

    def _fetch_epoch_year(self):
        if self._using_microbit_micropython():
            return None

        if self._connected_to_circuitpython() and "rtc" not in self._builtin_modules:
            return self._resolve_unknown_epoch()

        # The proper solution would be to query time.gmtime, but most devices don't have this function.
        # Luckily, time.localtime is good enough for deducing 1970 vs 2000 epoch.

        # Most obvious solution would be to query for 0-time, but CP doesn't support anything below Y2000,
        # so I'm querying this and adjusting later.
        val = self._evaluate(
            dedent(
                """
            try:
                from time import localtime as __thonny_localtime
                __thonny_helper.print_mgmt_value(__thonny_helper.builtins.tuple(__thonny_localtime(%d)))
                del __thonny_localtime
            except __thonny_helper.builtins.Exception as e:
                __thonny_helper.print_mgmt_value(__thonny_helper.builtins.str(e))
        """
                % Y2000_EPOCH_OFFSET
            )
        )

        if val[0] in (2000, 1999):
            # when it gives 2000 (or end of 1999) for 2000-01-01 counted from Posix epoch, then it uses Posix epoch
            # Used by Unix port, CP and Pycom
            return 1970
        elif val[0] in (2030, 2029):
            # when it looks 30 years off, then it must be 2000 epoch
            # Used by Pyboard and ESP-s
            return 2000
        else:
            result = self._resolve_unknown_epoch()
            if self._args.get("sync_time") or self._args.get("validate_time"):
                print("WARNING: Could not determine epoch year (%s), assuming %s" % (val, result))
            return result

    def _update_cwd(self):
        if not self._using_microbit_micropython():
            logger.debug("Updating cwd")
            self._cwd = self._evaluate("__thonny_helper.getcwd()")

    def _send_ready_message(self):
        args = dict(cwd=self._cwd)
        args["welcome_text"] = self._welcome_text

        self.send_message(ToplevelResponse(**args))

    def _write(self, data: bytes) -> int:
        if (
            RAW_MODE_CMD in data
            or NORMAL_MODE_CMD in data
            or INTERRUPT_CMD in data
            or EOT in data
            or PASTE_MODE_CMD in data
        ):
            logger.debug("Sending ctrl chars: %r", data)
        return self._connection.write(data)

    def _submit_input(self, cdata: str) -> None:
        # TODO: what if there is a previous unused data waiting
        assert self.get_connection().outgoing_is_empty()

        assert cdata.endswith("\n")
        if not cdata.endswith("\r\n"):
            # submission is done with CRLF
            cdata = cdata[:-1] + "\r\n"

        bdata = cdata.encode(ENCODING)
        to_be_written = bdata
        echo = b""
        with self._interrupt_lock:
            while to_be_written:
                block = self._extract_block_without_splitting_chars(to_be_written)
                self._write(block)
                # Try to consume the echo
                echo += self.get_connection().soft_read(len(block), timeout=1)
                to_be_written = to_be_written[len(block) :]

        if echo.replace(b"\r", b"").replace(b"\n", b"") != bdata.replace(b"\r", b"").replace(
            b"\n", b""
        ):
            if any(ord(c) > 127 for c in cdata):
                print(
                    "WARNING: MicroPython ignores non-ascii characters of the input",
                    file=sys.stderr,
                )
            else:
                # because of autoreload? timing problems? interruption?
                # Leave it.
                logger.warning("Unexpected echo. Expected %r, got %r" % (bdata, echo))
            self._connection.unread(echo)

    def send_message(self, msg: MessageFromBackend) -> None:
        if "cwd" not in msg:
            msg["cwd"] = self._cwd

        if "sys_path" not in msg:
            msg["sys_path"] = self._sys_path

        if "lib_dirs" not in msg:
            msg["lib_dirs"] = self._get_library_paths()

        super().send_message(msg)

    def _send_error_message(self, msg):
        self._send_output("\n" + msg + "\n", "stderr")

    def _execute(self, script, capture_output=False) -> Tuple[str, str]:
        if capture_output:
            output_lists = {"stdout": [], "stderr": []}

            def consume_output(data, stream_name):
                assert isinstance(data, str)
                output_lists[stream_name].append(data)

            self._execute_with_consumer(script, consume_output)
            result = ["".join(output_lists[name]) for name in ["stdout", "stderr"]]
            return result[0], result[1]
        else:
            self._execute_with_consumer(script, self._send_output)
            return "", ""

    def _execute_with_consumer(self, script, output_consumer):
        """Ensures prompt and submits the script.
        Reads (and doesn't return) until next prompt or connection error.

        If capture is False, then forwards output incrementally. Otherwise
        returns output if there are no problems, ie. all expected parts of the
        output are present and it reaches a prompt.
        Otherwise raises ManagementError.

        NB! If the consumer raises an exception, the processing may stop between prompts.

        The execution may block. In this case the user should do something (eg. provide
        required input or issue an interrupt). The UI should remind the interrupt in case
        of Thonny commands.
        """
        raise NotImplementedError()

    def _execute_without_output(self, script):
        """Meant for management tasks."""
        out, err = self._execute(script, capture_output=True)
        if out or err:
            raise ManagementError("Command output was not empty", script, out, err)

    def _evaluate(self, script):
        """Evaluate the output of the script or raise ManagementError, if anything looks wrong.

        Adds printing code if the script contains single expression and doesn't
        already contain printing code"""
        try:
            ast.parse(script, mode="eval")
            prefix = "__thonny_helper.print_mgmt_value("
            suffix = ")"
            if not script.strip().startswith(prefix):
                script = prefix + script + suffix
        except SyntaxError:
            pass

        out, err = self._execute(script, capture_output=True)
        if err:
            raise ManagementError("Script produced errors", script, out, err)
        elif (
            MGMT_VALUE_START.decode(ENCODING) not in out
            or MGMT_VALUE_END.decode(ENCODING) not in out
        ):
            raise ManagementError("Management markers missing", script, out, err)

        start_token_pos = out.index(MGMT_VALUE_START.decode(ENCODING))
        end_token_pos = out.index(MGMT_VALUE_END.decode(ENCODING))

        # a thread or IRQ handler may have written something before or after mgmt value
        prefix = out[:start_token_pos]
        value_str = out[start_token_pos + len(MGMT_VALUE_START) : end_token_pos]
        suffix = out[end_token_pos + len(MGMT_VALUE_END) :]

        try:
            value = ast.literal_eval(value_str)
        except Exception as e:
            raise ManagementError("Could not parse management response", script, out, err) from e

        self._send_output(prefix, "stdout")
        self._send_output(suffix, "stdout")
        return value

    def _forward_unexpected_output(self, stream_name="stdout"):
        "Invoked between commands"
        raise NotImplementedError()

    def _check_for_side_commands(self):
        # NB! EOFCommand gets different treatment depending whether it is read during processing a command
        # (ie. here) or it gets read when REPL is idle (ie. in mainloop)

        # most likely the queue is empty
        if self._incoming_message_queue.empty():
            return

        postponed = []
        while not self._incoming_message_queue.empty():
            cmd = self._incoming_message_queue.get()
            if isinstance(cmd, InputSubmission):
                self._submit_input(cmd.data)
            elif isinstance(cmd, EOFCommand):
                # in this context it is not supposed to soft-reboot
                self._write(EOT)
            else:
                postponed.append(cmd)

        # put back postponed commands
        while postponed:
            self._incoming_message_queue.put(postponed.pop(0))

    def _supports_directories(self):
        # NB! make sure self._cwd is queried first
        return bool(self._cwd)

    def _cmd_cd(self, cmd):
        if len(cmd.args) == 1:
            if not self._supports_directories():
                raise UserError("This device doesn't have directories")

            path = cmd.args[0]
            self._execute("__thonny_helper.chdir(%r)" % path)
            self._update_cwd()
            return {}
        else:
            raise UserError("%cd takes one parameter")

    def _cmd_Run(self, cmd):
        raise NotImplementedError()

    def _cmd_execute_source(self, cmd):
        # TODO: clear last object inspector requests dictionary
        if cmd.source:
            source = self._add_expression_statement_handlers(cmd.source)
            source = self._replace_last_repl_value_variables(source)
            report_time("befexeccc")
            self._execute(source, capture_output=False)
            self._check_prepare()
            report_time("affexeccc")
        # TODO: assign last value to _
        return {}

    def _cmd_execute_system_command(self, cmd):
        raise NotImplementedError()

    def _cmd_get_globals(self, cmd):
        if cmd.module_name == "__main__":
            globs = self._evaluate(
                "{name : (__thonny_helper.repr(value), __thonny_helper.builtins.id(value)) for (name, value) in __thonny_helper.builtins.globals().items() if not name.startswith('__')}"
            )
        else:
            globs = self._evaluate(
                dedent(
                    """
                import %s as __mod_for_globs
                __thonny_helper.print_mgmt_value(
                    {name : (__thonny_helper.repr(__thonny_helper.builtins.getattr(__mod_for_globs, name)), 
                             __thonny_helper.builtins.id(__thonny_helper.builtins.getattr(__mod_for_globs, name)))
                        in __thonny_helper.builtins.dir(__mod_for_globs) 
                        if not name.startswith('__')}
                )
                del __mod_for_globs
            """
                )
            )

        value_infos = {}
        for name, pair in globs.items():
            value_infos[name] = ValueInfo(pair[1], pair[0])

        logger.debug("Returning %d globals", len(value_infos))
        return {"module_name": cmd.module_name, "globals": value_infos}

    def _cmd_get_fs_info(self, cmd):
        raise NotImplementedError()

    def _cmd_get_object_info(self, cmd):
        context_id = cmd.get("context_id", None)
        basic_info = self._find_basic_object_info(cmd.object_id, context_id)
        if basic_info is None:
            return {"id": cmd.object_id, "error": "object info not available"}

        type_name = basic_info["type"].replace("<class '", "").replace("'>", "").strip()
        info = {
            "id": cmd.object_id,
            "repr": basic_info["repr"],
            "type": basic_info["type"],
            "full_type_name": type_name,
            "attributes": {},
        }

        info.update(self._get_object_info_extras(type_name, repr_str=basic_info["repr"]))
        if cmd.include_attributes:
            info["attributes"] = self._get_object_attributes(cmd.all_attributes)

        # need to keep the reference corresponding to object_id so that it can be later found as next context object
        # remove non-relevant items
        # TODO: add back links
        # TODO: release old links
        # relevant = set([cmd.object_id] + cmd.back_links + cmd.forward_links)
        self._execute(
            dedent(
                """
                if __thonny_helper.builtins.id(__thonny_helper.object_info) not in __thonny_helper.inspector_values:
                    __thonny_helper.inspector_values[__thonny_helper.builtins.id(__thonny_helper.object_info)] = __thonny_helper.object_info
            """
            )
        )

        return {"id": cmd.object_id, "info": info}

    def _cmd_shell_autocomplete(self, cmd):
        source = cmd.source
        response = dict(source=cmd.source, row=cmd.row, column=cmd.column, completions=[])

        # First the dynamic completions
        match = re.search(
            r"(\w+\.)*(\w+)?$", source
        )  # https://github.com/takluyver/ubit_kernel/blob/master/ubit_kernel/kernel.py
        if match:
            prefix = match.group()
            if "." in prefix:
                obj, prefix = prefix.rsplit(".", 1)
                names = self._evaluate(
                    "__thonny_helper.builtins.dir({obj}) if '{obj}' in __thonny_helper.builtins.locals() or '{obj}' in __thonny_helper.builtins.globals() else []".format(
                        obj=obj
                    )
                )
            else:
                names = self._evaluate("__thonny_helper.builtins.dir()")
        else:
            names = []
            prefix = ""

        # prevent TypeError (iterating over None)
        names = names if names else []

        for name in names:
            if name.startswith(prefix) and not name.startswith("__"):
                response["completions"].append(self._create_shell_completion(name, prefix))

        # add keywords, import modules etc. from jedi
        try:
            from thonny import jedi_utils

            # at the moment I'm assuming source is the code before cursor, not whole input
            lines = source.split("\n")
            jedi_completions = jedi_utils.get_script_completions(
                source,
                len(lines),
                len(lines[-1]),
                "<shell>",
                sys_path=self._get_sys_path_for_analysis(),
            )
            response["completions"] += [
                comp
                for comp in jedi_completions
                if (comp.type in ["module", "keyword"] or comp.module_name == "builtins")
                and self._should_present_completion(comp)
            ]
        except Exception as e:
            logger.exception("Problem with jedi shell autocomplete")

        return response

    def _create_shell_completion(self, name: str, prefix: str) -> CompletionInfo:
        return CompletionInfo(
            name=name,
            name_with_symbols=name,
            full_name=name,
            type="name",
            prefix_length=len(prefix),
            signatures=None,  # must be queried separately
            docstring=None,  # must be queried separately
            module_path=None,
            module_name=None,
        )

    def _find_basic_object_info(self, object_id, context_id):
        """If object is found then returns basic info and leaves object reference
        to __thonny_helper.object_info.

        Can't leave it in a global object, because when querying globals(),
        repr(globals()) would cause infinite recursion."""

        result = self._evaluate(
            dedent(
                """
                for __thonny_helper.object_info in (
                        [__thonny_helper.last_non_none_repl_value]
                        + __thonny_helper.builtins.list(__thonny_helper.builtins.globals().values()) 
                        + __thonny_helper.builtins.list(__thonny_helper.inspector_values.values())):
                    if __thonny_helper.builtins.id(__thonny_helper.object_info) == %d:
                        __thonny_helper.print_mgmt_value({
                            "repr" : __thonny_helper.builtins.repr(__thonny_helper.object_info),
                            "type": __thonny_helper.builtins.str(__thonny_helper.builtins.type(__thonny_helper.object_info))
                        })
                        break
                else:
                    __thonny_helper.object_info = None
                    __thonny_helper.print_mgmt_value(None)
            """
                % object_id
            )
        )

        if result is not None:
            return result
        elif context_id is not None:
            return self._evaluate(
                dedent(
                    """
                __thonny_helper.context_value = __thonny_helper.inspector_values.get(%d, None)
                
                if __thonny_helper.context_value is None:
                    __thonny_helper.object_info = None
                    __thonny_helper.print_mgmt_value(None)
                else:
                    __thonny_helper.context_children = [
                         __thonny_helper.builtins.getattr(__thonny_helper.context_value, name)
                         for name in __thonny_helper.builtins.dir(__thonny_helper.context_value)
                    ]
                    if __thonny_helper.builtins.isinstance(__thonny_helper.context_value, (set, tuple, list)):
                        __thonny_helper.context_children += __thonny_helper.builtins.list(__thonny_helper.context_value)
                    elif __thonny_helper.builtins.isinstance(__thonny_helper.context_value, __thonny_helper.builtins.dict):
                        __thonny_helper.context_children += __thonny_helper.builtins.list(__thonny_helper.context_value.values())
                    
                    for __thonny_helper.object_info in __thonny_helper.context_children:
                        if __thonny_helper.builtins.id(__thonny_helper.object_info) == %d:
                            __thonny_helper.print_mgmt_value({
                                "repr" : __thonny_helper.repr(__thonny_helper.object_info),
                                "type": __thonny_helper.builtins.str(__thonny_helper.builtins.type(__thonny_helper.object_info))
                            })
                            break
                    else:
                        __thonny_helper.object_info = None
                        __thonny_helper.print_mgmt_value(None)
                        
                __thonny_helper.context_value = None
                __thonny_helper.context_children = None
            """
                    % (context_id, object_id)
                )
            )
        else:
            return None

    def _get_object_attributes(self, all_attributes):
        """object is given in __thonny_helper.object_info"""
        atts = self._evaluate(
            "{name : ("
            "   __thonny_helper.builtins.id(__thonny_helper.builtins.getattr(__thonny_helper.object_info, name)),"
            "    __thonny_helper.repr(__thonny_helper.builtins.getattr(__thonny_helper.object_info, name))"
            ") for name in __thonny_helper.builtins.dir(__thonny_helper.object_info)}"
        )
        return {
            name: ValueInfo(atts[name][0], atts[name][1])
            for name in atts
            if not name.startswith("__") or all_attributes
        }

    def _get_object_info_extras(self, type_name: str, repr_str: str):
        """object is given in __thonny_helper.object_info"""
        if type_name in ("list", "tuple", "set"):
            items = self._evaluate(
                "[(__thonny_helper.builtins.id(x), __thonny_helper.repr(x)) for x in __thonny_helper.object_info]"
            )
            return {"elements": [ValueInfo(x[0], x[1]) for x in items]}
        elif type_name == "dict":
            items = self._evaluate(
                "[((__thonny_helper.builtins.id(key), __thonny_helper.repr(key)), (__thonny_helper.builtins.id(__thonny_helper.object_info[key]), "
                "__thonny_helper.repr(__thonny_helper.object_info[key]))) for key in __thonny_helper.object_info]"
            )
            return {
                "entries": [
                    (ValueInfo(x[0][0], x[0][1]), ValueInfo(x[1][0], x[1][1])) for x in items
                ]
            }
        elif type_name == "MicroBitImage":
            if repr_str.startswith("Image('") and repr_str.count(":") == 5:
                # ■ █ □ ●*✶•∙
                data = repr_str.replace("Image('", "").replace("')", "")
                content = (
                    data.replace(":", "\n")
                    .replace("0", "  ")
                    .replace("1", " ∙")
                    .replace("2", " ∙")
                    .replace("3", " •")
                    .replace("4", " •")
                    .replace("5", " ✶")
                    .replace("6", " ✶")
                    .replace("7", " *")
                    .replace("8", " *")
                    .replace("9", " ●")
                    + "\n\n"
                    + data.replace(":", "\n")
                    .replace("0", " 0")
                    .replace("1", " 1")
                    .replace("2", " 2")
                    .replace("3", " 3")
                    .replace("4", " 4")
                    .replace("5", " 5")
                    .replace("6", " 6")
                    .replace("7", " 7")
                    .replace("8", " 8")
                    .replace("9", " 9")
                )
                return {"microbit_image": content}
            else:
                return {}
        else:
            return {}

    def _cmd_delete(self, cmd):
        assert cmd.paths
        self._delete_sorted_paths(sorted(cmd.paths, key=len, reverse=True))

    def _cmd_get_active_distributions(self, cmd):
        try:
            current_state = self._perform_pipkin_operation_and_list(None)
        except Exception as e:
            logger.exception("Could not get active distributions")
            return dict(error=str(e))

        return dict(
            distributions={dist.key: dist for dist in current_state},
        )

    def _cmd_install_distributions(self, cmd):
        args = cast(List[str], cmd.args[:])
        assert isinstance(args, List)
        if "--user" in args:
            user = True
            args.remove("--user")
        else:
            user = False

        if "--upgrade" in args:
            upgrade = True
            args.remove("--upgrade")
        else:
            upgrade = False

        if "-r" in args:
            pos = args.index("-r")
            req_file = args[pos + 1]
            del args[pos + 1]
            del args[pos]
            requirement_files = [req_file]
        else:
            requirement_files = None

        assert not any([arg.startswith("-") for arg in args])
        specs = args

        try:
            new_state = self._perform_pipkin_operation_and_list(
                command="install",
                specs=specs,
                user=user,
                upgrade=upgrade,
                requirement_files=requirement_files,
            )
        except Exception as e:
            logger.exception("Could not install")
            return dict(error=str(e))

        return {"distributions": new_state}

    def _cmd_uninstall_distributions(self, cmd):
        try:
            new_state = self._perform_pipkin_operation_and_list(
                command="uninstall", packages=cmd.args, yes=True
            )
        except Exception as e:
            logger.exception("Could not uninstall")
            return dict(error=str(e))

        return {"distributions": new_state}

    def _get_library_paths(self) -> [str]:
        """Returns list of directories which are supposed to contain library code"""
        if self._sys_path is None:
            return None

        return [path for path in self._sys_path if "lib" in path and path.startswith("/")]

    def _guess_package_pypi_name(self, installed_name) -> str:
        return "micropython-" + installed_name

    def _mkdir(self, path: str) -> None:
        # assumes part path exists and path doesn't
        self._execute_without_output("__thonny_helper.os.mkdir(%r)" % path)

    @abstractmethod
    def _create_pipkin_adapter(self):
        ...

    def _perform_pipkin_operation_and_list(self, command: Optional[str], **kwargs) -> Set[DistInfo]:
        import pipkin.common
        from pipkin.session import Session

        adapter = self._create_pipkin_adapter()
        session = Session(adapter, tty=False)

        try:
            if command:
                assert hasattr(session, command)
                logger.info("Calling method %r in pipkin session with args %r", command, kwargs)
                getattr(session, command)(**kwargs)
            return {
                DistInfo(
                    key=di.key,
                    project_name=di.project_name,
                    version=di.version,
                    location=di.location,
                )
                for di in session.basic_list()
            }
        except pipkin.common.ManagementError as e:
            if e.script:
                logger.error("ManagementError.script: %s", e.script)
            if e.out:
                logger.error("ManagementError.out: %s", e.out)
            if e.err:
                logger.error("ManagementError.err: %s", e.err)
            raise
        finally:
            session.close()

    def _delete_sorted_paths(self, paths):
        self._execute_without_output(
            dedent(
                """
            def __thonny_delete(path):
                if __thonny_helper.os.stat(path)[0] & 0o170000 == 0o040000:
                    for name in __thonny_helper.listdir(path):
                        child_path = path + "/" + name
                        __thonny_delete(child_path)
                    __thonny_helper.rmdir(path)
                else:
                    __thonny_helper.os.remove(path)
            
            for __thonny_path in %r: 
                __thonny_delete(__thonny_path)
                
            del __thonny_path
            del __thonny_delete
            
        """
            )
            % paths
        )

    def _get_stat(
        self, path: str
    ) -> Optional[Tuple[int, int, int, int, int, int, int, int, int, int]]:
        if not self._supports_directories():
            func = "size"
        else:
            func = "stat"

        stat = self._evaluate(
            dedent(
                """
            try:
                __thonny_helper.print_mgmt_value(__thonny_helper.os.%s(%r))
            except __thonny_helper.builtins.Exception:
                __thonny_helper.print_mgmt_value(None)
            """
            )
            % (func, path)
        )

        if stat is None:
            return None
        elif isinstance(stat, int):
            return (0b1000000000000000, 0, 0, 0, 0, 0, stat, 0, 0, 0)
        else:
            return stat

    def _cmd_mkdir(self, cmd):
        assert self._supports_directories()
        assert cmd.path.startswith("/")
        assert not cmd.path.startswith("//")
        self._mkdir(cmd.path)

    def _should_present_completion(self, completion: CompletionInfo) -> bool:
        if completion.name.startswith("__"):
            return False

        if completion.module_path is None and completion.type == "module":
            # That's how jedi 0.18 (and maybe later) lists CPython stdlib modules
            return False

        if completion.module_name == "builtins":
            # Jedi's builtins.pyi is pretty good
            return True

        if completion.module_path:
            # if it's in our stubs folder, then it's good
            for path in self._get_sys_path_for_analysis():
                if os.path.normcase(completion.module_path).startswith(os.path.normcase(path)):
                    return True

            # somewhere else, not good
            return False

        return True

    def _get_sys_path_for_analysis(self) -> Optional[List[str]]:
        return [os.path.join(os.path.dirname(__file__), "base_api_stubs")]

    def _join_remote_path_parts(self, left, right):
        if left == "":  # micro:bit
            assert not self._supports_directories()
            return right.strip("/")

        return left.rstrip("/") + "/" + right.strip("/")

    def _get_file_size(self, path: str) -> int:
        stat = self._get_stat(path)
        if stat is None:
            raise OSError("Path '%s' does not exist" % path)

        return stat[STAT_SIZE_INDEX]

    def _get_stat_mode(self, path: str) -> Optional[int]:
        stat = self._get_stat(path)
        if stat is None:
            return None
        return stat[0]

    def _get_path_info(self, path: str) -> Optional[Dict]:
        stat = self._get_stat(path)

        if stat is None:
            return None

        _, basename = unix_dirname_basename(path)
        return self._expand_stat(stat, basename)

    def _get_dir_children_info(
        self, path: str, include_hidden: bool = False
    ) -> Optional[Dict[str, Dict]]:
        """The key of the result dict is simple name"""
        if self._supports_directories():
            raw_data = self._evaluate(
                dedent(
                    """
                __thonny_result = {} 
                try:
                    __thonny_names = __thonny_helper.listdir(%r)
                except __thonny_helper.builtins.OSError:
                    __thonny_helper.print_mgmt_value(None) 
                else:
                    for __thonny_name in __thonny_names:
                        if not __thonny_name.startswith(".") or %r:
                            try:
                                __thonny_result[__thonny_name] = __thonny_helper.os.stat(%r + __thonny_name)
                            except __thonny_helper.builtins.OSError as e:
                                __thonny_result[__thonny_name] = __thonny_helper.builtins.str(e)
                    __thonny_helper.print_mgmt_value(__thonny_result)
            """
                )
                % (path, include_hidden, path.rstrip("/") + "/")
            )
            if raw_data is None:
                return None
        elif path == "":
            # used to represent all files in micro:bit
            raw_data = self._evaluate(
                "{name : __thonny_helper.os.size(name) for name in __thonny_helper.os.listdir()}"
            )
        else:
            return None

        return {name: self._expand_stat(raw_data[name], name) for name in raw_data}

    def handle_connection_error(self, error=None):
        try:
            self._forward_unexpected_output("stderr")
        except:
            logger.warning("Could not forward output", exc_info=True)
        super().handle_connection_error(error)

    def _show_error(self, msg, end="\n"):
        self._send_output(msg + end, "stderr")

    def _replace_last_repl_value_variables(self, source: str) -> str:
        try:
            root = ast.parse(source)
        except SyntaxError:
            return source

        load_nodes = []
        has_store_nodes = False
        for node in ast.walk(root):
            if (
                isinstance(node, ast.arg)
                and node.arg == "_"
                or isinstance(node, ast.Name)
                and node.id == "_"
                and isinstance(node.ctx, ast.Store)
            ):
                has_store_nodes = True
            elif isinstance(node, ast.Name) and node.id == "_" and isinstance(node.ctx, ast.Load):
                load_nodes.append(node)

        if not load_nodes:
            return source

        if load_nodes and has_store_nodes:
            print("WARNING: Could not infer REPL _-variables", file=sys.stderr)
            return source

        lines = source.splitlines(keepends=True)
        for node in reversed(load_nodes):
            lines[node.lineno - 1] = (
                lines[node.lineno - 1][: node.col_offset]
                + "__thonny_helper.builtins.globals().get('_', __thonny_helper.last_non_none_repl_value)"
                + lines[node.lineno - 1][node.col_offset + 1 :]
            )

        new_source = "".join(lines)
        logger.debug("New source with replaced _-s: %r", new_source)
        return new_source

    def _add_expression_statement_handlers(self, source):
        try:
            root = ast.parse(source)

            from thonny.ast_utils import mark_text_ranges

            mark_text_ranges(root, source)
            self._mark_nodes_to_be_guarded_from_instrumentation(root, False)

            expr_stmts = []
            for node in ast.walk(root):
                if isinstance(node, ast.Expr) and not node.guarded:
                    expr_stmts.append(node)

            marker_prefix = "__thonny_helper.print_repl_value("
            marker_suffix = ")"

            lines = source.splitlines(keepends=True)
            for node in reversed(expr_stmts):
                lines[node.end_lineno - 1] = (
                    lines[node.end_lineno - 1][: node.end_col_offset]
                    + marker_suffix
                    + lines[node.end_lineno - 1][node.end_col_offset :]
                )

                lines[node.lineno - 1] = (
                    lines[node.lineno - 1][: node.col_offset]
                    + marker_prefix
                    + lines[node.lineno - 1][node.col_offset :]
                )

            new_source = "".join(lines)
            # make sure it parses
            ast.parse(new_source)
            return new_source
        except SyntaxError:
            return source
        except Exception as e:
            logger.warning("Problem adding Expr handlers", exc_info=e)
            return source

    def _avoid_printing_expression_statements(self, source):
        # temporary solution for https://github.com/thonny/thonny/issues/1441
        try:
            root = ast.parse(source)

            from thonny.ast_utils import mark_text_ranges

            mark_text_ranges(root, source)
            self._mark_nodes_to_be_guarded_from_instrumentation(root, False)

            expr_stmts = []
            for node in ast.walk(root):
                if isinstance(node, ast.Expr) and not node.guarded:
                    expr_stmts.append(node)

            marker_prefix = ""
            marker_suffix = " and None or None"

            lines = source.splitlines(keepends=True)
            for node in reversed(expr_stmts):
                lines[node.end_lineno - 1] = (
                    lines[node.end_lineno - 1][: node.end_col_offset]
                    + marker_suffix
                    + lines[node.end_lineno - 1][node.end_col_offset :]
                )

                lines[node.lineno - 1] = (
                    lines[node.lineno - 1][: node.col_offset]
                    + marker_prefix
                    + lines[node.lineno - 1][node.col_offset :]
                )

            new_source = "".join(lines)
            # make sure it parses
            ast.parse(new_source)
            return new_source
        except SyntaxError:
            return source
        except Exception as e:
            logger.warning("Problem adding Expr handlers", exc_info=e)
            return source

    def _mark_nodes_to_be_guarded_from_instrumentation(self, node, guarded_context):
        if (
            not guarded_context
            and isinstance(node, ast.FunctionDef)
            and node.decorator_list
            and any(self._is_asm_pio_decorator(decorator) for decorator in node.decorator_list)
        ):
            guarded_context = True

        node.guarded = guarded_context

        for child in ast.iter_child_nodes(node):
            self._mark_nodes_to_be_guarded_from_instrumentation(child, guarded_context)

    def _is_asm_pio_decorator(self, node):
        if not isinstance(node, ast.Call):
            return False

        if isinstance(node.func, ast.Attribute) and node.func.attr == "asm_pio":
            return True

        if isinstance(node.func, ast.Name) and node.func.id == "asm_pio":
            return True

        return False

    def _system_time_to_posix_time(self, value: float) -> float:
        result = value + self._get_epoch_offset()
        if self._args["local_rtc"]:
            # convert to UTC
            result += time.timezone

        return result

    def _get_epoch_offset(self) -> int:
        if self._epoch_year == 1970:
            return 0
        elif self._epoch_year == 2000:
            return Y2000_EPOCH_OFFSET
        else:
            raise NotImplementedError()

    def _expand_stat(self, stat: Union[Tuple, int, str], basename: str) -> Dict:
        error = None
        if isinstance(stat, int):
            # file size is only info available for micro:bit files
            size = stat
            modified = None
            kind = "file"
        elif isinstance(stat, str):
            kind = None
            size = None
            modified = None
            error = stat
        else:
            assert isinstance(stat, tuple)
            if stat[STAT_KIND_INDEX] & 0o170000 == 0o040000:
                kind = "dir"
                size = None
            else:
                kind = "file"
                size = stat[STAT_SIZE_INDEX]

            modified = self._system_time_to_posix_time(stat[STAT_MTIME_INDEX])

        result = {
            "kind": kind,
            "size": size,
            "modified": modified,
            "hidden": basename.startswith("."),
        }
        if error:
            result["error"] = error
        return result

    def _decode(self, data: bytes) -> str:
        return data.decode(encoding="UTF-8", errors="replace")

    def _log_management_error_details(self, e):
        logger.error(
            "ManagementError details:\n" + "SCRIPT: %s\n\n" + "STDOUT: %s\n\n" + "STDERR: %s\n\n",
            e.script,
            e.out,
            e.err,
        )


class ProtocolError(RuntimeError):
    pass


class ManagementError(ProtocolError):
    def __init__(self, msg, script, out, err):
        RuntimeError.__init__(self, msg)
        self.script = script
        self.out = out
        self.err = err


def unix_dirname_basename(path):
    if path == "/":
        return ("/", "")

    if "/" not in path:  # micro:bit
        return "", path

    path = path.rstrip("/")
    dir_, file_ = path.rsplit("/", maxsplit=1)
    if dir_ == "":
        dir_ = "/"

    return dir_, file_


def to_remote_path(path):
    return path.replace("\\", "/")


def ends_overlap(left, right) -> int:
    """Returns the length of maximum overlap between end of the first and start of the second"""
    max_overlap = min(len(left), len(right))
    for i in range(max_overlap, 0, -1):
        if left.endswith(right[:i]):
            return i

    return 0


class ReadOnlyFilesystemError(OSError):
    pass


def starts_with_continuation_byte(data):
    return data and is_continuation_byte(data[0])


def is_continuation_byte(byte):
    return (byte & 0b11000000) == 0b10000000


if __name__ == "__main__":
    print(ends_overlap("a", "b"))
    print(ends_overlap(">>>", ">>> "))
    print(ends_overlap("\n>>>", ">>> "))
    print(ends_overlap(">>> ", ">>> "))
    print(ends_overlap(">>> ", ">>>"))
    print(ends_overlap(">", ">>> "))
    print(ends_overlap("", ">>> "))
