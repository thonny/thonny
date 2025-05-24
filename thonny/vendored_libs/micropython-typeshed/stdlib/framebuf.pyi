"""
Frame buffer manipulation.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/framebuf.html

This module provides a general frame buffer which can be used to create
bitmap images, which can then be sent to a display.

---
Module: 'framebuf' on micropython-v1.25.0-esp32-ESP32_GENERIC-SPIRAM
"""

# MCU: {'variant': 'SPIRAM', 'build': '', 'arch': 'xtensawin', 'port': 'esp32', 'board': 'ESP32_GENERIC', 'board_id': 'ESP32_GENERIC-SPIRAM', 'mpy': 'v6.3', 'ver': '1.25.0', 'family': 'micropython', 'cpu': 'ESP32', 'version': '1.25.0'}
# Stubber: v1.25.0
from __future__ import annotations
from typing import Any, Optional, overload, Final
from _typeshed import Incomplete
from _mpy_shed import AnyReadableBuf, AnyWritableBuf
from typing_extensions import Awaitable, TypeAlias, TypeVar

MONO_HMSB: Final[int] = 4
MONO_HLSB: Final[int] = 3
RGB565: Final[int] = 1
MONO_VLSB: Final[int] = 0
MVLSB: Final[int] = 0
GS2_HMSB: Final[int] = 5
GS8: Final[int] = 6
GS4_HMSB: Final[int] = 2

def FrameBuffer1(*args, **kwargs) -> Incomplete: ...

