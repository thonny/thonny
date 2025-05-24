"""USB CDC Serial streams

The `usb_cdc` module allows access to USB CDC (serial) communications.

On Windows, each `Serial` is visible as a separate COM port. The ports will often
be assigned consecutively, `console` first, but this is not always true.

On Linux, the ports are typically ``/dev/ttyACM0`` and ``/dev/ttyACM1``.
The `console` port will usually be first.

On MacOS, the ports are typically ``/dev/cu.usbmodem<something>``. The something
varies based on the USB bus and port used. The `console` port will usually be first.
"""

from __future__ import annotations

from typing import List, Optional

from circuitpython_typing import ReadableBuffer, WriteableBuffer

console: Optional[Serial]
"""The `console` `Serial` object is used for the REPL, and for `sys.stdin` and `sys.stdout`.
   `console` is ``None`` if disabled.

However, note that `sys.stdin` and `sys.stdout` are text-based streams,
and the `console` object is a binary stream.
You do not normally need to write to `console` unless you want to write binary data.
"""

data: Optional[Serial]
"""A `Serial` object that can be used to send and receive binary data to and from
the host.
Note that `data` is *disabled* by default. ``data`` is ``None`` if disabled."""

def disable() -> None:
    """Do not present any USB CDC device to the host.
    Can be called in ``boot.py``, before USB is connected.
    Equivalent to ``usb_cdc.enable(console=False, data=False)``."""
    ...

def enable(*, console: bool = True, data: bool = False) -> None:
    """Enable or disable each CDC device. Can be called in ``boot.py``, before USB is connected.

    :param console bool: Enable or disable the `console` USB serial device.
      True to enable; False to disable. Enabled by default.
    :param data bool: Enable or disable the `data` USB serial device.
      True to enable; False to disable. *Disabled* by default.

    If you enable too many devices at once, you will run out of USB endpoints.
    The number of available endpoints varies by microcontroller.
    CircuitPython will go into safe mode after running boot.py to inform you if
    not enough endpoints are available.
    """
    ...

class Serial:
    """Receives cdc commands over USB"""

    def __init__(self) -> None:
        """You cannot create an instance of `usb_cdc.Serial`.
        The available instances are in the ``usb_cdc.serials`` tuple."""
        ...

    def read(self, size: int = -1) -> bytes:
        """Read at most ``size`` bytes. If ``size`` exceeds the internal buffer size,
        only the bytes in the buffer will be read. If ``size`` is not specified or is ``-1``,
        read as many bytes as possible, until the timeout expires.
        If `timeout` is > 0 or ``None``, and fewer than ``size`` bytes are available,
        keep waiting until the timeout expires or ``size`` bytes are available.

        If no bytes are read, return ``b''``. This is unlike, say, `busio.UART.read()`, which
        would return ``None``.

        :return: Data read
        :rtype: bytes"""
        ...

    def readinto(self, buf: WriteableBuffer) -> int:
        """Read bytes into the ``buf``. Read at most ``len(buf)`` bytes. If `timeout`
        is > 0 or ``None``, keep waiting until the timeout expires or ``len(buf)``
        bytes are available.

        :return: number of bytes read and stored into ``buf``
        :rtype: int"""
        ...

    def readline(self, size: int = -1) -> Optional[bytes]:
        r"""Read a line ending in a newline character ("\\n"), including the newline.
        Return everything readable if no newline is found and ``timeout`` is 0.
        Return ``None`` in case of error.

        This is a binary stream: the newline character "\\n" cannot be changed.
        If the host computer transmits "\\r" it will also be included as part of the line.

        :param int size: maximum number of characters to read. ``-1`` means as many as possible.
        :return: the line read
        :rtype: bytes or None"""
        ...

    def readlines(self) -> List[Optional[bytes]]:
        """Read multiple lines as a list, using `readline()`.

        .. warning:: If ``timeout`` is ``None``,
          `readlines()` will never return, because there is no way to indicate end of stream.

        :return: a list of the line read
        :rtype: list"""
        ...

    def write(self, buf: ReadableBuffer) -> int:
        """Write as many bytes as possible from the buffer of bytes.

        :return: the number of bytes written
        :rtype: int"""
        ...

    def flush(self) -> None:
        """Force out any unwritten bytes, waiting until they are written."""
        ...
    connected: bool
    """True if this Serial is connected to a host. (read-only)

    .. note:: The host is considered to be connected if it is asserting DTR (Data Terminal Ready).
      Most terminal programs and ``pyserial`` assert DTR when opening a serial connection.
      However, the C# ``SerialPort`` API does not. You must set ``SerialPort.DtrEnable``.
    """
    in_waiting: int
    """Returns the number of bytes waiting to be read on the USB serial input. (read-only)"""
    out_waiting: int
    """Returns the number of bytes waiting to be written on the USB serial output. (read-only)"""

    def reset_input_buffer(self) -> None:
        """Clears any unread bytes."""
        ...

    def reset_output_buffer(self) -> None:
        """Clears any unwritten bytes."""
        ...
    timeout: Optional[float]
    """The initial value of `timeout` is ``None``. If ``None``, wait indefinitely to satisfy
    the conditions of a read operation. If 0, do not wait. If > 0, wait only ``timeout`` seconds."""
    write_timeout: Optional[float]
    """The initial value of `write_timeout` is ``None``. If ``None``, wait indefinitely to finish
    writing all the bytes passed to ``write()``.If 0, do not wait.
    If > 0, wait only ``write_timeout`` seconds."""
