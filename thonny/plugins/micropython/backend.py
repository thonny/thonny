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

from thonny.common import (
    InputSubmission,
    InterruptCommand,
    EOFCommand,
    parse_message,
    ToplevelCommand,
    ToplevelResponse,
    InlineCommand,
    InlineResponse,
    UserError,
    serialize_message,
    BackendEvent,
    OBJECT_LINK_START,
    OBJECT_LINK_END,
)
import sys
import logging
import traceback
import queue
from thonny.plugins.micropython.connection import ConnectionClosedException
from textwrap import dedent
import ast
import re
from queue import Queue, Empty
import threading
import os
import time
import io
from thonny.running import EXPECTED_TERMINATION_CODE
from threading import Lock

ENCODING = "utf-8"

# Commands
INTERRUPT_CMD = b"\x03"

# Output tokens
VALUE_REPR_START = b"<repr>"
VALUE_REPR_END = b"</repr>"
EOT = b"\x04"
LAST_RESULT_NAME = "__last_thonny_repl_value__"

# first prompt when switching to raw mode (or after soft reboot in raw mode)
# Looks like it's not translatable in CP
# https://github.com/adafruit/circuitpython/blob/master/locale/circuitpython.pot
FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\n>"
FIRST_RAW_PROMPT_SUFFIX = b"\r\n>"

RAW_PROMPT = b">"

# How many seconds to wait for something that should appear quickly.
# In other words -- how long to wait with reporting a protocol error
# (hoping that the required piece is still coming)
WAIT_OR_CRASH_TIMEOUT = 3

SECONDS_IN_YEAR = 60 * 60 * 24 * 365

logger = logging.getLogger("thonny.micropython.backend")


def debug(msg):
    return
    print(msg, file=sys.stderr)


