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
import io
import logging
import os
import re
import sys
import textwrap
import threading
import time
import traceback
from abc import ABC
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
)
from thonny.plugins.micropython.connection import ConnectionClosedException
from thonny.running import EXPECTED_TERMINATION_CODE

ENCODING = "utf-8"

# Commands
INTERRUPT_CMD = b"\x03"

# Output tokens
VALUE_REPR_START = b"<repr>"
VALUE_REPR_END = b"</repr>"
EOT = b"\x04"
MGMT_VALUE_START = b"\x02"

# first prompt when switching to raw mode (or after soft reboot in raw mode)
# Looks like it's not translatable in CP
# https://github.com/adafruit/circuitpython/blob/master/locale/circuitpython.pot
FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\n>"
FIRST_RAW_PROMPT_SUFFIX = b"\r\n>"

RAW_PROMPT = b">"

# How many seconds to wait for something that should appear quickly.
# In other words -- how long to wait with reporting a protocol error
# (hoping that the required piece is still coming)
WAIT_OR_CRASH_TIMEOUT = 5

SECONDS_IN_YEAR = 60 * 60 * 24 * 365

STAT_KIND_INDEX = 0
STAT_SIZE_INDEX = 6
STAT_MTIME_INDEX = 8

logger = logging.getLogger("thonny.micropython.backend")


def debug(msg):
    return
    # print(msg, file=sys.stderr)


