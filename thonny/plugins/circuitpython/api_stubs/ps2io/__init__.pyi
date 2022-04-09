"""Support for PS/2 protocol

The `ps2io` module contains classes to provide PS/2 communication.

.. warning:: This module is not available in some SAMD21 builds. See the
  :ref:`module-support-matrix` for more info.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info."""

from __future__ import annotations

import microcontroller

class Ps2:
    """Communicate with a PS/2 keyboard or mouse

    Ps2 implements the PS/2 keyboard/mouse serial protocol, used in
    legacy devices. It is similar to UART but there are only two
    lines (Data and Clock). PS/2 devices are 5V, so bidirectional
    level converters must be used to connect the I/O lines to pins
    of 3.3V boards."""

    def __init__(
        self, data_pin: microcontroller.Pin, clock_pin: microcontroller.Pin
    ) -> None:
        """Create a Ps2 object associated with the given pins.

        :param ~microcontroller.Pin data_pin: Pin tied to data wire.
        :param ~microcontroller.Pin clock_pin: Pin tied to clock wire.
          This pin must support interrupts.

        Read one byte from PS/2 keyboard and turn on Scroll Lock LED::

          import ps2io
          import board

          kbd = ps2io.Ps2(board.D10, board.D11)

          while len(kbd) == 0:
              pass

          print(kbd.popleft())
          print(kbd.sendcmd(0xed))
          print(kbd.sendcmd(0x01))"""
        ...
    def deinit(self) -> None:
        """Deinitialises the Ps2 and releases any hardware resources for reuse."""
        ...
    def __enter__(self) -> Ps2:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    def popleft(self) -> int:
        """Removes and returns the oldest received byte. When buffer
        is empty, raises an IndexError exception."""
        ...
    def sendcmd(self, byte: int) -> int:
        """Sends a command byte to PS/2. Returns the response byte, typically
        the general ack value (0xFA). Some commands return additional data
        which is available through :py:func:`popleft()`.

        Raises a RuntimeError in case of failure. The root cause can be found
        by calling :py:func:`clear_errors()`. It is advisable to call
        :py:func:`clear_errors()` before :py:func:`sendcmd()` to flush any
        previous errors.

        :param int byte: byte value of the command"""
        ...
    def clear_errors(self) -> None:
        """Returns and clears a bitmap with latest recorded communication errors.

        Reception errors (arise asynchronously, as data is received):

        0x01: start bit not 0

        0x02: timeout

        0x04: parity bit error

        0x08: stop bit not 1

        0x10: buffer overflow, newest data discarded

        Transmission errors (can only arise in the course of sendcmd()):

        0x100: clock pin didn't go to LO in time

        0x200: clock pin didn't go to HI in time

        0x400: data pin didn't ACK

        0x800: clock pin didn't ACK

        0x1000: device didn't respond to RTS

        0x2000: device didn't send a response byte in time"""
        ...
    def __bool__(self) -> bool: ...
    def __len__(self) -> int:
        """Returns the number of received bytes in buffer, available
        to :py:func:`popleft()`."""
        ...
