import binascii
import os
import re
import struct
import sys
import time
from logging import getLogger
from textwrap import dedent, indent
from typing import BinaryIO, Callable, List, Optional, Union

# make sure thonny folder is in sys.path (relevant in dev)
thonny_container = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if thonny_container not in sys.path:
    sys.path.insert(0, thonny_container)

import thonny
from thonny import report_time
from thonny.backend import UploadDownloadMixin, convert_newlines_if_has_shebang
from thonny.common import (
    PROCESS_ACK,
    BackendEvent,
    EOFCommand,
    OscEvent,
    ToplevelResponse,
    execute_system_command,
    serialize_message,
)
from thonny.misc_utils import find_volumes_by_name
from thonny.plugins.micropython.connection import MicroPythonConnection
from thonny.plugins.micropython.mp_back import (
    EOT,
    NORMAL_MODE_CMD,
    PASTE_MODE_CMD,
    PASTE_MODE_LINE_PREFIX,
    RAW_MODE_CMD,
    SOFT_REBOOT_CMD,
    WAIT_OR_CRASH_TIMEOUT,
    Y2000_EPOCH_OFFSET,
    ManagementError,
    MicroPythonBackend,
    ProtocolError,
    ReadOnlyFilesystemError,
    ends_overlap,
    is_continuation_byte,
    starts_with_continuation_byte,
)
from thonny.plugins.micropython.mp_common import (
    PASTE_SUBMIT_MODE,
    RAW_PASTE_SUBMIT_MODE,
    RAW_SUBMIT_MODE,
)
from thonny.plugins.micropython.webrepl_connection import WebReplConnection

RAW_PASTE_COMMAND = b"\x05A\x01"
RAW_PASTE_CONFIRMATION = b"R\x01"
RAW_PASTE_CONTINUE = b"\x01"


BAUDRATE = 115200
ENCODING = "utf-8"

# Commands

# Output tokens
ESC = b"\x1b"
ST = b"\x1b\\"
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
logger = getLogger("thonny.plugins.micropython.bare_metal_backend")


