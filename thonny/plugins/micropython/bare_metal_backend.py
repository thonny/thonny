import binascii
import datetime
import logging
import os
import queue
import re
import struct
import time
from textwrap import dedent, indent
from typing import BinaryIO, Callable, Optional, Tuple, Union

import thonny
from thonny.backend import UploadDownloadMixin
from thonny.common import (
    BackendEvent,
    InlineResponse,
    ToplevelResponse,
    UserError,
    execute_system_command,
    serialize_message,
    EOFCommand,
)
from thonny.misc_utils import find_volumes_by_name, sizeof_fmt
from thonny.plugins.micropython.backend import (
    MicroPythonBackend,
    ManagementError,
    ReadOnlyFilesystemError,
    ends_overlap,
    Y2000_EPOCH_OFFSET,
    PASTE_MODE_CMD,
    PASTE_MODE_LINE_PREFIX,
    EOT,
    WAIT_OR_CRASH_TIMEOUT,
)
from thonny.common import ConnectionFailedException
from thonny.plugins.micropython.webrepl_connection import (
    WebReplConnection,
    WebreplBinaryMsg,
)

PASTE_SUBMIT_MODE = "paste"
RAW_PASTE_SUBMIT_MODE = "raw_paste"
RAW_SUBMIT_MODE = "raw"

RAW_PASTE_COMMAND = b"\x05A\x01"
RAW_PASTE_CONFIRMATION = b"R\x01"
RAW_PASTE_CONTINUE = b"\x01"

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
NORMAL_PROMPT = b">>> "
LF = b"\n"
OK = b"OK"

# first prompt when switching to raw mode (or after soft reboot in raw mode)
# Looks like it's not translatable in CP
# https://github.com/adafruit/circuitpython/blob/master/locale/circuitpython.pot
FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\n>"

# https://forum.micropython.org/viewtopic.php?f=12&t=7652&hilit=w600#p43640
W600_FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\r\n>"

RAW_PROMPT = b">"

WEBREPL_REQ_S = "<2sBBQLH64s"
WEBREPL_PUT_FILE = 1
WEBREPL_GET_FILE = 2

TRACEBACK_MARKER = b"Traceback (most recent call last):"

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

# Can't use __name__, because it will be "__main__"
logger = logging.getLogger("thonny.plugins.micropython.bare_metal_backend")


def debug(msg):
    return
    # print(msg, file=sys.stderr)


