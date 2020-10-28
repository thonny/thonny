"""A fast RGB(W) pixel buffer library for like NeoPixel and DotStar.

The `_pixelbuf` module provides the :py:class:`PixelBuf` class to accelerate
RGB(W) strip/matrix manipulation, such as DotStar and Neopixel.

Byteorders are configured with strings, such as "RGB" or "RGBD"."""
def colorwheel(n: int) -> Any:
    """C implementation of the common wheel() function found in many examples.
    Returns the colorwheel RGB value as an integer value for n (usable in :py:class:`PixelBuf`, neopixel, and dotstar)."""
    ...

def wheel(n: Any) -> Any:
    """Use of wheel() is deprecated. Please use colorwheel()."""

class PixelBuf:
    """A fast RGB[W] pixel buffer for LED and similar devices."""

    def __init__(self, size: int, *, byteorder: str = "BGR", brightness: float = 0, auto_write: bool = False, header: bytes = b"", trailer: bytes = b""):
        """Create a PixelBuf object of the specified size, byteorder, and bits per pixel.

        When brightness is less than 1.0, a second buffer will be used to store the color values
        before they are adjusted for brightness.

        When ``P`` (PWM duration) is present as the 4th character of the byteorder
        string, the 4th value in the tuple/list for a pixel is the individual pixel
        brightness (0.0-1.0) and will enable a Dotstar compatible 1st byte for each
        pixel.

        :param ~int size: Number of pixels
        :param ~str byteorder: Byte order string (such as "RGB", "RGBW" or "PBGR")
        :param ~float brightness: Brightness (0 to 1.0, default 1.0)
        :param ~bool auto_write: Whether to automatically write pixels (Default False)
        :param bytes header: Sequence of bytes to always send before pixel values.
        :param bytes trailer: Sequence of bytes to always send after pixel values."""
        ...

    bpp: Any = ...
    """The number of bytes per pixel in the buffer (read-only)"""

    brightness: Any = ...
    """Float value between 0 and 1.  Output brightness.

    When brightness is less than 1.0, a second buffer will be used to store the color values
    before they are adjusted for brightness."""

    auto_write: Any = ...
    """Whether to automatically write the pixels after each update."""

    byteorder: Any = ...
    """byteorder string for the buffer (read-only)"""

    def show(self, ) -> Any:
        """Transmits the color data to the pixels so that they are shown. This is done automatically
        when `auto_write` is True."""
        ...

def fill(color: Any) -> Any:
    """Fills the given pixelbuf with the given color."""
    ...

    def __getitem__(self, index: Any) -> Any:
        """Returns the pixel value at the given index as a tuple of (Red, Green, Blue[, White]) values
        between 0 and 255.  When in PWM (DotStar) mode, the 4th tuple value is a float of the pixel
        intensity from 0-1.0."""
        ...

    def __setitem__(self, index: Any, value: Any) -> Any:
        """Sets the pixel value at the given index.  Value can either be a tuple or integer.  Tuples are
        The individual (Red, Green, Blue[, White]) values between 0 and 255.  If given an integer, the
        red, green and blue values are packed into the lower three bytes (0xRRGGBB).
        For RGBW byteorders, if given only RGB values either as an int or as a tuple, the white value
        is used instead when the red, green, and blue values are the same."""
        ...

