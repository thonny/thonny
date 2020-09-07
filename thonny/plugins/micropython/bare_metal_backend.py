import binascii
import datetime
import logging
import os
import queue
import re
import sys
import time
from _ast import Not
from textwrap import dedent, indent
from typing import BinaryIO, Callable, Optional, Tuple, Union

from thonny.backend import UploadDownloadMixin
from thonny.common import (
    BackendEvent,
    InlineResponse,
    ToplevelResponse,
    UserError,
    execute_system_command,
    serialize_message,
)
from thonny.misc_utils import find_volumes_by_name, sizeof_fmt
from thonny.plugins.micropython.backend import (
    WAIT_OR_CRASH_TIMEOUT,
    MicroPythonBackend,
    ManagementError,
    ReadOnlyFilesystemError,
    _report_internal_error,
    ends_overlap,
    unix_dirname_basename,
    Y2000_EPOCH_OFFSET,
)
from thonny.common import ConnectionFailedException

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

# https://forum.micropython.org/viewtopic.php?f=12&t=7652&hilit=w600#p43640
W600_FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\r\n>"
FIRST_RAW_PROMPT_SUFFIX = b"\r\n>"

RAW_PROMPT = b">"


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
    # print(msg, file=sys.stderr)


class BareMetalMicroPythonBackend(MicroPythonBackend, UploadDownloadMixin):
    def __init__(self, connection, clean, args):
        self._connection = connection
        self._startup_time = time.time()
        self._interrupt_suggestion_given = False
        self._raw_prompt_ensured = False

        MicroPythonBackend.__init__(self, clean, args)

    def _get_custom_helpers(self):
        return dedent(
            """
            @classmethod
            def getcwd(cls):
                if hasattr(cls, "getcwd"):
                    return cls.os.getcwd()
                else:
                    # micro:bit
                    return ""
            
            @classmethod
            def chdir(cls, x):
                return cls.os.chdir(x)
            
            @classmethod
            def rmdir(cls, x):
                return cls.os.rmdir(x)
        """
        )

    def _process_until_initial_prompt(self, clean):
        if clean:
            self._interrupt_to_raw_prompt()
        else:
            # Order first raw prompt to be output when the code is done.
            # If the device is already at raw prompt then it gets repeated as first raw prompt.
            # If it is at normal prompt then outputs first raw prompt
            self._connection.write(RAW_MODE_CMD)
            self._forward_output_until_active_prompt(self._send_output)

    def _fetch_welcome_text(self) -> str:
        self._connection.write(NORMAL_MODE_CMD)
        self._raw_prompt_ensured = False
        welcome_text = self._connection.read_until(NORMAL_PROMPT).strip(b"\r\n >")
        if os.name != "nt":
            welcome_text = welcome_text.replace(b"\r\n", b"\n")

        return self._decode(welcome_text)

    def _fetch_builtin_modules(self):
        script = "help('modules')"
        out, err = self._execute(script, capture_output=True)
        if err or not out:
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

    def _resolve_unknown_epoch(self) -> int:
        if self._connected_to_circuitpython() or self._connected_to_pycom():
            return 1970
        else:
            return 2000

    def _sync_time(self):
        """Sets the time on the pyboard to match the time on the host."""

        # RTC works on UTC
        now = datetime.datetime.now(tz=datetime.timezone.utc).timetuple()

        if self._connected_to_microbit():
            return
        elif self._connected_to_circuitpython():
            specific_script = dedent(
                """
                from rtc import RTC as __thonny_RTC
                __thonny_RTC().datetime = {ts}
                del __thonny_RTC
            """
            ).format(ts=tuple(now))
        else:
            specific_script = dedent(
                """
                from machine import RTC as __thonny_RTC
                try:
                    __thonny_RTC().datetime({datetime_ts})
                except:
                    __thonny_RTC().init({init_ts})
                del __thonny_RTC

            """
            ).format(
                datetime_ts=(
                    now.tm_year,
                    now.tm_mon,
                    now.tm_mday,
                    now.tm_wday + 1,
                    now.tm_hour,
                    now.tm_min,
                    now.tm_sec,
                    0,
                ),
                init_ts=tuple(now)[:6] + (0, 0),
            )

        script = (
            dedent(
                """
            try:
            %s
                __thonny_helper.print_mgmt_value(True)
            except Exception as e:
                __thonny_helper.print_mgmt_value(str(e))
        """
            )
            % indent(specific_script, "    ")
        )

        val = self._evaluate(script)
        if isinstance(val, str):
            print("WARNING: Could not sync device's clock: " + val)

    def _get_utc_timetuple_from_device(self) -> Union[tuple, str]:
        if self._connected_to_microbit():
            return "This device does not have a real-time clock"
        elif self._connected_to_circuitpython():
            specific_script = dedent(
                """
                from rtc import RTC as __thonny_RTC
                __thonny_helper.print_mgmt_value(tuple(__thonny_RTC().datetime)[:6])
                del __thonny_RTC
                """
            )
        else:
            specific_script = dedent(
                """
                from machine import RTC as __thonny_RTC
                try:
                    # now() on some devices also gives weekday, so prefer datetime
                    __thonny_temp = tuple(__thonny_RTC().datetime())
                    # remove weekday from index 3
                    __thonny_helper.print_mgmt_value(__thonny_temp[0:3] + __thonny_temp[4:7])
                    del __thonny_temp
                except:
                    __thonny_helper.print_mgmt_value(tuple(__thonny_RTC().now())[:6])
                del __thonny_RTC
                """
            )

        script = (
            dedent(
                """
            try:
            %s
            except Exception as e:
                __thonny_helper.print_mgmt_value(str(e))
        """
            )
            % indent(specific_script, "    ")
        )

        val = self._evaluate(script)
        return val

    def _get_actual_time_tuple_on_device(self):
        script = dedent(
            """
            try:
                try:
                    from time import localtime as __thonny_localtime
                    __thonny_helper.print_mgmt_value(tuple(__thonny_localtime()))
                    del __thonny_localtime
                except:
                    # some CP boards
                    from rtc import RTC as __thonny_RTC
                    __thonny_helper.print_mgmt_value(tuple(__thonny_RTC().datetime))
                    del __thonny_RTC
            except Exception as e:
                __thonny_helper.print_mgmt_value(str(e))
        """
        )

        return self._evaluate(script)

    def _update_cwd(self):
        if self._connected_to_microbit():
            self._cwd = ""
        else:
            super()._update_cwd()

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
            self._connection.reset_output_buffer()  # cancels previous writes
            self._connection.write(INTERRUPT_CMD)
            self._connection.write(RAW_MODE_CMD)
            time.sleep(delay)
            discarded_bytes += self._connection.read_all()
            if discarded_bytes.endswith(FIRST_RAW_PROMPT) or discarded_bytes.endswith(
                W600_FIRST_RAW_PROMPT
            ):
                self._soft_reboot_after_interrupting_to_raw_prompt()
                self._raw_prompt_ensured = True
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

    def _soft_reboot_after_interrupting_to_raw_prompt(self):
        self._connection.write(SOFT_REBOOT_CMD)
        # CP runs code.py after soft-reboot even in raw repl, so I'll send some Ctrl-C to intervene
        # # (they don't do anything in raw repl)
        self._connection.write(INTERRUPT_CMD)
        self._connection.write(INTERRUPT_CMD)
        output = self._connection.soft_read_until(FIRST_RAW_PROMPT, timeout=2)
        if not output.endswith(FIRST_RAW_PROMPT):
            self._show_error("Could not soft-reboot after reaching raw prompt. Got %s" % output)

    def _soft_reboot(self):
        # Need to go to normal mode. MP doesn't run user code in raw mode
        # (CP does, but it doesn't hurt to do it there as well)
        self._connection.write(NORMAL_MODE_CMD)
        self._raw_prompt_ensured = False
        self._connection.read_until(NORMAL_PROMPT)
        self._connection.write(SOFT_REBOOT_CMD)
        self._forward_output_until_active_prompt(self._send_output)
        self._ensure_raw_prompt()
        self.send_message(ToplevelResponse(cwd=self._cwd))

    def _transform_output(self, data, stream_name):
        # Any keypress wouldn't work
        return data.replace(
            "Press any key to enter the REPL. Use CTRL-D to reload.",
            "Press Ctrl-C to enter the REPL. Use CTRL-D to reload.",
        )

    def _write(self, data):
        self._connection.write(data)

    def _submit_input(self, cdata: str) -> None:
        # TODO: what if there is a previous unused data waiting
        assert self._connection.outgoing_is_empty()

        assert cdata.endswith("\n")
        if not cdata.endswith("\r\n"):
            # submission is done with CRLF
            cdata = cdata[:-1] + "\r\n"

        bdata = cdata.encode(ENCODING)

        with self._interrupt_lock:
            self._write(bdata)
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
            logging.warning("Unexpected echo. Expected %r, got %r" % (bdata, echo))
            self._connection.unread(echo)

    def _submit_code(self, script):
        assert script  # otherwise EOT produces soft reboot

        # assuming we are already in a prompt
        self._forward_unexpected_output()
        self._ensure_raw_prompt()

        # send command
        with self._interrupt_lock:
            self._connection.write(script.encode(ENCODING) + EOT)
            debug("Wrote " + script + "\n--------\n")

            # fetch command confirmation
            confirmation = self._connection.soft_read(2, timeout=WAIT_OR_CRASH_TIMEOUT)

        if confirmation != OK:
            data = confirmation + self._connection.read_all()
            data += self._connection.read(1, timeout=1, timeout_is_soft=True)
            data += self._connection.read_all()
            self._report_internal_error(
                "Could not read command confirmation. Got " + repr(data) + "\n\nSCRIPT:\n" + script
            )
        else:
            debug("GOTOK")

    def _ensure_raw_prompt(self):
        if self._raw_prompt_ensured:
            return

        debug("Ensuring raw prompt")
        self._connection.write(RAW_MODE_CMD)

        prompt = (
            self._connection.read_until(
                FIRST_RAW_PROMPT_SUFFIX, timeout=WAIT_OR_CRASH_TIMEOUT, timeout_is_soft=True
            )
            + self._connection.read_all()
        )

        if not prompt.endswith(FIRST_RAW_PROMPT_SUFFIX):
            self._send_output(prompt, "stdout")
            raise TimeoutError("Could not ensure raw prompt")

        self._raw_prompt_ensured = True
        debug("Restoring helpers")
        self._prepare_helpers()
        self._update_cwd()

    def _execute_with_consumer(self, script, output_consumer: Callable[[str, str], None]):
        """Expected output after submitting the command and reading the confirmation is following:

        stdout
        EOT
        stderr
        EOT
        RAW_PROMPT
        """

        self._submit_code(script)

        terminator = self._forward_output_until_eot_or_active_propmt(output_consumer, "stdout")
        if terminator != EOT:
            # an unexpected prompt
            return

        terminator = self._forward_output_until_eot_or_active_propmt(output_consumer, "stderr")
        if terminator != EOT:
            # an unexpected prompt
            return

        data = self._connection.read(1) + self._connection.read_all()
        if data == RAW_PROMPT:
            # happy path
            self._raw_prompt_ensured = True
            return
        else:
            self._connection.unread(data)
            self._forward_output_until_active_prompt(output_consumer, "stdout")

    def _forward_output_until_active_prompt(
        self, output_consumer: Callable[[str, str], None], stream_name="stdout"
    ):
        """Used for finding initial prompt or forwarding problematic output
        in case of parse errors"""
        while True:
            terminator = self._forward_output_until_eot_or_active_propmt(
                output_consumer, stream_name
            )
            if terminator in (NORMAL_PROMPT, RAW_PROMPT, FIRST_RAW_PROMPT):
                self._raw_prompt_ensured = terminator in (RAW_PROMPT, FIRST_RAW_PROMPT)
                return terminator
            else:
                output_consumer(self._decode(terminator), "stdout")

    def _forward_output_until_eot_or_active_propmt(self, output_consumer, stream_name="stdout"):
        """Meant for incrementally forwarding stdout from user statements,
        scripts and soft-reboots. Also used for forwarding side-effect output from
        expression evaluations and for capturing help("modules") output.
        In these cases it is expected to arrive to an EOT.

        Also used for initial prompt searching or for recovering from a protocol error.
        In this case it must work until active normal prompt or first raw prompt.

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

        The method returns EOT, RAW_PROMPT or NORMAL_PROMPT, depending on which terminator
        ended the processing.

        The terminating EOT may be either the first EOT from normal raw-REPL
        output or the starting EOT from Thonny expression (or, in principle, even
        the second raw-REPL EOT or terminating Thonny expression EOT)
        -- the caller will do the interpretation.

        Because ot the special role of EOT and NORMAL_PROMT, we assume user code
        will not output these. If it does, processing may break.
        It may succceed if the propmt is followed by something (quickly enough)
        -- that's why we look for *active* prompt, ie. prompt without following text.
        TODO: Experiment with this!

        Output produced by background threads (eg. in WiPy ESP32) cause even more difficulties,
        because it becomes impossible to say whether we are at prompt and output
        is from another thread or the main thread is still running.
        For now I'm ignoring these problems and assume all output comes from the main thread.
        """
        INCREMENTAL_OUTPUT_BLOCK_CLOSERS = re.compile(
            b"|".join(map(re.escape, [FIRST_RAW_PROMPT, NORMAL_PROMPT, LF, EOT]))
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
                # TODO: this suggestion should be implemented in Shell
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

                if not pending:
                    # nothing to parse
                    continue

            pending += new_data

            if pending.endswith(EOT):
                output_consumer(self._decode(pending[: -len(EOT)]), stream_name)
                return EOT

            elif pending.endswith(LF) and not pending.endswith(FIRST_RAW_PROMPT[:-1]):
                output_consumer(self._decode(pending), stream_name)
                pending = b""

            elif pending.endswith(NORMAL_PROMPT) or pending.endswith(FIRST_RAW_PROMPT):
                # This looks like prompt.
                # Make sure it is not followed by anything.
                # Note that in this context the prompt usually means something is wrong
                # (EOT would have been the happy path), so no need to hurry.
                # The only case where this path is happy path is just after connecting.
                follow_up = self._connection.soft_read(1, timeout=0.5)
                if follow_up:
                    # Nope, the prompt is not active.
                    # (Actually it may be that a background thread has produced this follow up,
                    # but this would be too hard to consider.)
                    # Don't output yet, because the follow up may turn into another prompt
                    # and they can be captured all together.
                    self._connection.unread(follow_up)
                    # read propmt must remain in pending
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
                    output_consumer(self._decode(out), stream_name)

                    return terminator

            elif ends_overlap(pending, NORMAL_PROMPT) or ends_overlap(pending, FIRST_RAW_PROMPT):
                # Maybe we have a prefix of the prompt and the rest is still coming?
                # (it's OK to wait a bit, as the user output usually ends with a newline, ie not
                # with a prompt prefix)
                follow_up = self._connection.soft_read(1, timeout=0.3)
                if not follow_up:
                    # most likely not a Python prompt, let's forget about it
                    output_consumer(self._decode(pending), stream_name)
                    pending = b""
                else:
                    # Let's try the possible prefix again in the next iteration
                    # (I'm unreading otherwise the read_until won't see the whole prompt
                    # and needs to wait for the timeout)
                    if ends_overlap(pending, NORMAL_PROMPT):
                        n = ends_overlap(pending, NORMAL_PROMPT)
                    else:
                        n = ends_overlap(pending, FIRST_RAW_PROMPT)

                    try_again = pending[-n:]
                    pending = pending[:-n]
                    self._connection.unread(try_again + follow_up)

            else:
                # No EOT or prompt in sight.
                # Output and keep working.
                output_consumer(self._decode(pending), stream_name)
                pending = b""

    def _forward_unexpected_output(self, stream_name="stdout"):
        "Invoked between commands"
        data = self._connection.read_all()
        if data:
            self._raw_prompt_ensured = data.endswith(FIRST_RAW_PROMPT)

            met_prompt = False
            while data.endswith(NORMAL_PROMPT) or data.endswith(FIRST_RAW_PROMPT):
                # looks like the device was resetted
                met_prompt = True

                if data.endswith(NORMAL_PROMPT):
                    terminator = NORMAL_PROMPT
                else:
                    terminator = FIRST_RAW_PROMPT

                # hide the prompt from the output ...
                data = data[: -len(terminator)]

            self._send_output(data.decode(ENCODING, "replace"), stream_name)
            if met_prompt:
                # ... and recreate Thonny prompt
                self.send_message(ToplevelResponse())

    def _cmd_execute_system_command(self, cmd):
        # Can't use stdin, because a thread is draining it
        execute_system_command(cmd, cwd=self._local_cwd, disconnect_stdin=True)

    def _cmd_get_fs_info(self, cmd):
        result = self._evaluate(
            dedent(
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
                __thonny_sizes = [__thonny_helper.os.size(name) for name in __thonny_helper.listdir()]
                __thonny_used = None
                __thonny_total = None
                __thonny_free = None
            
            __thonny_helper.print_mgmt_value({
                "total" : __thonny_total,
                "used" : __thonny_used,
                "free": __thonny_free,
                "sizes": __thonny_sizes
            })  
                
            del __thonny_total
            del __thonny_free
            del __thonny_used
            del __thonny_sizes
            """
            )
            % cmd.path
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

    def _cmd_upload(self, cmd):
        self._check_sync_time()
        return super(BareMetalMicroPythonBackend, self)._cmd_upload(cmd)

    def _cmd_write_file(self, cmd):
        self._check_sync_time()
        return super(BareMetalMicroPythonBackend, self)._cmd_write_file(cmd)

    def _delete_sorted_paths(self, paths):
        if not self._supports_directories():
            # micro:bit
            self._execute_without_output(
                dedent(
                    """
                for __thonny_path in %r: 
                    __thonny_helper.os.remove(__thonny_path)
                    
                del __thonny_path
                
            """
                )
                % paths
            )
        else:
            try:
                super()._delete_sorted_paths(paths)
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

    def _get_stat_mode_for_upload(self, path: str) -> Optional[int]:
        return self._get_stat_mode(path)

    def _mkdir_for_upload(self, path: str) -> None:
        self._mkdir(path)

    def _read_file(
        self, source_path: str, target_fp: BinaryIO, callback: Callable[[int, int], None]
    ) -> None:
        # TODO: Is it better to read from mount when possible? Is the mount up to date when the file
        # is written via serial? Does the MP API give up to date bytes when the file is written via mount?

        hex_mode = self._should_hexlify(source_path)

        self._execute_without_output("__thonny_fp = open(%r, 'rb')" % source_path)
        if hex_mode:
            self._execute_without_output("from binascii import hexlify as __temp_hexlify")

        block_size = 1024
        file_size = self._get_file_size(source_path)
        num_bytes_read = 0
        while True:
            callback(num_bytes_read, file_size)
            if hex_mode:
                block = binascii.unhexlify(
                    self._evaluate("__temp_hexlify(__thonny_fp.read(%s))" % block_size)
                )
            else:
                block = self._evaluate("__thonny_fp.read(%s)" % block_size)

            if block:
                target_fp.write(block)
                num_bytes_read += len(block)

            if len(block) < block_size:
                break

        self._execute_without_output(
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

    def _write_file(
        self,
        source_fp: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
    ) -> None:
        try:
            self._write_file_via_serial(source_fp, target_path, file_size, callback)
        except ReadOnlyFilesystemError:
            self._write_file_via_mount(source_fp, target_path, file_size, callback)

        # self._sync_all_filesystems()

    def _write_file_via_mount(
        self,
        source: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
    ) -> None:
        mounted_target_path = self._internal_path_to_mounted_path(target_path)
        with open(mounted_target_path, "wb") as f:
            bytes_written = 0
            block_size = 4 * 1024
            while True:
                callback(bytes_written, file_size)
                block = source.read(block_size)
                if block:
                    bytes_written += f.write(block)
                    f.flush()
                    os.fsync(f)

                if len(block) < block_size:
                    break

        assert bytes_written == file_size

        return bytes_written

    def _write_file_via_serial(
        self,
        source_fp: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
    ) -> None:
        out, err = self._execute(
            dedent(
                """
            try:
                __thonny_path = '{path}'
                __thonny_written = 0
                __thonny_fp = open(__thonny_path, 'wb')
            except Exception as e:
                print(str(e))
            """
            ).format(path=target_path),
            capture_output=True,
        )

        if "readonly" in (out + err).replace("-", "").lower():
            raise ReadOnlyFilesystemError()
        elif out + err:
            raise RuntimeError(
                "Could not open file %s for writing, output:\n%s" % (target_path, out + err)
            )

        # Define function to allow shorter write commands
        hex_mode = self._should_hexlify(target_path)
        if hex_mode:
            self._execute_without_output(
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
            self._execute_without_output(
                dedent(
                    """
                def __W(x):
                    global __thonny_written
                    __thonny_written += __thonny_fp.write(x)
            """
                )
            )

        bytes_sent = 0
        block_size = 512
        while True:
            callback(bytes_sent, file_size)
            block = source_fp.read(block_size)

            if block:
                if hex_mode:
                    script = "__W(%r)" % binascii.hexlify(block)
                else:
                    script = "__W(%r)" % block
                out, err = self._execute(script, capture_output=True)
                if out or err:
                    self._show_error(
                        "\nCould not write next block after having written %d bytes to %s"
                        % (bytes_sent, target_path)
                    )
                    if bytes_sent > 0:
                        self._show_error(
                            "Make sure your device's filesystem has enough free space. "
                            + "(When overwriting a file, the old content may occupy space "
                            "until the end of the operation.)\n"
                        )
                    raise ManagementError(script, out, err)
                bytes_sent += len(block)

            if len(block) < block_size:
                break

        bytes_received = self._evaluate("__thonny_written")

        if bytes_received != bytes_sent:
            raise UserError("Expected %d written bytes but wrote %d" % (bytes_sent, bytes_received))

        # clean up
        self._execute_without_output(
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
        self._execute_without_output(
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

    def _makedirs(self, path):
        if path == "/":
            return

        try:
            super()._makedirs(path)
        except Exception as e:
            if "read-only" in str(e).lower():
                self._makedirs_via_mount(path)

        self._sync_all_filesystems()

    def _makedirs_via_mount(self, path):
        mounted_path = self._internal_path_to_mounted_path(path)
        assert mounted_path is not None, "Couldn't find mounted path for " + path
        os.makedirs(mounted_path, exist_ok=True)

    def _delete_via_mount(self, paths):
        for path in paths:
            mounted_path = self._internal_path_to_mounted_path(path)
            assert mounted_path is not None
            import shutil

            shutil.rmtree(mounted_path)

    def _get_fs_mount_label(self):
        # This method is most likely required with CircuitPython,
        # so try its approach first
        # https://learn.adafruit.com/welcome-to-circuitpython/the-circuitpy-drive
        result = self._evaluate(
            dedent(
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
            
            __thonny_helper.print_mgmt_value(__thonny_result)
            
            del __thonny_result
            """
            )
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

    def _should_hexlify(self, path):
        if "binascii" not in self._builtin_modules:
            return False

        for ext in (".py", ".txt", ".csv"):
            if path.lower().endswith(ext):
                return False

        return True

    def _is_connected(self):
        return self._connection._error is None

    def _get_epoch_offset(self) -> int:
        # https://docs.micropython.org/en/latest/library/utime.html
        # NB! Some boards (eg Pycom) may use Posix epoch!
        try:
            return super()._get_epoch_offset()
        except NotImplementedError:
            return Y2000_EPOCH_OFFSET

    def _get_sep(self):
        if self._supports_directories():
            return "/"
        else:
            return ""

    def _decode(self, data: bytes) -> str:
        return data.decode(ENCODING, errors="replace")


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

    import ast
    import sys

    args = ast.literal_eval(sys.argv[1])

    try:
        if args["port"] is None:
            # remain busy
            while True:
                time.sleep(1000)
        elif args["port"] == "webrepl":
            from thonny.plugins.micropython.webrepl_connection import WebReplConnection

            connection = WebReplConnection(args["url"], args["password"], args["min_write_delay"])
        else:
            from thonny.plugins.micropython.serial_connection import (
                DifficultSerialConnection,
                SerialConnection,
            )

            connection = SerialConnection(args["port"], BAUDRATE)
            # connection = DifficultSerialConnection(args["port"], BAUDRATE)

        backend = BareMetalMicroPythonBackend(connection, clean=args["clean"], args=args)

    except ConnectionFailedException as e:
        text = "\n" + str(e) + "\n"
        msg = BackendEvent(event_type="ProgramOutput", stream_name="stderr", data=text)
        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()
