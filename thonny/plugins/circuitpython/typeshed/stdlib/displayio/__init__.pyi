"""High level, display object compositing system

The `displayio` module contains classes to define what objects to display.
It is optimized for low memory use and, therefore, computes final pixel
values for dirty regions as needed.

Separate modules manage transmitting the display contents to a display.

For more a more thorough explanation and guide for using `displayio`, please
refer to `this Learn guide
<https://learn.adafruit.com/circuitpython-display-support-using-displayio>`_.
"""

from __future__ import annotations

import typing
from typing import Iterator, Optional, Tuple, Union

import vectorio
from circuitpython_typing import ReadableBuffer

CIRCUITPYTHON_TERMINAL: Group
"""The `displayio.Group` that is the displayed serial terminal (REPL)."""

from busdisplay import BusDisplay as Display
from epaperdisplay import EPaperDisplay
from fourwire import FourWire
from i2cdisplaybus import I2CDisplayBus as I2CDisplay

def release_displays() -> None:
    """Releases any actively used displays so their buses and pins can be used again. This will also
    release the builtin display on boards that have one. You will need to reinitialize it yourself
    afterwards. This may take seconds to complete if an active EPaperDisplay is refreshing.

    Use this once in your code.py if you initialize a display. Place it right before the
    initialization so the display is active as long as possible."""
    ...

class Colorspace:
    """The colorspace for a `ColorConverter` to operate in"""

    RGB888: Colorspace
    """The standard 24-bit colorspace.  Bits 0-7 are blue, 8-15 are green, and 16-24 are red. (0xRRGGBB)"""

    RGB565: Colorspace
    """The standard 16-bit colorspace.  Bits 0-4 are blue, bits 5-10 are green, and 11-15 are red (0bRRRRRGGGGGGBBBBB)"""

    RGB565_SWAPPED: Colorspace
    """The swapped 16-bit colorspace.  First, the high and low 8 bits of the number are swapped, then they are interpreted as for RGB565"""

    RGB555: Colorspace
    """The standard 15-bit colorspace.  Bits 0-4 are blue, bits 5-9 are green, and 11-14 are red.  The top bit is ignored. (0bxRRRRRGGGGGBBBBB)"""

    RGB555_SWAPPED: Colorspace
    """The swapped 15-bit colorspace.  First, the high and low 8 bits of the number are swapped, then they are interpreted as for RGB555"""

class Bitmap:
    """Stores values of a certain size in a 2D array

    Bitmaps can be treated as read-only buffers. If the number of bits in a pixel is 8, 16, or 32; and the number of bytes
    per row is a multiple of 4, then the resulting memoryview will correspond directly with the bitmap's contents. Otherwise,
    the bitmap data is packed into the memoryview with unspecified padding.

    A Bitmap can be treated as a buffer, allowing its content to be
    viewed and modified using e.g., with ``ulab.numpy.frombuffer``,
    but the `displayio.Bitmap.dirty` method must be used to inform
    displayio when a bitmap was modified through the buffer interface.

    `bitmaptools.arrayblit` can also be useful to move data efficiently
    into a Bitmap."""

    def __init__(self, width: int, height: int, value_count: int) -> None:
        """Create a Bitmap object with the given fixed size. Each pixel stores a value that is used to
        index into a corresponding palette. This enables differently colored sprites to share the
        underlying Bitmap. value_count is used to minimize the memory used to store the Bitmap.

        :param int width: The number of values wide
        :param int height: The number of values high
        :param int value_count: The number of possible pixel values."""
        ...
    width: int
    """Width of the bitmap. (read only)"""
    height: int
    """Height of the bitmap. (read only)"""
    bits_per_value: int
    """Bits per Pixel of the bitmap. (read only)"""
    def __getitem__(self, index: Union[Tuple[int, int], int]) -> int:
        """Returns the value at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          print(bitmap[0,1])"""
        ...

    def __setitem__(self, index: Union[Tuple[int, int], int], value: int) -> None:
        """Sets the value at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          bitmap[0,1] = 3"""
        ...

    def fill(self, value: int) -> None:
        """Fills the bitmap with the supplied palette index value."""
        ...

    def dirty(self, x1: int = 0, y1: int = 0, x2: int = -1, y2: int = -1) -> None:
        """Inform displayio of bitmap updates done via the buffer
        protocol.

        :param int x1: Minimum x-value for rectangular bounding box to be considered as modified
        :param int y1: Minimum y-value for rectangular bounding box to be considered as modified
        :param int x2: Maximum x-value (exclusive) for rectangular bounding box to be considered as modified
        :param int y2: Maximum y-value (exclusive) for rectangular bounding box to be considered as modified

        If x1 or y1 are not specified, they are taken as 0.  If x2 or y2
        are not specified, or are given as -1, they are taken as the width
        and height of the image.  Thus, calling dirty() with the
        default arguments treats the whole bitmap as modified.

        When a bitmap is modified through the buffer protocol, the
        display will not be properly updated unless the bitmap is
        notified of the "dirty rectangle" that encloses all modified
        pixels."""
        ...

    def deinit(self) -> None:
        """Release resources allocated by Bitmap."""
        ...

