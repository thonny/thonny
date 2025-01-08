from __future__ import annotations

from typing import Optional

import busio
import microcontroller

class AuroraMemoryFramebuffer:
    """A framebuffer for Pervasive Displays Aurora E-paper displays.

    These displays are 2 color only.

    This initializes a display and connects it to CircuitPython.

    For Example::

        import busio
        import framebufferio
        from aurora_epaper import AuroraMemoryFramebuffer
        spi = busio.SPI(EINK_CLKS, EINK_MOSI, EINK_MISO)
        aurora = AuroraMemoryFramebuffer(spi, EINK_CS, EINK_RST, EINK_BUSY, EINK_DISCHARGE, HEIGHT, WIDTH)
        display = framebufferio.FramebufferDisplay(t, auto_refresh=False)
        display.refresh()

    For more information on how these displays are driven see:
    https://www.pervasivedisplays.com/wp-content/uploads/2023/02/4P018-00_04_G2_Aurora-Mb_COG_Driver_Interface_Timing_for_small-size_20231107.pdf
    """

    def __init__(
        self,
        spi_bus: busio.SPI,
        chip_select: microcontroller.Pin,
        reset: microcontroller.Pin,
        busy: microcontroller.Pin,
        discharge: microcontroller.Pin,
        width: int,
        height: int,
        power: Optional[microcontroller.Pin] = None,
        free_bus: Optional[bool] = True,
    ) -> None:
        """Create a framebuffer for the Aurora CoG display.

        .. note:: Displays of size 1.9" and 2.6" are not tested, and may exibit unexpected behavior.

        :param busio.SPI spi_bus: The SPI bus that the display is connected to
        :param microcontroller.Pin chip_select: The pin connected to the displays chip select input
        :param microcontroller.Pin reset: The pin connected to the displays reset input
        :param microcontroller.Pin busy: The pin connected to the displays busy output
        :param microcontroller.Pin discharge: The pin connected to the displays discharge input
        :param int width: The width of the display in pixels
        :param int height: The height of the display in pixels
        :param microcontroller.Pin power: The pin that controls power to the display (optional).
        :param bool free_bus: Determines whether the SPI bus passed in will be freed when the frame buffer is freed (optional).
        """
        ...

    def deinit(self) -> None:
        """Free the resources (pins, timers, etc.) associated with this
        AuroraMemoryFramebuffer instance.  After deinitialization, no further operations
        may be performed."""
        ...

    def set_temperature(self, celsius: int) -> None:
        """Set the ambient temperature (in celsius) for the display driver.
        Higher temperature means faster update speed.
        """
        ...
    free_bus: bool
    """When True the spi bus passed into the device will be freed on deinit.
    If you have multiple displays this could be used to keep the other active on soft reset."""
    ...
