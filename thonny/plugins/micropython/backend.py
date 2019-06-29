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
from thonny.plugins.micropython.connection import ConnectionClosedException
from time import sleep
from textwrap import dedent
import ast
import re
from queue import Queue
import threading
import os
from thonny.plugins.micropython.serial_connection import SerialConnection

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
    def __init__(self, connection):
        self._connection = connection
        self._cwd = None
        self._command_queue = Queue()  # populated by reader thread

        self._command_reading_thread = threading.Thread(target=self._read_commands, daemon=True)
        self._command_reading_thread.start()

        self._process_until_initial_raw_prompt()

        debug("after inrp")
        self._welcome_text = self._fetch_welcome_text()
        debug("after welc: " + self._welcome_text)
        self._cwd = self._fetch_cwd()
        debug("after fetch: " + self._cwd)

        self._send_ready_message()
        debug("after welc")

        self._mainloop()

    def _mainloop(self):
        try:
            while True:
                try:
                    cmd = self._command_queue.get()
                    if isinstance(cmd, InputSubmission):
                        self._submit_input(cmd.data)
                    else:
                        self.handle_command(cmd)
                except KeyboardInterrupt:
                    self._interrupt()
        except Exception:
            logger.exception("Crash in mainloop")
            traceback.print_exc()

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

    def _fetch_cwd(self):
        if not self._supports_directories():
            return None
        else:
            result = self._evaluate("__module_os.getcwd()", prelude="import os as __module_os")
            assert result is not None, "Could not fetch cwd"
            return result

    def _send_ready_message(self):
        self.send_message(ToplevelResponse(welcome_text=self._welcome_text, cwd=self._cwd))

    def _interrupt(self):
        try:
            self._connection.write(INTERRUPT_CMD)
        except ConnectionClosedException as e:
            self._handle_connection_closed(e)

    def _soft_reboot(self):
        if not self.idle:
            # TODO: ignore??
            # self._connection.write(b"\r\x03")
            self.interrupt()

        # Need to go to normal mode. MP doesn't run user code in raw mode
        # (CP does, but it doesn't hurt to do it there as well)
        self._connection.write(NORMAL_MODE_CMD)
        self._connection.read_until(NORMAL_PROMPT)

        self._connection.write(SOFT_REBOOT_CMD)

        # Returning to the raw prompt will be handled by
        # _read_next_serial_message

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

        try:
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

        except ConnectionClosedException as e:
            self._handle_connection_closed(e)

    def send_message(self, msg):
        if "cwd" not in msg:
            msg["cwd"] = self._cwd

        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()

    def _send_output(self, data, stream_name):
        if not data:
            return
        msg = BackendEvent(event_type="ProgramOutput", stream_name=stream_name, data=data)
        self.send_message(msg)

    def _flush_output(self):
        "TODO: send current stdout and stderr to UI"

    def _handle_connection_closed(self, e):
        self._show_error_connect_again("\nLost connection to the device (%s)." % e)
        self.idle = False
        try:
            self._connection.close()
        except Exception:
            logging.exception("Closing serial")
        finally:
            self._connection = None

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
        
        Because of soft-reboot we can't assume we'll find all 
        
        Output produced by background threads (eg. in WiPy ESP32) cause even more difficulties, 
        because it becomes impossible to say whether we are at prompt and output
        is from another thread or the main thread is running.
        For now I'm ignoring these problems and assume all output comes from the main thread.
         
        """
        # TODO: experiment with Ctrl+C, Ctrl+D, reset
        eot_count = 0
        value = None
        done = False
        out = b""
        err = b""

        assert not capture_output

        while not done:
            # There may be an input submission waiting
            # and we can't progress without resolving it first
            self._check_for_side_commands()

            # Process input in chunks (max 1 parsing marker per chunk).
            # Prefer whole lines (to reduce the number of events),
            # but don't wait too long for eol.
            output = self._connection.soft_read_until(BLOCK_CLOSERS, timeout=0.01)
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

            if capture_output:
                if stream_name == "stdout":
                    out += output
                else:
                    assert stream_name == "stderr"
                    err += output
            else:
                # TODO: deal with partial UTF-8 chars
                self._send_output(output.decode(ENCODING), stream_name)

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
                self._soft_reboot()
            else:
                postponed.append(cmd)

        # put back postponed commands
        while postponed:
            self._command_queue.put(postponed.pop(0))

    def _supports_directories(self):
        if "micro:bit" in self._welcome_text.lower():
            return False
        else:
            return True

    def _cmd_interrupt(self, cmd):
        self._interrupt()

    def _cmd_cd(self, cmd):
        if len(cmd.args) == 1:
            if not self._supports_directories():
                raise UserError("This device doesn't have directories")

            path = cmd.args[0]
            self._execute("import os as __thonny_os; __module_os.chdir(%r)" % path)
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


class ExecutionError(Exception):
    pass


def _report_internal_error():
    print("PROBLEM WITH THONNY'S BACK-END:\n", file=sys.stderr)
    traceback.print_exc()


if __name__ == "__main__":
    connection = SerialConnection("COM7", BAUDRATE)
    vm = MicroPythonBackend(connection)
