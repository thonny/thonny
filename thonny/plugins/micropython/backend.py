"""
MP 1.12

>>> import uos
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
import logging
import os
import re
import sys
import textwrap
import threading
import time
import traceback
from abc import ABC, abstractmethod
from queue import Empty, Queue
from textwrap import dedent
from threading import Lock
from typing import Optional, Dict, Union, Tuple, List

from thonny.backend import MainBackend
from thonny.common import (
    OBJECT_LINK_END,
    OBJECT_LINK_START,
    BackendEvent,
    EOFCommand,
    InlineCommand,
    InlineResponse,
    InputSubmission,
    ImmediateCommand,
    ToplevelCommand,
    ToplevelResponse,
    UserError,
    parse_message,
    serialize_message,
    MessageFromBackend,
    Record,
    CommandToBackend,
    ValueInfo,
)
from thonny.common import ConnectionClosedException
from thonny.running import EXPECTED_TERMINATION_CODE

ENCODING = "utf-8"

# Commands
INTERRUPT_CMD = b"\x03"

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


logger = logging.getLogger(__name__)


def debug(msg):
    return
    # print(msg, file=sys.stderr)


class MicroPythonBackend(MainBackend, ABC):
    def __init__(self, clean, args):
        self._args = args
        self._prev_time = time.time()
        self._local_cwd = None
        self._cwd = args.get("cwd")
        self._progress_times = {}
        self._welcome_text = None
        self._sys_path = None
        self._epoch_year = None
        self._builtin_modules = []
        self._api_stubs_path = args.get("api_stubs_path")
        self._builtins_info = self._fetch_builtins_info()

        MainBackend.__init__(self)
        try:
            self._report_time("before prepare")
            self._process_until_initial_prompt(clean)
            if self._welcome_text is None:
                self._welcome_text = self._fetch_welcome_text()
                self._report_time("got welcome")

            self._prepare_after_soft_reboot(clean)

            if not self._builtin_modules:
                self._builtin_modules = self._fetch_builtin_modules()
                logger.debug("Built-in modules: %s", self._builtin_modules)

            self._prepare_rtc()
            self._send_ready_message()
            self._report_time("sent ready")
            self.mainloop()
        except ConnectionClosedException as e:
            self._on_connection_closed(e)
        except Exception:
            logger.exception("Crash in backend")

    def _prepare_after_soft_reboot(self, clean=False):
        self._report_time("bef preparing helpers")
        script = self._get_all_helpers()
        self._check_perform_just_in_case_gc()
        self._execute_without_output(script)
        self._report_time("prepared helpers")

        self._update_cwd()
        self._report_time("got cwd")
        self._sys_path = self._fetch_sys_path()

        self._report_time("prepared")
        self._check_perform_just_in_case_gc()
        logger.info("Prepared")

    def _prepare_rtc(self):
        if self._epoch_year is None:
            self._epoch_year = self._fetch_epoch_year()

        self._check_sync_time()
        if self._args.get("validate_time"):
            self._validate_time()

    def _check_perform_just_in_case_gc(self):
        if self._connected_to_microbit():
            # May fail to allocate memory without this
            self._perform_gc()

    def _check_sync_time(self):
        if self._args.get("sync_time"):
            self._sync_time()

    def _perform_gc(self):
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

    def _get_all_helpers(self):
        # Can't import functions into class context:
        # https://github.com/micropython/micropython/issues/6198
        return (
            dedent(
                """
            class __thonny_helper:
                try:
                    import uos as os
                except ImportError:
                    import os
                import sys
                import builtins
                
                # for object inspector
                inspector_values = dict()
                @classmethod
                def print_repl_value(cls, obj):
                    global _
                    if obj is not None:
                        cls.builtins.print({start_marker!r} % id(obj), repr(obj), {end_marker!r}, sep='')
                        _ = obj
                
                @classmethod
                def print_mgmt_value(cls, obj):
                    cls.builtins.print({mgmt_start!r}, repr(obj), {mgmt_end!r}, sep='', end='')
                    
                @staticmethod
                def repr(obj):
                    try:
                        s = repr(obj)
                        if len(s) > 50:
                            s = s[:50] + "..."
                        return s
                    except Exception as e:
                        return "<could not serialize: " + str(e) + ">"
                    
                @classmethod
                def listdir(cls, x):
                    if hasattr(cls.os, "listdir"):
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
            + textwrap.indent(self._get_custom_helpers(), "    ")
        )

    def _get_custom_helpers(self):
        return ""

    def _sync_time(self):
        raise NotImplementedError()

    def _get_time_for_rtc(self):
        if self._args["utc_clock"]:
            return datetime.datetime.now(tz=datetime.timezone.utc).timetuple()
        else:
            return datetime.datetime.now().timetuple()

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

    def _process_until_initial_prompt(self, clean):
        raise NotImplementedError()

    def _perform_idle_tasks(self):
        self._forward_unexpected_output()

    def _handle_user_input(self, msg: InputSubmission) -> None:
        self._submit_input(msg.data)

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        raise NotImplementedError()

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        if cmd["name"] == "interrupt":
            # don't interrupt while command or input is being written
            with self._interrupt_lock:
                if self._current_command:
                    self._current_command.interrupted = True
                self._write(INTERRUPT_CMD)
                time.sleep(0.1)
                self._write(INTERRUPT_CMD)
                time.sleep(0.1)
                self._write(INTERRUPT_CMD)

    def _handle_normal_command(self, cmd: CommandToBackend) -> None:
        logger.info("Handling command '%s'", cmd.name)
        self._report_time("before " + cmd.name)
        assert isinstance(cmd, (ToplevelCommand, InlineCommand))

        if "local_cwd" in cmd:
            self._local_cwd = cmd["local_cwd"]

        def create_error_response(**kw):
            if "error" not in kw:
                kw["error"] = traceback.format_exc()

            if isinstance(cmd, ToplevelCommand):
                return ToplevelResponse(command_name=cmd.name, **kw)
            else:
                return InlineResponse(command_name=cmd.name, **kw)

        handler = getattr(self, "_cmd_" + cmd.name, None)

        if handler is None:
            response = create_error_response(error="Unknown command: " + cmd.name)
        else:
            try:
                response = handler(cmd)
            except SystemExit as e:
                # Must be caused by Thonny or plugins code
                if isinstance(cmd, ToplevelCommand):
                    logger.exception("Unexpected SystemExit", exc_info=e)
                response = create_error_response(SystemExit=True)
            except UserError as e:
                sys.stderr.write(str(e) + "\n")
                response = create_error_response()
            except KeyboardInterrupt:
                response = create_error_response(error="Interrupted", interrupted=True)
            except ConnectionClosedException as e:
                self._on_connection_closed(e)
            except ManagementError as e:
                logger.info("Caught ManagementError", exc_info=e)
                if "KeyboardInterrupt" in e.err:
                    response = create_error_response(error="Interrupted", interrupted=True)
                else:
                    self._show_error("\nNB! Thonny could not execute '%s'." % cmd.name)
                    # traceback.print_exc() # I'll know the trace from command
                    if self._management_error_is_not_thonnys_fault(e):
                        self._show_error(
                            (
                                "It looks like %s has arrived to an unexpected state"
                                " or there have been communication problems."
                                " See Thonny's backend.log for more information."
                            )
                            % (
                                "CircuitPython"
                                if self._connected_to_circuitpython()
                                else "MicroPython"
                            )
                        )
                    else:
                        self._show_error("\n")
                        self._show_error("SCRIPT:\n" + e.script + "\n")
                        self._show_error("STDOUT:\n" + e.out + "\n")
                        self._show_error("STDERR:\n" + e.err + "\n")

                    self._show_error(
                        "You may need to reconnect, Stop/Restart or hard-reset your device.\n"
                    )
                    response = create_error_response(error="ManagementError")
            except Exception as e:
                _report_internal_error(e)
                response = create_error_response(context_info="other unhandled exception")

        if response is None:
            response = {}

        if response is False:
            # Command doesn't want to send any response
            return

        elif isinstance(response, dict):
            if isinstance(cmd, ToplevelCommand):
                response = ToplevelResponse(command_name=cmd.name, **response)
            elif isinstance(cmd, InlineCommand):
                response = InlineResponse(cmd.name, **response)

        debug("cmd: " + str(cmd) + ", respin: " + str(response))
        self.send_message(self._prepare_command_response(response, cmd))

        self._check_perform_just_in_case_gc()

        self._report_time("after " + cmd.name)

    def _should_keep_going(self) -> bool:
        return self._is_connected()

    def _is_connected(self) -> bool:
        raise NotImplementedError()

    def _connected_to_microbit(self):
        return "micro:bit" in self._welcome_text.lower()

    def _connected_to_pyboard(self):
        return "pyb" in self._welcome_text.lower() or "pyb" in self._builtin_modules

    def _connected_to_circuitpython(self):
        return "circuitpython" in self._welcome_text.lower()

    def _connected_to_pycom(self):
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

    def _fetch_builtins_info(self):
        result = {}

        for name in ["builtins.py", "builtins.pyi"]:
            path = os.path.join(self._api_stubs_path, name)
            if os.path.exists(path):
                result = parse_api_information(path)

        return result

    def _fetch_epoch_year(self):
        if self._connected_to_microbit():
            return None

        # The proper solution would be to query time.gmtime, but most devices don't have this function.
        # Luckily, time.localtime is good enough for deducing 1970 vs 2000 epoch.

        # Most obvious solution would be to query for 0-time, but CP doesn't support anything below Y2000,
        # so I'm querying this and adjusting later.
        val = self._evaluate(
            dedent(
                """
            try:
                from time import localtime as __thonny_localtime
                __thonny_helper.print_mgmt_value(tuple(__thonny_localtime(%d)))
                del __thonny_localtime
            except Exception as e:
                __thonny_helper.print_mgmt_value(str(e))
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
        if not self._connected_to_microbit():
            self._cwd = self._evaluate("__thonny_helper.getcwd()")

    def _send_ready_message(self):
        args = dict(cwd=self._cwd)
        args["welcome_text"] = self._welcome_text

        self.send_message(ToplevelResponse(**args))

    def _write(self, data):
        raise NotImplementedError()

    def _submit_input(self, cdata: str) -> None:
        raise NotImplementedError()

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
            raise ManagementError(script, out, err)

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
        if (
            err
            or MGMT_VALUE_START.decode(ENCODING) not in out
            or MGMT_VALUE_END.decode(ENCODING) not in out
        ):
            raise ManagementError(script, out, err)

        start_token_pos = out.index(MGMT_VALUE_START.decode(ENCODING))
        end_token_pos = out.index(MGMT_VALUE_END.decode(ENCODING))

        # a thread or IRQ handler may have written something before or after mgmt value
        prefix = out[:start_token_pos]
        value_str = out[start_token_pos + len(MGMT_VALUE_START) : end_token_pos]
        suffix = out[end_token_pos + len(MGMT_VALUE_END) :]

        try:
            value = ast.literal_eval(value_str)
            self._send_output(prefix, "stdout")
            self._send_output(suffix, "stdout")
            return value
        except SyntaxError:
            raise ManagementError(script, out, err)

    def _forward_unexpected_output(self, stream_name="stdout"):
        "Invoked between commands"
        raise NotImplementedError()

    def _management_error_is_not_thonnys_fault(self, e):
        outerr = ""
        if e.out:
            outerr += e.out
        if e.err:
            outerr += e.err
        # https://github.com/micropython/micropython/issues/7171
        # https://github.com/micropython/micropython/issues/6899
        return (
            "NameError: name '__thonny_helper' isn't defined" in outerr
            or "SyntaxError" in outerr
            or "IndentationError" in outerr
            or "UnicodeDecodeError" in outerr
        )

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
                self._write(b"\x04")
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
            self._report_time("befexeccc")
            self._execute(source, capture_output=False)
            self._check_prepare()
            self._report_time("affexeccc")
        # TODO: assign last value to _
        return {}

    def _cmd_execute_system_command(self, cmd):
        raise NotImplementedError()

    def _cmd_get_globals(self, cmd):
        if cmd.module_name == "__main__":
            globs = self._evaluate(
                "{name : (__thonny_helper.repr(value), id(value)) for (name, value) in globals().items() if not name.startswith('__')}"
            )
        else:
            globs = self._evaluate(
                dedent(
                    """
                import %s as __mod_for_globs
                __thonny_helper.print_mgmt_value(
                    {name : (__thonny_helper.repr(getattr(__mod_for_globs, name)), 
                             id(getattr(__mod_for_globs, name)))
                        in dir(__mod_for_globs) 
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

        info.update(self._get_object_info_extras(type_name))
        if cmd.include_attributes:
            info["attributes"] = self._get_object_attributes(cmd.all_attributes)

        # need to keep the reference corresponding to object_id so that it can be later found as next context object
        # remove non-relevant items
        # TODO: add back links
        # relevant = set([cmd.object_id] + cmd.back_links + cmd.forward_links)
        self._execute(
            dedent(
                """
                if id(__thonny_helper.object_info) not in __thonny_helper.inspector_values:
                    __thonny_helper.inspector_values[id(__thonny_helper.object_info)] = __thonny_helper.object_info
            """
            )
        )

        return {"id": cmd.object_id, "info": info}

    def _find_basic_object_info(self, object_id, context_id):
        """If object is found then returns basic info and leaves object reference
        to __thonny_helper.object_info.

        Can't leave it in a global object, because when querying globals(),
        repr(globals()) would cause inifite recursion."""

        result = self._evaluate(
            dedent(
                """
                for __thonny_helper.object_info in (
                        list(globals().values()) 
                        + list(__thonny_helper.inspector_values.values())):
                    if id(__thonny_helper.object_info) == %d:
                        __thonny_helper.print_mgmt_value({
                            "repr" : repr(__thonny_helper.object_info),
                            "type": str(type(__thonny_helper.object_info))
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
                         getattr(__thonny_helper.context_value, name)
                         for name in dir(__thonny_helper.context_value)
                    ]
                    if isinstance(__thonny_helper.context_value, (set, tuple, list)):
                        __thonny_helper.context_children += list(__thonny_helper.context_value)
                    elif isinstance(__thonny_helper.context_value, dict):
                        __thonny_helper.context_children += list(__thonny_helper.context_value.values())
                    
                    for __thonny_helper.object_info in __thonny_helper.context_children:
                        if id(__thonny_helper.object_info) == %d:
                            __thonny_helper.print_mgmt_value({
                                "repr" : __thonny_helper.repr(__thonny_helper.object_info),
                                "type": str(type(__thonny_helper.object_info))
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
        """object is given in __thonny_helper.object_info """
        atts = self._evaluate(
            "{name : ("
            "   id(getattr(__thonny_helper.object_info, name)),"
            "    __thonny_helper.repr(getattr(__thonny_helper.object_info, name))"
            ") for name in dir(__thonny_helper.object_info)}"
        )
        return {
            name: ValueInfo(atts[name][0], atts[name][1])
            for name in atts
            if not name.startswith("__") or all_attributes
        }

    def _get_object_info_extras(self, type_name):
        """object is given in __thonny_helper.object_info """
        if type_name in ("list", "tuple", "set"):
            items = self._evaluate(
                "[(id(x), __thonny_helper.repr(x)) for x in __thonny_helper.object_info]"
            )
            return {"elements": [ValueInfo(x[0], x[1]) for x in items]}
        elif type_name == "dict":
            items = self._evaluate(
                "[((id(key), __thonny_helper.repr(key)), (id(__thonny_helper.object_info[key]), "
                "__thonny_helper.repr(__thonny_helper.object_info[key]))) for key in __thonny_helper.object_info]"
            )
            return {
                "entries": [
                    (ValueInfo(x[0][0], x[0][1]), ValueInfo(x[1][0], x[1][1])) for x in items
                ]
            }
        else:
            return {}

    def _cmd_delete(self, cmd):
        assert cmd.paths
        self._delete_sorted_paths(sorted(cmd.paths, key=len, reverse=True))

    def _cmd_get_active_distributions(self, cmd):
        try:
            dists = {}
            for path in self._get_library_paths():
                children = self._get_dir_children_info(path)
                if children is None:
                    continue
                for name, info in children.items():
                    if info["kind"] == "dir":
                        key = name
                    elif name.endswith(".py"):
                        key = name[:-3]
                    elif name.endswith(".mpy"):
                        key = name[:-4]
                    else:
                        continue

                    dists[key] = {
                        "project_name": key,
                        "key": key,
                        "guessed_pypi_name": self._guess_package_pypi_name(key),
                        "location": path,
                        "version": "n/a",
                    }

            return dict(
                distributions=dists,
                usersitepackages=None,
            )
        except Exception:
            return InlineResponse("get_active_distributions", error=traceback.format_exc())

    def _cmd_get_module_info(self, cmd):
        location = None
        effective_items = []
        shadowed_items = []

        for lib_dir in self._get_library_paths():
            dir_children = self._get_dir_children_info(lib_dir)
            if not dir_children:
                continue

            # print(lib_dir, dir_children)

            if cmd.module_name in dir_children and dir_children[cmd.module_name]["kind"] == "dir":
                # dir takes precedence over .py and .mpy
                # presence of __init__.py is not required
                dir_full_path = lib_dir + "/" + cmd.module_name
                descendants = self._get_dir_descendants_info(dir_full_path)
                # print("desc", dir_full_path, descendants)
                desc_paths = list(sorted(descendants.keys()))

                if not effective_items:  # ie. it's the first one found
                    effective_items.append(dir_full_path)
                    effective_items.extend(desc_paths)
                    location = lib_dir
                else:
                    shadowed_items.extend(desc_paths)

            for suffix in [".py", ".mpy"]:
                with_suffix = cmd.module_name + suffix
                if with_suffix in dir_children and dir_children[with_suffix]["kind"] == "file":
                    full_path = lib_dir + "/" + with_suffix
                    if not effective_items:
                        effective_items.append(full_path)
                        location = lib_dir
                    else:
                        shadowed_items.append(full_path)

        return {
            "location": location,
            "effective_items": effective_items,
            "shadowed_items": shadowed_items,
            "module_name": cmd.module_name,
        }

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
            except Exception:
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

    def _cmd_editor_autocomplete(self, cmd):
        # template for the response
        result = dict(source=cmd.source, row=cmd.row, column=cmd.column)

        try:
            from thonny import jedi_utils

            completions = jedi_utils.get_script_completions(
                cmd.source,
                cmd.row,
                cmd.column,
                filename=cmd.filename,
                sys_path=[self._api_stubs_path],
            )
            result["completions"] = self._filter_completions(completions)
        except Exception as e:
            logger.exception("Problem with editor autocomplete", exc_info=e)
            result["error"] = "Autocomplete error"

        return result

    def _filter_completions(self, completions):
        # filter out completions not applicable to MicroPython
        result = []
        for completion in completions:
            if completion.name.startswith("__"):
                continue

            if completion.parent() and completion.full_name:
                parent_name = completion.parent().name
                name = completion.name
                root = completion.full_name.split(".")[0]

                # jedi proposes names from CPython builtins
                if root in self._builtins_info and name not in self._builtins_info[root]:
                    continue

                if parent_name == "builtins" and name not in self._builtins_info:
                    continue

            result.append({"name": completion.name, "complete": completion.complete})

        return result

    def _cmd_shell_autocomplete(self, cmd):
        source = cmd.source

        # TODO: combine dynamic results and jedi results
        if source.strip().startswith("import ") or source.strip().startswith("from "):
            # this needs the power of jedi
            response = {"source": cmd.source}

            try:
                from thonny import jedi_utils

                # at the moment I'm assuming source is the code before cursor, not whole input
                lines = source.split("\n")
                completions = jedi_utils.get_script_completions(
                    source, len(lines), len(lines[-1]), "<shell>", sys_path=[self._api_stubs_path]
                )
                response["completions"] = self._filter_completions(completions)
            except Exception as e:
                logger.exception("Problem with shell autocomplete", exc_info=e)
                response["error"] = "Autocomplete error"

            return response
        else:
            # use live data
            match = re.search(
                r"(\w+\.)*(\w+)?$", source
            )  # https://github.com/takluyver/ubit_kernel/blob/master/ubit_kernel/kernel.py
            if match:
                prefix = match.group()
                if "." in prefix:
                    obj, prefix = prefix.rsplit(".", 1)
                    names = self._evaluate(
                        "dir({obj}) if '{obj}' in locals() or '{obj}' in globals() else []".format(
                            obj=obj
                        )
                    )
                else:
                    names = self._evaluate("dir()")
            else:
                names = []
                prefix = ""

            completions = []

            # prevent TypeError (iterating over None)
            names = names if names else []

            for name in names:
                if name.startswith(prefix) and not name.startswith("__"):
                    completions.append({"name": name, "complete": name[len(prefix) :]})

            return {"completions": completions, "source": source}

    def _cmd_dump_api_info(self, cmd):
        "For use during development of the plug-in"

        self._execute_without_output(
            dedent(
                """
            def __get_object_atts(obj):
                result = []
                errors = []
                for name in dir(obj):
                    try:
                        val = getattr(obj, name)
                        result.append((name, repr(val), repr(type(val))))
                    except BaseException as e:
                        errors.append("Couldn't get attr '%s' from object '%r', Err: %r" % (name, obj, e))
                return (result, errors)
        """
            )
        )

        for module_name in sorted(self._fetch_builtin_modules()):
            if (
                not module_name.startswith("_")
                and not module_name.startswith("adafruit")
                # and not module_name == "builtins"
            ):
                file_name = os.path.join(
                    self._api_stubs_path, module_name.replace(".", "/") + ".py"
                )
                self._dump_module_stubs(module_name, file_name)

    def _dump_module_stubs(self, module_name, file_name):
        self._execute_without_output("import {0}".format(module_name))

        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with io.open(file_name, "w", encoding="utf-8", newline="\n") as fp:
            if module_name not in [
                "webrepl",
                "_webrepl",
                "gc",
                "http_client",
                "http_client_ssl",
                "http_server",
                "framebuf",
                "example_pub_button",
                "flashbdev",
            ]:
                self._dump_object_stubs(fp, module_name, "")

    def _dump_object_stubs(self, fp, object_expr, indent):
        if object_expr in [
            "docs.conf",
            "pulseio.PWMOut",
            "adafruit_hid",
            "upysh",
            # "webrepl",
            # "gc",
            # "http_client",
            # "http_server",
        ]:
            print("SKIPPING problematic name:", object_expr)
            return

        print("DUMPING", indent, object_expr)
        items, errors = self._evaluate("__get_object_atts({0})".format(object_expr))

        if errors:
            print("ERRORS", errors)

        for name, rep, typ in sorted(items, key=lambda x: x[0]):
            if name.startswith("__"):
                continue

            print("DUMPING", indent, object_expr, name)
            print("  * " + name + " : " + typ)

            if typ in ["<class 'function'>", "<class 'bound_method'>"]:
                fp.write(indent + "def " + name + "():\n")
                fp.write(indent + "    pass\n\n")
            elif typ in ["<class 'str'>", "<class 'int'>", "<class 'float'>"]:
                fp.write(indent + name + " = " + rep + "\n")
            elif typ == "<class 'type'>" and indent == "":
                # full expansion only on toplevel
                fp.write("\n")
                fp.write(indent + "class " + name + ":\n")  # What about superclass?
                fp.write(indent + "    ''\n")
                self._dump_object_stubs(fp, "{0}.{1}".format(object_expr, name), indent + "    ")
            else:
                # keep only the name
                fp.write(indent + name + " = None\n")

    def _join_remote_path_parts(self, left, right):
        if left == "":  # micro:bit
            assert not self._supports_directories()
            return right.strip("/")

        return left.rstrip("/") + "/" + right.strip("/")

    def _get_file_size(self, path: str) -> int:
        stat = self._get_stat(path)
        if stat is None:
            raise RuntimeError("Path '%s' does not exist" % path)

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
                except OSError:
                    __thonny_helper.print_mgmt_value(None) 
                else:
                    for __thonny_name in __thonny_names:
                        if not __thonny_name.startswith(".") or %r:
                            try:
                                __thonny_result[__thonny_name] = __thonny_helper.os.stat(%r + __thonny_name)
                            except OSError as e:
                                __thonny_result[__thonny_name] = str(e)
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

    def _on_connection_closed(self, error=None):
        self._forward_unexpected_output("stderr")
        message = "Connection lost"
        if error:
            message += " (" + str(error) + ")"
        self._send_output("\n" + message + "\n", "stderr")
        self._send_output("\n" + "Use Stop/Restart to reconnect." + "\n", "stderr")
        sys.exit(EXPECTED_TERMINATION_CODE)

    def _show_error(self, msg):
        self._send_output(msg + "\n", "stderr")

    def _add_expression_statement_handlers(self, source):
        try:
            root = ast.parse(source)

            from thonny.ast_utils import mark_text_ranges

            mark_text_ranges(root, source)

            expr_stmts = []
            for node in ast.walk(root):
                if isinstance(node, ast.Expr):
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

            expr_stmts = []
            for node in ast.walk(root):
                if isinstance(node, ast.Expr):
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

    def _report_time(self, caption):
        new_time = time.time()
        # print("TIME %s: %.3f" % (caption, new_time - self._prev_time))
        self._prev_time = new_time

    def _system_time_to_posix_time(self, value: float) -> float:
        result = value + self._get_epoch_offset()
        if not self._args["utc_clock"]:
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


class ManagementError(RuntimeError):
    def __init__(self, script, out, err):
        msg = (
            "Problem with a management command\n\n"
            + "SCRIPT:\n"
            + script
            + "\n\n"
            + "STDOUT:\n"
            + out
            + "\n\n"
            + "STDERR:\n"
            + err
            + "\n\n"
        )

        RuntimeError.__init__(self, msg)
        self.script = script
        self.out = out
        self.err = err


def _report_internal_error(exception=None):
    logger.exception("PROBLEM WITH THONNY'S BACK-END:", exc_info=exception)


def parse_api_information(file_path):
    import tokenize

    with tokenize.open(file_path) as fp:
        source = fp.read()

    tree = ast.parse(source)

    defs = {}

    # TODO: read also docstrings ?

    for toplevel_item in tree.body:
        if isinstance(toplevel_item, ast.ClassDef):
            class_name = toplevel_item.name
            member_names = []
            for item in toplevel_item.body:
                if isinstance(item, ast.FunctionDef):
                    member_names.append(item.name)
                elif isinstance(item, ast.Assign):
                    # TODO: check Python 3.4
                    "TODO: item.targets[0].id"

            defs[class_name] = member_names

    return defs


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


class ReadOnlyFilesystemError(RuntimeError):
    pass


if __name__ == "__main__":
    print(ends_overlap("a", "b"))
    print(ends_overlap(">>>", ">>> "))
    print(ends_overlap("\n>>>", ">>> "))
    print(ends_overlap(">>> ", ">>> "))
    print(ends_overlap(">>> ", ">>>"))
    print(ends_overlap(">", ">>> "))
    print(ends_overlap("", ">>> "))