class MicroPythonBackend:
    def __init__(self, connection, clean, api_stubs_path):
        self._connection = connection
        self._local_cwd = None
        self._cwd = None
        self._command_queue = Queue()  # populated by reader thread
        self._progress_times = {}

        self._api_stubs_path = api_stubs_path

        self._command_reading_thread = threading.Thread(target=self._read_commands, daemon=True)
        self._command_reading_thread.start()

        self._writing_lock = Lock()

        try:
            self._prepare(clean)
            self._mainloop()
        except ConnectionClosedException as e:
            self._on_connection_closed(e)
        except Exception:
            logger.exception("Crash in backend")
            traceback.print_exc()

    def _prepare(self, clean):
        self._process_until_initial_prompt(clean)
        self._prepare_helpers()
        self._cwd = self._fetch_cwd()
        self._welcome_text = self._fetch_welcome_text()
        self._builtin_modules = self._fetch_builtin_modules()
        self._builtins_info = self._fetch_builtins_info()

        self._send_ready_message()

    def _prepare_helpers(self):
        self._execute(
            dedent(
                """
            class __thonny_helper:
                import os
                import sys
                
                try:
                    from os import listdir
                except ImportError:
                    @staticmethod
                    def listdir(x):
                        return [rec[0] for rec in os.listdir() if rec[0] not in ('.', '..')]
                
                try:
                    from os import chdir
                    from os import getcwd
                except ImportError:
                    
        """
            )
        )

    def _process_until_initial_prompt(self, clean):
        raise NotImplementedError()

    def _mainloop(self):
        while True:
            self._check_for_connection_errors()
            try:
                cmd = self._command_queue.get(timeout=0.1)
            except Empty:
                # No command in queue, but maybe a thread produced output meanwhile
                # or the user resetted the device
                self._forward_unexpected_output()
                continue

            if isinstance(cmd, InputSubmission):
                self._submit_input(cmd.data)
            elif isinstance(cmd, EOFCommand):
                self._soft_reboot(False)
            else:
                self.handle_command(cmd)

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

    def _fetch_cwd(self):
        raise NotImplementedError()

    def _send_ready_message(self):
        self.send_message(ToplevelResponse(welcome_text=self._welcome_text, cwd=self._cwd))

    def _check_send_inline_progress(self, cmd, value, maximum, description=None):
        assert "id" in cmd
        prev_time = self._progress_times.get(cmd["id"], 0)
        if value != maximum and time.time() - prev_time < 0.2:
            # Don't notify too often
            return
        else:
            self._progress_times[cmd["id"]] = time.time()

        if description is None:
            description = cmd.get("description", "Working...")

        self.send_message(
            BackendEvent(
                event_type="InlineProgress",
                command_id=cmd["id"],
                value=value,
                maximum=maximum,
                description=description,
            )
        )

    def _soft_reboot(self, side_command):
        raise NotImplementedError()

    def _read_commands(self):
        "works in separate thread"

        while True:
            line = sys.stdin.readline()
            if line == "":
                logger.info("Read stdin EOF")
                sys.exit()
            cmd = parse_message(line)
            if isinstance(cmd, InterruptCommand):
                # This is a priority command and will be handled right away
                self._interrupt_in_command_reading_thread()
            else:
                self._command_queue.put(cmd)

    def _interrupt_in_command_reading_thread(self):
        with self._writing_lock:
            # don't interrupt while command or input is being written
            self._connection.write(INTERRUPT_CMD)
            time.sleep(0.1)
            self._connection.write(INTERRUPT_CMD)
            time.sleep(0.1)
            self._connection.write(INTERRUPT_CMD)
            print("sent interrupt")

    def handle_command(self, cmd):
        assert isinstance(cmd, (ToplevelCommand, InlineCommand))

        if "local_cwd" in cmd:
            self._local_cwd = cmd["local_cwd"]

        def create_error_response(**kw):
            if not "error" in kw:
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

    def _submit_input(self, cdata: str) -> None:
        # TODO: what if there is a previous unused data waiting
        assert self._connection.outgoing_is_empty()

        assert cdata.endswith("\n")
        if not cdata.endswith("\r\n"):
            # submission is done with CRLF
            cdata = cdata[:-1] + "\r\n"

        bdata = cdata.encode(ENCODING)

        with self._writing_lock:
            self._connection.write(bdata)
            # Try to consume the echo

            try:
                echo = self._connection.read(len(bdata))
            except queue.Empty:
                # leave it.
                logging.warning("Timeout when reading input echo")
                return

        if echo != bdata:
            # because of autoreload? timing problems? interruption?
            # Leave it.
            logging.warning("Unexpected echo. Expected %s, got %s" % (bdata, echo))
            self._connection.unread(echo)

    def send_message(self, msg):
        if "cwd" not in msg:
            msg["cwd"] = self._cwd

        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()

    def _send_output(self, data, stream_name):
        if not data:
            return

        if isinstance(data, bytes):
            data = data.decode(ENCODING, errors="replace")

        data = self._transform_output(data)
        msg = BackendEvent(event_type="ProgramOutput", stream_name=stream_name, data=data)
        self.send_message(msg)

    def _send_error_message(self, msg):
        self._send_output("\n" + msg + "\n", "stderr")

    def _transform_output(self, data):
        return data

    def _execute(self, script, timeout, capture):
        """Ensures prompt and submits the script.
        Reads (and doesn't return) until next active prompt or connection error.
        
        If capture is False, then forwards output incrementally. Otherwise
        returns (out, err) if there are no problems, ie. all parts of the 
        output are present and it reaches active prompt.
        Otherwise raises ProtocolError.
        
        The execution may block. In this case the user should do something (eg. provide
        required input or issue an interrupt). The UI should remind the interrupt in case
        of Thonny commands.
        """
        raise NotImplementedError()

    def _execute_without_errors(self, script):
        """Meant for management tasks. stdout will be unexpected but tolerated.
        stderr will cause exception"""
        result = self._evaluate("True", prelude=script)
        assert result is True

    def _evaluate_to_repr(self, expr, prelude="", cleanup="", timeout=SECONDS_IN_YEAR):
        """Uses REPL to evaluate and print the repr of given expression.
        
        Side effects before printing the repr always get forwarded.
        Returns the repr only if everything goes according to the plan.
        Raises ProtocolError if anything looks fishy.
        """
        script = ""
        if prelude:
            script += prelude + "\n"
        script += "print(%r, repr(%s), sep='', end=%r)" % (
            (EOT + VALUE_REPR_START).decode(),
            expr,
            VALUE_REPR_END.decode(),
        )
        if cleanup:
            script += "\n" + cleanup

        stdout, value_repr, err = self._execute(script, timeout=timeout, capture_stdout=False)

        assert not stdout

        if value_repr is None:
            raise ProtocolError("Could not find value repr", err)
        elif err:
            raise ProtocolError(
                "Evaluated with errors",
                EOT + VALUE_REPR_START + value_repr + VALUE_REPR_END + EOT + err,
            )
        else:
            return value_repr

    def _execute_and_capture_output(self, script, timeout=5):
        """Executes script in raw repl, captures stdout and consumes terminators.
        Returns stdout if everything goes well. 
        Raises ProtocolError if anything looks fishy.
        """
        stdout, value_repr, err = self._execute(script, timeout=timeout, capture_stdout=True)

        if value_repr is not None:
            raise ProtocolError(
                "Unexpected value repr",
                stdout + EOT + VALUE_REPR_START + value_repr + VALUE_REPR_END + EOT + err,
            )
        elif err:
            raise ProtocolError("Captured output with errors", stdout + EOT + err)
        else:
            return stdout

    def _evaluate(self, expr, prelude="", cleanup=""):
        value_repr = self._evaluate_to_repr(expr, prelude, cleanup)
        return ast.literal_eval(value_repr)

    def _forward_output_until_active_prompt(self, stream_name="stdout"):
        """Used for finding initial prompt or forwarding problematic output 
        in case of protocol errors"""
        raise NotImplementedError()

    def _forward_unexpected_output(self, stream_name="stdout"):
        "Invoked between commands"
        raise NotImplementedError()

    def _check_for_side_commands(self):
        # most likely the queue is empty
        if self._command_queue.empty():
            return

        postponed = []
        while not self._command_queue.empty():
            cmd = self._command_queue.get()
            if isinstance(cmd, InputSubmission):
                self._submit_input(cmd.data)
            elif isinstance(cmd, EOFCommand):
                self._soft_reboot(True)
            else:
                postponed.append(cmd)

        # put back postponed commands
        while postponed:
            self._command_queue.put(postponed.pop(0))

    def _supports_directories(self):
        # NB! make sure self._cwd is queried first
        return bool(self._cwd)

    def _cmd_cd(self, cmd):
        raise NotImplementedError()

    def _cmd_Run(self, cmd):
        """Only for %run $EDITOR_CONTENT. Clean runs will be handled differently."""
        # TODO: clear last object inspector requests dictionary
        assert cmd.get("source")
        self._execute(cmd.source, timeout=SECONDS_IN_YEAR, capture_stdout=False)        
        return {}

    def _cmd_execute_source(self, cmd):
        # TODO: clear last object inspector requests dictionary
        source = self._add_expression_statement_handlers(cmd.source)
        self._execute(source, timeout=SECONDS_IN_YEAR, capture_stdout=False)
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
                "{name : repr(getattr(__mod_for_globs, name)) in dir(__mod_for_globs) if not name.startswith('__')}",
                prelude="import %s as __mod_for_globs",
            )
        return {"module_name": cmd.module_name, "globals": globs}

    def _cmd_get_dirs_child_data(self, cmd):
        data = self._get_dirs_child_data_generic(cmd["paths"])
        dir_separator = "/"
        return {"node_id": cmd["node_id"], "dir_separator": dir_separator, "data": data}

    def _cmd_get_fs_info(self, cmd):
        raise NotImplementedError()

    def _cmd_write_file(self, cmd):
        raise NotImplementedError()

    def _cmd_delete(self, cmd):
        raise NotImplementedError()

    def _cmd_read_file(self, cmd):
        raise NotImplementedError()

    def _cmd_download(self, cmd):
        total_size = 0
        completed_files_size = 0
        remote_files = self._list_remote_files_with_info(cmd["source_paths"])
        target_dir = cmd["target_dir"].rstrip("/").rstrip("\\")

        download_items = []
        for file in remote_files:
            total_size += file["size"]
            # compute filenames (and subdirs) in target_dir
            # relative to the context of the user selected items
            assert file["path"].startswith(file["original_context"])
            path_suffix = file["path"][len(file["original_context"]) :].strip("/").strip("\\")
            target_path = os.path.join(target_dir, os.path.normpath(path_suffix))
            download_items.append(dict(source=file["path"], target=target_path, size=file["size"]))

        if not cmd["allow_overwrite"]:
            targets = [item["target"] for item in download_items]
            existing_files = list(filter(os.path.exists, targets))
            if existing_files:
                return {
                    "existing_files": existing_files,
                    "source_paths": cmd["source_paths"],
                    "target_dir": cmd["target_dir"],
                    "description": cmd["description"],
                }

        def notify(current_file_progress):
            self._check_send_inline_progress(
                cmd, completed_files_size + current_file_progress, total_size
            )

        # replace the indeterminate progressbar with determinate as soon as possible
        notify(0)

        for item in download_items:
            written_bytes = self._download_file(item["source"], item["target"], notify)
            assert written_bytes == item["size"]
            completed_files_size += item["size"]

    def _cmd_upload(self, cmd):
        completed_files_size = 0
        local_files = self._list_local_files_with_info(cmd["source_paths"])
        target_dir = cmd["target_dir"]
        assert target_dir.startswith("/") or not self._supports_directories()
        assert not target_dir.endswith("/") or target_dir == "/"

        upload_items = []
        for file in local_files:
            # compute filenames (and subdirs) in target_dir
            # relative to the context of the user selected items
            assert file["path"].startswith(file["original_context"])
            path_suffix = file["path"][len(file["original_context"]) :].strip("/").strip("\\")
            target_path = self._join_remote_path_parts(target_dir, to_remote_path(path_suffix))
            upload_items.append(dict(source=file["path"], target=target_path, size=file["size"]))

        if not cmd["allow_overwrite"]:
            targets = [item["target"] for item in upload_items]
            existing_files = self._get_existing_remote_files(targets)
            if existing_files:
                return {
                    "existing_files": existing_files,
                    "source_paths": cmd["source_paths"],
                    "target_dir": cmd["target_dir"],
                    "description": cmd["description"],
                }

        total_size = sum([item["size"] for item in upload_items])

        def notify(current_file_progress):
            self._check_send_inline_progress(
                cmd, completed_files_size + current_file_progress, total_size
            )

        # replace the indeterminate progressbar with determinate as soon as possible
        notify(0)

        for item in upload_items:
            written_bytes = self._upload_file(item["source"], item["target"], notify)
            assert written_bytes == item["size"]
            completed_files_size += item["size"]

    def _cmd_mkdir(self, cmd):
        raise NotImplementedError()

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
                        "dir({}) if '{}' in locals() or '{}' in globals() else []".format(
                            obj, obj, obj
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

        self._execute_without_errors(
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
        self._execute_without_errors("import {0}".format(module_name))

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
            self._send_text_to_shell("  * " + name + " : " + typ, "stdout")

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

    def _list_local_files_with_info(self, paths):
        def rec_list_with_size(path):
            result = {}
            if os.path.isfile(path):
                result[path] = os.path.getsize(path)
            elif os.path.isdir(path):
                for name in os.listdir(path):
                    result.update(rec_list_with_size(os.path.join(path, name)))
            else:
                raise RuntimeError("Can't process " + path)

            return result

        result = []
        for requested_path in paths:
            sizes = rec_list_with_size(requested_path)
            for path in sizes:
                result.append(
                    {
                        "path": path,
                        "size": sizes[path],
                        "original_context": os.path.dirname(requested_path),
                    }
                )

        result.sort(key=lambda rec: rec["path"])
        return result

    def _list_remote_files_with_info(self, paths):
        # prepare universal functions
        self._execute_without_errors(
            dedent(
                """
            try:
                import os as __thonny_os
                from os import stat as __thonny_stat
                
                def __thonny_getsize(path):
                    return __thonny_stat(path)[6]
                
                def __thonny_isdir(path):
                    return __thonny_stat(path)[0] & 0o170000 == 0o040000
                    
            except ImportError:
                __thonny_stat = None
                # micro:bit
                from os import size as __thonny_getsize
                
                def __thonny_isdir(path):
                    return False
        """
            )
        )

        self._execute_without_errors(
            dedent(
                """
            def __thonny_rec_list_with_size(path):
                result = {}
                if __thonny_isdir(path):
                    for name in __thonny_os.listdir(path):
                        result.update(__thonny_rec_list_with_size(path + "/" + name))
                else:
                    result[path] = __thonny_getsize(path)
    
                return result
        """
            )
        )

        result = []
        for requested_path in paths:
            sizes = self._evaluate("__thonny_rec_list_with_size(%r)" % requested_path)
            for path in sizes:
                result.append(
                    {
                        "path": path,
                        "size": sizes[path],
                        "original_context": os.path.dirname(requested_path),
                    }
                )

        result.sort(key=lambda rec: rec["path"])

        self._execute_without_errors(
            dedent(
                """
                del __thonny_os
                del __thonny_stat
                del __thonny_getsize
                del __thonny_isdir
                del __thonny_rec_list_with_size
            """
            )
        )
        return result

    def _get_existing_remote_files(self, paths):
        if self._supports_directories():
            func = "stat"
        else:
            func = "size"

        return self._evaluate(
            "__thonny_result",
            prelude=dedent(
                """
                import os as __thonny_os
                __thonny_result = []
                for __thonny_path in %r:
                    try:
                        __thonny_os.%s(__thonny_path)
                        __thonny_result.append(__thonny_path)
                    except OSError:
                        pass
                """
            )
            % (paths, func),
            cleanup=dedent(
                """
                del __thonny_os
                del __thonny_result
                del __thonny_path
                """
            ),
        )

    def _join_remote_path_parts(self, left, right):
        if left == "":  # micro:bit
            assert not self._supports_directories()
            return right.strip("/")

        return left.rstrip("/") + "/" + right.strip("/")

    def _get_file_size(self, path):
        return self._evaluate("__thonny_os.stat(%r)[6]" % path, prelude="import os as __thonny_os")

    def _upload_file(self, source, target, notifier):
        raise NotImplementedError()

    def _download_file(self, source, target, notifier=None):
        raise NotImplementedError()

    def _get_dirs_child_data_generic(self, paths):
        return self._evaluate(
            "__thonny_result",
            prelude=dedent(
                """
                import os as __thonny_os
                # Init all vars, so that they can be deleted
                # even if the loop makes no iterations
                __thonny_result = {}
                __thonny_path = None
                __thonny_st = None 
                __thonny_child_names = None
                __thonny_children = None
                __thonny_name = None
                __thonny_real_path = None
                __thonny_full = None
                
                for __thonny_path in %(paths)r:
                    __thonny_real_path = __thonny_path or '/'
                    try:
                        __thonny_child_names = __thonny_os.listdir(__thonny_real_path)
                    except OSError:
                        # probably deleted directory
                        __thonny_children = None
                    else:
                        __thonny_children = {}
                        for __thonny_name in __thonny_child_names:
                            if __thonny_name.startswith('.') or __thonny_name == "System Volume Information":
                                continue
                            __thonny_full = (__thonny_real_path + '/' + __thonny_name).replace("//", "/")
                            try:
                                __thonny_st = __thonny_os.stat(__thonny_full)
                                if __thonny_st[0] & 0o170000 == 0o040000:
                                    # directory
                                    __thonny_children[__thonny_name] = {"kind" : "dir", "size" : None}
                                else:
                                    __thonny_children[__thonny_name] = {"kind" : "file", "size" :__thonny_st[6]}
                                
                                # converting from 2000-01-01 epoch to Unix epoch 
                                __thonny_children[__thonny_name]["time"] = max(__thonny_st[8], __thonny_st[9]) + 946684800
                            except OverflowError:
                                # Probably "System Volume Information" in trinket
                                # https://github.com/thonny/thonny/issues/923
                                pass
                            
                    __thonny_result[__thonny_path] = __thonny_children                            
            """
            )
            % {"paths": paths},
            cleanup=dedent(
                """
                del __thonny_os
                del __thonny_st
                del __thonny_children
                del __thonny_name
                del __thonny_path
                del __thonny_full
                del __thonny_result
                del __thonny_real_path
            """
            ),
        )

    def _check_for_connection_errors(self):
        self._connection._check_for_error()

    def _on_connection_closed(self, error=None):
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

            temp_name = "__thonny_value__"
            marker_prefix = (
                "[globals().__setitem__({result_name!r}, {temp_name})"
                " or print({start_marker!r} + {temp_name} + '@' + str(id({temp_name})) + {end_marker!r})"
                " for {temp_name} in ["
            ).format(
                result_name=LAST_RESULT_NAME,
                temp_name=temp_name,
                start_marker=OBJECT_LINK_START,
                end_marker=OBJECT_LINK_END,
            )

            marker_suffix = "] if {temp_name} is not None]".format(temp_name=temp_name)

            lines = source.splitlines(keepends=True)
            for node in reversed(expr_stmts):
                lines[node.lineno] = (
                    lines[node.lineno][: node.col_offset]
                    + marker_prefix
                    + lines[node.lineno][node.col_offset :]
                )
                lines[node.end_lineno] = (
                    lines[node.end_lineno][: node.end_col_offset]
                    + marker_suffix
                    + lines[node.end_lineno][node.end_col_offset :]
                )
            
            new_source = "".join(lines)
            # make sure it parses
            ast.parse(new_source)
            return new_source
        except Exception:
            logging.getLogger("thonny").exception("Problem adding Expr handlers")
            return source


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


def linux_dirname_basename(path):
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


class ReadOnlyFilesystemError(RuntimeError):
    pass
