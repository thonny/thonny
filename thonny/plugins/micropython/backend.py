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
    ValueInfo,
)
import sys
import logging
import traceback
import queue
from thonny.plugins.micropython.connection import (
    ConnectionClosedException,
    ConnectionFailedException,
)
from textwrap import dedent
import ast
import re
from queue import Queue, Empty
import threading
import os
import time
from thonny.misc_utils import find_volumes_by_name
import jedi
import io
import tokenize
from thonny.running import EXPECTED_TERMINATION_CODE

BAUDRATE = 115200
ENCODING = "utf-8"

# Commands
RAW_MODE_CMD = b"\x01"
NORMAL_MODE_CMD = b"\x02"
INTERRUPT_CMD = b"\x03"
SOFT_REBOOT_CMD = b"\x04"

# Output tokens
THONNY_MSG_START = b"\x02"
THONNY_MSG_END = b"\x04"
EOT = b"\x04"
NORMAL_PROMPT = b">>> "
LF = b"\n"
OK = b"OK"

# first prompt when switching to raw mode (or after soft reboot in raw mode)
# Looks like it's not translatable in CP
# https://github.com/adafruit/circuitpython/blob/master/locale/circuitpython.pot
FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\n>"

RAW_PROMPT = b">"

BLOCK_CLOSERS = re.compile(
    b"|".join(map(re.escape, [LF, EOT, THONNY_MSG_START, NORMAL_PROMPT, FIRST_RAW_PROMPT]))
)


logger = logging.getLogger("thonny.micropython.backend")


def debug(msg):
    return
    print(msg, file=sys.stderr)


