"""A fast RGB(W) pixel buffer library for like NeoPixel and DotStar

The `adafruit_pixelbuf` module provides the :py:class:`PixelBuf` class to accelerate
RGB(W) strip/matrix manipulation, such as DotStar and Neopixel.

Byteorders are configured with strings, such as "RGB" or "RGBD"."""

from __future__ import annotations

from typing import List, Tuple, Union, overload

from circuitpython_typing import ReadableBuffer

# The types accepted when getting a pixel value
PixelReturnType = Union[
    Tuple[int, int, int], Tuple[int, int, int, int], Tuple[int, int, int, float]
]
PixelReturnSequence = Tuple[PixelReturnType]
# The types returned when getting a pixel value
PixelType = Union[int, PixelReturnType]
PixelSequence = Union[Tuple[PixelType], List[PixelType]]

class PixelBuf:
    """A fast RGB[W] pixel buffer for LED and similar devices."""

    def __init__(
        self,
        size: int,
        *,
        byteorder: str = "BGR",
        brightness: float = 0,
        auto_write: bool = False,
        header: ReadableBuffer = b"",
        trailer: ReadableBuffer = b"",
    ) -> None:
        """Create a PixelBuf object of the specified size, byteorder, and bits per pixel.

        When brightness is less than 1.0, a second buffer will be used to store the color values
        before they are adjusted for brightness.

        When ``P`` (PWM duration) is present as the 4th character of the byteorder
        string, the 4th value in the tuple/list for a pixel is the individual pixel
        brightness (0.0-1.0) and will enable a Dotstar compatible 1st byte for each
        pixel.

        :param int size: Number of pixels
        :param str byteorder: Byte order string (such as "RGB", "RGBW" or "PBGR")
        :param float brightness: Brightness (0 to 1.0, default 1.0)
        :param bool auto_write: Whether to automatically write pixels (Default False)
        :param ~circuitpython_typing.ReadableBuffer header: Sequence of bytes to always send before pixel values.
        :param ~circuitpython_typing.ReadableBuffer trailer: Sequence of bytes to always send after pixel values.
        """
        ...
    bpp: int
    """The number of bytes per pixel in the buffer (read-only)"""
    brightness: float
    """Float value between 0 and 1.  Output brightness.

    When brightness is less than 1.0, a second buffer will be used to store the color values
    before they are adjusted for brightness."""
    auto_write: bool
    """Whether to automatically write the pixels after each update."""
    byteorder: str
    """byteorder string for the buffer (read-only)"""

    def show(self) -> None:
        """Transmits the color data to the pixels so that they are shown. This is done automatically
        when `auto_write` is True."""
        ...

    def fill(self, color: PixelType) -> None:
        """Fills the given pixelbuf with the given color."""
        ...

    @overload
    def __getitem__(self, index: slice) -> PixelReturnSequence:
        """Returns the pixel value at the given index as a tuple of (Red, Green, Blue[, White]) values
        between 0 and 255.  When in PWM (DotStar) mode, the 4th tuple value is a float of the pixel
        intensity from 0-1.0."""
        ...

    @overload
    def __getitem__(self, index: int) -> PixelReturnType:
        """Returns the pixel value at the given index as a tuple of (Red, Green, Blue[, White]) values
        between 0 and 255.  When in PWM (DotStar) mode, the 4th tuple value is a float of the pixel
        intensity from 0-1.0."""
        ...

    @overload
    def __setitem__(self, index: slice, value: PixelSequence) -> None: ...
    @overload
    def __setitem__(self, index: int, value: PixelType) -> None:
        """Sets the pixel value at the given index.  Value can either be a tuple or integer.  Tuples are
        The individual (Red, Green, Blue[, White]) values between 0 and 255.  If given an integer, the
        red, green and blue values are packed into the lower three bytes (0xRRGGBB).
        For RGBW byteorders, if given only RGB values either as an int or as a tuple, the white value
        is used instead when the red, green, and blue values are the same."""
        ...
