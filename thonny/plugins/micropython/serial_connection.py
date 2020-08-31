import logging
import platform
import sys
import threading
import time
from textwrap import dedent

from thonny.plugins.micropython.backend import FIRST_RAW_PROMPT
from thonny.plugins.micropython.bare_metal_backend import NORMAL_PROMPT
from thonny.common import ConnectionFailedException
from thonny.plugins.micropython.connection import MicroPythonConnection


class SerialConnection(MicroPythonConnection):
    def __init__(self, port, baudrate, skip_reader=False):
        import serial
        from serial.serialutil import SerialException

        super().__init__()

        try:
            self._serial = serial.Serial(port, baudrate=baudrate, timeout=None)
        except SerialException as error:
            err_str = str(error)
            if "FileNotFoundError" in err_str:
                err_str = "port not found"
            message = "Unable to connect to " + port + ": " + err_str

            # TODO: check if these error codes also apply to Linux and Mac
            if error.errno == 13 and platform.system() == "Linux":
                # TODO: check if user already has this group
                message += "\n\n" + dedent(
                    """\
                Try adding yourself to the 'dialout' group:
                > sudo usermod -a -G dialout <username>
                (NB! This needs to be followed by reboot or logging out and logging in again!)"""
                )

            elif "PermissionError" in message:
                message += "\n\n" + dedent(
                    """\
                If you have serial connection to the device from another program,
                then disconnect it there."""
                )

            elif error.errno == 16:
                message += "\n\n" + "Try restarting the device."

            raise ConnectionFailedException(message)

        if skip_reader:
            self._reading_thread = None
        else:
            self._reading_thread = threading.Thread(target=self._listen_serial, daemon=True)
            self._reading_thread.start()

    def write(self, data, block_size=255, delay=0.01):
        # delay and block size taken from rshell
        # https://github.com/dhylands/rshell/blob/master/rshell/pyboard.py#L242
        for i in range(0, len(data), block_size):
            block = data[i : i + block_size]
            # self._log_data(b"[" + block + b"]")
            size = self._serial.write(block)
            assert size == len(block)
            time.sleep(delay)
        return len(data)

    def _listen_serial(self):
        "NB! works in background thread"
        try:
            data = b""
            while True:
                data += self._serial.read(1)  # To avoid busy loop
                if len(data) == 0:
                    self._error = "EOF"
                    # print("LISTEN EOFFFFFFFFFF")
                    break
                data += self._serial.read_all()

                # don't publish incomplete utf-8 data
                try:
                    data.decode("utf-8")  # testing if data decodes
                    to_be_published = data
                    data = b""
                except UnicodeDecodeError as e:
                    if e.start == 0:
                        # Invalid start byte, ie. we have missed first byte(s) of the codepoint.
                        # No use of waiting, output everything
                        to_be_published = data
                        data = b""
                    else:
                        to_be_published = data[: e.start]
                        data = data[e.start :]

                if to_be_published:
                    self._make_output_available(to_be_published)

        except Exception as e:
            self._error = str(e)

    def incoming_is_empty(self):
        return self._serial.in_waiting == 0 and super().incoming_is_empty()

    def outgoing_is_empty(self):
        return self._serial.out_waiting == 0

    def reset_output_buffer(self):
        self._serial.reset_output_buffer()

    def close(self):
        if self._serial is not None:
            try:
                self._serial.cancel_read()
                if self._reading_thread:
                    self._reading_thread.join()
            finally:
                try:
                    self._serial.close()
                    self._serial = None
                except Exception:
                    logging.exception("Couldn't close serial")


class DifficultSerialConnection(SerialConnection):
    """For hardening the communication protocol"""

    def _make_output_available(self, data, block=True):

        # output prompts in parts
        if FIRST_RAW_PROMPT in data or NORMAL_PROMPT in data:
            if FIRST_RAW_PROMPT in data:
                start = data.find(FIRST_RAW_PROMPT)
                end = start + len(FIRST_RAW_PROMPT)
            else:
                start = data.find(NORMAL_PROMPT)
                end = start + len(NORMAL_PROMPT)

            super()._make_output_available(data[: start + 1], block=block)
            time.sleep(0.1)
            super()._make_output_available(data[start + 1 : end - 1], block=block)
            time.sleep(0.1)
            super()._make_output_available(data[end - 1 :], block=block)
        else:
            super()._make_output_available(data, block=block)


def debug(*args, file=sys.stderr):
    print(*args, file=file)