class ColorConverter:
    """Converts one color format to another."""

    def __init__(
        self, *, input_colorspace: Colorspace = Colorspace.RGB888, dither: bool = False
    ) -> None:
        """Create a ColorConverter object to convert color formats.

        :param Colorspace colorspace: The source colorspace, one of the Colorspace constants
        :param bool dither: Adds random noise to dither the output image"""
        ...

    def convert(self, color: int) -> int:
        """Converts the given color to RGB565 according to the Colorspace"""
        ...
    dither: bool
    """When `True` the ColorConverter dithers the output by adding random noise when
    truncating to display bitdepth"""
    def make_transparent(self, color: int) -> None:
        """Set the transparent color or index for the ColorConverter. This will
        raise an Exception if there is already a selected transparent index.

        :param int color: The color to be transparent"""

    def make_opaque(self, color: int) -> None:
        """Make the ColorConverter be opaque and have no transparent pixels.

        :param int color: [IGNORED] Use any value"""

class Group:
    """Manage a group of sprites and groups and how they are inter-related."""

    def __init__(self, *, scale: int = 1, x: int = 0, y: int = 0) -> None:
        """Create a Group of a given size and scale. Scale is in one dimension. For example, scale=2
        leads to a layer's pixel being 2x2 pixels when in the group.

        :param int scale: Scale of layer pixels in one dimension.
        :param int x: Initial x position within the parent.
        :param int y: Initial y position within the parent."""
        ...
    hidden: bool
    """True when the Group and all of its layers are not visible. When False, the Group's layers
    are visible if they haven't been hidden."""
    scale: int
    """Scales each pixel within the Group in both directions. For example, when scale=2 each pixel
    will be represented by 2x2 pixels."""
    x: int
    """X position of the Group in the parent."""
    y: int
    """Y position of the Group in the parent."""
    def append(
        self,
        layer: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> None:
        """Append a layer to the group. It will be drawn above other layers."""
        ...

    def insert(
        self,
        index: int,
        layer: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> None:
        """Insert a layer into the group."""
        ...

    def index(
        self,
        layer: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> int:
        """Returns the index of the first copy of layer. Raises ValueError if not found."""
        ...

    def pop(
        self, i: int = -1
    ) -> Union[vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid]:
        """Remove the ith item and return it."""
        ...

    def remove(
        self,
        layer: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> None:
        """Remove the first copy of layer. Raises ValueError if it is not present."""
        ...

    def __bool__(self) -> bool: ...
    def __contains__(
        self,
        item: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> bool: ...
    def __iter__(
        self,
    ) -> Iterator[
        Union[vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid]
    ]: ...
    def __len__(self) -> int:
        """Returns the number of layers in a Group"""
        ...

    def __getitem__(
        self, index: int
    ) -> Union[vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid]:
        """Returns the value at the given index.

        This allows you to::

          print(group[0])"""
        ...

    def __setitem__(
        self,
        index: int,
        value: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> None:
        """Sets the value at the given index.

        This allows you to::

          group[0] = sprite"""
        ...

    def __delitem__(self, index: int) -> None:
        """Deletes the value at the given index.

        This allows you to::

          del group[0]"""
        ...

    def sort(self, key: function, reverse: bool) -> None:
        """Sort the members of the group."""
        ...

class OnDiskBitmap:
    """Loads values straight from disk. This minimizes memory use but can lead to
    much slower pixel load times. These load times may result in frame tearing where only part of
    the image is visible.

    It's easiest to use on a board with a built in display such as the `Hallowing M0 Express
    <https://www.adafruit.com/product/3900>`_.

    .. code-block:: Python

      import board
      import displayio
      import time
      import pulseio

      board.DISPLAY.brightness = 0
      splash = displayio.Group()
      board.DISPLAY.root_group = splash

      odb = displayio.OnDiskBitmap('/sample.bmp')
      face = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader)
      splash.append(face)
      # Wait for the image to load.
      board.DISPLAY.refresh(target_frames_per_second=60)

      # Fade up the backlight
      for i in range(100):
          board.DISPLAY.brightness = 0.01 * i
          time.sleep(0.05)

      # Wait forever
      while True:
          pass"""

    def __init__(self, file: Union[str, typing.BinaryIO]) -> None:
        """Create an OnDiskBitmap object with the given file.

        :param file file: The name of the bitmap file.  For backwards compatibility, a file opened in binary mode may also be passed.

        Older versions of CircuitPython required a file opened in binary
        mode. CircuitPython 7.0 modified OnDiskBitmap so that it takes a
        filename instead, and opens the file internally.  A future version
        of CircuitPython will remove the ability to pass in an opened file.
        """
        ...
    width: int
    """Width of the bitmap. (read only)"""
    height: int
    """Height of the bitmap. (read only)"""
    pixel_shader: Union[ColorConverter, Palette]
    """The image's pixel_shader.  The type depends on the underlying
    bitmap's structure.  The pixel shader can be modified (e.g., to set the
    transparent pixel or, for palette shaded images, to update the palette.)"""

class Palette:
    """Map a pixel palette_index to a full color. Colors are transformed to the display's format internally to
    save memory."""

    def __init__(self, color_count: int, *, dither: bool = False) -> None:
        """Create a Palette object to store a set number of colors.

        :param int color_count: The number of colors in the Palette
        :param bool dither: When true, dither the RGB color before converting to the display's color space
        """
        ...
    dither: bool
    """When `True` the Palette dithers the output color by adding random
    noise when truncating to display bitdepth"""
    def __bool__(self) -> bool: ...
    def __len__(self) -> int:
        """Returns the number of colors in a Palette"""
        ...

    def __getitem__(self, index: int) -> Optional[int]:
        r"""Return the pixel color at the given index as an integer."""
        ...

    def __setitem__(
        self, index: int, value: Union[int, ReadableBuffer, Tuple[int, int, int]]
    ) -> None:
        r"""Sets the pixel color at the given index. The index should be an integer in the range 0 to color_count-1.

        The value argument represents a color, and can be from 0x000000 to 0xFFFFFF (to represent an RGB value).
        Value can be an int, bytes (3 bytes (RGB) or 4 bytes (RGB + pad byte)), bytearray,
        or a tuple or list of 3 integers.

        This allows you to::

          palette[0] = 0xFFFFFF                     # set using an integer
          palette[1] = b'\xff\xff\x00'              # set using 3 bytes
          palette[2] = b'\xff\xff\x00\x00'          # set using 4 bytes
          palette[3] = bytearray(b'\x00\x00\xFF')   # set using a bytearay of 3 or 4 bytes
          palette[4] = (10, 20, 30)                 # set using a tuple of 3 integers"""
        ...

    def make_transparent(self, palette_index: int) -> None: ...
    def make_opaque(self, palette_index: int) -> None: ...
    def is_transparent(self, palette_index: int) -> bool:
        """Returns `True` if the palette index is transparent.  Returns `False` if opaque."""
        ...

class TileGrid:
    """A grid of tiles sourced out of one bitmap

    Position a grid of tiles sourced from a bitmap and pixel_shader combination. Multiple grids
    can share bitmaps and pixel shaders.

    A single tile grid is also known as a Sprite."""

    def __init__(
        self,
        bitmap: Union[Bitmap, OnDiskBitmap],
        *,
        pixel_shader: Union[ColorConverter, Palette],
        width: int = 1,
        height: int = 1,
        tile_width: Optional[int] = None,
        tile_height: Optional[int] = None,
        default_tile: int = 0,
        x: int = 0,
        y: int = 0,
    ) -> None:
        """Create a TileGrid object. The bitmap is source for 2d pixels. The pixel_shader is used to
        convert the value and its location to a display native pixel color. This may be a simple color
        palette lookup, a gradient, a pattern or a color transformer.

        To save RAM usage, tile values are only allowed in the range from 0 to 255 inclusive (single byte values).

        tile_width and tile_height match the height of the bitmap by default.

        :param Bitmap,OnDiskBitmap bitmap: The bitmap storing one or more tiles.
        :param ColorConverter,Palette pixel_shader: The pixel shader that produces colors from values
        :param int width: Width of the grid in tiles.
        :param int height: Height of the grid in tiles.
        :param int tile_width: Width of a single tile in pixels. Defaults to the full Bitmap and must evenly divide into the Bitmap's dimensions.
        :param int tile_height: Height of a single tile in pixels. Defaults to the full Bitmap and must evenly divide into the Bitmap's dimensions.
        :param int default_tile: Default tile index to show.
        :param int x: Initial x position of the left edge within the parent.
        :param int y: Initial y position of the top edge within the parent."""
    hidden: bool
    """True when the TileGrid is hidden. This may be False even when a part of a hidden Group."""
    x: int
    """X position of the left edge in the parent."""
    y: int
    """Y position of the top edge in the parent."""
    width: int
    """Width of the tilegrid in tiles."""
    height: int
    """Height of the tilegrid in tiles."""
    tile_width: int
    """Width of a single tile in pixels."""
    tile_height: int
    """Height of a single tile in pixels."""
    flip_x: bool
    """If true, the left edge rendered will be the right edge of the right-most tile."""
    flip_y: bool
    """If true, the top edge rendered will be the bottom edge of the bottom-most tile."""
    transpose_xy: bool
    """If true, the TileGrid's axis will be swapped. When combined with mirroring, any 90 degree
    rotation can be achieved along with the corresponding mirrored version."""
    def contains(self, touch_tuple: tuple) -> bool:
        """Returns True if the first two values in ``touch_tuple`` represent an x,y coordinate
        inside the tilegrid rectangle bounds."""
    pixel_shader: Union[ColorConverter, Palette]
    """The pixel shader of the tilegrid."""
    bitmap: Union[Bitmap, OnDiskBitmap]
    """The bitmap of the tilegrid."""
    def __getitem__(self, index: Union[Tuple[int, int], int]) -> int:
        """Returns the tile index at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          print(grid[0])"""
        ...

    def __setitem__(self, index: Union[Tuple[int, int], int], value: int) -> None:
        """Sets the tile index at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          grid[0] = 10

        or::

          grid[0,0] = 10"""
        ...
