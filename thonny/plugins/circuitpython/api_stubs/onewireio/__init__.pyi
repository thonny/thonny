"""Low-level bit primitives for Maxim (formerly Dallas Semi) one-wire protocol.

   Protocol definition is here: https://www.maximintegrated.com/en/app-notes/index.mvp/id/126"""

from __future__ import annotations

import microcontroller

class OneWire:
    def __init__(self, pin: microcontroller.Pin) -> None:
        """Create a OneWire object associated with the given pin.

        The object implements the lowest level timing-sensitive bits of the protocol.

        :param ~microcontroller.Pin pin: Pin connected to the OneWire bus

        .. note:: The OneWire class is available on `busio` and `bitbangio` in CircuitPython
                  7.x for backwards compatibility but will be removed in CircuitPython 8.0.0.

        Read a short series of pulses::

          import onewireio
          import board

          onewire = onewireio.OneWire(board.D7)
          onewire.reset()
          onewire.write_bit(True)
          onewire.write_bit(False)
          print(onewire.read_bit())"""
        ...
    def deinit(self) -> None:
        """Deinitialize the OneWire bus and release any hardware resources for reuse."""
        ...
    def __enter__(self) -> OneWire:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    def reset(self) -> bool:
        """Reset the OneWire bus and read presence

        :returns: False when at least one device is present
        :rtype: bool"""
        ...
    def read_bit(self) -> bool:
        """Read in a bit

        :returns: bit state read
        :rtype: bool"""
        ...
    def write_bit(self, value: bool) -> None:
        """Write out a bit based on value."""
        ...