class BareMetalMicroPythonBackend(MicroPythonBackend, UploadDownloadMixin):
    def __init__(self, connection, clean, args):
        self._connection = connection
        self._startup_time = time.time()
        self._last_inferred_fs_mount: Optional[str] = None

        self._submit_mode = args.get("submit_mode", None)
        if self._submit_mode is None:
            self._submit_mode = self._infer_submit_mode()

        self._write_block_size = args.get("write_block_size", None)
        if self._write_block_size is None:
            self._write_block_size = self._infer_write_block_size()

        # write delay is used only with original raw submit mode
        self._write_block_delay = args.get("write_block_delay", None)
        if self._write_block_delay is None:
            self._write_block_delay = self._infer_write_block_delay()

        # Serial over Bluetooth (eg. with Robot Inventor Hub in Windows) may need
        # flow control even for data read from the device.
        self._read_block_size = args.get("read_block_size", None)
        if self._read_block_size is None:
            self._read_block_size = self._infer_read_block_size()

        logger.info(
            "Initial submit_mode: %s, "
            "write_block_size: %s, "
            "write_block_delay: %s, "
            "read_block_size: %s",
            self._submit_mode,
            self._write_block_size,
            self._write_block_delay,
            self._read_block_size,
        )

        self._last_prompt = None

        MicroPythonBackend.__init__(self, clean, args)

    def get_connection(self) -> MicroPythonConnection:
        return self._connection

    def _check_prepare(self):
        out, err = self._execute(
            "__thonny_helper.builtins.print('__thonny_helper' in __thonny_helper.builtins.dir())",
            capture_output=True,
        )
        if out.strip() == "True":
            return

        self._prepare_after_soft_reboot(False)

    def _get_helper_code(self):
        if self._using_microbit_micropython():
            return super()._get_helper_code()

        result = super()._get_helper_code()

        # Provide unified interface with Unix variant, which has anemic uos
        result += indent(
            dedent(
                """
            @builtins.classmethod
            def getcwd(cls):
                return cls.os.getcwd()
            
            @builtins.classmethod
            def chdir(cls, x):
                return cls.os.chdir(x)
            
            @builtins.classmethod
            def rmdir(cls, x):
                return cls.os.rmdir(x)
        """
            ),
            "    ",
        )

        if self._read_block_size and self._read_block_size > 0:
            # make sure management prints are done in blocks
            result = result.replace("cls.builtins.print", "cls.controlled_print")
            from thonny.plugins.micropython.serial_connection import OUTPUT_ENQ

            result += indent(
                dedent(
                    """
                _print_block_size = {print_block_size}
            
                @builtins.classmethod
                def controlled_print(cls, *args, sep=" ", end="\\n"):
                    for arg_i, arg in enumerate(args):
                        if sep and arg_i > 0:
                            cls.builtins.print(end=sep)
                        data = __thonny_helper.builtins.str(arg)
                        
                        for i in __thonny_helper.builtins.range(0, __thonny_helper.builtins.len(data), cls._print_block_size):
                            cls.builtins.print(end=data[i:i+cls._print_block_size])
                            cls.builtins.print(end={out_enq!r})
                            cls.sys.stdin.read(1) # ack
                        
                    cls.builtins.print(end=end)
            """
                ).format(print_block_size=self._read_block_size, out_enq=OUTPUT_ENQ),
                "    ",
            )

        return result

    def _infer_write_block_size(self):
        # https://forum.micropython.org/viewtopic.php?f=15&t=3698
        # https://forum.micropython.org/viewtopic.php?f=15&t=4896&p=28132

        # M5Stack Atom (FT232 USB) may produce corrupted output on Windows with
        # paste mode and larger block sizes (problem confirmed with 128, 64 and 30 bytes blocks)
        # https://github.com/thonny/thonny/issues/2143
        # Don't know any other good solutions besides avoiding paste mode for this device.
        return 127

    def _infer_read_block_size(self):
        # TODO:
        # in Windows it should be > 0 if the port is bluetooth over serial
        # (description: Standard Serial over Bluetooth link
        # or interface: Bluetooth Peripheral Device (available only with Adafruit module,
        # otherwise None
        # or hwid: BTHENUM\{00001101-0000-1000-8000-00805F9B34FB}_VID&00010397_PID&0002\8&1748680D&0&A8E2C19C9760_C0000000)
        return 0

    def _infer_write_block_delay(self):
        if self._submit_mode in (PASTE_SUBMIT_MODE, RAW_PASTE_SUBMIT_MODE):
            return 0
        elif self._connected_over_webrepl():
            # ESP-32 needs long delay to work reliably over raw mode WebREPL
            # https://github.com/micropython/micropython/issues/2497
            # TODO: consider removing when this gets fixed
            return 0.5
        else:
            return 0.01

    def _process_until_initial_prompt(self, interrupt: bool, clean: bool) -> None:
        logger.debug("_process_until_initial_prompt, clean=%s", clean)

        poke_after = 0.05
        if interrupt:
            interrupt_times = [0.0, 0.1, 0.2]
            advice_delay = interrupt_times[-1] + 2.0
        else:
            interrupt_times = None
            advice_delay = 2.0

        self._process_output_until_active_prompt(
            self._send_output,
            interrupt_times=interrupt_times,
            poke_after=poke_after,
            advice_delay=advice_delay,
        )

        if clean:
            self._clear_repl()

    def _infer_submit_mode(self):
        if self._connected_over_webrepl():
            logger.info("Choosing paste submit mode because of WebREPL")
            return PASTE_SUBMIT_MODE

        return RAW_PASTE_SUBMIT_MODE

    def _fetch_welcome_text(self) -> str:
        self._write(NORMAL_MODE_CMD)
        out, err = self._capture_output_until_active_prompt()
        welcome_text = out.strip("\r\n >")
        if os.name != "nt":
            welcome_text = welcome_text.replace("\r\n", "\n")
            welcome_text += "\n"
        else:
            welcome_text += "\r\n"

        return welcome_text

    def _fetch_builtin_modules(self):
        script = "__thonny_helper.builtins.help('modules')"
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

        if self._using_microbit_micropython():
            return
        elif self._connected_to_circuitpython():
            if "rtc" not in self._builtin_modules:
                logger.warning("Can't sync time as 'rtc' module is missing")
                return

            specific_script = dedent(
                """
                from rtc import RTC as __thonny_RTC
                __thonny_RTC().datetime = {ts}
                del __thonny_RTC
            """
            ).format(ts=tuple(now))
        else:
            # RTC.init is used in PyCom, RTC.datetime is used by the rest
            specific_script = dedent(
                """
                from machine import RTC as __thonny_RTC
                try:
                    __thonny_RTC().datetime({datetime_ts})
                except:
                    __thonny_RTC().init({init_ts})
                finally:
                    del __thonny_RTC

            """
            ).format(
                datetime_ts=(
                    now.tm_year,
                    now.tm_mon,
                    now.tm_mday,
                    now.tm_wday,
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
            except __thonny_helper.builtins.Exception as e:
                __thonny_helper.print_mgmt_value(__thonny_helper.builtins.str(e))
        """
            )
            % indent(specific_script, "    ")
        )

        val = self._evaluate(script)
        if isinstance(val, str):
            print("WARNING: Could not sync device's clock: " + val)

    def _get_utc_timetuple_from_device(self) -> Union[tuple, str]:
        if self._using_microbit_micropython():
            return "This device does not have a real-time clock"
        elif self._connected_to_circuitpython():
            specific_script = dedent(
                """
                from rtc import RTC as __thonny_RTC
                __thonny_helper.print_mgmt_value(__thonny_helper.builtins.tuple(__thonny_RTC().datetime)[:6])
                del __thonny_RTC
                """
            )
        else:
            specific_script = dedent(
                """
                from machine import RTC as __thonny_RTC
                try:
                    # now() on some devices also gives weekday, so prefer datetime
                    __thonny_temp = __thonny_helper.builtins.tuple(__thonny_RTC().datetime())
                    # remove weekday from index 3
                    __thonny_helper.print_mgmt_value(__thonny_temp[0:3] + __thonny_temp[4:7])
                    del __thonny_temp
                except:
                    __thonny_helper.print_mgmt_value(__thonny_helper.builtins.tuple(__thonny_RTC().now())[:6])
                del __thonny_RTC
                """
            )

        script = (
            dedent(
                """
            try:
            %s
            except __thonny_helper.builtins.Exception as e:
                __thonny_helper.print_mgmt_value(__thonny_helper.builtins.str(e))
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
                    __thonny_helper.print_mgmt_value(__thonny_helper.builtins.tuple(__thonny_localtime()))
                    del __thonny_localtime
                except:
                    # some CP boards
                    from rtc import RTC as __thonny_RTC
                    __thonny_helper.print_mgmt_value(__thonny_helper.builtins.tuple(__thonny_RTC().datetime))
                    del __thonny_RTC
            except __thonny_helper.builtins.Exception as e:
                __thonny_helper.print_mgmt_value(__thonny_helper.builtins.str(e))
        """
        )

        return self._evaluate(script)

    def _update_cwd(self):
        if self._using_microbit_micropython():
            self._cwd = ""
        else:
            super()._update_cwd()

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        self._soft_reboot_for_restarting_user_program()

    def _ensure_raw_mode(self):
        if self._last_prompt in [
            RAW_PROMPT,
            EOT + RAW_PROMPT,
            FIRST_RAW_PROMPT,
            W600_FIRST_RAW_PROMPT,
        ]:
            return

        logger.info("Requesting raw mode at %r", self._last_prompt)

        # assuming we are currently on a normal prompt
        self._write(RAW_MODE_CMD)
        self._log_output_until_active_prompt()
        if self._last_prompt == NORMAL_PROMPT:
            # Don't know why this happens sometimes (eg. when interrupting a Ctrl+D or restarted
            # program, which is outputting text on ESP32)
            logger.info("Found normal prompt instead of expected raw prompt. Trying again.")
            self._write(RAW_MODE_CMD)
            time.sleep(0.5)
            self._log_output_until_active_prompt()

        if self._last_prompt not in [FIRST_RAW_PROMPT, W600_FIRST_RAW_PROMPT]:
            logger.error(
                "Could not enter raw prompt, got %r",
                self._last_prompt,
            )
            raise ProtocolError("Could not enter raw prompt")
        else:
            logger.info("Entered raw prompt")

    def _ensure_normal_mode(self, force=False):
        if self._last_prompt == NORMAL_PROMPT and not force:
            return

        logger.info("Requesting normal mode at %r", self._last_prompt)
        self._write(NORMAL_MODE_CMD)
        self._log_output_until_active_prompt()
        assert self._last_prompt == NORMAL_PROMPT, (
            "Could not get normal prompt, got %s" % self._last_prompt
        )

    def _clear_repl(self):
        """NB! assumes prompt and may be called without __thonny_helper"""
        logger.debug("_create_fresh_repl")
        self._ensure_raw_mode()
        self._write(SOFT_REBOOT_CMD)
        assuming_ok = self._connection.soft_read(2, timeout=0.1)
        if assuming_ok != OK:
            logger.warning("Got %r after requesting soft reboot")
        self._check_reconnect()
        self._forward_output_until_active_prompt()
        logger.debug("Done _create_fresh_repl")

    def _soft_reboot_for_restarting_user_program(self):
        # Need to go to normal mode. MP doesn't run user code in raw mode
        # (CP does, but it doesn't hurt to do it there as well)
        logger.debug("_soft_reboot_for_restarting_user_program")
        self._ensure_normal_mode()
        self._write(SOFT_REBOOT_CMD)
        self._check_reconnect()
        self._process_output_until_active_prompt(self._send_output)
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

    def _submit_code(self, script):
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
                    # raw is safest, as some M5 ESP32-s don't play nice with paste mode,
                    # even with as small block size as 30 (echo is randomly missing characters)
                    self._submit_mode = RAW_SUBMIT_MODE
                    self._write_block_size = self._infer_write_block_size()
                    self._write_block_delay = self._infer_write_block_delay()
                    logger.warning(
                        "Could not use raw_paste, falling back to %s"
                        + " with write_block_size %s and write_block_delay %s",
                        self._submit_mode,
                        self._write_block_size,
                        self._write_block_delay,
                    )
                    self._submit_code_via_raw_mode(to_be_sent)
            else:
                self._submit_code_via_raw_mode(to_be_sent)

    def _submit_code_via_paste_mode(self, script_bytes: bytes) -> None:
        # Go to paste mode
        self._ensure_normal_mode()
        self._write(PASTE_MODE_CMD)
        discarded = self._connection.read_until(PASTE_MODE_LINE_PREFIX)
        logger.debug("Discarding %r", discarded)

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

        # push and read confirmation
        self._write(EOT)
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
            logger.error(
                "Could not read command confirmation for script\n\n: %s\n\n" "Got: %r",
                self._decode(script_bytes),
                data,
            )
            raise ProtocolError("Could not read command confirmation")

    def _submit_code_via_raw_paste_mode(self, script_bytes: bytes) -> None:
        # Occasionally, the device initially supports raw paste but later doesn't allow it (?)
        # https://github.com/thonny/thonny/issues/1545

        self._ensure_raw_mode()
        self._connection.set_text_mode(False)
        self._write(RAW_PASTE_COMMAND)
        response = self._connection.soft_read(2, timeout=WAIT_OR_CRASH_TIMEOUT)
        if response != RAW_PASTE_CONFIRMATION:
            # perhaps the device doesn't support raw paste ...
            response += self._connection.soft_read_until(FIRST_RAW_PROMPT, timeout=0.5)
            if response.endswith(FIRST_RAW_PROMPT):
                # ... yup, it doesn't support it
                self._last_prompt = FIRST_RAW_PROMPT
                raise RawPasteNotSupportedError()
            else:
                logger.error("Got %r instead of raw-paste confirmation", response)
                raise ProtocolError("Could not get raw-paste confirmation")

        self._raw_paste_write(script_bytes)
        self._connection.set_text_mode(True)

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
                    self._write(b"\x04")
                    logger.debug(
                        "Abrupt end of raw paste submit after submitting %s bytes out of %s",
                        i,
                        len(command_bytes),
                    )
                    return
                else:
                    # Unexpected data from device.
                    logger.error("Unexpected read during raw paste: %r", data)
                    raise ProtocolError("Unexpected read during raw paste")
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
            logger.error("Could not complete raw paste. Ack: %r", data)
            raise ProtocolError("Could not complete raw paste")

    def _execute_with_consumer(self, script, output_consumer: Callable[[str, str], None]):
        report_time("befsubcode")
        self._submit_code(script)
        report_time("affsubcode")
        self._process_output_until_active_prompt(output_consumer)
        report_time("affforw")

    def _process_output_until_active_prompt(
        self,
        output_consumer: Callable[[str, str], None],
        stream_name="stdout",
        interrupt_times: Optional[List[float]] = None,
        poke_after: Optional[float] = None,
        advice_delay: Optional[float] = None,
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

        have_read_non_whitespace = False
        have_poked = False
        have_given_advice = False
        have_given_output_based_interrupt = False
        last_new_data = b""
        last_new_data_time = 0

        start_time = time.time()
        num_interrupts_before = self._number_of_interrupts_sent

        if interrupt_times:
            interrupt_times_left = interrupt_times.copy()
        else:
            interrupt_times_left = []

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

            spent_time = time.time() - start_time
            interrupts_given_here = self._number_of_interrupts_sent - num_interrupts_before

            # advice (if requested) is warranted if there has been attempt to interrupt
            # or nothing has appeared to the output (which may be confusing)
            if (
                advice_delay is not None
                and not have_given_advice
                and not "Ctrl-C" in self._last_sent_output  # CircuitPython's advice
                and (
                    not have_read_non_whitespace
                    and spent_time > advice_delay
                    or interrupts_given_here > 0
                    and time.time() - self._last_interrupt_time > advice_delay
                )
            ):
                logger.info("Giving advice")
                self._show_error(
                    "\nDevice is busy or does not respond. Your options:\n\n"
                    + "  - wait until it completes current work;\n"
                    + "  - use Ctrl+C to interrupt current work;\n"
                    + "  - reset the device and try again;\n"
                    + "  - check connection properties;\n"
                    + "  - make sure the device has suitable MicroPython / CircuitPython / firmware;\n"
                    + "  - make sure the device is not in bootloader mode.\n"
                )
                have_given_advice = True
            elif (
                poke_after is not None
                and spent_time > poke_after
                and not have_read_non_whitespace
                and not have_poked
            ):
                logger.info("Poking")
                self._write(RAW_MODE_CMD)
                have_poked = True
            elif interrupt_times_left and spent_time >= interrupt_times_left[0]:
                self._interrupt()
                interrupt_times_left.pop(0)
            elif (
                time.time() - last_new_data_time > 0.5
                and self._output_warrants_interrupt(last_new_data)
                and not have_given_output_based_interrupt
            ):
                self._interrupt()
                have_given_output_based_interrupt = True

            # Prefer whole lines, but allow also incremental output to single line
            new_data = self._connection.soft_read_until(
                INCREMENTAL_OUTPUT_BLOCK_CLOSERS, timeout=0.05
            )
            if new_data:
                if new_data.strip():
                    have_read_non_whitespace = True
                last_new_data = new_data
                last_new_data_time = time.time()

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

            if not new_data and not pending:
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
                if follow_up == ESC:
                    # See if it's followed by a OSC code, like the one output by CircuitPython 8
                    follow_up += self._connection.soft_read_until(ST)
                    if follow_up.endswith(ST):
                        logger.debug("Found OSC sequence %r", follow_up)
                        self.send_message(OscEvent(follow_up.decode("utf-8", errors="replace")))
                    follow_up = b""

                if follow_up:
                    logger.info("Found inactive prompt followed by %r", follow_up)
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
                    logger.debug("Found prompt %r", current_prompt)
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

        self._process_output_until_active_prompt(collect_output)

        return output["stdout"], output["stderr"]

    def _log_output_until_active_prompt(
        self, interrupt_times: Optional[List[float]] = None, poke_after: Optional[float] = None
    ) -> None:
        def collect_output(data, stream):
            logger.info("Discarding %s: %r", stream, data)

        self._process_output_until_active_prompt(
            collect_output, interrupt_times=interrupt_times, poke_after=poke_after
        )

    def _forward_output_until_active_prompt(
        self, interrupt_times: Optional[List[float]] = None, poke_after: Optional[float] = None
    ) -> None:
        self._process_output_until_active_prompt(
            self._send_output, interrupt_times=interrupt_times, poke_after=poke_after
        )

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
        return self._cmd_Run_or_run(cmd, True)

    def _cmd_run(self, cmd):
        return self._cmd_Run_or_run(cmd, False)

    def _cmd_Run_or_run(self, cmd, restart_interpreter_before_run):
        """Only for %run $EDITOR_CONTENT. start runs will be handled differently."""
        if cmd.get("source"):
            if restart_interpreter_before_run:
                self._clear_repl()

            if self._submit_mode == PASTE_SUBMIT_MODE:
                source = self._avoid_printing_expression_statements(cmd.source)
                if restart_interpreter_before_run:
                    logger.debug("Ensuring normal mode after soft reboot")
                    self._ensure_normal_mode(force=True)
            else:
                source = cmd.source

            self._execute(source, capture_output=False)
            if restart_interpreter_before_run:
                self._prepare_after_soft_reboot(False)
        return {}

    def _cmd_execute_system_command(self, cmd):
        # Can't use stdin, because a thread is draining it
        returncode = execute_system_command(cmd, cwd=self._local_cwd, disconnect_stdin=True)
        return {"returncode": returncode}

    def _cmd_get_fs_info(self, cmd):
        if self._using_microbit_micropython():
            used = self._evaluate(
                dedent(
                    """
                    __thonny_helper.print_mgmt_value(
                        __thonny_helper.builtins.sum([__thonny_helper.os.size(name) for name in __thonny_helper.os.listdir()])
                    )  
                    """
                )
            )
            return {
                "total": None,
                "used": used,
                "free": None,
                "comment": "Assuming around 30 kB of storage space for user files.",
            }

        else:
            result = self._evaluate(
                dedent(
                    """
                __thonny_stat = __thonny_helper.os.statvfs(%r)
                __thonny_total = __thonny_stat[2] * __thonny_stat[0]
                __thonny_free = __thonny_stat[3] * __thonny_stat[0]

                __thonny_helper.print_mgmt_value({
                    "total" : __thonny_total,
                    "used" : __thonny_total - __thonny_free,
                    "free": __thonny_free,
                })  

                del __thonny_stat 
                del __thonny_total
                del __thonny_free
                """
                )
                % cmd.path
            )

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
            except ManagementError as e:
                if self._contains_read_only_error(e.out + e.err):
                    self._delete_via_mount(paths)
                else:
                    raise

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

        self._execute_without_output(
            "__thonny_fp = __thonny_helper.builtins.open(%r, 'rb')" % source_path
        )
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
        self._connection.set_text_mode(False)
        try:
            self._write(rec)
            assert self._read_websocket_response() == 0

            bytes_read = 0
            callback(bytes_read, file_size)
            while True:
                # report ready
                self._write(b"\0")

                (block_size,) = struct.unpack("<H", self._connection.read(2))
                if block_size == 0:
                    break
                while block_size:
                    buf = self._connection.read(block_size)
                    if not buf:
                        raise OSError("Could not read in WebREPL binary protocol")
                    bytes_read += len(buf)
                    target_fp.write(buf)
                    block_size -= len(buf)
                    callback(bytes_read, file_size)

            assert self._read_websocket_response() == 0
        finally:
            self._connection.set_text_mode(True)

    def _write_file(
        self,
        source_fp: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
        make_shebang_scripts_executable: bool,
    ) -> None:
        start_time = time.time()

        if make_shebang_scripts_executable:
            source_fp, _ = convert_newlines_if_has_shebang(source_fp)
            # No need (or not possible?) to set mode on bare metal

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

    def _contains_read_only_error(self, s: str) -> bool:
        canonic_out = s.replace("-", "").lower()
        return (
            "readonly" in canonic_out or "errno 30" in canonic_out or "oserror: 30" in canonic_out
        )

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
                __thonny_path = '{path}'
                __thonny_written = 0
                __thonny_fp = __thonny_helper.builtins.open(__thonny_path, 'wb')
            """
            ).format(path=target_path),
            capture_output=True,
        )

        if self._contains_read_only_error(out + err):
            raise ReadOnlyFilesystemError()
        elif out + err:
            raise OSError(
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
                    if __thonny_helper.builtins.hasattr(__thonny_helper.os, "sync"):
                        __thonny_helper.os.sync()
            """
                )
            )
        elif self._using_microbit_micropython():
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
                    if __thonny_helper.builtins.hasattr(__thonny_helper.os, "sync"):
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
                    raise OSError("Could not complete file writing", script, out, err)
                bytes_sent += len(block)

            if len(block) < block_size:
                break

        bytes_received = self._evaluate("__thonny_written")

        if bytes_received != bytes_sent:
            raise OSError("Expected %d written bytes but wrote %d" % (bytes_sent, bytes_received))

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
        self._connection.set_text_mode(False)
        try:
            self._write(rec[:10])
            self._write(rec[10:])
            assert self._read_websocket_response() == 0

            bytes_sent = 0
            callback(bytes_sent, file_size)
            while True:
                block = source.read(1024)
                if not block:
                    break
                self._write(block)
                bytes_sent += len(block)
                callback(bytes_sent, file_size)

            assert self._read_websocket_response() == 0
        finally:
            self._connection.set_text_mode(True)

    def _read_websocket_response(self):
        data = self._connection.read(4)
        sig, code = struct.unpack("<2sH", data)
        assert sig == b"WB"
        return code

    def _sync_remote_filesystem(self):
        self._execute_without_output(
            dedent(
                """
            if __thonny_helper.builtins.hasattr(__thonny_helper.os, "sync"):
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
            if self._contains_read_only_error(e.err):
                self._makedirs_via_mount(path)
            else:
                raise

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
            except __thonny_helper.builtins.ImportError:
                __thonny_result = None 
            except __thonny_helper.builtins.OSError:
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
        if self._last_inferred_fs_mount and os.path.isdir(self._last_inferred_fs_mount):
            logger.debug("Using cached mount path %r", self._last_inferred_fs_mount)
            return self._last_inferred_fs_mount

        logger.debug("Computing mount path")

        label = self._get_fs_mount_label()
        if label is None:
            self._last_inferred_fs_mount = None
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
                self._last_inferred_fs_mount = candidates[0]

        return self._last_inferred_fs_mount

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

    def _get_file_operation_block_size(self):
        # don't forget that the size may be expanded up to 4x where converted to Python
        # bytes literal
        if self._using_microbit_micropython():
            return 512
        else:
            return 1024

    def _extract_block_without_splitting_chars(self, source_bytes: bytes) -> bytes:
        i = self._write_block_size
        while i > 1 and i < len(source_bytes) and is_continuation_byte(source_bytes[i]):
            i -= 1

        return source_bytes[:i]

    def _output_warrants_interrupt(self, data):
        return False

    def _create_pipkin_adapter(self):
        if self._connected_over_webrepl():
            from pipkin.bare_metal import WebReplAdapter

            class_ = WebReplAdapter
            kwargs = {}
        else:
            from pipkin.bare_metal import SerialPortAdapter

            class_ = SerialPortAdapter
            kwargs = {}
            if self._connected_to_circuitpython():
                try:
                    kwargs["mount_path"] = self._get_fs_mount()
                except Exception:
                    logger.warning("Could not get mount path", exc_info=True)

        return class_(
            self._connection,
            submit_mode=self._submit_mode,
            write_block_size=self._write_block_size,
            write_block_delay=self._write_block_delay,
            **kwargs,
        )

    def _report_internal_exception(self, msg: str) -> None:
        super()._report_internal_exception(msg)

        e = sys.exc_info()[1]
        if isinstance(e, ManagementError):
            self._log_management_error_details(e)

        self._show_error(
            'You may need to press "Stop/Restart" or hard-reset your '
            + "%s device and try again.\n" % self._get_interpreter_kind()
        )


class GenericBareMetalMicroPythonBackend(BareMetalMicroPythonBackend):
    def _get_sys_path_for_analysis(self) -> Optional[List[str]]:
        return [
            os.path.join(os.path.dirname(__file__), "generic_api_stubs"),
        ] + super()._get_sys_path_for_analysis()


class RawPasteNotSupportedError(RuntimeError):
    pass


def launch_bare_metal_backend(backend_class: Callable[..., BareMetalMicroPythonBackend]) -> None:
    thonny.configure_backend_logging()
    print(PROCESS_ACK)

    import ast

    args = ast.literal_eval(sys.argv[1])
    logger.info("Starting backend, args: %r", args)

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

        backend = backend_class(connection, clean=args["clean"], args=args)

    except ConnectionError as e:
        text = "\n" + str(e) + "\n"
        msg = BackendEvent(event_type="ProgramOutput", stream_name="stderr", data=text)
        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()
        sys.exit(1)


if __name__ == "__main__":
    launch_bare_metal_backend(GenericBareMetalMicroPythonBackend)
