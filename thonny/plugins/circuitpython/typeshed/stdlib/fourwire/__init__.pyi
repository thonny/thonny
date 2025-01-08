"""Connects to a BusDisplay over a four wire bus

"""

from __future__ import annotations

from typing import Optional

import busio
import microcontroller
from circuitpython_typing import ReadableBuffer

class FourWire:
    """Manage updating a display over SPI four wire protocol in the background while Python code runs.
    It doesn't handle display initialization."""

    def __init__(
        self,
        spi_bus: busio.SPI,
        *,
        command: Optional[microcontroller.Pin],
        chip_select: Optional[microcontroller.Pin],
        reset: Optional[microcontroller.Pin] = None,
        baudrate: int = 24000000,
        polarity: int = 0,
        phase: int = 0,
    ) -> None:
        """Create a FourWire object associated with the given pins.

        The SPI bus and pins are then in use by the display until `displayio.release_displays()` is
        called even after a reload. (It does this so CircuitPython can use the display after your code
        is done.) So, the first time you initialize a display bus in code.py you should call
        :py:func:`displayio.release_displays` first, otherwise it will error after the first code.py run.

        If the ``command`` pin is not specified, a 9-bit SPI mode will be simulated by adding a
        data/command bit to every bit being transmitted, and splitting the resulting data back
        into 8-bit bytes for transmission. The extra bits that this creates at the end are ignored
        by the receiving device.

        :param busio.SPI spi_bus: The SPI bus that make up the clock and data lines
        :param microcontroller.Pin command: Data or command pin. When None, 9-bit SPI is simulated.
        :param microcontroller.Pin chip_select: Chip select pin
        :param microcontroller.Pin reset: Reset pin. When None only software reset can be used
        :param int baudrate: Maximum baudrate in Hz for the display on the bus
        :param int polarity: the base state of the clock line (0 or 1)
        :param int phase: the edge of the clock that data is captured. First (0)
            or second (1). Rising or falling depends on clock polarity."""
        ...

    def reset(self) -> None:
        """Performs a hardware reset via the reset pin. Raises an exception if called when no reset pin
        is available."""
        ...

    def send(
        self, command: int, data: ReadableBuffer, *, toggle_every_byte: bool = False
    ) -> None:
        """Sends the given command value followed by the full set of data. Display state, such as
        vertical scroll, set via ``send`` may or may not be reset once the code is done.
        """
        ...
