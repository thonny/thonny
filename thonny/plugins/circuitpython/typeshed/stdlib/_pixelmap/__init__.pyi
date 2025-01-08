"""A fast pixel mapping library

The `_pixelmap` module provides the :py:class:`PixelMap` class to accelerate
RGB(W) strip/matrix manipulation, such as DotStar and Neopixel."""

from __future__ import annotations

from typing import List, Tuple, Union, overload

# The types accepted when getting a pixel value
PixelReturnType = Union[
    Tuple[int, int, int], Tuple[int, int, int, int], Tuple[int, int, int, float]
]
PixelReturnSequence = Tuple[PixelReturnType]
# The types returned when getting a pixel value
PixelType = Union[int, PixelReturnType]
PixelSequence = Union[Tuple[PixelType], List[PixelType]]

from adafruit_pixelbuf import PixelBuf, PixelReturnType, PixelSequence, PixelType

class PixelMap:
    def __init__(
        self, pixelbuf: PixelBuf, indices: Tuple[Union[int, Tuple[int]]]
    ) -> None:
        """Construct a PixelMap object that uses the given indices of the underlying pixelbuf"""
    auto_write: bool
    """True if updates should be automatically written"""
    bpp: int
    """The number of bytes per pixel in the buffer (read-only)"""
    byteorder: str
    """byteorder string for the buffer (read-only)"""

    def fill(self, color: PixelType) -> None:
        """Fill all the pixels in the map with the given color"""

    def indices(self, index: int) -> Tuple[int]:
        """Return the PixelBuf indices for a PixelMap index"""

    @overload
    def __getitem__(self, index: slice) -> PixelReturnSequence:
        """Retrieve the value of the underlying pixels."""
        ...

    @overload
    def __getitem__(self, index: int) -> PixelReturnType:
        """Retrieve the value of one of the underlying pixels at 'index'."""
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

    def __len__(self) -> int:
        """Length of the map"""

    def show(self) -> None:
        """Transmits the color data to the pixels so that they are shown. This is done automatically
        when `auto_write` is True."""
        ...
