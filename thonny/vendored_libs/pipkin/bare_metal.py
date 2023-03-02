import ast
import binascii
import errno
import os
import re
import struct
import time
from abc import ABC
from logging import getLogger
from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Tuple

from pipkin import UserError
from pipkin.adapters import BaseAdapter
from pipkin.common import CommunicationError, ManagementError, ProtocolError
from pipkin.connection import MicroPythonConnection, ReadingTimeoutError
from pipkin.serial_connection import SerialConnection
from pipkin.util import starts_with_continuation_byte

logger = getLogger(__name__)

RAW_MODE_CMD = b"\x01"
NORMAL_MODE_CMD = b"\x02"
INTERRUPT_CMD = b"\x03"
SOFT_REBOOT_CMD = b"\x04"
PASTE_MODE_CMD = b"\x05"
PASTE_MODE_LINE_PREFIX = b"=== "

PASTE_SUBMIT_MODE = "paste"
RAW_PASTE_SUBMIT_MODE = "raw_paste"
RAW_SUBMIT_MODE = "raw"

RAW_PASTE_COMMAND = b"\x05A\x01"
RAW_PASTE_CONFIRMATION = b"R\x01"
RAW_PASTE_CONTINUE = b"\x01"

MGMT_VALUE_START = b"<pipkin>"
MGMT_VALUE_END = b"</pipkin>"

# How many seconds to wait for something that should appear quickly.
# In other words -- how long to wait with reporting a protocol error
# (hoping that the required piece is still coming)
WAIT_OR_CRASH_TIMEOUT = 5

FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\n>"

RAW_PROMPT = b">"


WEBREPL_REQ_S = "<2sBBQLH64s"
WEBREPL_PUT_FILE = 1
WEBREPL_GET_FILE = 2


EOT = b"\x04"
NORMAL_PROMPT = b">>> "
LF = b"\n"
OK = b"OK"
ESC = b"\x1b"
ST = b"\x1b\\"

ENCODING = "utf-8"
TRACEBACK_MARKER = b"Traceback (most recent call last):"

OutputConsumer = Callable[[str, str], None]