class FrameBuffer:
    """
    The FrameBuffer class provides a pixel buffer which can be drawn upon with
    pixels, lines, rectangles, text and even other FrameBuffer's. It is useful
    when generating output for displays.

    For example::

        import framebuf

        # FrameBuffer needs 2 bytes for every RGB565 pixel
        fbuf = framebuf.FrameBuffer(bytearray(100 * 10 * 2), 100, 10, framebuf.RGB565)

        fbuf.fill(0)
        fbuf.text('MicroPython!', 0, 0, 0xffff)
        fbuf.hline(0, 9, 96, 0xffff)
    """

    def poly(self, x, y, coords, c, f: Optional[Any] = None) -> Incomplete:
        """
        Given a list of coordinates, draw an arbitrary (convex or concave) closed
        polygon at the given x, y location using the given color.

        The *coords* must be specified as a :mod:`array` of integers, e.g.
        ``array('h', [x0, y0, x1, y1, ... xn, yn])``.

        The optional *f* parameter can be set to ``True`` to fill the polygon.
        Otherwise just a one pixel outline is drawn.
        """
        ...

    def vline(self, x: int, y: int, h: int, c: int, /) -> None:
        """
        Draw a line from a set of coordinates using the given color and
        a thickness of 1 pixel. The `line` method draws the line up to
        a second set of coordinates whereas the `hline` and `vline`
        methods draw horizontal and vertical lines respectively up to
        a given length.
        """

    @overload
    def pixel(self, x: int, y: int, /) -> int:
        """
        If *c* is not given, get the color value of the specified pixel.
        If *c* is given, set the specified pixel to the given color.
        """

    @overload
    def pixel(self, x: int, y: int, c: int, /) -> None:
        """
        If *c* is not given, get the color value of the specified pixel.
        If *c* is given, set the specified pixel to the given color.
        """

    def text(self, s: str, x: int, y: int, c: int = 1, /) -> None:
        """
        Write text to the FrameBuffer using the coordinates as the upper-left
        corner of the text. The color of the text can be defined by the optional
        argument but is otherwise a default value of 1. All characters have
        dimensions of 8x8 pixels and there is currently no way to change the font.
        """
        ...

    def rect(self, x: int, y: int, w: int, h: int, c: int, /) -> None:
        """
        Draw a rectangle at the given location, size and color.

        The optional *f* parameter can be set to ``True`` to fill the rectangle.
        Otherwise just a one pixel outline is drawn.
        """
        ...

    def scroll(self, xstep: int, ystep: int, /) -> None:
        """
        Shift the contents of the FrameBuffer by the given vector. This may
        leave a footprint of the previous colors in the FrameBuffer.
        """
        ...

    def ellipse(self, x, y, xr, yr, c, f, m: Optional[Any] = None) -> None:
        """
        Draw an ellipse at the given location. Radii *xr* and *yr* define the
        geometry; equal values cause a circle to be drawn. The *c* parameter
        defines the color.

        The optional *f* parameter can be set to ``True`` to fill the ellipse.
        Otherwise just a one pixel outline is drawn.

        The optional *m* parameter enables drawing to be restricted to certain
        quadrants of the ellipse. The LS four bits determine which quadrants are
        to be drawn, with bit 0 specifying Q1, b1 Q2, b2 Q3 and b3 Q4. Quadrants
        are numbered counterclockwise with Q1 being top right.
        """
        ...

    def line(self, x1: int, y1: int, x2: int, y2: int, c: int, /) -> None:
        """
        Draw a line from a set of coordinates using the given color and
        a thickness of 1 pixel. The `line` method draws the line up to
        a second set of coordinates whereas the `hline` and `vline`
        methods draw horizontal and vertical lines respectively up to
        a given length.
        """
        ...

    def blit(
        self,
        fbuf: FrameBuffer,
        x: int,
        y: int,
        key: int = -1,
        palette: Optional[bytes] = None,
        /,
    ) -> None:
        """
        Draw another FrameBuffer on top of the current one at the given coordinates.
        If *key* is specified then it should be a color integer and the
        corresponding color will be considered transparent: all pixels with that
        color value will not be drawn. (If the *palette* is specified then the *key*
        is compared to the value from *palette*, not to the value directly from
        *fbuf*.)

        The *palette* argument enables blitting between FrameBuffers with differing
        formats. Typical usage is to render a monochrome or grayscale glyph/icon to
        a color display. The *palette* is a FrameBuffer instance whose format is
        that of the current FrameBuffer. The *palette* height is one pixel and its
        pixel width is the number of colors in the source FrameBuffer. The *palette*
        for an N-bit source needs 2**N pixels; the *palette* for a monochrome source
        would have 2 pixels representing background and foreground colors. The
        application assigns a color to each pixel in the *palette*. The color of the
        current pixel will be that of that *palette* pixel whose x position is the
        color of the corresponding source pixel.
        """
        ...

    def hline(self, x: int, y: int, w: int, c: int, /) -> None:
        """
        Draw a line from a set of coordinates using the given color and
        a thickness of 1 pixel. The `line` method draws the line up to
        a second set of coordinates whereas the `hline` and `vline`
        methods draw horizontal and vertical lines respectively up to
        a given length.
        """

    def fill(self, c: int, /) -> None:
        """
        Fill the entire FrameBuffer with the specified color.
        """
        ...

    def fill_rect(self, *args, **kwargs) -> Incomplete: ...
    def __init__(
        self,
        buffer: AnyWritableBuf,
        width: int,
        height: int,
        format: int,
        stride: int = ...,
        /,
    ) -> None:
        """
        Construct a FrameBuffer object.  The parameters are:

            - *buffer* is an object with a buffer protocol which must be large
              enough to contain every pixel defined by the width, height and
              format of the FrameBuffer.
            - *width* is the width of the FrameBuffer in pixels
            - *height* is the height of the FrameBuffer in pixels
            - *format* specifies the type of pixel used in the FrameBuffer;
              permissible values are listed under Constants below. These set the
              number of bits used to encode a color value and the layout of these
              bits in *buffer*.
              Where a color value c is passed to a method, c is a small integer
              with an encoding that is dependent on the format of the FrameBuffer.
            - *stride* is the number of pixels between each horizontal line
              of pixels in the FrameBuffer. This defaults to *width* but may
              need adjustments when implementing a FrameBuffer within another
              larger FrameBuffer or screen. The *buffer* size must accommodate
              an increased step size.

        One must specify valid *buffer*, *width*, *height*, *format* and
        optionally *stride*.  Invalid *buffer* size or dimensions may lead to
        unexpected errors.
        """
