import pathlib
import sys
import threading
import time
from logging import getLogger
from textwrap import dedent

from .connection import MicroPythonConnection

OUTPUT_ENQ = b"\x05"
OUTPUT_ACK = b"\x06"
NORMAL_PROMPT = b">>> "
FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\n>"


logger = getLogger(__name__)


class SerialConnection(MicroPythonConnection):
    def __init__(self, port, baudrate=115200, dtr=None, rts=None, skip_reader=False):
        import serial
        from serial.serialutil import SerialException

        super().__init__()

        try:
            self._serial = serial.Serial(
                port=None, baudrate=baudrate, timeout=None, write_timeout=2, exclusive=True
            )
            # Tweaking dtr and rts was proposed by
            # https://github.com/thonny/thonny/pull/1187
            # but in some cases it messes up communication.
            # At the same time, in some cases it is required
            # https://github.com/thonny/thonny/issues/1462
            # See also https://github.com/micropython/micropython/pull/10347
            if dtr is not None:
                logger.debug("Setting DTR to %s", dtr)
                self._serial.dtr = dtr
            if rts is not None:
                logger.debug("Setting RTS to %s", rts)
                self._serial.rts = rts

            self._serial.port = port
            logger.debug("Opening serial port %s", port)
            self._serial.open()
        except SerialException as error:
            err_str = str(error)
            if "FileNotFoundError" in err_str:
                err_str = "port not found"
            message = "Unable to connect to " + port + ": " + err_str

            # TODO: check if these error codes also apply to Linux and Mac
            if error.errno == 13 and sys.platform == "linux":
                try:
                    group = pathlib.Path(self._serial.port).group()
                except Exception:
                    logger.warning("Could not query group for '%s'", self._serial.port)
                    group = "dialoutfb"

                # TODO: check if user already has this group
                message += "\n\n" + dedent(
                    """\
                Try adding yourself to the '{group}' group:
                > sudo usermod -a -G {group} <username>
                (NB! You may need to reboot your system after this!)""".format(
                        group=group
                    )
                )

            elif "PermissionError" in message or "Could not exclusively lock" in message:
                message += "\n\n" + dedent(
                    """\
                If you have serial connection to the device from another program, then disconnect it there first."""
                )

            elif error.errno == 16:
                message += "\n\n" + "Try restarting the device."

            raise ConnectionRefusedError(message) from error

        if skip_reader:
            self._reading_thread = None
        else:
            self._reading_thread = threading.Thread(target=self._listen_serial, daemon=True)
            self._reading_thread.start()

    def write(self, data: bytes) -> int:
        size = self._serial.write(data)
        # print(data.decode(), end="")
        assert size == len(data)
        return len(data)

    def _listen_serial(self):
        "NB! works in background thread"
        try:
            data = b""
            while not self._reader_stopped:
                data += self._serial.read(1)  # To avoid busy loop
                if len(data) == 0:
                    self._error = "EOF"
                    # print("LISTEN EOFFFFFFFFFF")
                    break
                data += self._serial.read_all()
                # logger.debug("GOT %r", data)

                if data.endswith(OUTPUT_ENQ) and self.text_mode:
                    # Flow control.
                    logger.debug("Read ENQ, responding with ACK")
                    # Assuming connection is idle and it is safe to write in this thread
                    self._serial.write(OUTPUT_ACK)
                    self._serial.flush()
                    data = data[:-1]
                    continue

                # don't publish incomplete utf-8 data
                try:
                    if self.text_mode:
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
                    logger.exception("Couldn't close serial")


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
