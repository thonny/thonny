"""Communicates to a display IC over I2C"""

from __future__ import annotations

from typing import Optional

import busio
import microcontroller
from circuitpython_typing import ReadableBuffer

class I2CDisplayBus:
    """Manage updating a display over I2C in the background while Python code runs.
    It doesn't handle display initialization.

    .. seealso:: See `busdisplay.BusDisplay` and `epaperdisplay.EPaperDisplay`
        for how to initialize a display, given an `I2CDisplayBus`.
    """

    def __init__(
        self,
        i2c_bus: busio.I2C,
        *,
        device_address: int,
        reset: Optional[microcontroller.Pin] = None,
    ) -> None:
        """Create a I2CDisplayBus object associated with the given I2C bus and reset pin.

        The I2C bus and pins are then in use by the display until `displayio.release_displays()` is
        called even after a reload. (It does this so CircuitPython can use the display after your code
        is done.) So, the first time you initialize a display bus in code.py you should call
        :py:func:`displayio.release_displays` first, otherwise it will error after the first code.py run.

        :param busio.I2C i2c_bus: The I2C bus that make up the clock and data lines
        :param int device_address: The I2C address of the device
        :param microcontroller.Pin reset: Reset pin. When None only software reset can be used
        """
        ...

    def reset(self) -> None:
        """Performs a hardware reset via the reset pin. Raises an exception if called when no reset pin
        is available."""
        ...

    def send(self, command: int, data: ReadableBuffer) -> None:
        """Sends the given command value followed by the full set of data. Display state, such as
        vertical scroll, set via ``send`` may or may not be reset once the code is done.
        """
        ...