class MicroPythonBackend(MainBackend, ABC):
    def __init__(self, clean, api_stubs_path, cwd=None):

        MainBackend.__init__(self)

        self._prev_time = time.time()

        self._local_cwd = None
        self._cwd = cwd
        self._progress_times = {}
        self._welcome_text = None

        self._api_stubs_path = api_stubs_path

        try:
            self._report_time("before prepare")
            self._prepare(clean)
            self.mainloop()
        except ConnectionClosedException as e:
            self._on_connection_closed(e)
        except ProtocolError as e:
            self._send_output("ProtocolError: %s\n" % (e.message,), "stderr")
            self._send_output("CAPTURED DATA: %s\n" % (e.captured,), "stderr")
        except Exception:
            logger.exception("Crash in backend")
            traceback.print_exc()

    def _prepare(self, clean):
        self._process_until_initial_prompt(clean)

        self._report_time("bef preparing helpers")
        self._prepare_helpers()
        self._report_time("prepared helpers")

        if self._welcome_text is None:
            self._welcome_text = self._fetch_welcome_text()
            self._report_time("got welcome")

        self._update_cwd()
        self._report_time("got cwd")

        if self._welcome_text:
            # not required when a script is run in os_backend
            self._send_ready_message()
            self._report_time("sent ready")

        self._builtin_modules = self._fetch_builtin_modules()
        self._builtins_info = self._fetch_builtins_info()

        self._report_time("prepared")

    def _prepare_helpers(self):
        script = self._get_all_helpers()
        self._execute_without_output(script)

    def _get_all_helpers(self):
        # Can't import functions into class context:
        # https://github.com/micropython/micropython/issues/6198
        return (
            dedent(
                """
            class __thonny_helper:
                import os
                import sys
                
                # for object inspector
                last_repl_values = []
                @classmethod
                def print_repl_value(cls, obj):
                    if obj is not None:
                        cls.last_repl_values.append(obj)
                        cls.last_repl_values = cls.last_repl_values[-{num_values_to_keep}:]
                        print({start_marker!r}, obj, '@', id(obj), {end_marker!r}, sep='')
                
                @staticmethod
                def print_mgmt_value(obj):
                    print({mgmt_marker!r}, repr(obj), sep='', end='')
                    
                @classmethod
                def listdir(cls, x):
                    if hasattr(cls.os, "listdir"):
                        return cls.os.listdir(x)
                    else:
                        return [rec[0] for rec in cls.os.ilistdir(x) if rec[0] not in ('.', '..')]
            """
            ).format(
                num_values_to_keep=self._get_num_values_to_keep(),
                start_marker=OBJECT_LINK_START,
                end_marker=OBJECT_LINK_END,
                mgmt_marker=MGMT_VALUE_START.decode(ENCODING),
            )
            + "\n"
            + textwrap.indent(self._get_custom_helpers(), "    ")
        )

    def _get_custom_helpers(self):
        return ""

    def _get_num_values_to_keep(self):
        """How many last evaluated REPL values and visited Object inspector values to keep
        in internal lists for the purpose of retrieving them by id for Object inspector"""
        return 5

    def _process_until_initial_prompt(self, clean):
        raise NotImplementedError()

    def _perform_idle_tasks(self):
        self._forward_unexpected_output()

    def _handle_user_input(self, msg: InputSubmission) -> None:
        self._submit_input(msg.data)

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        self._soft_reboot(False)

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        if cmd["name"] == "interrupt":
            with self._interrupt_lock:
                # don't interrupt while command or input is being written
                self._write(INTERRUPT_CMD)
                time.sleep(0.1)
                self._write(INTERRUPT_CMD)
                time.sleep(0.1)
                self._write(INTERRUPT_CMD)
                print("sent interrupt")

    def _handle_normal_command(self, cmd: CommandToBackend) -> None:

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
            except SystemExit:
                # Must be caused by Thonny or plugins code
                if isinstance(cmd, ToplevelCommand):
                    traceback.print_exc()
                response = create_error_response(SystemExit=True)
            except UserError as e:
                sys.stderr.write(str(e) + "\n")
                response = create_error_response()
            except KeyboardInterrupt:
                response = create_error_response(error="Interrupted", interrupted=True)
            except ProtocolError as e:
                self._send_output(
                    "THONNY FAILED TO EXECUTE %s (%s)\n" % (cmd.name, e.message), "stderr"
                )
                self._send_output("CAPTURED DATA: %r\n" % e.captured, "stderr")
                self._send_output("TRYING TO RECOVER ...\n", "stderr")
                # TODO: detect when there is no output for long time and suggest interrupt
                self._forward_output_until_active_prompt("stdout")
                response = create_error_response(error=e.message)
            except Exception:
                _report_internal_error()
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

        if "id" in cmd and "command_id" not in response:
            response["command_id"] = cmd["id"]

        debug("cmd: " + str(cmd) + ", respin: " + str(response))
        self.send_message(response)

        self._report_time("after " + cmd.name)

    def _should_keep_going(self) -> bool:
        return self._is_connected()

    def _is_connected(self):
        raise NotImplementedError()

    def _fetch_welcome_text(self):
        raise NotImplementedError()

    def _fetch_builtin_modules(self):
        raise NotImplementedError()

    def _fetch_builtins_info(self):
        """
        for p in self._get_api_stubs_path():
            builtins_file = os.path.join(p, "__builtins__.py")
            if os.path.exists(builtins_file):
                return parse_api_information(builtins_file)
        """
        path = os.path.join(self._api_stubs_path, "builtins.py")
        if os.path.exists(path):
            return parse_api_information(path)
        else:
            return {}

    def _update_cwd(self):
        if "micro:bit" not in self._welcome_text.lower():
            self._cwd = self._evaluate("__thonny_helper.getcwd()")

    def _send_ready_message(self):
        self.send_message(ToplevelResponse(welcome_text=self._welcome_text, cwd=self._cwd))

    def _soft_reboot(self, side_command):
        raise NotImplementedError()

    def _write(self, data):
        raise NotImplementedError()

    def _submit_input(self, cdata: str) -> None:
        raise NotImplementedError()

    def send_message(self, msg):
        if "cwd" not in msg:
            msg["cwd"] = self._cwd

        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()

    def _send_error_message(self, msg):
        self._send_output("\n" + msg + "\n", "stderr")

    def _execute(self, script, capture_output=False) -> Tuple[str, str]:
        if capture_output:
            output_lists = {"stdout": [], "stderr": []}

            def consume_output(data, stream_name):
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
        Otherwise raises ProtocolError.
        
        The execution may block. In this case the user should do something (eg. provide
        required input or issue an interrupt). The UI should remind the interrupt in case
        of Thonny commands.
        """
        raise NotImplementedError()

    def _execute_without_output(self, script):
        """Meant for management tasks."""
        out, err = self._execute(script, capture_output=True)
        if out or err:
            self._handle_bad_output(script, out, err)

    def _evaluate(self, script):
        """Evaluate the output of the script or raise ProtocolError, if anything looks wrong.
        
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
            return self._handle_bad_output(script, out, err)

        if MGMT_VALUE_START.decode(ENCODING) not in out:
            return self._handle_bad_output(script, out, err)

        side_effects, value_str = out.rsplit(MGMT_VALUE_START.decode(ENCODING), maxsplit=1)
        if side_effects:
            logging.getLogger("thonny").warning(
                "Unexpected output from MP evaluate:\n" + side_effects + "\nSCRIPT:\n" + script
            )

        try:
            return ast.literal_eval(value_str)
        except SyntaxError:
            return self._handle_bad_output(script, out, err)

    def _forward_output_until_active_prompt(self, output_consumer, stream_name="stdout"):
        """Used for finding initial prompt or forwarding problematic output 
        in case of protocol errors"""
        raise NotImplementedError()

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
                self._submit_input(EOT.decode())
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
        """Only for %run $EDITOR_CONTENT. Clean runs will be handled differently."""
        # TODO: clear last object inspector requests dictionary
        if cmd.get("source"):
            self._execute(cmd.source, capture_output=False)
            self._update_cwd()
        return {}

    def _cmd_execute_source(self, cmd):
        # TODO: clear last object inspector requests dictionary
        if cmd.source:
            source = self._add_expression_statement_handlers(cmd.source)
            self._execute(source, capture_output=False)
            self._update_cwd()
        # TODO: assign last value to _
        return {}

    def _cmd_execute_system_command(self, cmd):
        raise NotImplementedError()

    def _cmd_get_globals(self, cmd):
        if cmd.module_name == "__main__":
            globs = self._evaluate(
                "{name : repr(value) for (name, value) in globals().items() if not name.startswith('__')}"
            )
        else:
            globs = self._evaluate(
                dedent(
                    """
                import %s as __mod_for_globs
                __thonny_helper.print_mgmt_value(
                    {name : repr(getattr(__mod_for_globs, name)) 
                        in dir(__mod_for_globs) 
                        if not name.startswith('__')}
                )
                del __mod_for_globs
            """
                )
            )
        return {"module_name": cmd.module_name, "globals": globs}

    def _cmd_get_fs_info(self, cmd):
        raise NotImplementedError()

    def _cmd_delete(self, cmd):
        assert cmd.paths
        self._delete_sorted_paths(sorted(cmd.paths, key=len, reverse=True))

    def _mkdir(self, path: str) -> None:
        # assumes part path exists and path doesn't
        self._execute("__thonny_helper.os.mkdir(%r)" % path)

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
        self._mkdir(cmd.path)

    def _cmd_editor_autocomplete(self, cmd):
        # template for the response
        result = dict(source=cmd.source, row=cmd.row, column=cmd.column)

        try:
            import jedi

            script = jedi.Script(cmd.source, cmd.row, cmd.column, sys_path=[self._api_stubs_path])
            completions = script.completions()
            result["completions"] = self._filter_completions(completions)
        except Exception:
            traceback.print_exc()
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
                import jedi

                # at the moment I'm assuming source is the code before cursor, not whole input
                lines = source.split("\n")
                script = jedi.Script(
                    source, len(lines), len(lines[-1]), sys_path=[self._api_stubs_path]
                )
                completions = script.completions()
                response["completions"] = self._filter_completions(completions)
            except Exception:
                traceback.print_exc()
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

    def _get_dir_children_info(self, path: str) -> Optional[Dict[str, Dict]]:
        """The key of the result dict is simple name"""
        if self._supports_directories():
            raw_data = self._evaluate(
                dedent(
                    """
                __thonny_result = {} 
                try:
                    __thonny_names = __thonny_helper.os.listdir(%r)
                except OSError:
                    __thonny_helper.print_mgmt_value(None) 
                else:
                    for __thonny_name in __thonny_names:
                        try:
                            __thonny_result[__thonny_name] = __thonny_helper.os.stat(%r + __thonny_name)
                        except OSError as e:
                            __thonny_result[__thonny_name] = str(e)
                    __thonny_helper.print_mgmt_value(__thonny_result)
            """
                )
                % (path, path.rstrip("/") + "/")
            )
            if raw_data is None:
                return None
        elif path == "":
            # used to represent all files in micro:bit
            raw_data = self._evaluate(
                "{name : __thonny_helper.os.size(name) for name in __thonny_helper.os.listdir(%r)}"
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

    def _handle_bad_output(self, script, out, err):
        self._show_error("PROBLEM WITH INTERNAL MANAGEMENT COMMAND\n")
        self._show_error("COMMAND:\n" + script + "\n")
        self._show_error("STDOUT:\n" + out + "\n")
        self._show_error("STDERR:\n" + err + "\n")

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
        except Exception:
            logging.getLogger("thonny").exception("Problem adding Expr handlers")
            return source

    def _report_time(self, caption):
        new_time = time.time()
        # print("TIME %s: %.3f" % (caption, new_time - self._prev_time))
        self._prev_time = new_time

    def _system_time_to_posix_time(self, value: float) -> float:
        return value + self._get_epoch_offset()

    def _get_epoch_offset(self) -> int:
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


class ProtocolError(Exception):
    def __init__(self, message, captured):
        Exception.__init__(self, message)
        self.message = message
        self.captured = captured


class ExecutionError(Exception):
    pass


def _report_internal_error():
    print("PROBLEM WITH THONNY'S BACK-END:\n", file=sys.stderr)
    traceback.print_exc()


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


def ends_overlap(left, right):
    """Returns whether the left ends with one of the non-empty prefixes of the right"""
    for i in range(1, min(len(left), len(right)) + 1):
        if left.endswith(right[:i]):
            return True

    return False


class ReadOnlyFilesystemError(RuntimeError):
    pass