class BareMetalAdapter(BaseAdapter, ABC):
    def __init__(
        self,
        connection: MicroPythonConnection,
        submit_mode: Optional[str] = None,
        write_block_size: Optional[int] = None,
        write_block_delay: Optional[float] = None,
    ):
        super().__init__()
        self._connection = connection
        (
            self._submit_mode,
            self._write_block_size,
            self._write_block_delay,
        ) = self._infer_submit_parameters(submit_mode, write_block_size, write_block_delay)
        self._last_prompt: Optional[bytes] = None

        self._interrupt_to_prompt()
        self._prepare_helper()
        self._builtin_modules = self._fetch_builtin_modules()
        logger.debug("Builtin modules: %r", self._builtin_modules)

    def get_dir_sep(self) -> str:
        return "/"

    def _infer_submit_parameters(
        self,
        submit_mode: Optional[str] = None,
        write_block_size: Optional[int] = None,
        write_block_delay: Optional[float] = None,
    ) -> Tuple[str, int, float]:

        if submit_mode is None:
            submit_mode = RAW_PASTE_SUBMIT_MODE

        if write_block_size is None:
            write_block_size = 255

        if write_block_delay is None:
            if submit_mode == RAW_SUBMIT_MODE:
                write_block_delay = 0.01
            else:
                write_block_delay = 0.0

        return submit_mode, write_block_size, write_block_delay

    def _fetch_builtin_modules(self) -> List[str]:
        script = "__pipkin_helper.builtins.help('modules')"
        out, err = self._execute_and_capture_output(script)
        if err or not out:
            logger.warning("Could not query builtin modules")
            return []

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

    def _interrupt_to_prompt(self) -> None:
        # It's safer to thoroughly interrupt before poking with RAW_MODE_CMD
        # as Pico may get stuck otherwise
        # https://github.com/micropython/micropython/issues/7867
        interventions = [(INTERRUPT_CMD, 0.1), (INTERRUPT_CMD, 0.1), (RAW_MODE_CMD, 0.1)]

        for cmd, timeout in interventions:
            self._write(cmd)
            try:
                self._log_output_until_active_prompt(timeout=timeout)
                break
            except TimeoutError as e:
                logger.debug(
                    "Could not get prompt with intervention %r and timeout %r. Read bytes: %r",
                    cmd,
                    timeout,
                    getattr(e, "read_bytes", "?"),
                )
                # Try again as long as there are interventions left
        else:
            raise CommunicationError("Could not get raw REPL")

    def _log_output(self, data: bytes, stream: str = "stdout") -> None:
        logger.debug("read %s: %r", stream, data)

    def _prepare_helper(self) -> None:
        script = (
            dedent(
                """
            class __pipkin_helper:
                import builtins
                try:
                    import uos as os
                except builtins.ImportError:
                    import os
                import sys

                @builtins.classmethod
                def print_mgmt_value(cls, obj):
                    cls.builtins.print({mgmt_start!r}, cls.builtins.repr(obj), {mgmt_end!r}, sep='', end='')
            """
            ).format(
                mgmt_start=MGMT_VALUE_START.decode(ENCODING),
                mgmt_end=MGMT_VALUE_END.decode(ENCODING),
            )
            + "\n"
        ).lstrip()
        self._execute_without_output(script)

    def fetch_sys_path(self) -> List[str]:
        return self._evaluate("__pipkin_helper.sys.path")

    def fetch_sys_implementation(self) -> Tuple[str, str, int]:
        return self._evaluate("__pipkin_helper.builtins.tuple(__pipkin_helper.sys.implementation)")

    def get_user_packages_path(self) -> Optional[str]:
        return None

    def read_file(self, path: str) -> bytes:

        hex_mode = self._should_hexlify(path)

        open_script = f"__pipkin_fp = __pipkin_helper.builtins.open({path!r}, 'rb')"
        out, err = self._execute_and_capture_output(open_script)

        if (out + err).strip():
            if any(str(nr) in out + err for nr in [errno.ENOENT, errno.ENODEV]):
                raise FileNotFoundError(f"Can't find {path} on target")
            else:
                raise ManagementError(
                    f"Could not open file {path} for reading", script=open_script, out=out, err=err
                )

        if hex_mode:
            self._execute_without_output("from binascii import hexlify as __temp_hexlify")

        block_size = 1024
        num_bytes_read = 0
        blocks = []
        while True:
            if hex_mode:
                block = binascii.unhexlify(
                    self._evaluate("__temp_hexlify(__pipkin_fp.read(%s))" % block_size)
                )
            else:
                block = self._evaluate("__pipkin_fp.read(%s)" % block_size)

            if block:
                blocks.append(block)
                num_bytes_read += len(block)

            if len(block) < block_size:
                break

        self._execute_without_output(
            dedent(
                """
            __pipkin_fp.close()
            del __pipkin_fp
            try:
                del __temp_hexlify
            except:
                pass
            """
            )
        )

        return b"".join(blocks)

    def remove_file_if_exists(self, path: str) -> None:
        self._execute_without_output(
            dedent(
                f"""
            try:
                __pipkin_helper.os.stat({path!r})
            except __pipkin_helper.builtins.OSError:
                pass
            else:
                __pipkin_helper.os.remove({path!r})            
        """
            )
        )

    def remove_dir_if_empty(self, path: str) -> bool:
        return self._evaluate(
            dedent(
                f"""
            if __pipkin_helper.os.listdir({path!r}):
                __pipkin_helper.print_mgmt_value(False)
            else:
                __pipkin_helper.os.remove({path!r})
                __pipkin_helper.print_mgmt_value(True)
        """
            )
        )

    def mkdir_in_existing_parent_exists_ok(self, path: str) -> None:
        self._execute_without_output(
            dedent(
                f"""
            try:
                __pipkin_helper.os.stat({path!r})
            except __pipkin_helper.builtins.OSError:
                __pipkin_helper.os.mkdir({path!r})
        """
            )
        )

    def list_meta_dir_names(self, path: str, dist_name: Optional[str] = None) -> List[str]:
        if dist_name:
            dist_name_condition = f"and name.startswith({dist_name+'-'!r})"
        else:
            dist_name_condition = ""

        return self._evaluate(
            dedent(
                f"""
            try:
                __pipkin_helper.print_mgmt_value([
                    name for name 
                    in __pipkin_helper.os.listdir({path!r}) 
                    if name.endswith('.dist-info') {dist_name_condition}
                ])
            except __pipkin_helper.builtins.OSError as e:
                __pipkin_helper.print_mgmt_value([])
"""
            )
        )

    def _submit_code(self, script: str) -> None:
        assert script

        to_be_sent = script.encode("UTF-8")
        logger.debug("Submitting via %s: %r", self._submit_mode, to_be_sent[:1000])

        # assuming we are already at a prompt, but threads may have produced something extra
        discarded_bytes = self._connection.read_all()
        if discarded_bytes:
            logger.info("Discarding %r", discarded_bytes)

        if self._submit_mode == PASTE_SUBMIT_MODE:
            self._submit_code_via_paste_mode(to_be_sent)
        elif self._submit_mode == RAW_PASTE_SUBMIT_MODE:
            try:
                self._submit_code_via_raw_paste_mode(to_be_sent)
            except RawPasteNotSupportedError:
                logger.warning("Could not use expected raw paste, falling back to paste mode")
                self._submit_mode = PASTE_SUBMIT_MODE
                self._submit_code_via_paste_mode(to_be_sent)
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
            block = to_be_written[self._write_block_size :]
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
                "Could not read command confirmation for script\n\n: %s\n\n" + "Got: %r",
                script_bytes,
                data,
            )
            raise ProtocolError("Could not read command confirmation")

    def _submit_code_via_raw_paste_mode(self, script_bytes: bytes) -> None:
        self._ensure_raw_mode()
        self._connection.set_text_mode(False)
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

    def _ensure_raw_mode(self):
        if self._last_prompt in [
            RAW_PROMPT,
            EOT + RAW_PROMPT,
            FIRST_RAW_PROMPT,
        ]:
            return
        logger.debug("requesting raw mode at %r", self._last_prompt)

        # assuming we are currently on a normal prompt
        self._write(RAW_MODE_CMD)
        self._log_output_until_active_prompt()
        if self._last_prompt == NORMAL_PROMPT:
            # Don't know why this happens sometimes (e.g. when interrupting a Ctrl+D or restarted
            # program, which is outputting text on ESP32)
            logger.info("Found normal prompt instead of expected raw prompt. Trying again.")
            self._write(RAW_MODE_CMD)
            time.sleep(0.5)
            self._log_output_until_active_prompt()

        if self._last_prompt != FIRST_RAW_PROMPT:
            logger.error(
                "Could not enter raw prompt, got %r",
                self._last_prompt,
            )
            raise ProtocolError("Could not enter raw prompt")

    def _ensure_normal_mode(self, force=False):
        if self._last_prompt == NORMAL_PROMPT and not force:
            return

        logger.debug("requesting normal mode at %r", self._last_prompt)
        self._write(NORMAL_MODE_CMD)
        self._log_output_until_active_prompt()
        assert self._last_prompt == NORMAL_PROMPT, (
            "Could not get normal prompt, got %s" % self._last_prompt
        )

    def _log_output_until_active_prompt(self, timeout: float = WAIT_OR_CRASH_TIMEOUT) -> None:
        def collect_output(data, stream):
            if data:
                logger.info("Discarding %s: %r", stream, data)

        self._process_output_until_active_prompt(collect_output, timeout=timeout)

    def _capture_output_until_active_prompt(self, timeout: float) -> Tuple[str, str]:
        output = {"stdout": "", "stderr": ""}

        def collect_output(data, stream):
            output[stream] += data

        self._process_output_until_active_prompt(collect_output, timeout=timeout)

        return output["stdout"], output["stderr"]

    def _process_output_until_active_prompt(
        self,
        output_consumer: OutputConsumer,
        timeout: float,
    ):

        PROMPT_MARKERS = [NORMAL_PROMPT, EOT + RAW_PROMPT, FIRST_RAW_PROMPT]
        PROMPT_MARKERS_RE = re.compile(
            b"|".join(
                map(
                    re.escape,
                    PROMPT_MARKERS,
                )
            )
        )

        start_time = time.time()

        while True:
            spent_time = time.time() - start_time
            time_left = max(timeout - spent_time, 0.0)
            data = self._connection.read_until(PROMPT_MARKERS_RE, timeout=time_left)
            assert any(data.endswith(marker) for marker in PROMPT_MARKERS)

            for prompt in PROMPT_MARKERS:
                if data.endswith(prompt):
                    self._last_prompt = prompt
                    content = data[: -len(self._last_prompt)]
                    if EOT in content:
                        out, err = content.split(EOT, maxsplit=1)
                    elif TRACEBACK_MARKER in content:
                        out, err = content.split(TRACEBACK_MARKER, maxsplit=1)
                        err = TRACEBACK_MARKER + err
                    else:
                        out = content
                        err = b""
                    output_consumer(out.decode(ENCODING), "stdout")
                    if err:
                        output_consumer(err.decode(ENCODING), "stderr")
                    break

            # Check if it's really active prompt
            follow_up = self._connection.soft_read(1, timeout=0.01)
            if follow_up == ESC:
                # See if it's followed by a OSC code, like the one output by CircuitPython 8
                follow_up += self._connection.soft_read_until(ST)
                if follow_up.endswith(ST):
                    logger.debug("Dropping OSC sequence %r", follow_up)
                follow_up = b""
            if follow_up:
                # Nope, the prompt is not active.
                # (Actually it may be that a background thread has produced this follow up,
                # but this would be too hard to consider.)
                # Don't output yet, because the follow-up may turn into another prompt,
                # and they can be captured all together.
                self._connection.unread(follow_up)
                output_consumer(self._last_prompt.decode(ENCODING), "stdout")
            else:
                break

    def _evaluate(self, script: str) -> Any:
        """Evaluate the output of the script or raise error, if anything looks wrong.

        Adds printing code if the script contains single expression and doesn't
        already contain printing code"""
        try:
            ast.parse(script, mode="eval")
            prefix = "__pipkin_helper.print_mgmt_value("
            suffix = ")"
            if not script.strip().startswith(prefix):
                script = prefix + script + suffix
        except SyntaxError:
            pass

        out, err = self._execute_and_capture_output(script)
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

        if prefix:
            logger.warning("Eval output had unexpected prefix: %r", prefix)
        if suffix:
            logger.warning("Eval output had unexpected suffix: %r", suffix)

        return value

    def _write(self, data: bytes) -> None:
        if (
            RAW_MODE_CMD in data
            or NORMAL_MODE_CMD in data
            or INTERRUPT_CMD in data
            or EOT in data
            or PASTE_MODE_CMD in data
        ):
            logger.debug("Sending ctrl chars: %r", data)
        num_bytes = self._connection.write(data)
        assert num_bytes == len(data)

    def _should_hexlify(self, path):
        if "binascii" not in self._builtin_modules and "ubinascii" not in self._builtin_modules:
            return False

        for ext in (".py", ".txt", ".csv", "METADATA", "RECORD"):
            if path.lower().endswith(ext):
                return False

        return True

    def _execute_without_output(self, script: str, timeout: float = WAIT_OR_CRASH_TIMEOUT) -> None:
        """Meant for management tasks."""
        out, err = self._execute_and_capture_output(script, timeout=timeout)
        if out or err:
            raise ManagementError("Command output was not empty", script, out, err)

    def _execute_and_capture_output(
        self, script: str, timeout: float = WAIT_OR_CRASH_TIMEOUT
    ) -> Tuple[str, str]:
        output_lists: Dict[str, List[str]] = {"stdout": [], "stderr": []}

        def consume_output(data, stream_name):
            assert isinstance(data, str)
            output_lists[stream_name].append(data)

        self._execute_with_consumer(script, consume_output, timeout=timeout)
        result = ["".join(output_lists[name]) for name in ["stdout", "stderr"]]
        return result[0], result[1]

    def _execute_with_consumer(
        self, script, output_consumer: OutputConsumer, timeout: float
    ) -> None:
        self._submit_code(script)
        self._process_output_until_active_prompt(output_consumer, timeout=timeout)


