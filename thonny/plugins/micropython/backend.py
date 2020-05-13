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
    execute_system_command,
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
from thonny.misc_utils import find_volumes_by_name, sizeof_fmt
import io
import tokenize
from thonny.running import EXPECTED_TERMINATION_CODE
import binascii
from threading import Lock

# See https://github.com/dhylands/rshell/blob/master/rshell/main.py
# for UART_BUFFER_SIZE vs USB_BUFFER_SIZE
# ampy uses 32 bytes: https://github.com/pycampers/ampy/blob/master/ampy/files.py
# I'm not worrying so much, because reader thread reads continuously
# and writer (SerialConnection) has it's own blocks and delays
BUFFER_SIZE = 512

BAUDRATE = 115200
ENCODING = "utf-8"

# Commands
RAW_MODE_CMD = b"\x01"
NORMAL_MODE_CMD = b"\x02"
INTERRUPT_CMD = b"\x03"
SOFT_REBOOT_CMD = b"\x04"

# Output tokens
VALUE_REPR_START = b"<repr>"
VALUE_REPR_END = b"</repr>"
STX = b"\x02"
EOT = b"\x04"
NORMAL_PROMPT = b">>> "
LF = b"\n"
OK = b"OK"

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

FALLBACK_BUILTIN_MODULES = [
    "cmath",
    "gc",
    "math",
    "sys",
    "array",
    # "binascii", # don't include it, as it may give false signal for reader/writer
    "collections",
    "errno",
    "hashlib",
    "heapq",
    "io",
    "json",
    "os",
    "re",
    "select",
    "socket",
    "ssl",
    "struct",
    "time",
    "zlib",
    "_thread",
    "btree",
    "framebuf",
    "machine",
    "micropython",
    "network",
    "bluetooth",
    "cryptolib",
    "ctypes",
    "pyb",
    "esp",
    "esp32",
]

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

        self._startup_time = time.time()
        self._interrupt_suggestion_given = False

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
        if clean:
            self._interrupt_to_raw_prompt()
            self._clear_environment()
        else:
            self._connection.write(RAW_MODE_CMD)
            self._forward_output_until_active_prompt()

        self._cwd = self._fetch_cwd()
        self._welcome_text = self._fetch_welcome_text()
        self._builtin_modules = self._fetch_builtin_modules()
        self._builtins_info = self._fetch_builtins_info()

        self._send_ready_message()

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
        self._connection.write(NORMAL_MODE_CMD)
        welcome_text = self._connection.read_until(NORMAL_PROMPT).strip(b"\r\n >")
        if os.name != "nt":
            welcome_text = welcome_text.replace(b"\r\n", b"\n")

        # Go back to raw prompt
        self._connection.write(RAW_MODE_CMD)
        self._connection.read_until(FIRST_RAW_PROMPT)

        return welcome_text.decode(ENCODING, errors="replace")

    def _fetch_uname(self):
        res = self._evaluate("__thonny_os.uname()", prelude="import os as __thonny_os")
        return {
            "sysname": res[0],
            "nodename": res[1],
            "release": res[2],
            "version": res[3],
            "machine": res[4],
        }

    def _fetch_builtin_modules(self):
        out = self._execute_and_capture_output("help('modules')")
        if out is None:
            self._send_error_message(
                "Could not query builtin modules. Code completion may not work properly."
            )
            return FALLBACK_BUILTIN_MODULES

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
            "__thonny_os.getcwd() if hasattr(__thonny_os, 'getcwd') else ''",
            prelude="import os as __thonny_os",
        )

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

    def _interrupt_to_raw_prompt(self):
        # NB! Sometimes disconnecting and reconnecting (on macOS?)
        # too quickly causes anomalies. See CalliopeMiniProxy for more details

        discarded_bytes = b""

        for delay in [0.05, 0.5, 0.1, 1.0, 3.0, 5.0]:
            # Interrupt several times, because with some drivers first interrupts seem to vanish
            if delay >= 1:
                self._show_error(
                    "Could not enter REPL. Trying again with %d second waiting time..." % delay
                )
            self._connection.reset_output_buffer()
            self._connection.write(INTERRUPT_CMD)
            self._connection.write(RAW_MODE_CMD)
            time.sleep(delay)
            discarded_bytes += self._connection.read_all()
            if discarded_bytes.endswith(FIRST_RAW_PROMPT) or discarded_bytes.endswith(b"\r\n>"):
                break
        else:
            max_tail_length = 500
            if len(discarded_bytes) > max_tail_length:
                discarded_bytes_str = (
                    "[skipping %d bytes] ..." % (len(discarded_bytes) - max_tail_length)
                ) + repr(discarded_bytes[:-max_tail_length])
            else:
                discarded_bytes_str = repr(discarded_bytes)
            self._show_error(
                "Could not enter REPL. Giving up. Read bytes:\n"
                + discarded_bytes_str
                + "\n\nYour options:\n\n"
                + "  - check connection properties;\n"
                + "  - make sure the device has suitable firmware;\n"
                + "  - make sure the device is not in bootloader mode;\n"
                + "  - reset the device and try again;\n"
                + "  - try other serial clients (Putty, TeraTerm, screen, ...);\n"
                + "  - ask for help in Thonny's forum or issue tracker."
            )
            sys.exit()

    def _soft_reboot(self, side_command):
        if side_command:
            self._interrupt_to_raw_prompt()

        # Need to go to normal mode. MP doesn't run user code in raw mode
        # (CP does, but it doesn't hurt to do it there as well)
        self._connection.write(NORMAL_MODE_CMD)
        self._connection.read_until(NORMAL_PROMPT)

        self._connection.write(SOFT_REBOOT_CMD)

        if not side_command:
            self._forward_output_until_active_prompt()
            self.send_message(ToplevelResponse(cwd=self._cwd))

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
        # Any keypress wouldn't work
        return data.replace(
            "Press any key to enter the REPL. Use CTRL-D to reload.",
            "Press Ctrl-C to enter the REPL. Use CTRL-D to reload.",
        )

    def _ensure_raw_propmt(self):
        # similar to _interrupt_to_raw_prompt, but assumes we are already in a prompt
        self._forward_unexpected_output()
        self._connection.write(RAW_MODE_CMD)
        prompt = self._connection.read_until(FIRST_RAW_PROMPT_SUFFIX, 1, True)
        if not prompt.endswith(FIRST_RAW_PROMPT_SUFFIX):
            raise TimeoutError("Could not ensure raw prompt")

    def _submit_code_to_raw_repl(self, script):
        assert script  # otherwise EOT produces soft reboot

        self._ensure_raw_propmt()

        # send command
        with self._writing_lock:
            self._connection.write(script.encode(ENCODING) + EOT)
            debug("Wrote " + script + "\n--------\n")

            # fetch command confirmation
            confirmation = self._connection.soft_read(2, timeout=WAIT_OR_CRASH_TIMEOUT)

        if confirmation != OK:
            raise ProtocolError(
                "Could not read command confirmation", confirmation + self._connection.read_all()
            )

        debug("GOTOK")

    def _execute_in_raw_mode(self, script, timeout, capture_stdout):
        """Ensures raw prompt and submits the script.
        Returns (out, value_repr, err) if there are no problems, ie. all parts of the 
        output are present and it reaches active raw prompt.
        Otherwise raises ProtocolError.
        
        Expected output after submitting the command and reading the confirmation is following:
        
            - User code: 
                stdout
                EOT
                stderr
                EOT
                RAW_PROMPT
                
            - Thonny management/evaluation commands:
                stdout (rare, eg. produced by unorthodox __repr__ methods)  
                EOT + VALUE_REPR_START + value_repr + VALUE_REPR_END
                EOT 
                EOT
                RAW_PROMPT
        
        The execution may block. In this case the user should do something (eg. provide
        required input or issue an interrupt). The UI should remind the interrupt in case
        of Thonny commands.
        """

        self._submit_code_to_raw_repl(script)

        # The part until first EOT is supposed to be stdout output.
        # If capture is not required then it is produced by user code,
        # ie. the output produced should be forwarded as it appears.
        if capture_stdout:
            stdout_block = self._connection.soft_read_until(EOT, timeout=timeout)
            if stdout_block.endswith(EOT):
                out = stdout_block[: -len(EOT)]
            else:
                raise ProtocolError("Captured output was not terminated properly", stdout_block)
        else:
            out = b""
            terminator = self._forward_output_until_eot_or_active_propmt()
            if terminator != EOT:
                raise ProtocolError("Incremental output was not terminated properly", terminator)
            stdout_block = out + terminator

        # Remaining part must contain value repr and empty stderr or (possibly empty) stderr alone.
        # Value repr followed by non-empty stderr (eg. by cleanup code) is considered a protocol
        # error. This part can be read as one block. It should appear quite quickly as the first
        # EOT is already present.
        final_terminator = EOT + RAW_PROMPT
        value_err_block = self._connection.soft_read_until(final_terminator, WAIT_OR_CRASH_TIMEOUT)
        if not value_err_block.endswith(final_terminator):
            raise ProtocolError(
                "Value/stderr was not terminated properly", stdout_block + value_err_block
            )

        trimmed_value_err_block = value_err_block[: -len(final_terminator)]
        # trimmed_value_err_block may or may not contain value-repr block
        if trimmed_value_err_block.count(EOT) == 0:
            value_repr = None
            err = trimmed_value_err_block
        elif (
            trimmed_value_err_block.count(EOT) == 1
            and trimmed_value_err_block.startswith(VALUE_REPR_START)
            and trimmed_value_err_block.endswith(VALUE_REPR_END + EOT)
        ):
            value_repr = trimmed_value_err_block[
                len(VALUE_REPR_START) : -len(VALUE_REPR_END + EOT)
            ].decode(ENCODING)
            err = b""
        else:
            raise ProtocolError(
                "Unexpected structure in value/stderr block", stdout_block + value_err_block
            )

        # The final condition -- the raw prompt we reached must be active prompt,
        # ie. it must be the end of the output
        remainder = self._connection.soft_read(1, timeout=0.01) + self._connection.read_all()
        if remainder:
            raise ProtocolError(
                "Unexpected output after raw prompt", stdout_block + value_err_block + remainder
            )

        return out.decode(ENCODING), value_repr, err.decode(ENCODING)

    def _execute_without_errors(self, script):
        """Meant for management tasks. stdout will be unexpected but tolerated.
        stderr will cause exception"""
        result = self._evaluate("True", prelude=script)
        assert result is True

    def _evaluate_to_repr(self, expr, prelude="", cleanup="", timeout=SECONDS_IN_YEAR):
        """Uses raw-REPL to evaluate and print the repr of given expression.
        
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

        stdout, value_repr, err = self._execute_in_raw_mode(
            script, timeout=timeout, capture_stdout=False
        )

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
        stdout, value_repr, err = self._execute_in_raw_mode(
            script, timeout=timeout, capture_stdout=True
        )

        if value_repr is not None:
            raise ProtocolError(
                "Unexpected value repr",
                stdout + EOT + VALUE_REPR_START + value_repr + VALUE_REPR_END + EOT + err,
            )
        elif err:
            raise ProtocolError("Captured output with errors", stdout + EOT + err)
        else:
            return stdout

    def _execute_user_code(self, script):
        """Executes the code in raw REPL and forwards output / err,
        if all goes according to protocol. Raises ProtocolError othewise."""
        stdout, value_repr, err = self._execute_in_raw_mode(
            script, timeout=SECONDS_IN_YEAR, capture_stdout=False
        )

        if value_repr is not None:
            raise ProtocolError(
                "Unexpected value repr",
                stdout + EOT + VALUE_REPR_START + value_repr + VALUE_REPR_END + EOT + err,
            )
        else:
            self._send_output(stdout, "stdout")
            self._send_output(err, "stderr")

    def _evaluate(self, expr, prelude="", cleanup=""):
        value_repr = self._evaluate_to_repr(expr, prelude, cleanup)
        return ast.literal_eval(value_repr)

    def _forward_output_until_active_prompt(self, stream_name="stdout"):
        """Used for finding initial prompt or forwarding problematic output 
        in case of parse errors"""
        while True:
            terminator = self._forward_output_until_eot_or_active_propmt(stream_name)
            if terminator in (NORMAL_PROMPT, RAW_PROMPT, FIRST_RAW_PROMPT):
                return terminator
            else:
                self._send_output(terminator, "stdout")

    def _forward_output_until_eot_or_active_propmt(self, stream_name="stdout"):
        """Meant for incrementally forwarding stdout from user statements, 
        scripts and soft-reboots. Also used for forwarding side-effect output from 
        expression evaluations and for capturing help("modules") output.
        In these cases it is expected to arrive to an EOT.
        
        Also used for initial prompt searching or for recovering from a protocol error.
        In this case it must work until active prompt.
        
        The code may have been submitted in any of the REPL modes or
        automatically via (soft-)reset.
        
        NB! The processing may end in normal mode even if the command was started 
        in raw mode (eg. when user presses reset during processing in some devices)!
        
        The processing may also end in FIRST_RAW_REPL, when it was started in 
        normal REPL and Ctrl+A was issued during processing (ie. before Ctrl+C in 
        this example):
        
            6
            7
            8
            9
            10
            Traceback (most recent call last):
              File "main.py", line 5, in <module>
            KeyboardInterrupt:
            MicroPython v1.11-624-g210d05328 on 2019-12-09; ESP32 module with ESP32
            Type "help()" for more information.
            >>>
            raw REPL; CTRL-B to exit
            >
        
        (Preceding output does not contain EOT)
        Note that this Ctrl+A may have been issued even before Thonny connected to
        the device.

        Note that interrupt does not affect the structure of the output -- it is
        presented just like any other exception.
        
        The method returns pair of captured output (or b"" if not requested)
        and EOT, RAW_PROMPT or NORMAL_PROMPT, depending on which terminator ended the processing.
        
        The terminating EOT may be either the first EOT from normal raw-REPL
        output or the starting EOT from Thonny expression (or, in principle, even
        the second raw-REPL EOT or terminating Thonny expression EOT) 
        -- the caller will do the interpretation.
        
        Because ot the special role of EOT and NORMAL_PROMT, we assume user code
        will not output these. If it does, processing will break.
        TODO: Experiment with this!
        
        Output produced by background threads (eg. in WiPy ESP32) cause even more difficulties, 
        because it becomes impossible to say whether we are at prompt and output
        is from another thread or the main thread is still running.
        For now I'm ignoring these problems and assume all output comes from the main thread.
        """
        INCREMENTAL_OUTPUT_BLOCK_CLOSERS = re.compile(
            b"|".join(map(re.escape, [LF, EOT, NORMAL_PROMPT, FIRST_RAW_PROMPT]))
        )

        pending = b""
        while True:
            # There may be an input submission waiting
            # and we can't progress without resolving it first
            self._check_for_side_commands()

            # Prefer whole lines, but allow also incremental output to single line
            # Note that here I'm not looking for non-first raw prompt, because this
            # is always preceded by EOT.
            new_data = self._connection.soft_read_until(
                INCREMENTAL_OUTPUT_BLOCK_CLOSERS, timeout=0.05
            )
            if not new_data:
                # In case we are still waiting for the first bits after connecting ...
                if (
                    self._connection.num_bytes_received == 0
                    and not self._interrupt_suggestion_given
                    and time.time() - self._startup_time > 1.5
                ):
                    self._show_error(
                        "\n"
                        + "Device is busy or does not respond. Your options:\n\n"
                        + "  - wait until it completes current work;\n"
                        + "  - use Ctrl+C to interrupt current work;\n"
                        + "  - use Stop/Restart to interrupt more and enter REPL.\n"
                    )
                    self._interrupt_suggestion_given = True

                continue

            pending += new_data

            if pending.endswith(EOT):
                self._send_output(pending[: -len(EOT)], stream_name)
                return EOT

            elif pending.endswith(LF):
                self._send_output(pending, stream_name)
                pending = b""

            elif pending.endswith(NORMAL_PROMPT) or pending.endswith(FIRST_RAW_PROMPT):
                # This looks like prompt (or its prefix).
                # Make sure it is not followed by anything.
                # Note that in this context the prompt means something is wrong
                # (EOT would have been the happy path), so no need to hurry.
                # The only case where this path is happy path is just after connecting.
                follow_up = self._connection.soft_read(1, timeout=0.5)
                if follow_up:
                    # Nope, the prompt is not active.
                    # (Actually it may be that a background thread has produced this follow up,
                    # but this would be too hard to consider.)
                    # Don't output yet, because the follow up may turn into another prompt
                    # and they can be captured all together.
                    pending += follow_up
                else:
                    # let's hope it is an active prompt
                    if pending.endswith(NORMAL_PROMPT):
                        terminator = NORMAL_PROMPT
                    else:
                        terminator = FIRST_RAW_PROMPT

                    # Strip all trailing prompts
                    out = pending
                    while True:
                        if out.endswith(NORMAL_PROMPT):
                            out = out[: -len(NORMAL_PROMPT)]
                        elif out.endswith(FIRST_RAW_PROMPT):
                            out = out[: -len(FIRST_RAW_PROMPT)]
                        else:
                            break
                    self._send_output(out, stream_name)

                    return terminator

            elif ends_overlap(pending, NORMAL_PROMPT) or ends_overlap(pending, FIRST_RAW_PROMPT):
                # Maybe we have a prefix of the prompt and the rest is still coming?
                follow_up = self._connection.soft_read(1, timeout=0.1)
                if not follow_up:
                    # most likely not a Python prompt, let's forget about it
                    self._send_output(pending, stream_name)
                    pending = b""
                else:
                    # Let's withhold this for now
                    pending += follow_up

            else:
                # No EOT or prompt in sight.
                # Output and keep working.
                self._send_output(pending, stream_name)
                pending = b""

    def _forward_unexpected_output(self, stream_name="stdout"):
        "Invoked between commands"
        data = self._connection.read_all()
        at_prompt = False

        while data.endswith(NORMAL_PROMPT) or data.endswith(FIRST_RAW_PROMPT):
            # looks like the device was resetted
            at_prompt = True

            if data.endswith(NORMAL_PROMPT):
                terminator = NORMAL_PROMPT
            else:
                terminator = FIRST_RAW_PROMPT

            # hide the prompt from the output ...
            data = data[: -len(terminator)]

        self._send_output(data.decode(ENCODING, "replace"), stream_name)
        if at_prompt:
            # ... and recreate Thonny prompt
            self.send_message(ToplevelResponse())

        self._check_for_connection_errors()

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
        self._execute_without_errors("globals().clear(); __name__ = '__main__'")

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

    def _connected_to_microbit(self):
        return "micro:bit" in self._welcome_text.lower()

    def _cmd_cd(self, cmd):
        if len(cmd.args) == 1:
            if not self._supports_directories():
                raise UserError("This device doesn't have directories")

            path = cmd.args[0]
            self._execute_without_errors("import os as __thonny_os; __thonny_os.chdir(%r)" % path)
            self._cwd = self._fetch_cwd()
            return {}
        else:
            raise UserError("%cd takes one parameter")

    def _cmd_Run(self, cmd):
        # self._clear_environment()
        assert cmd.get("source")
        self._execute_user_code(cmd["source"])
        return {}

    def _cmd_execute_source(self, cmd):
        try:
            # Try to parse as expression
            ast.parse(cmd.source, mode="eval")
            # If it didn't fail then source is an expression
            value_repr = self._evaluate_to_repr(cmd.source)
            if value_repr is None:
                value_repr = repr(None)
            return {"value_info": ValueInfo(0, value_repr)}
        except SyntaxError:
            # source is a statement (or invalid syntax)
            self._execute_user_code(cmd.source)
            return {}

    def _cmd_execute_system_command(self, cmd):
        # Can't use stdin, because a thread is draining it
        execute_system_command(cmd, cwd=self._local_cwd, disconnect_stdin=True)

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
        if self._supports_directories():
            data = self._get_dirs_child_data_generic(cmd["paths"])
            dir_separator = "/"
        else:
            assert cmd["paths"] == {""}, "Bad command: " + repr(cmd)
            sizes = self._get_microbit_file_sizes()
            root_data = {name: {"kind": "file", "size": size} for (name, size) in sizes.items()}
            data = {"": root_data}
            dir_separator = ""

        return {"node_id": cmd["node_id"], "dir_separator": dir_separator, "data": data}

    def _cmd_get_fs_info(self, cmd):
        return self._get_fs_info(cmd.path)

    def _cmd_write_file(self, cmd):
        def generate_blocks(content_bytes, block_size):
            for i in range(0, len(content_bytes), block_size):
                yield content_bytes[i : i + block_size]

        self._write_file(generate_blocks(cmd["content_bytes"], BUFFER_SIZE), cmd["path"])

        return InlineResponse(
            command_name="write_file", path=cmd["path"], editor_id=cmd.get("editor_id")
        )

    def _cmd_delete(self, cmd):
        assert cmd.paths

        paths = sorted(cmd.paths, key=lambda x: len(x), reverse=True)

        try:
            self._delete_via_serial(paths)
        except Exception as e:
            if "read-only" in str(e).lower():
                self._delete_via_mount(paths)

        self._sync_all_filesystems()

    def _internal_path_to_mounted_path(self, path):
        mount_path = self._get_fs_mount()
        if mount_path is None:
            return None

        flash_prefix = self._get_flash_prefix()
        if not path.startswith(flash_prefix):
            return None

        path_suffix = path[len(flash_prefix) :]

        return os.path.join(mount_path, os.path.normpath(path_suffix))

    def _cmd_read_file(self, cmd):
        try:
            content_bytes = b"".join(self._read_file(cmd["path"]))
            error = None
        except Exception as e:
            _report_internal_error()
            error = str(e)
            content_bytes = None

        return {"content_bytes": content_bytes, "path": cmd["path"], "error": error}

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
        assert self._supports_directories()
        assert cmd.path.startswith("/")
        self._makedirs(cmd.path)
        self._sync_all_filesystems()

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

    def _read_file(self, path):
        # TODO: read from mount when possible
        # file_size = self._get_file_size(path)
        block_size = 512
        hex_mode = self.should_hexlify(path)

        self._execute_without_errors("__thonny_fp = open(%r, 'rb')" % path)
        if hex_mode:
            self._execute_without_errors("from binascii import hexlify as __temp_hexlify")

        while True:
            if hex_mode:
                block = binascii.unhexlify(
                    self._evaluate("__temp_hexlify(__thonny_fp.read(%s))" % block_size)
                )
            else:
                block = self._evaluate("__thonny_fp.read(%s)" % block_size)
            if block:
                yield block
            if len(block) < block_size:
                break

        self._execute_without_errors(
            dedent(
                """
            __thonny_fp.close()
            del __thonny_fp
            try:
                del __temp_hexlify
            except:
                pass
            """
            )
        )

    def _write_file(self, content_blocks, target_path, notifier=None):
        try:
            result = self._write_file_via_serial(content_blocks, target_path, notifier)
        except ReadOnlyFilesystemError:
            result = self._write_file_via_mount(content_blocks, target_path, notifier)

        self._sync_all_filesystems()
        return result

    def _write_file_via_mount(self, content_blocks, target_path, notifier=None):
        mounted_target_path = self._internal_path_to_mounted_path(target_path)
        with open(mounted_target_path, "wb") as f:
            bytes_written = 0
            for block in content_blocks:
                bytes_written += f.write(block)
                f.flush()
                os.fsync(f)
                if notifier is not None:
                    notifier(bytes_written)

        return bytes_written

    def _write_file_via_serial(self, content_blocks, target_path, notifier=None):
        # prelude
        result = self._evaluate(
            "__thonny_result",
            dedent(
                """
            try:
                __thonny_path = '{path}'
                __thonny_written = 0
                __thonny_fp = open(__thonny_path, 'wb')
                __thonny_result = "OK"
            except Exception as e:
                __thonny_result = str(e)
            """
            ).format(path=target_path),
        )

        if "readonly" in result.replace("-", "").lower():
            raise ReadOnlyFilesystemError()

        elif result != "OK":
            raise RuntimeError("Problem opening file for writing: " + result)

        # Define function to allow shorter write commands
        hex_mode = self.should_hexlify(target_path)
        if hex_mode:
            self._execute_without_errors(
                dedent(
                    """
                from binascii import unhexlify as __thonny_unhex
                def __W(x):
                    global __thonny_written
                    __thonny_written += __thonny_fp.write(__thonny_unhex(x))
                    __thonny_fp.flush()
            """
                )
            )
        else:
            self._execute_without_errors(
                dedent(
                    """
                def __W(x):
                    global __thonny_written
                    __thonny_written += __thonny_fp.write(x)
            """
                )
            )

        bytes_sent = 0
        for block in content_blocks:
            if hex_mode:
                script = "__W(%r)" % binascii.hexlify(block)
            else:
                script = "__W(%r)" % block
            self._execute_without_errors(script)
            print("Wrote", script)
            bytes_sent += len(block)
            if notifier is not None:
                notifier(bytes_sent)

        bytes_received = self._evaluate("__thonny_written")

        if bytes_received != bytes_sent:
            raise UserError("Expected %d written bytes but wrote %d" % (bytes_sent, bytes_received))

        # clean up
        self._execute_without_errors(
            dedent(
                """
                try:
                    del __W
                    del __thonny_written
                    del __thonny_path
                    __thonny_fp.close()
                    del __thonny_fp
                    del __thonny_result
                    del __thonny_unhex
                except:
                    pass
            """
            )
        )

        return bytes_sent

    def _sync_all_filesystems(self):
        self._execute_without_errors(
            dedent(
                """
            try:
                from os import sync as __thonny_sync
                __thonny_sync()
                del __thonny_sync
            except ImportError:
                pass
        """
            )
        )

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
        if self._supports_directories():
            script = "__thonny_os.stat(%r)[6]"
        else:
            script = "os.stat(%r)[6]"

        return self._evaluate(script % path, prelude="import os as __thonny_os")

    def _makedirs(self, path):
        if path == "/":
            return

        try:
            self._makedirs_via_serial(path)
        except Exception as e:
            if "read-only" in str(e).lower():
                self._makedirs_via_mount(path)

    def _makedirs_via_mount(self, path):
        mounted_path = self._internal_path_to_mounted_path(path)
        assert mounted_path is not None, "Couldn't find mounted path for " + path
        os.makedirs(mounted_path, exist_ok=True)

    def _makedirs_via_serial(self, path):
        if path == "/":
            return
        path = path.rstrip("/")

        script = (
            dedent(
                """
            import os as __thonny_os
            __thonny_parts = %r.split('/')
            for i in range(2, len(__thonny_parts) + 1):
                __thonny_path = "/".join(__thonny_parts[:i])
                try:
                    __thonny_os.stat(__thonny_path)
                except OSError:
                    # does not exist
                    __thonny_os.mkdir(__thonny_path)
            
            del __thonny_parts
            try:
                del __thonny_path
            except:
                pass
        """
            )
            % path
        )

        self._execute_without_errors(script)

    def _delete_via_mount(self, paths):
        for path in paths:
            mounted_path = self._internal_path_to_mounted_path(path)
            assert mounted_path is not None
            import shutil
            shutil.rmtree(mounted_path)

    def _delete_via_serial(self, paths):
        if not self._supports_directories():
            self._execute_without_errors(
                dedent(
                    """
                import os as __thonny_os
                for __thonny_path in %r: 
                    __thonny_os.remove(__thonny_path)
                    
                del __thonny_path
                del __thonny_os
            """
                )
                % paths
            )
        else:
            self._execute_without_errors(
                dedent(
                    """
                import os as __thonny_os
                def __thonny_delete(path):
                    if __thonny_os.stat(path)[0] & 0o170000 == 0o040000:
                        for name in __thonny_os.listdir(path):
                            child_path = path + "/" + name
                            __thonny_delete(child_path)
                        __thonny_os.rmdir(path)
                    else:
                        __thonny_os.remove(path)
                
                for __thonny_path in %r: 
                    __thonny_delete(__thonny_path)
                    
                del __thonny_path
                del __thonny_delete
                del __thonny_os
            """
                )
                % paths
            )

    def _upload_file(self, source, target, notifier):
        assert target.startswith("/") or not self._supports_directories()
        target_dir, _ = linux_dirname_basename(target)
        assert target_dir.startswith("/") or not self._supports_directories()

        self._makedirs(target_dir)

        def block_generator():
            with open(source, "rb") as source_fp:
                while True:
                    block = source_fp.read(512)
                    if block:
                        yield block
                    else:
                        break

        return self._write_file(block_generator(), target, notifier=notifier)

    def _download_file(self, source, target, notifier=None):
        os.makedirs(os.path.dirname(target), exist_ok=True)
        bytes_written = 0
        with open(target, "wb") as out_fp:
            for block in self._read_file(source):
                out_fp.write(block)
                os.fsync(out_fp)
                bytes_written += len(block)
                notifier(bytes_written)

        return bytes_written

    def _get_fs_mount_label(self):
        # This method is most likely required with CircuitPython,
        # so try its approach first
        # https://learn.adafruit.com/welcome-to-circuitpython/the-circuitpy-drive
        result = self._evaluate(
            "__thonny_result",
            prelude=dedent(
                """
            try:
                from storage import getmount as __thonny_getmount
                try:
                    __thonny_result = __thonny_getmount("/").label
                finally:
                    del __thonny_getmount
            except ImportError:
                __thonny_result = None 
            except OSError:
                __thonny_result = None 
        """
            ),
            cleanup="del __thonny_result",
        )

        if result is not None:
            return result

        if self._welcome_text is None:
            return None

        """
        # following is not reliable and probably not needed 
        markers_by_name = {"PYBFLASH": {"pyb"}, "CIRCUITPY": {"circuitpython"}}

        for name in markers_by_name:
            for marker in markers_by_name[name]:
                if marker.lower() in self._welcome_text.lower():
                    return name
        """

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
        label = self._get_fs_mount_label()
        if label is None:
            return None
        else:
            candidates = find_volumes_by_name(
                self._get_fs_mount_label(),
                # querying A can be very slow
                skip_letters="A",
            )
            if len(candidates) == 0:
                raise RuntimeError("Could not find volume " + self._get_fs_mount_label())
            elif len(candidates) > 1:
                raise RuntimeError("Found several possible mount points: %s" % candidates)
            else:
                return candidates[0]

    def _get_fs_info(self, path):
        result = self._evaluate(
            dedent(
                """{
                    "total" : __thonny_total,
                    "used" : __thonny_used,
                    "free": __thonny_free,
                    "sizes": __thonny_sizes
                }"""
            ),
            prelude=dedent(
                """
                try:
                    from os import statvfs as __thonny_statvfs
                    __thonny_stat = __thonny_statvfs(%r)
                    __thonny_total = __thonny_stat[2] * __thonny_stat[0]
                    __thonny_free = __thonny_stat[3] * __thonny_stat[0]
                    __thonny_used = __thonny_total - __thonny_free
                    __thonny_sizes = None
                    del __thonny_statvfs
                    del __thonny_stat 
                except ImportError:
                    import os as __thonny_os
                    __thonny_sizes = [__thonny_os.size(name) for name in __thonny_os.listdir()]
                    __thonny_used = None
                    __thonny_total = None
                    __thonny_free = None  
                    del __thonny_os
            """
            )
            % path,
            cleanup=dedent(
                """
                del __thonny_total
                del __thonny_free
                del __thonny_used
                del __thonny_sizes
            """
            ),
        )

        if result["sizes"] is not None:
            if self._connected_to_microbit():
                comment = "Assuming around 30 kB of storage space for user files."
            else:
                comment = "Don't know the size of storage space on this device."

            files_total_size = sum(result["sizes"])

            # TODO: compute number of used blocks
            if files_total_size > 0:
                comment += "\n\n" + "At least %s of it is used by %d file(s)." % (
                    sizeof_fmt(files_total_size),
                    len(result["sizes"]),
                )

            result["comment"] = comment
            del result["sizes"]

        return result

    def _get_microbit_file_sizes(self):
        return self._evaluate(
            "{name : __thonny_os.size(name) for name in __thonny_os.listdir()}",
            prelude="import os as __thonny_os",
            cleanup="del __thonny_os",
        )

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

    def should_hexlify(self, path):
        if "binascii" not in self._builtin_modules:
            return False

        for ext in (".py", ".txt", ".csv"):
            if path.lower().endswith(ext):
                return False

        return True


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


def ends_overlap(left, right):
    """Returns whether the left ends with one of the non-empty prefixes of the right"""
    for i in range(1, min(len(left), len(right)) + 1):
        if left.endswith(right[:i]):
            return True

    return False


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


if __name__ == "__main__":
    THONNY_USER_DIR = os.environ["THONNY_USER_DIR"]
    logger = logging.getLogger("thonny.micropython.backend")
    logger.propagate = False
    logFormatter = logging.Formatter("%(levelname)s: %(message)s")
    file_handler = logging.FileHandler(
        os.path.join(THONNY_USER_DIR, "micropython-backend.log"), encoding="UTF-8", mode="w"
    )
    file_handler.setFormatter(logFormatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", type=lambda s: True if s == "True" else False)
    parser.add_argument("--port", type=str)
    parser.add_argument("--url", type=str)
    parser.add_argument("--password", type=str)
    parser.add_argument("--api_stubs_path", type=str)
    parser.add_argument("--min_write_delay", type=float, default=0.01)
    args = parser.parse_args()

    port = None if args.port == "None" else args.port
    try:
        if port is None:
            # remain busy
            while True:
                time.sleep(1000)
        elif port == "webrepl":
            from thonny.plugins.micropython.webrepl_connection import WebReplConnection

            connection = WebReplConnection(args.url, args.password, args.min_write_delay)
        else:
            from thonny.plugins.micropython.serial_connection import SerialConnection
            from thonny.plugins.micropython.serial_connection import DifficultSerialConnection

            connection = SerialConnection(port, BAUDRATE)
            # connection = DifficultSerialConnection(port, BAUDRATE)

        vm = MicroPythonBackend(connection, clean=args.clean, api_stubs_path=args.api_stubs_path)

    except ConnectionFailedException as e:
        text = "\n" + str(e) + "\n"
        msg = BackendEvent(event_type="ProgramOutput", stream_name="stderr", data=text)
        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()