class BareMetalMicroPythonBackend(MicroPythonBackend, UploadDownloadMixin):
    def __init__(self, connection, clean, args):
        self._connection = connection
        self._startup_time = time.time()
        self._interrupt_suggestion_given = False

        # https://forum.micropython.org/viewtopic.php?f=15&t=3698
        # https://forum.micropython.org/viewtopic.php?f=15&t=4896&p=28132
        self._write_block_size = args.get("write_block_size", None)
        self._write_block_delay = args.get("write_block_delay", None)
        if self._write_block_size is None:
            self._write_block_size = 255
        if self._write_block_delay is None:
            if self._connected_over_webrepl():
                # ESP-32 needs long delay to work reliably over raw mode WebREPL
                # TODO: consider removing when this gets fixed
                self._write_block_delay = 0.5
            else:
                self._write_block_delay = 0.01

        self._submit_mode = args.get("submit_mode", None)
        logger.debug(
            "Initial submit_mode: %s, block_size: %s, block_delay: %s",
            self._submit_mode,
            self._write_block_size,
            self._write_block_delay,
        )

        self._last_prompt = None

        MicroPythonBackend.__init__(self, clean, args)

    def _check_prepare(self):
        out, err = self._execute("print('__thonny_helper' in dir())", capture_output=True)
        if out.strip() == "True":
            return

        self._prepare_after_soft_reboot(False)

    def _get_custom_helpers(self):
        if self._connected_to_microbit():
            return ""

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
        logger.debug("_process_until_initial_prompt, clean=%s", clean)
        if clean:
            self._interrupt_to_raw_prompt()
            self._soft_reboot_in_raw_prompt_without_running_main()
        else:
            # Discard what's printed by now and order a prompt, so that we get to know
            # if the REPL is already idle
            discarded = self._connection.read_all()
            self._write(RAW_MODE_CMD)
            self._forward_output_until_active_prompt(self._send_output)

        if self._submit_mode is None:
            self._choose_submit_mode()

    def _choose_submit_mode(self):
        if self._connected_over_webrepl():
            logger.info("Choosing paste submit mode because of WebREPL")
            self._submit_mode = PASTE_SUBMIT_MODE
            return

        # at least sometimes, we end up at normal prompt, although we asked for raw prompt
        self._ensure_raw_mode()
        self._write(RAW_PASTE_COMMAND)
        response = self._connection.soft_read(2)
        assert len(response) == 2, "Could not read response for raw paste command: " + response
        if response == RAW_PASTE_CONFIRMATION:
            logger.info("Choosing raw paste submit mode")
            self._submit_mode = RAW_PASTE_SUBMIT_MODE
            self._write(EOT)
            discarding = self._connection.read_until(RAW_PROMPT)
        else:
            discarding = self._connection.read_until(RAW_PROMPT)
            logger.info("Choosing raw submit mode (%r)", response + discarding)
            self._submit_mode = RAW_SUBMIT_MODE

        discarding += self._connection.read_all()

    def _fetch_welcome_text(self) -> str:
        self._write(NORMAL_MODE_CMD)
        out, err = self._capture_output_until_active_prompt()
        welcome_text = out.strip("\r\n >")
        if os.name != "nt":
            welcome_text = welcome_text.replace("\r\n", "\n")

        return welcome_text

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
        """Sets the time to match the time on the host."""

        now = self._get_time_for_rtc()

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

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        self._soft_reboot_for_restarting_user_program()

    def _interrupt_to_raw_prompt(self):
        # NB! Sometimes disconnecting and reconnecting (on macOS?)
        # too quickly causes anomalies. See CalliopeMiniProxy for more details
        logger.debug("_interrupt_to_raw_prompt")
        discarded_bytes = b""

        for delay in [0.05, 0.5, 0.1, 1.0, 3.0, 5.0]:
            # Interrupt several times, because with some drivers first interrupts seem to vanish
            if delay >= 1:
                self._show_error(
                    "Could not enter REPL. Trying again with %d second waiting time..." % delay
                )
            self._connection.reset_output_buffer()  # cancels previous writes
            self._write(INTERRUPT_CMD)
            self._write(RAW_MODE_CMD)
            time.sleep(delay)
            self._capture_output_until_active_prompt()
            if self._last_prompt in [FIRST_RAW_PROMPT, W600_FIRST_RAW_PROMPT]:
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

        logger.debug("Done _interrupt_to_raw_prompt")

    def _soft_reboot_in_raw_prompt_without_running_main(self):
        logger.debug("_soft_reboot_in_raw_prompt_without_running_main")
        self._write(SOFT_REBOOT_CMD + INTERRUPT_CMD)
        self._check_reconnect()
        self._capture_output_until_active_prompt()

        logger.debug("Done soft reboot in raw prompt")

    def _ensure_raw_mode(self):
        if self._last_prompt in [
            RAW_PROMPT,
            EOT + RAW_PROMPT,
            FIRST_RAW_PROMPT,
            W600_FIRST_RAW_PROMPT,
        ]:
            return
        logger.debug("requesting raw mode at %r", self._last_prompt)

        # assuming we are currently on a normal prompt
        self._write(RAW_MODE_CMD)
        out, err = self._capture_output_until_active_prompt()
        if self._last_prompt == NORMAL_PROMPT:
            # Don't know why this happens sometimes (eg. when interrupting a Ctrl+D or restarted
            # program, which is outputting text on ESP32)
            logger.info("Found normal prompt instead of expected raw prompt. Trying again.")
            self._write(RAW_MODE_CMD)
            time.sleep(0.5)
            out, err = self._capture_output_until_active_prompt()

        if self._last_prompt not in [FIRST_RAW_PROMPT, W600_FIRST_RAW_PROMPT]:
            raise AssertionError(
                "Could not enter raw prompt, got %r"
                % ((out + err).encode(ENCODING) + self._last_prompt)
            )

    def _ensure_normal_mode(self, force=False):
        if self._last_prompt == NORMAL_PROMPT and not force:
            return

        logger.debug("requesting normal mode at %r", self._last_prompt)
        self._write(NORMAL_MODE_CMD)
        self._capture_output_until_active_prompt()
        assert self._last_prompt == NORMAL_PROMPT, (
            "Could not get normal prompt, got %s" % self._last_prompt
        )

    def _soft_reboot_without_running_main(self):
        logger.debug("_soft_reboot_without_running_main")
        self._interrupt_to_raw_prompt()
        self._soft_reboot_in_raw_prompt_without_running_main()
        logger.debug("Done _soft_reboot_without_running_main")

    def _soft_reboot_for_restarting_user_program(self):
        # Need to go to normal mode. MP doesn't run user code in raw mode
        # (CP does, but it doesn't hurt to do it there as well)
        logger.debug("_soft_reboot_for_restarting_user_program")
        self._ensure_normal_mode()
        self._write(SOFT_REBOOT_CMD)
        self._check_reconnect()
        self._forward_output_until_active_prompt(self._send_output)
        logger.debug("Restoring helpers")
        self._prepare_after_soft_reboot(False)
        self.send_message(ToplevelResponse(cwd=self._cwd))
        logger.debug("_soft_reboot_for_restarting_user_program")

    def _check_reconnect(self):
        if self._connected_over_webrepl():
            time.sleep(1)
            logger.info("Reconnecting to WebREPL")
            self._connection = self._connection.close_and_return_new_connection()

    def _connected_over_webrepl(self):
        from thonny.plugins.micropython.webrepl_connection import WebReplConnection

        return isinstance(self._connection, WebReplConnection)

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
        to_be_written = bdata
        echo = b""
        with self._interrupt_lock:
            while to_be_written:
                block = self._extract_block_without_splitting_chars(to_be_written)
                self._write(block)
                # Try to consume the echo
                echo += self._connection.soft_read(len(block), timeout=1)
                to_be_written = to_be_written[len(block) :]

        if echo != bdata:
            # because of autoreload? timing problems? interruption?
            # Leave it.
            logging.warning("Unexpected echo. Expected %r, got %r" % (bdata, echo))
            self._connection.unread(echo)

    def _submit_code(self, script):
        """
        Code is submitted via paste mode, because this provides echo, which can be used as flow control.

        The echo of a written block must be read before next block is written.
        Safe USB block size is 64 bytes (may be larger for some devices),
        but we need to account for b"=== " added by the paste mode in the echo, so each block is sized such that
        its echo doesn't exceed self._write_block_size (some devices may have problem with outputs bigger than that).
        (OK, most likely the reading thread will eliminate the problem with output buffer, but just in case...)
        """
        assert script

        # assuming we are already at a prompt, but threads may have produced something
        self._forward_unexpected_output()

        to_be_sent = script.encode("UTF-8")
        logger.debug("Submitting via %s: %r", self._submit_mode, to_be_sent[:70])
        with self._interrupt_lock:
            if self._submit_mode == PASTE_SUBMIT_MODE:
                self._submit_code_via_paste_mode(to_be_sent)
            elif self._submit_mode == RAW_PASTE_SUBMIT_MODE:
                try:
                    self._submit_code_via_raw_paste_mode(to_be_sent)
                except RawPasteNotSupportedError:
                    logger.info("WARNING: Could not use expected raw paste, falling back to raw")
                    self._submit_code_via_raw_mode(to_be_sent)
            else:
                self._submit_code_via_raw_mode(to_be_sent)

    def _submit_code_via_paste_mode(self, script_bytes: bytes) -> None:
        # Go to paste mode
        self._ensure_normal_mode()
        self._connection.write(PASTE_MODE_CMD)
        self._connection.read_until(PASTE_MODE_LINE_PREFIX)

        # Send script
        while script_bytes:
            block = script_bytes[: self._write_block_size]
            script_bytes = script_bytes[self._write_block_size :]

            # find proper block boundary
            while True:
                expected_echo = block.replace(b"\r\n", b"\r\n" + PASTE_MODE_LINE_PREFIX)
                if (
                    len(expected_echo) > self._write_block_size
                    or block.endswith(b"\r")
                    or len(block) > 2
                    and starts_with_continuation_byte(script_bytes)
                ):
                    # move last byte to the next block
                    script_bytes = block[-1:] + script_bytes
                    block = block[:-1]
                    continue
                else:
                    break

            self._write(block)
            self._connection.read_all_expected(expected_echo, timeout=WAIT_OR_CRASH_TIMEOUT)

        # push and read comfirmation
        self._connection.write(EOT)
        expected_confirmation = b"\r\n"
        actual_confirmation = self._connection.read(
            len(expected_confirmation), timeout=WAIT_OR_CRASH_TIMEOUT
        )
        assert actual_confirmation == expected_confirmation, "Expected %r, got %r" % (
            expected_confirmation,
            actual_confirmation,
        )

    def _submit_code_via_raw_mode(self, script_bytes: bytes) -> None:
        self._ensure_raw_mode()

        to_be_written = script_bytes + EOT

        while to_be_written:
            block = self._extract_block_without_splitting_chars(to_be_written)
            self._write(block)
            to_be_written = to_be_written[len(block) :]
            if to_be_written:
                time.sleep(self._write_block_delay)

        # fetch command confirmation
        confirmation = self._connection.soft_read(2, timeout=WAIT_OR_CRASH_TIMEOUT)

        if confirmation != OK:
            data = confirmation + self._connection.read_all()
            data += self._connection.read(1, timeout=1, timeout_is_soft=True)
            data += self._connection.read_all()
            raise AssertionError(
                "Could not read command confirmation. Got "
                + repr(data)
                + "\n\nSCRIPT:\n"
                + repr(script_bytes)
            )

    def _submit_code_via_raw_paste_mode(self, script_bytes: bytes) -> None:
        self._ensure_raw_mode()
        self._connection.set_unicode_guard(False)
        self._write(RAW_PASTE_COMMAND)
        response = self._connection.soft_read(2, timeout=WAIT_OR_CRASH_TIMEOUT)
        if response != RAW_PASTE_CONFIRMATION:
            # Occasionally, the device initially supports raw paste but later doesn't allow it
            # https://github.com/thonny/thonny/issues/1545
            time.sleep(0.01)
            response += self._connection.read_all()
            if response == FIRST_RAW_PROMPT:
                self._last_prompt = FIRST_RAW_PROMPT
                raise RawPasteNotSupportedError()
            else:
                raise AssertionError("Got %r instead of raw-paste confirmation" % response)

        self._raw_paste_write(script_bytes)
        self._connection.set_unicode_guard(True)

    def _raw_paste_write(self, command_bytes):
        # Adapted from https://github.com/micropython/micropython/commit/a59282b9bfb6928cd68b696258c0dd2280244eb3#diff-cf10d3c1fe676599a983c0ec85b78c56c9a6f21b2d896c69b3e13f34d454153e

        # Read initial header, with window size.
        data = self._connection.soft_read(2, timeout=2)
        assert len(data) == 2, "Could not read initial header, got %r" % (
            data + self._connection.read_all()
        )
        window_size = data[0] | data[1] << 8
        window_remain = window_size

        # Write out the command_bytes data.
        i = 0
        while i < len(command_bytes):
            while window_remain == 0 or not self._connection.incoming_is_empty():
                data = self._connection.soft_read(1, timeout=WAIT_OR_CRASH_TIMEOUT)
                if data == b"\x01":
                    # Device indicated that a new window of data can be sent.
                    window_remain += window_size
                elif data == b"\x04":
                    # Device indicated abrupt end, most likely a syntax error.
                    # Acknowledge it and finish.
                    self._connection.write(b"\x04")
                    logger.debug(
                        "Abrupt end of raw paste submit after submitting %s bytes out of %s",
                        i,
                        len(command_bytes),
                    )
                    return
                else:
                    # Unexpected data from device.
                    raise AssertionError("Unexpected read during raw paste: {}".format(data))
            # Send out as much data as possible that fits within the allowed window.
            b = command_bytes[i : min(i + window_remain, len(command_bytes))]
            self._write(b)
            window_remain -= len(b)
            i += len(b)

        # Indicate end of data.
        self._write(b"\x04")

        # Wait for device to acknowledge end of data.
        data = self._connection.soft_read_until(b"\x04", timeout=WAIT_OR_CRASH_TIMEOUT)
        if not data.endswith(b"\x04"):
            raise AssertionError("could not complete raw paste: {}".format(data))

    def _execute_with_consumer(self, script, output_consumer: Callable[[str, str], None]):
        self._report_time("befsubcode")
        self._submit_code(script)
        self._report_time("affsubcode")
        self._forward_output_until_active_prompt(output_consumer)
        self._report_time("affforw")

    def _forward_output_until_active_prompt(
        self, output_consumer: Callable[[str, str], None], stream_name="stdout"
    ):
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
        It may succeed if the prompt is followed by something (quickly enough)
        -- that's why we look for *active* prompt, ie. prompt without following text.
        TODO: Experiment with this!

        Output produced by background threads (eg. in WiPy ESP32) cause even more difficulties,
        because it becomes impossible to say whether we are at prompt and output
        is from another thread or the main thread is still running.
        For now I'm ignoring these problems and assume all output comes from the main thread.
        """

        # Don't want to block on lone EOT (the first EOT), because finding the second EOT
        # together with raw prompt marker is the most important.
        INCREMENTAL_OUTPUT_BLOCK_CLOSERS = re.compile(
            b"|".join(
                map(
                    re.escape,
                    [NORMAL_PROMPT, LF, EOT + RAW_PROMPT, FIRST_RAW_PROMPT, W600_FIRST_RAW_PROMPT],
                )
            )
        )

        prompts = [EOT + RAW_PROMPT, NORMAL_PROMPT, FIRST_RAW_PROMPT, W600_FIRST_RAW_PROMPT]

        pending = b""
        while True:
            # There may be an input submission waiting
            # and we can't progress without resolving it first
            self._check_for_side_commands()

            # Prefer whole lines, but allow also incremental output to single line
            new_data = self._connection.soft_read_until(
                INCREMENTAL_OUTPUT_BLOCK_CLOSERS, timeout=0.05
            )

            # Try to separate stderr from stdout in raw mode
            eot_pos = new_data.find(EOT)
            if (
                eot_pos >= 0
                and new_data[eot_pos : eot_pos + 2] != EOT + RAW_PROMPT
                and stream_name == "stdout"
            ):
                # start of stderr in raw mode
                out, err = new_data.split(EOT, maxsplit=1)
                pending += out
                output_consumer(self._decode(pending), stream_name)
                pending = b""
                new_data = err
                stream_name = "stderr"
            elif self._submit_mode == PASTE_SUBMIT_MODE and TRACEBACK_MARKER in new_data:
                # start of stderr in paste mode
                stream_name = "stderr"

            if not new_data:
                # In case we are still waiting for the first bits after connecting ...
                # TODO: this suggestion should be implemented in Shell
                if (
                    self._connection.num_bytes_received == 0
                    and not self._interrupt_suggestion_given
                    and time.time() - self._connection.startup_time > 2.5
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

            for current_prompt in prompts:
                if pending.endswith(current_prompt):
                    break
            else:
                current_prompt = None

            if current_prompt:
                # This looks like prompt.
                # Make sure it is not followed by anything.
                follow_up = self._connection.soft_read(1, timeout=0.01)
                if follow_up:
                    # Nope, the prompt is not active.
                    # (Actually it may be that a background thread has produced this follow up,
                    # but this would be too hard to consider.)
                    # Don't output yet, because the follow up may turn into another prompt
                    # and they can be captured all together.
                    self._connection.unread(follow_up)
                    # read prompt must remain in pending
                    continue
                else:
                    # let's hope it is an active prompt
                    # Strip all trailing prompts
                    while True:
                        for potential_prompt in prompts:
                            if pending.endswith(potential_prompt):
                                pending = pending[: -len(potential_prompt)]
                        else:
                            break
                    output_consumer(self._decode(pending), stream_name)
                    self._last_prompt = current_prompt
                    # logger.debug("Found prompt %r", current_prompt)
                    return current_prompt

            if pending.endswith(LF):
                # Maybe it's a penultimate char in a first raw repl?
                if pending.endswith(FIRST_RAW_PROMPT[:-1]) or pending.endswith(
                    W600_FIRST_RAW_PROMPT[:-1]
                ):
                    pending += self._connection.soft_read(1)
                    self._connection.unread(pending)
                    pending = b""
                else:
                    output_consumer(self._decode(pending), stream_name)
                    pending = b""
                continue

            for potential_prompt in prompts:
                if ends_overlap(pending, potential_prompt):
                    # Maybe we have a prefix of the prompt and the rest is still coming?
                    # (it's OK to wait a bit, as the user output usually ends with a newline, ie not
                    # with a prompt prefix)
                    follow_up = self._connection.soft_read(1, timeout=0.3)
                    if not follow_up:
                        # most likely not a Python prompt, let's forget about it
                        output_consumer(self._decode(pending), stream_name)
                        pending = b""
                        continue
                    else:
                        # Let's try the possible prefix again in the next iteration
                        # (I'm unreading otherwise the read_until won't see the whole prompt
                        # and needs to wait for the timeout)
                        n = ends_overlap(pending, potential_prompt)

                        try_again = pending[-n:]
                        pending = pending[:-n]
                        self._connection.unread(try_again + follow_up)
                        continue

            else:
                # No prompt in sight.
                # Output and keep working.
                output_consumer(self._decode(pending), stream_name)
                pending = b""
                continue

    def _capture_output_until_active_prompt(self):
        output = {"stdout": "", "stderr": ""}

        def collect_output(data, stream):
            output[stream] += data

        self._forward_output_until_active_prompt(collect_output)

        return output["stdout"], output["stderr"]

    def _forward_unexpected_output(self, stream_name="stdout"):
        "Invoked between commands"
        # TODO: This should be as careful as _forward_output_until_active_prompt
        data = self._connection.read_all(check_error=False)
        if data:
            met_prompt = False
            while data.endswith(NORMAL_PROMPT) or data.endswith(FIRST_RAW_PROMPT):
                # looks like the device was resetted
                if data.endswith(NORMAL_PROMPT):
                    prompt = NORMAL_PROMPT
                else:
                    prompt = FIRST_RAW_PROMPT

                if not met_prompt:
                    met_prompt = True
                    self._last_prompt = prompt

                # hide the prompt from the output ...
                data = data[: -len(prompt)]

            self._send_output(data.decode(ENCODING, "replace"), stream_name)
            if met_prompt:
                self._check_prepare()
                # ... and recreate Thonny prompt
                self.send_message(ToplevelResponse())

    def _cmd_Run(self, cmd):
        """Only for %run $EDITOR_CONTENT. start runs will be handled differently."""
        reset_environment_before_run = True  # TODO: make it configurable
        if cmd.get("source"):
            if reset_environment_before_run:
                self._soft_reboot_without_running_main()

            if self._submit_mode == PASTE_SUBMIT_MODE:
                source = self._avoid_printing_expression_statements(cmd.source)
                if reset_environment_before_run:
                    logger.debug("Ensuring normal mode after soft reboot")
                    self._ensure_normal_mode(force=True)
            else:
                source = cmd.source

            self._execute(source, capture_output=False)
            if reset_environment_before_run:
                self._prepare_after_soft_reboot(False)
        return {}

    def _cmd_execute_system_command(self, cmd):
        # Can't use stdin, because a thread is draining it
        returncode = execute_system_command(cmd, cwd=self._local_cwd, disconnect_stdin=True)
        return {"returncode": returncode}

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
                __thonny_sizes = [__thonny_helper.os.size(name) for name in __thonny_helper.os.listdir()]
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

    def _cmd_prepare_disconnect(self, cmd):
        logger.info("Preparing disconnect")
        # NB! Don't let the mainloop see the prompt and act on it
        self._connection.stop_reader()
        self._write(NORMAL_MODE_CMD)

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

            self._sync_remote_filesystem()

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
        start_time = time.time()

        if self._connected_over_webrepl():
            size = self._read_file_via_webrepl_file_protocol(source_path, target_fp, callback)
        else:
            # TODO: Is it better to read from mount when possible? Is the mount up to date when the file
            # is written via serial? Does the MP API give up to date bytes when the file is written via mount?
            size = self._read_file_via_serial(source_path, target_fp, callback)

        logger.info("Read %s in %.1f seconds", source_path, time.time() - start_time)
        return size

    def _read_file_via_serial(
        self, source_path: str, target_fp: BinaryIO, callback: Callable[[int, int], None]
    ) -> None:

        hex_mode = self._should_hexlify(source_path)

        self._execute_without_output("__thonny_fp = open(%r, 'rb')" % source_path)
        if hex_mode:
            self._execute_without_output("from binascii import hexlify as __temp_hexlify")

        block_size = self._get_file_operation_block_size()
        file_size = self._get_file_size(source_path)
        num_bytes_read = 0
        while True:
            if self._current_command_is_interrupted():
                raise KeyboardInterrupt()
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

    def _read_file_via_webrepl_file_protocol(
        self, source_path: str, target_fp: BinaryIO, callback: Callable[[int, int], None]
    ):
        """
        Adapted from https://github.com/micropython/webrepl/blob/master/webrepl_cli.py
        """
        assert self._connected_over_webrepl()

        file_size = self._get_file_size(source_path)

        src_fname = source_path.encode("utf-8")
        rec = struct.pack(
            WEBREPL_REQ_S, b"WA", WEBREPL_GET_FILE, 0, 0, 0, len(src_fname), src_fname
        )
        self._write(WebreplBinaryMsg(rec))
        assert self._read_websocket_response() == 0

        bytes_read = 0
        callback(bytes_read, file_size)
        while True:
            # report ready
            self._write(WebreplBinaryMsg(b"\0"))

            (block_size,) = struct.unpack("<H", self._connection.read(2))
            if block_size == 0:
                break
            while block_size:
                buf = self._connection.read(block_size)
                if not buf:
                    raise OSError()
                bytes_read += len(buf)
                target_fp.write(buf)
                block_size -= len(buf)
                callback(bytes_read, file_size)

        assert self._read_websocket_response() == 0

    def _write_file(
        self,
        source_fp: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
    ) -> None:
        start_time = time.time()

        if self._connected_over_webrepl():
            self._write_file_via_webrepl_file_protocol(source_fp, target_path, file_size, callback)
        else:
            try:
                self._write_file_via_serial(source_fp, target_path, file_size, callback)
            except ReadOnlyFilesystemError:
                self._write_file_via_mount(source_fp, target_path, file_size, callback)

        logger.info("Wrote %s in %.1f seconds", target_path, time.time() - start_time)
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

        canonic_out = (out + err).replace("-", "").lower()
        if "readonly" in canonic_out or "errno 30" in canonic_out:
            logger.info(
                "Could not write via serial, got '%s'. Assuming read-only filesystem.", out + err
            )
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
                    if hasattr(__thonny_helper.os, "sync"):
                        __thonny_helper.os.sync()
            """
                )
            )
        elif self._connected_to_microbit():
            # doesn't have neither BytesIO.flush, nor os.sync
            self._execute_without_output(
                dedent(
                    """
                def __W(x):
                    global __thonny_written
                    __thonny_written += __thonny_fp.write(x)
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
                    __thonny_fp.flush()
                    if hasattr(__thonny_helper.os, "sync"):
                        __thonny_helper.os.sync()
            """
                )
            )

        bytes_sent = 0
        block_size = self._get_file_operation_block_size()

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

    def _write_file_via_webrepl_file_protocol(
        self,
        source: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
    ) -> None:
        """
        Adapted from https://github.com/micropython/webrepl/blob/master/webrepl_cli.py
        """
        assert self._connected_over_webrepl()

        dest_fname = target_path.encode("utf-8")
        rec = struct.pack(
            WEBREPL_REQ_S, b"WA", WEBREPL_PUT_FILE, 0, 0, file_size, len(dest_fname), dest_fname
        )
        self._write(WebreplBinaryMsg(rec[:10]))
        self._write(WebreplBinaryMsg(rec[10:]))
        assert self._read_websocket_response() == 0

        bytes_sent = 0
        callback(bytes_sent, file_size)
        while True:
            block = source.read(1024)
            if not block:
                break
            self._write(WebreplBinaryMsg(block))
            bytes_sent += len(block)
            callback(bytes_sent, file_size)

        assert self._read_websocket_response() == 0

        return bytes_sent

    def _read_websocket_response(self):
        data = self._connection.read(4)
        sig, code = struct.unpack("<2sH", data)
        assert sig == b"WB"
        return code

    def _sync_remote_filesystem(self):
        self._execute_without_output(
            dedent(
                """
            if hasattr(__thonny_helper.os, "sync"):
                __thonny_helper.os.sync()        
        """
            )
        )

    def _sync_local_filesystem(self):
        if hasattr(os, "sync"):
            os.sync()

    def _mkdir(self, path):
        if path == "/":
            return

        try:
            super()._mkdir(path)
        except ManagementError as e:
            if "read-only" in e.err.lower():
                self._makedirs_via_mount(path)

        self._sync_remote_filesystem()

    def _makedirs_via_mount(self, path):
        mounted_path = self._internal_path_to_mounted_path(path)
        assert mounted_path is not None, "Couldn't find mounted path for " + path
        os.makedirs(mounted_path, exist_ok=True)
        self._sync_local_filesystem()

    def _delete_via_mount(self, paths):
        for path in paths:
            mounted_path = self._internal_path_to_mounted_path(path)
            assert mounted_path is not None
            if os.path.isdir(mounted_path):
                import shutil

                shutil.rmtree(mounted_path)
            else:
                os.remove(mounted_path)

        self._sync_local_filesystem()

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
        if "binascii" not in self._builtin_modules and "ubinascii" not in self._builtin_modules:
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

    def _extract_block_without_splitting_chars(self, source_bytes: bytes) -> bytes:
        i = self._write_block_size
        while i > 1 and i < len(source_bytes) and is_continuation_byte(source_bytes[i]):
            i -= 1

        return source_bytes[:i]

    def _get_file_operation_block_size(self):
        # don't forget that the size may be expanded up to 4x where converted to Python
        # bytes literal
        if self._connected_to_microbit():
            return 512
        else:
            return 1024