class MicroPythonBackend:
    def __init__(self, connection, clean, api_stubs_path):
        self._connection = connection
        self._cwd = None
        self._command_queue = Queue()  # populated by reader thread

        self._api_stubs_path = api_stubs_path

        self._command_reading_thread = threading.Thread(target=self._read_commands, daemon=True)
        self._command_reading_thread.start()

        self._startup_time = time.time()
        self._ctrl_suggestion_given = False

        try:
            self._prepare(clean)
            self._mainloop()
        except ConnectionClosedException:
            self._on_connection_closed()
        except Exception:
            logger.exception("Crash in backend")
            traceback.print_exc()

    def _prepare(self, clean):
        if clean:
            self._interrupt_to_raw_prompt()
            self._clear_environment()
        else:
            self._process_until_initial_raw_prompt()

        self._cwd = self._fetch_cwd()
        self._welcome_text = self._fetch_welcome_text()
        self._builtin_modules = self._fetch_builtin_modules()
        self._builtins_info = self._fetch_builtins_info()

        self._send_ready_message()

    def _mainloop(self):
        while True:
            try:
                self._check_for_connection_errors()
                cmd = self._command_queue.get(timeout=0.1)
                if isinstance(cmd, InputSubmission):
                    self._submit_input(cmd.data)
                elif isinstance(cmd, EOFCommand):
                    self._soft_reboot(False)
                elif isinstance(cmd, InterruptCommand):
                    self._interrupt()
                else:
                    self.handle_command(cmd)
            except Empty:
                self._check_for_idle_events()
            except KeyboardInterrupt:
                self._interrupt()

    def _fetch_welcome_text(self):
        self._connection.write(NORMAL_MODE_CMD)
        welcome_text = self._connection.read_until(NORMAL_PROMPT).strip(b"\r\n >")
        if os.name != "nt":
            welcome_text = welcome_text.replace(b"\r\n", b"\n")

        # Go back to raw prompt
        self._connection.write(RAW_MODE_CMD)
        self._connection.read_until(FIRST_RAW_PROMPT)

        return welcome_text.decode(ENCODING)

    def _fetch_uname(self):
        res = self._evaluate("__module_os.uname()", prelude="import os as __module_os")
        return {
            "sysname": res[0],
            "nodename": res[1],
            "release": res[2],
            "version": res[3],
            "machine": res[4],
        }

    def _fetch_builtin_modules(self):
        out, err, _ = self._execute("help('modules')", capture_output=True)
        assert not err, "Error was: %r" % err

        modules_str_lines = out.strip().splitlines()

        last_line = modules_str_lines[-1].strip()
        if last_line.count(" ") > 0 and "  " not in last_line and "\t" not in last_line:
            # probably something like "plus any modules on the filesystem"
            # (can be in different languages)
            modules_str_lines = modules_str_lines[:-1]

        modules_str = (
            " ".join(modules_str_lines)
            .replace("/__init__", "")
            .replace("__main__", "")
            .replace("/", ".")
        )

        return modules_str.split()

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
        return self._evaluate(
            "__module_os.getcwd() if hasattr(__module_os, 'getcwd') else None",
            prelude="import os as __module_os",
        )

    def _send_ready_message(self):
        self.send_message(ToplevelResponse(welcome_text=self._welcome_text, cwd=self._cwd))

    def _interrupt(self):
        self._connection.write(INTERRUPT_CMD)

    def _interrupt_to_raw_prompt(self):
        # NB! Sometimes disconnecting and reconnecting (on macOS?)
        # too quickly causes anomalies. See CalliopeMiniProxy for more details

        discarded_bytes = b""

        for delay in [0.05, 0.5, 0.1, 2.0]:
            # Interrupt several times, because with some drivers first interrupts seem to vanish
            self._connection.reset_output_buffer()
            self._connection.write(INTERRUPT_CMD)
            self._connection.write(RAW_MODE_CMD)
            time.sleep(delay)
            discarded_bytes += self._connection.read_all()
            if discarded_bytes.endswith(FIRST_RAW_PROMPT) or discarded_bytes.endswith(b"\r\n>"):
                break
        else:
            raise TimeoutError("Can't get to raw prompt. Read bytes: " + str(discarded_bytes))

    def _soft_reboot(self, side_command):
        if side_command:
            self._interrupt_to_raw_prompt()

        # Need to go to normal mode. MP doesn't run user code in raw mode
        # (CP does, but it doesn't hurt to do it there as well)
        self._connection.write(NORMAL_MODE_CMD)
        self._connection.read_until(NORMAL_PROMPT)

        self._connection.write(SOFT_REBOOT_CMD)

        if not side_command:
            self._process_until_raw_prompt()
            self.send_message(ToplevelResponse(cwd=self._cwd))

    def _read_commands(self):
        "works in separate thread"

        while True:
            line = sys.stdin.readline()
            if line == "":
                logger.info("Read stdin EOF")
                sys.exit()
            cmd = parse_message(line)
            self._command_queue.put(cmd)

    def handle_command(self, cmd):
        assert isinstance(cmd, (ToplevelCommand, InlineCommand))

        def create_error_response(**kw):
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
                response = create_error_response(user_exception=self._prepare_user_exception())
            except Exception:
                _report_internal_error()
                response = create_error_response(context_info="other unhandled exception")

        if response is False:
            # Command doesn't want to send any response
            return

        elif isinstance(response, dict):
            if isinstance(cmd, ToplevelCommand):
                response = ToplevelResponse(command_name=cmd.name, **response)
            elif isinstance(cmd, InlineCommand):
                response = InlineResponse(cmd.name, **response)

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

        self._connection.write(bdata)
        # Try to consume the echo

        try:
            echo = self._connection.read(len(bdata))
        except queue.Empty:
            # leave it.
            logging.warning("Timeout when reading echo")
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
        data = self._transform_output(data)
        msg = BackendEvent(event_type="ProgramOutput", stream_name=stream_name, data=data)
        self.send_message(msg)

    def _transform_output(self, data):
        # Any keypress wouldn't work
        return data.replace(
            "Press any key to enter the REPL. Use CTRL-D to reload.",
            "Press Ctrl-C to enter the REPL. Use CTRL-D to reload.",
        )

    def _execute(self, script, capture_output=False):
        # self._ensure_raw_propmt()

        # send command
        self._connection.write(script.encode(ENCODING) + EOT)
        debug("Wrote " + script + "\n--------\n")

        # fetch command confirmation
        ok = self._connection.read(2)
        debug("GOTOK")
        assert ok == OK, "Expected OK, got %r, followed by %r" % (ok, self._connection.read_all())
        return self._process_until_raw_prompt(capture_output)

    def _execute_print_expr(self, expr, prelude="", cleanup="", capture_output=False):
        # assuming expr really contains an expression
        # separator is for separating side-effect output and printed value
        script = ""
        if prelude:
            script += prelude + "\n"
        script += "print(%r, repr(%s), sep='', end=%r)" % (
            THONNY_MSG_START.decode(),
            expr,
            THONNY_MSG_END.decode(),
        )

        # assuming cleanup doesn't cause output
        if cleanup:
            script += "\n" + cleanup

        return self._execute(script, capture_output)

    def _evaluate(self, expr, prelude="", cleanup=""):
        _, _, value_repr = self._execute_print_expr(expr, prelude, cleanup)
        debug("GOTVALUE")
        if value_repr is None:
            return None
        else:
            return ast.literal_eval(value_repr)

    def _process_until_initial_raw_prompt(self):
        self._connection.write(RAW_MODE_CMD)
        try:
            self._process_until_raw_prompt()
        except KeyboardInterrupt:
            self._interrupt()

    def _process_until_raw_prompt(self, capture_output=False):
        """
        Forwards output, extracts Thonny message, replaces normal prompts with raw prompts.
        
        This is executed when some code is running or just after requesting raw prompt.
        
        After submitting commands to the raw REPL, the output should be like
        {stdout}\x04\{stderr}\x04\n\>
        In the end of {stdout} there may be \x02{value-for-thonny}
        
        Interrupts will alter the execution, but from the response parsing
        perspective they don't matter as they look like any other exception.
        
        Things get complicated because of soft-reboots, which always end with
        regular prompt. Soft-reboots can occur because of Ctrl+D, machine.soft_reset()
        and even reset button (micro:bit).
        
        Because of soft-reboot we can't assume we'll find the terminating markers for 
        each command.
        
        Output produced by background threads (eg. in WiPy ESP32) cause even more difficulties, 
        because it becomes impossible to say whether we are at prompt and output
        is from another thread or the main thread is running.
        For now I'm ignoring these problems and assume all output comes from the main thread.
         
        """
        # TODO: experiment with Ctrl+C, Ctrl+D, reset
        eot_count = 0
        value = None
        done = False
        output = b""
        out = b""
        err = b""
        debug("proura")
        while not done:
            if (
                self._connection.num_bytes_received == 0
                and not self._ctrl_suggestion_given
                and time.time() - self._startup_time > 1.5
            ):
                self._send_output(
                    "\n"
                    + "Device is busy or does not respond. Your options:\n\n"
                    + "  - check the connection properties;\n"
                    + "  - make sure the device has suitable firmware;\n"
                    + "  - make sure the device is not in bootloader mode;\n"
                    + "  - wait until current work is complete;\n"
                    + "  - use Ctrl+C to interrupt current work.\n",
                    "stderr",
                )
                self._ctrl_suggestion_given = True

            # There may be an input submission waiting
            # and we can't progress without resolving it first
            self._check_for_side_commands()

            # Process input in chunks (max 1 parsing marker per chunk).
            # Prefer whole lines (to reduce the number of events),
            # but don't wait too long for eol.
            output += self._connection.soft_read_until(BLOCK_CLOSERS, timeout=0.05)
            stream_name = "stderr" if eot_count == 1 else "stdout"

            if output.endswith(THONNY_MSG_START):
                debug("MSGSTA: " + str(output))
                output = output[: -len(THONNY_MSG_START)]

                # Low chance of failure (eg. because of precisely timed reboot),
                # therefore it's safe to use big timeout
                temp = self._connection.soft_read_until(THONNY_MSG_END, timeout=3)
                if temp.endswith(THONNY_MSG_END):
                    value = temp[: -len(THONNY_MSG_END)]
                    debug("GOTVALUE: " + str(value))
                else:
                    # failure, restore everything to help diagnosis
                    output = output + THONNY_MSG_START + temp

            elif output.endswith(EOT):
                debug("EOT: " + str(output))
                output = output[: -len(EOT)]
                eot_count += 1
                if eot_count == 2:
                    # Normal completion of the command
                    # big chance of being at the raw prompt
                    temp = self._connection.soft_read_until(RAW_PROMPT, timeout=0.1)
                    if temp == RAW_PROMPT and self._connection.incoming_is_empty():
                        done = True
                    elif temp:
                        # Failure, temp needs to be parsed again
                        self._connection.unread(temp)

            elif output.endswith(FIRST_RAW_PROMPT) and self._connection.incoming_is_empty():
                debug("FIRAPRO: " + str(output))
                output = output[: -len(FIRST_RAW_PROMPT)]
                done = True

            elif (
                output.endswith(NORMAL_PROMPT)
                and self._connection.peek_incoming() == b"\r\n" + FIRST_RAW_PROMPT
            ):
                debug("NOPRO: " + str(output))
                output = output + self._connection.read_until(FIRST_RAW_PROMPT)
                # skip both normal and raw prompt together
                # (otherwise they get processed separately)
                output = output[: -len(NORMAL_PROMPT + b"\r\n" + FIRST_RAW_PROMPT)]
                done = True

            elif output.endswith(NORMAL_PROMPT) and self._connection.incoming_is_empty():
                debug("NOPRO2: " + str(output))
                output = output[: -len(NORMAL_PROMPT)]
                # switch to raw mode and continue
                self._connection.write(RAW_MODE_CMD)

            if output.endswith(FIRST_RAW_PROMPT[:-1]):
                # incomplete raw prompt, wait for more
                pass
            else:
                if capture_output:
                    if stream_name == "stdout":
                        out += output
                    else:
                        assert stream_name == "stderr"
                        err += output
                else:
                    # TODO: deal with partial UTF-8 chars
                    self._send_output(output.decode(ENCODING), stream_name)
                output = b""

        debug("doneproc")
        return (
            out.decode(ENCODING),
            err.decode(ENCODING),
            None if value is None else value.decode(ENCODING),
        )

    def _clear_environment(self):
        # TODO: Ctrl+D in raw repl is perfect for MicroPython
        # but on CircuitPython it runs main.py

        # TODO: which is better:
        # self._execute_async(dedent("""
        #    for name in globals():
        #        if not name.startswith("__"):
        #            del globals()[name]
        # """).strip())
        # or
        self._execute("globals().clear(); __name__ = '__main__'")

    def _check_for_side_commands(self):
        # TODO: do interrupts in reading thread
        # most likely the queue is empty
        if self._command_queue.empty():
            return

        postponed = []
        while not self._command_queue.empty():
            cmd = self._command_queue.get()
            if isinstance(cmd, InputSubmission):
                self._submit_input(cmd.data)
            elif isinstance(cmd, InterruptCommand):
                self._interrupt()
            elif isinstance(cmd, EOFCommand):
                self._soft_reboot(True)
            else:
                postponed.append(cmd)

        # put back postponed commands
        while postponed:
            self._command_queue.put(postponed.pop(0))

    def _check_for_idle_events(self):
        self._send_output(self._connection.read_all().decode(ENCODING, "replace"), "stdout")
        self._check_for_connection_errors()

    def _supports_directories(self):
        # NB! make sure self._cwd is queried first
        return self._cwd is not None

    def _cmd_interrupt(self, cmd):
        self._interrupt()

    def _cmd_cd(self, cmd):
        if len(cmd.args) == 1:
            if not self._supports_directories():
                raise UserError("This device doesn't have directories")

            path = cmd.args[0]
            self._execute("import os as __module_os; __module_os.chdir(%r)" % path)
            self._cwd = self._fetch_cwd()
            return {}
        else:
            raise UserError("%cd takes one parameter")

    def _cmd_Run(self, cmd):
        self._clear_environment()
        assert cmd.get("source")
        self._execute(cmd["source"])
        return {}

    def _cmd_execute_source(self, cmd):
        try:
            # Try to parse as expression
            ast.parse(cmd.source, mode="eval")
            # If it didn't fail then source is an expression
            _, _, value_repr = self._execute_print_expr(cmd.source)
            if value_repr is None:
                value_repr = repr(None)
            return {"value_info": ValueInfo(0, value_repr)}
        except SyntaxError:
            # source is a statement (or invalid syntax)
            self._execute(cmd.source)
            return {}

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
        if "micro:bit" in self._welcome_text.lower():
            data = self._get_dirs_child_data_microbit(cmd)
            dir_separator = ""
        else:
            data = self._get_dirs_child_data_generic(cmd)
            dir_separator = "/"

        return {"node_id": cmd["node_id"], "dir_separator": dir_separator, "data": data}

    def _cmd_write_file(self, cmd):
        mount_name = self._get_fs_mount_name()
        if mount_name is not None:
            # CircuitPython devices only allow writing via mount,
            # other mounted devices may show outdated data in mount
            # when written via serial.
            self._write_file_via_mount(cmd)
        else:
            self._write_file_via_serial(cmd)

        return InlineResponse(
            command_name="write_file", path=cmd["path"], editor_id=cmd.get("editor_id")
        )

    def _write_file_via_mount(self, cmd):
        # TODO: should be done async in background process

        flash_prefix = self._get_flash_prefix()
        if cmd["path"].startswith(flash_prefix):
            path_suffix = cmd["path"][len(flash_prefix) :]
        elif cmd["path"].startswith("/"):
            path_suffix = cmd["path"][1:]
        else:
            # something like micro:bit but with mounted fs
            path_suffix

        target_path = os.path.join(self._get_fs_mount(), path_suffix)
        with open(target_path, "wb") as f:
            f.write(cmd["content_bytes"])
            f.flush()
            os.fsync(f)

    def _write_file_via_serial(self, cmd):
        data = cmd["content_bytes"]

        # Don't create too long commands
        BUFFER_SIZE = 512

        # prelude
        out, err, __ = self._execute(
            dedent(
                """
            __temp_path = '{path}'
            __temp_f = open(__temp_path, 'wb')
            __temp_written = 0
            """
            ).format(path=cmd["path"]),
            capture_output=True,
        )

        if out:
            self._send_output(out, "stdout")
        if err:
            self._send_output(err, "stderr")
        if out or err:
            return

        size = len(data)
        for i in range(0, size, BUFFER_SIZE):
            chunk_size = min(BUFFER_SIZE, size - i)
            chunk = data[i : i + chunk_size]
            self._execute(
                "__temp_written += __temp_f.write({chunk!r})".format(chunk=chunk),
                capture_output=True,
            )

        bytes_written = self._evaluate(
            "__temp_written",
            cleanup=dedent(
                """
                __temp_f.close()
                del __temp_f
                del __temp_written
                del __temp_path
            """
            ),
        )

        if bytes_written != size:
            raise UserError("Expected %d written bytes but wrote %d" % (size, bytes_written))

    def _cmd_read_file(self, cmd):
        # TODO: better to read piecewise?
        content_bytes = self._evaluate(
            "__temp_content",
            prelude=dedent(
                """
                __temp_path = '%(path)s' 
                with open(__temp_path, 'rb') as __temp_fp:
                    __temp_content = __temp_fp.read()
                """
            )
            % cmd,
            cleanup="del __temp_fp; del __temp_path; del __temp_content",
        )

        return {"content_bytes": content_bytes, "path": cmd["path"]}

    def _cmd_editor_autocomplete(self, cmd):
        # template for the response
        result = dict(source=cmd.source, row=cmd.row, column=cmd.column)

        try:
            script = jedi.Script(cmd.source, cmd.row, cmd.column, sys_path=[self._api_stubs_path])
            completions = script.completions()
            result["completions"] = self._filter_completions(completions)
        except Exception:
            result["error"] = "Autocomplete error"

        return result

    def _filter_completions(self, completions):
        # filter out completions not applicable to MicroPython
        result = []
        for completion in completions:
            if completion.name.startswith("__"):
                continue

            parent_name = completion.parent().name
            name = completion.name
            root = completion.full_name.split(".")[0]

            # jedi proposes names from CPython builtins
            if root in self._builtins_info and name not in self._builtins_info[root]:
                continue

            if parent_name == "builtins" and name not in self._builtins_info:
                continue

            result.append({"name": name, "complete": completion.complete})

        return result

    def _cmd_shell_autocomplete(self, cmd):
        source = cmd.source

        # TODO: combine dynamic results and jedi results
        if source.strip().startswith("import ") or source.strip().startswith("from "):
            # this needs the power of jedi
            response = {"source": cmd.source}

            try:
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
                    names = self._evaluate("dir(%s)" % obj)
                else:
                    names = self._evaluate("dir()")
            else:
                names = []
                prefix = ""

            completions = []
            for name in names:
                if name.startswith(prefix) and not name.startswith("__"):
                    completions.append({"name": name, "complete": name[len(prefix) :]})

            return {"completions": completions, "source": source}

    def _cmd_dump_api_info(self, cmd):
        "For use during development of the plug-in"

        self._execute(
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
        out, err, __ = self._execute("import {0}".format(module_name), capture_output=True)
        if out or err:
            print("FAILED IMPORTING MODULE:", module_name, "\nErr: " + out + err)
            return

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

    def _get_fs_mount_name(self):
        if self._welcome_text is None:
            return None

        markers_by_name = {"PYBFLASH": {"pyblite", "pyboard"}, "CIRCUITPY": {"circuitpython"}}

        for name in markers_by_name:
            for marker in markers_by_name[name]:
                if marker.lower() in self._welcome_text.lower():
                    return name

        return None

    def _get_flash_prefix(self):
        if not self._supports_directories():
            return ""
        elif (
            "LoBo" in self._welcome_text
            or "WiPy with ESP32" in self._welcome_text
            or "PYBLITE" in self._welcome_text
            or "PYBv" in self._welcome_text
            or "PYBOARD" in self._welcome_text.upper()
        ):
            return "/flash/"
        else:
            return "/"

    def _get_fs_mount(self):
        if self._get_fs_mount_name() is None:
            return None
        else:
            candidates = find_volumes_by_name(
                self._get_fs_mount_name(),
                # querying A can be very slow
                skip_letters="A",
            )
            if len(candidates) == 0:
                raise RuntimeError("Could not find volume " + self._get_fs_mount_name())
            elif len(candidates) > 1:
                raise RuntimeError("Found several possible mount points: %s" % candidates)
            else:
                return candidates[0]

    def _get_dirs_child_data_microbit(self, cmd):
        """let it be here so micro:bit works with generic proxy as well"""

        assert cmd["paths"] == {""}, "Bad command: " + repr(cmd)
        file_sizes = self._evaluate(
            "{name : __module_os.size(name) for name in __module_os.listdir()}"
        )
        return {"": file_sizes}

    def _get_dirs_child_data_generic(self, cmd):
        return self._evaluate(
            "__temp_result",
            prelude=dedent(
                """
                import os as __module_os
                # Init all vars, so that they can be deleted
                # even if the loop makes no iterations
                __temp_result = {}
                __temp_path = None
                __temp_st = None 
                __temp_children = None
                __temp_name = None
                __temp_real_path = None
                __temp_full = None
                
                for __temp_path in %(paths)r:
                    __temp_real_path = __temp_path or '/'
                    __temp_children = {}
                    for __temp_name in __module_os.listdir(__temp_real_path):
                        if __temp_name.startswith('.') or __temp_name == "System Volume Information":
                            continue
                        __temp_full = (__temp_real_path + '/' + __temp_name).replace("//", "/")
                        # print("processing", __temp_full)
                        __temp_st = __module_os.stat(__temp_full)
                        if __temp_st[0] & 0o170000 == 0o040000:
                            # directory
                            __temp_children[__temp_name] = None
                        else:
                            __temp_children[__temp_name] = __temp_st[6]
                            
                    __temp_result[__temp_path] = __temp_children                            
            """
            )
            % {"paths": cmd.paths},
            cleanup=dedent(
                """
                del __module_os
                del __temp_st
                del __temp_children
                del __temp_name
                del __temp_path
                del __temp_full
            """
            ),
        )

    def _check_for_connection_errors(self):
        self._connection._check_for_error()

    def _on_connection_closed(self):
        self._send_output(
            "\n" + "Connection closed. Use 'Run → Stop / Restart' to reconnect." + "\n", "stderr"
        )
        sys.exit(EXPECTED_TERMINATION_CODE)


class ExecutionError(Exception):
    pass


def _report_internal_error():
    print("PROBLEM WITH THONNY'S BACK-END:\n", file=sys.stderr)
    traceback.print_exc()


def parse_api_information(file_path):
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", type=lambda s: True if s == "True" else False)
    parser.add_argument("--port", type=str)
    parser.add_argument("--url", type=str)
    parser.add_argument("--password", type=str)
    parser.add_argument("--api_stubs_path", type=str)
    args = parser.parse_args()

    port = None if args.port == "None" else args.port
    try:
        if port is None:
            # remain busy
            while True:
                time.sleep(1000)
        elif port == "webrepl":
            from thonny.plugins.micropython.webrepl_connection import WebReplConnection

            connection = WebReplConnection(args.url, args.password)
        else:
            from thonny.plugins.micropython.serial_connection import SerialConnection

            connection = SerialConnection(port, BAUDRATE)

        vm = MicroPythonBackend(connection, clean=args.clean, api_stubs_path=args.api_stubs_path)

    except ConnectionFailedException as e:
        text = "\n" + str(e) + "\n"
        msg = BackendEvent(event_type="ProgramOutput", stream_name="stderr", data=text)
        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()
