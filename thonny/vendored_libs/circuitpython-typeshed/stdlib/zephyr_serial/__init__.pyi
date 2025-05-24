"""Zephyr UART driver for fixed busses."""

from __future__ import annotations

from typing import Optional

from circuitpython_typing import ReadableBuffer, WriteableBuffer

class UART:
    """A bidirectional serial protocol. Already initialized for Zephyr defined
       busses in :py:mod:`board`.

    .. raw:: html

        <p>
        <details>
        <summary>Available on these boards</summary>
        <ul>
        {% for board in support_matrix_reverse["zephyr_serial.UART"] %}
        <li> {{ board }}
        {% endfor %}
        </ul>
        </details>
        </p>

    """

    def deinit(self) -> None:
        """Deinitialises the UART and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> UART:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def read(self, nbytes: Optional[int] = None) -> Optional[bytes]:
        """Read bytes.  If ``nbytes`` is specified then read at most that many
        bytes. Otherwise, read everything that arrives until the connection
        times out. Providing the number of bytes expected is highly recommended
        because it will be faster. If no bytes are read, return ``None``.

        .. note:: When no bytes are read due to a timeout, this function returns ``None``.
          This matches the behavior of `io.RawIOBase.read` in Python 3, but
          differs from pyserial which returns ``b''`` in that situation.

        :return: Data read
        :rtype: bytes or None"""
        ...

    def readinto(self, buf: WriteableBuffer) -> Optional[int]:
        """Read bytes into the ``buf``. Read at most ``len(buf)`` bytes.

        :return: number of bytes read and stored into ``buf``
        :rtype: int or None (on a non-blocking error)

        *New in CircuitPython 4.0:* No length parameter is permitted."""
        ...

    def readline(self) -> bytes:
        """Read a line, ending in a newline character, or
        return ``None`` if a timeout occurs sooner, or
        return everything readable if no newline is found and
        ``timeout=0``

        :return: the line read
        :rtype: bytes or None"""
        ...

    def write(self, buf: ReadableBuffer) -> Optional[int]:
        """Write the buffer of bytes to the bus.

        *New in CircuitPython 4.0:* ``buf`` must be bytes, not a string.

          :return: the number of bytes written
          :rtype: int or None"""
        ...
    baudrate: int
    """The current baudrate."""
    in_waiting: int
    """The number of bytes in the input buffer, available to be read"""
    timeout: float
    """The current timeout, in seconds (float)."""

    def reset_input_buffer(self) -> None:
        """Discard any unread characters in the input buffer."""
        ...
