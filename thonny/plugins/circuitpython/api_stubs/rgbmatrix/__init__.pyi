"""Low-level routines for bitbanged LED matrices"""

class RGBMatrix:
    """Displays an in-memory framebuffer to a HUB75-style RGB LED matrix."""

    def __init__(self, *, width: Any, bit_depth: Any, rgb_pins: Any, addr_pins: Any, clock_pin: Any, latch_pin: Any, output_enable_pin: Any, doublebuffer: Any = True, framebuffer: Any = None, height: Any = 0):
        """Create a RGBMatrix object with the given attributes.  The height of
        the display is determined by the number of rgb and address pins:
        len(rgb_pins) // 3 * 2 ** len(address_pins).  With 6 RGB pins and 4
        address lines, the display will be 32 pixels tall.  If the optional height
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
        `array.array` and `ulab.array` objects are most often useful.
        To update the content, modify the framebuffer and call refresh.

        If a framebuffer is not passed in, one is allocated and initialized
        to all black.  In any case, the framebuffer can be retrieved
        by passing the RGBMatrix object to memoryview().

        If doublebuffer is False, some memory is saved, but the display may
        flicker during updates.

        A RGBMatrix is often used in conjunction with a
        `framebufferio.FramebufferDisplay`."""

    def deinit(self, ) -> Any:
        """Free the resources (pins, timers, etc.) associated with this
        rgbmatrix instance.  After deinitialization, no further operations
        may be performed."""
        ...

    brightness: Any = ...
    """In the current implementation, 0.0 turns the display off entirely
    and any other value up to 1.0 turns the display on fully."""

    def refresh(self) -> Any: ...
    """Transmits the color data in the buffer to the pixels so that
    they are shown."""

    width: int = ...
    """The width of the display, in pixels"""

    height: int = ...
    """The height of the display, in pixels"""

