"""Low-level routines for bitbanged LED matrices

For more information about working with RGB matrix panels in CircuitPython, see
`the dedicated learn guide <https://learn.adafruit.com/rgb-led-matrices-matrix-panels-with-circuitpython>`_.
"""

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

        Tiled matrices, those with more than one panel, must be laid out `in a specific order, as detailed in the guide
        <https://learn.adafruit.com/rgb-led-matrices-matrix-panels-with-circuitpython/advanced-multiple-panels>`_.

        At least 6 RGB pins and 5 address pins are supported, for common panels with up to 64 rows of pixels.
        Some microcontrollers may support more, up to a soft limit of 30 RGB pins and 8 address pins.

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
        `framebufferio.FramebufferDisplay`.

        On boards designed for use with RGBMatrix panels, ``board.MTX_ADDRESS`` is a tuple of all the address pins, and ``board.MTX_COMMON`` is a dictionary with ``rgb_pins``, ``clock_pin``, ``latch_pin``, and ``output_enable_pin``.
        For panels that use fewer than the maximum number of address pins, "slice" ``MTX_ADDRESS`` to get the correct number of address pins.
        Using these board properties makes calling the constructor simpler and more portable:

        .. code-block:: python

            matrix = rgbmatrix.RGBMatrix(..., addr_pins=board.MTX_ADDRESS[:4], **board.MTX_COMMON)

        :param int width: The overall width of the whole matrix in pixels. For a matrix with multiple panels in row, this is the width of a single panel times the number of panels across.
        :param int tile: In a multi-row matrix, the number of rows of panels
        :param int bit_depth: The color depth of the matrix. A value of 1 gives 8 colors, a value of 2 gives 64 colors, and so on. Increasing bit depth increases the CPU and RAM usage of the RGBMatrix, and may lower the panel refresh rate. The framebuffer is always in RGB565 format regardless of the bit depth setting
        :param bool serpentine: In a multi-row matrix, True when alternate rows of panels are rotated 180°, which can reduce wiring length
        :param Sequence[digitalio.DigitalInOut] rgb_pins: The matrix's RGB pins in the order ``(R1,G1,B1,R2,G2,B2...)``
        :param Sequence[digitalio.DigitalInOut] addr_pins: The matrix's address pins in the order ``(A,B,C,D...)``
        :param digitalio.DigitalInOut clock_pin: The matrix's clock pin
        :param digitalio.DigitalInOut latch_pin: The matrix's latch pin
        :param digitalio.DigitalInOut output_enable_pin: The matrix's output enable pin
        :param bool doublebuffer: True if the output is double-buffered
        :param Optional[WriteableBuffer] framebuffer: A pre-allocated framebuffer to use. If unspecified, a framebuffer is allocated
        :param int height: The optional overall height of the whole matrix in pixels. This value is not required because it can be calculated as described above.
        """

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