def starts_with_continuation_byte(data):
    return data and is_continuation_byte(data[0])


def is_continuation_byte(byte):
    return (byte & 0b11000000) == 0b10000000


class RawPasteNotSupportedError(RuntimeError):
    pass


if __name__ == "__main__":
    THONNY_USER_DIR = os.environ["THONNY_USER_DIR"]

    thonny.configure_backend_logging()

    import ast
    import sys

    args = ast.literal_eval(sys.argv[1])

    try:
        if args["port"] is None:
            # remain busy
            while True:
                time.sleep(1000)
        elif args["port"] == "webrepl":
            connection = WebReplConnection(args["url"], args["password"])
        else:
            from thonny.plugins.micropython.serial_connection import (
                DifficultSerialConnection,
                SerialConnection,
            )

            connection = SerialConnection(
                args["port"], BAUDRATE, dtr=args.get("dtr"), rts=args.get("rts")
            )
            # connection = DifficultSerialConnection(args["port"], BAUDRATE)

        if "circuitpython" in args.get("proxy_class", "").lower():
            from thonny.plugins.circuitpython.cirpy_backend import CircuitPythonBackend

            backend = CircuitPythonBackend(connection, clean=args["clean"], args=args)
        elif "pipico" in args.get("proxy_class", "").lower():
            from thonny.plugins.rpi_pico.rpi_pico_backend import RaspberryPiPicoBackend

            backend = RaspberryPiPicoBackend(connection, clean=args["clean"], args=args)
        else:
            backend = BareMetalMicroPythonBackend(connection, clean=args["clean"], args=args)

    except ConnectionFailedException as e:
        text = "\n" + str(e) + "\n"
        msg = BackendEvent(event_type="ProgramOutput", stream_name="stderr", data=text)
        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()
