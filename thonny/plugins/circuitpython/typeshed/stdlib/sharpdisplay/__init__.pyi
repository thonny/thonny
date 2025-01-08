"""Support for Sharp Memory Display framebuffers

For more information about working with Sharp Memory Displays,
see `this Learn guide <https://learn.adafruit.com/adafruit-sharp-memory-display-breakout/circuitpython-displayio-setup>`_.
"""

from __future__ import annotations

import busio
import microcontroller

class SharpMemoryFramebuffer:
    """A framebuffer for a memory-in-pixel display. Sharp makes monochrome displays and JDI used
    to make 8-color displays.

    This initializes a display and connects it into CircuitPython. Unlike other
    objects in CircuitPython, Display objects live until `displayio.release_displays()`
    is called. This is done so that CircuitPython can use the display itself."""

    def __init__(
        self,
        spi_bus: busio.SPI,
        chip_select: microcontroller.Pin,
        width: int,
        height: int,
        baudrate: int = 2000000,
        jdi_display: bool = False,
    ) -> None:
        """Create a framebuffer for the memory-in-pixel display.

        :param busio.SPI spi_bus: The SPI bus that the display is connected to
        :param microcontroller.Pin chip_select: The pin connect to the display's chip select line
        :param int width: The width of the display in pixels
        :param int height: The height of the display in pixels
        :param int baudrate: The baudrate to communicate with the screen at
        :param bool jdi_display: When True, work with an 8-color JDI display. Otherwise, a monochrome Sharp display.
        """
        ...

    def deinit(self) -> None:
        """Free the resources (pins, timers, etc.) associated with this
        SharpMemoryFramebuffer instance.  After deinitialization, no further operations
        may be performed."""
        ...
