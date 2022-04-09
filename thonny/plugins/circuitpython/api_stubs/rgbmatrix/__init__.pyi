"""Low-level routines for bitbanged LED matrices"""

from __future__ import annotations

from typing import Optional, Sequence

import digitalio
from circuitpython_typing import WriteableBuffer

class RGBMatrix:
    """Displays an in-memory framebuffer to a HUB75-style RGB LED matrix."""

    def __init__(
        self,
        *,
        width: int,
        bit_depth: int,
        rgb_pins: Sequence[digitalio.DigitalInOut],
        addr_pins: Sequence[digitalio.DigitalInOut],
        clock_pin: digitalio.DigitalInOut,
        latch_pin: digitalio.DigitalInOut,
        output_enable_pin: digitalio.DigitalInOut,
        doublebuffer: bool = True,
        framebuffer: Optional[WriteableBuffer] = None,
        height: int = 0,
        tile: int = 1,
        serpentine: bool = True,
    ) -> None:
        """Create a RGBMatrix object with the given attributes.  The height of
        the display is determined by the number of rgb and address pins and the number of tiles:
        ``len(rgb_pins) // 3 * 2 ** len(address_pins) * abs(tile)``.  With 6 RGB pins, 4
        address lines, and a single matrix, the display will be 32 pixels tall.  If the optional height
        parameter is specified and is not 0, it is checked against the calculated
        height.

        Up to 30 RGB pins and 8 address pins are supported.

        The RGB pins must be within a single "port" and performance and memory
        usage are best when they are all within "close by" bits of the port.
        The clock pin must also be on the same port as the RGB pins.  See the
        documentation of the underlying protomatter C library for more
        information.  Generally, Adafruit's interface boards are designed so
        that these requirements are met when matched with the intended
        microcontroller board.  For instance, the Feather M4 Express works
        together with the RGB Matrix Feather.

        The framebuffer is in "RGB565" format.

        "RGB565" means that it is organized as a series of 16-bit numbers
        where the highest 5 bits are interpreted as red, the next 6 as
        green, and the final 5 as blue.  The object can be any buffer, but
        `array.array` and ``ulab.ndarray`` objects are most often useful.
        To update the content, modify the framebuffer and call refresh.

        If a framebuffer is not passed in, one is allocated and initialized
        to all black.  In any case, the framebuffer can be retrieved
        by passing the RGBMatrix object to memoryview().

        If doublebuffer is False, some memory is saved, but the display may
        flicker during updates.

        A RGBMatrix is often used in conjunction with a
        `framebufferio.FramebufferDisplay`."""
    def deinit(self) -> None:
        """Free the resources (pins, timers, etc.) associated with this
        rgbmatrix instance.  After deinitialization, no further operations
        may be performed."""
        ...
    brightness: float
    """In the current implementation, 0.0 turns the display off entirely
    and any other value up to 1.0 turns the display on fully."""

    def refresh(self) -> None:
        """Transmits the color data in the buffer to the pixels so that
        they are shown."""
        ...
    width: int
    """The width of the display, in pixels"""

    height: int
    """The height of the display, in pixels"""