class SerialPortAdapter(BareMetalAdapter):
    def __init__(
        self,
        connection: SerialConnection,
        submit_mode: Optional[str] = None,
        write_block_size: Optional[int] = None,
        write_block_delay: Optional[float] = None,
        mount_path: Optional[str] = None,
    ):
        super().__init__(
            connection,
            submit_mode=submit_mode,
            write_block_size=write_block_size,
            write_block_delay=write_block_delay,
        )
        self._mount_path = mount_path
        self._read_only_filesystem = False

    def _internal_path_to_mounted_path(self, target_path: str) -> str:
        assert self._mount_path
        assert target_path.startswith("/")
        return os.path.normpath(os.path.join(self._mount_path, target_path[1:]))

    def write_file_in_existing_dir(self, path: str, content: bytes) -> None:
        start_time = time.time()

        if self._read_only_filesystem:
            self._write_file_via_mount(path, content)

        try:
            self._write_file_via_serial(path, content)
        except ReadOnlyFilesystemError:
            self._read_only_filesystem = True
            self._write_file_via_mount(path, content)

        logger.info("Wrote %s in %.1f seconds", path, time.time() - start_time)

    def _write_file_via_mount(
        self,
        target_path: str,
        content: bytes,
    ) -> None:
        mounted_target_path = self._internal_path_to_mounted_path(target_path)
        with open(mounted_target_path, "wb") as f:
            bytes_written = 0
            block_size = 4 * 1024
            to_be_written = content
            while to_be_written:
                block = to_be_written[:block_size]
                bytes_written += f.write(block)
                assert bytes_written
                f.flush()
                os.fsync(f)
                to_be_written = to_be_written[block_size:]

        assert bytes_written == len(content)

    def _write_file_via_serial(
        self, target_path: str, content: bytes, can_hexlify: bool = True
    ) -> None:
        out, err = self._execute_and_capture_output(
            dedent(
                """
                __pipkin_path = '{path}'
                __pipkin_written = 0
                __pipkin_fp = __pipkin_helper.builtins.open(__pipkin_path, 'wb')
            """
            ).format(path=target_path),
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
                from binascii import unhexlify as __pipkin_unhex
                def __W(x):
                    global __pipkin_written
                    __pipkin_written += __pipkin_fp.write(__pipkin_unhex(x))
                    __pipkin_fp.flush()
                    if __pipkin_helper.builtins.hasattr(__pipkin_helper.os, "sync"):
                        __pipkin_helper.os.sync()
            """
                )
            )
        else:
            self._execute_without_output(
                dedent(
                    """
                def __W(x):
                    global __pipkin_written
                    __pipkin_written += __pipkin_fp.write(x)
                    __pipkin_fp.flush()
                    if __pipkin_helper.builtins.hasattr(__pipkin_helper.os, "sync"):
                        __pipkin_helper.os.sync()
            """
                )
            )

        bytes_sent = 0
        block_size = 1024

        to_be_written = content
        while to_be_written:
            block = to_be_written[:block_size]
            if hex_mode:
                script = "__W(%r)" % binascii.hexlify(block)
            else:
                script = "__W(%r)" % block
            out, err = self._execute_and_capture_output(script)
            if out or err:
                logger.error("Writing file produced unexpected output (%r) or error (%r)", out, err)
                raise UserError(
                    "Could not write next block after having written %d bytes to %s"
                    % (bytes_sent, target_path)
                )

            bytes_sent += len(block)
            to_be_written = to_be_written[block_size:]

        bytes_received = self._evaluate("__pipkin_written")

        if bytes_received != bytes_sent:
            raise OSError("Expected %d written bytes but wrote %d" % (bytes_sent, bytes_received))

        # clean up
        self._execute_without_output(
            dedent(
                """
                try:
                    del __W
                    del __pipkin_written
                    del __pipkin_path
                    __pipkin_fp.close()
                    del __pipkin_fp
                    del __pipkin_result
                    del __pipkin_unhex
                except:
                    pass
            """
            )
        )

    def remove_file_if_exists(self, path: str) -> None:
        if self._read_only_filesystem:
            self._remove_file_via_mount(path)
            return

        try:
            super().remove_file_if_exists(path)
        except ManagementError as e:
            if self._contains_read_only_error(e.out + e.err):
                self._read_only_filesystem = True
                self._remove_file_via_mount(path)
            else:
                raise

    def _remove_file_via_mount(self, target_path: str) -> None:
        logger.info("Removing %s via mount", target_path)
        mounted_target_path = self._internal_path_to_mounted_path(target_path)
        assert os.path.isfile(mounted_target_path)
        os.remove(mounted_target_path)

    def _contains_read_only_error(self, s: str) -> bool:
        canonic_out = s.replace("-", "").lower()
        return (
            "readonly" in canonic_out
            or f"errno {errno.EROFS}" in canonic_out
            or f"oserror: {errno.EROFS}" in canonic_out
        )

    def mkdir_in_existing_parent_exists_ok(self, path: str) -> None:
        if self._read_only_filesystem:
            self._mkdir_via_mount(path)
            return

        try:
            super().mkdir_in_existing_parent_exists_ok(path)
        except ManagementError as e:
            if self._contains_read_only_error(e.out + e.err):
                self._read_only_filesystem = True
                self._mkdir_via_mount(path)
            else:
                raise

    def _mkdir_via_mount(self, path: str) -> bool:
        mounted_path = self._internal_path_to_mounted_path(path)
        if not os.path.isdir(mounted_path):
            assert not os.path.exists(mounted_path)
            os.mkdir(mounted_path, 0o755)
            return True
        else:
            return False

    def remove_dir_if_empty(self, path: str) -> bool:
        if self._read_only_filesystem:
            return self._remove_dir_if_empty_via_mount(path)

        try:
            return super().remove_dir_if_empty(path)
        except ManagementError as e:
            if self._contains_read_only_error(e.out + e.err):
                self._read_only_filesystem = True
                return self._remove_dir_if_empty_via_mount(path)
            else:
                raise

    def _remove_dir_if_empty_via_mount(self, path: str) -> bool:
        mounted_path = self._internal_path_to_mounted_path(path)
        if os.listdir(mounted_path):
            return False
        else:
            os.rmdir(mounted_path)
            return True


class WebReplAdapter(BareMetalAdapter):
    def write_file_in_existing_dir(self, path: str, content: bytes) -> None:
        """
        Adapted from https://github.com/micropython/webrepl/blob/master/webrepl_cli.py
        """
        dest_fname = path.encode("utf-8")
        rec = struct.pack(
            WEBREPL_REQ_S, b"WA", WEBREPL_PUT_FILE, 0, 0, len(content), len(dest_fname), dest_fname
        )
        self._connection.set_text_mode(False)
        try:
            self._write(rec[:10])
            self._write(rec[10:])
            assert self._read_websocket_response() == 0

            to_be_written = content
            block_size = 1024
            while to_be_written:
                block = to_be_written[:block_size]
                self._write(block)
                to_be_written = to_be_written[block_size:]

            assert self._read_websocket_response() == 0
        finally:
            self._connection.set_text_mode(True)

    def _read_websocket_response(self):
        data = self._connection.read(4)
        sig, code = struct.unpack("<2sH", data)
        assert sig == b"WB"
        return code


class RawPasteNotSupportedError(RuntimeError):
    pass


class ReadOnlyFilesystemError(OSError):
    pass
