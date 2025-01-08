"""Collection of bitmap manipulation tools

.. note:: If you're looking for information about displaying bitmaps on
    screens in CircuitPython, see `this Learn guide
    <https://learn.adafruit.com/circuitpython-display-support-using-displayio>`_
    for information about using the :py:mod:`displayio` module.
"""

from __future__ import annotations

import typing
from typing import Optional, Tuple, Union

import displayio
from circuitpython_typing import ReadableBuffer

def rotozoom(
    dest_bitmap: displayio.Bitmap,
    source_bitmap: displayio.Bitmap,
    *,
    ox: int,
    oy: int,
    dest_clip0: Tuple[int, int],
    dest_clip1: Tuple[int, int],
    px: int,
    py: int,
    source_clip0: Tuple[int, int],
    source_clip1: Tuple[int, int],
    angle: float,
    scale: float,
    skip_index: int,
) -> None:
    """Inserts the source bitmap region into the destination bitmap with rotation
    (angle), scale and clipping (both on source and destination bitmaps).

    :param bitmap dest_bitmap: Destination bitmap that will be copied into
    :param bitmap source_bitmap: Source bitmap that contains the graphical region to be copied
    :param int ox: Horizontal pixel location in destination bitmap where source bitmap
           point (px,py) is placed. Defaults to None which causes it to use the horizontal
           midway point of the destination bitmap.
    :param int oy: Vertical pixel location in destination bitmap where source bitmap
           point (px,py) is placed. Defaults to None which causes it to use the vertical
           midway point of the destination bitmap.
    :param Tuple[int,int] dest_clip0: First corner of rectangular destination clipping
           region that constrains region of writing into destination bitmap
    :param Tuple[int,int] dest_clip1: Second corner of rectangular destination clipping
           region that constrains region of writing into destination bitmap
    :param int px: Horizontal pixel location in source bitmap that is placed into the
           destination bitmap at (ox,oy). Defaults to None which causes it to use the
           horizontal midway point in the source bitmap.
    :param int py: Vertical pixel location in source bitmap that is placed into the
           destination bitmap at (ox,oy). Defaults to None which causes it to use the
           vertical midway point in the source bitmap.
    :param Tuple[int,int] source_clip0: First corner of rectangular source clipping
           region that constrains region of reading from the source bitmap
    :param Tuple[int,int] source_clip1: Second corner of rectangular source clipping
           region that constrains region of reading from the source bitmap
    :param float angle: Angle of rotation, in radians (positive is clockwise direction).
           Defaults to None which gets treated as 0.0 radians or no rotation.
    :param float scale: Scaling factor. Defaults to None which gets treated as 1.0 or same
           as original source size.
    :param int skip_index: Bitmap palette index in the source that will not be copied,
           set to None to copy all pixels"""
    ...

class BlendMode:
    """The blend mode for `alphablend` to operate use"""

    Normal: BlendMode
    """Blend with equal parts of the two source bitmaps"""

    Screen: BlendMode
    """Blend based on the value in each color channel. The result keeps the lighter colors and discards darker colors."""

def alphablend(
    dest_bitmap: displayio.Bitmap,
    source_bitmap_1: displayio.Bitmap,
    source_bitmap_2: displayio.Bitmap,
    colorspace: displayio.Colorspace,
    factor1: float = 0.5,
    factor2: Optional[float] = None,
    blendmode: Optional[BlendMode] = BlendMode.Normal,
    skip_source1_index: Union[int, None] = None,
    skip_source2_index: Union[int, None] = None,
) -> None:
    """Alpha blend the two source bitmaps into the destination.

    It is permitted for the destination bitmap to be one of the two
    source bitmaps.

    :param bitmap dest_bitmap: Destination bitmap that will be written into
    :param bitmap source_bitmap_1: The first source bitmap
    :param bitmap source_bitmap_2: The second source bitmap
    :param float factor1: The proportion of bitmap 1 to mix in
    :param float factor2: The proportion of bitmap 2 to mix in.  If specified as `None`, ``1-factor1`` is used.  Usually the proportions should sum to 1.
    :param displayio.Colorspace colorspace: The colorspace of the bitmaps. They must all have the same colorspace.  Only the following colorspaces are permitted:  ``L8``, ``RGB565``, ``RGB565_SWAPPED``, ``BGR565`` and ``BGR565_SWAPPED``.
    :param bitmaptools.BlendMode blendmode: The blend mode to use. Default is Normal.
    :param int skip_source1_index: Bitmap palette or luminance index in source_bitmap_1 that will not be blended, set to None to blend all pixels
    :param int skip_source2_index: Bitmap palette or luminance index in source_bitmap_2 that will not be blended, set to None to blend all pixels

    For the L8 colorspace, the bitmaps must have a bits-per-value of 8.
    For the RGB colorspaces, they must have a bits-per-value of 16."""

def fill_region(
    dest_bitmap: displayio.Bitmap, x1: int, y1: int, x2: int, y2: int, value: int
) -> None:
    """Draws the color value into the destination bitmap within the
    rectangular region bounded by (x1,y1) and (x2,y2), exclusive.

    :param bitmap dest_bitmap: Destination bitmap that will be written into
    :param int x1: x-pixel position of the first corner of the rectangular fill region
    :param int y1: y-pixel position of the first corner of the rectangular fill region
    :param int x2: x-pixel position of the second corner of the rectangular fill region (exclusive)
    :param int y2: y-pixel position of the second corner of the rectangular fill region (exclusive)
    :param int value: Bitmap palette index that will be written into the rectangular
           fill region in the destination bitmap"""
    ...

def boundary_fill(
    dest_bitmap: displayio.Bitmap,
    x: int,
    y: int,
    fill_color_value: int,
    replaced_color_value: int,
) -> None:
    """Draws the color value into the destination bitmap enclosed
    area of pixels of the background_value color. Like "Paint Bucket"
    fill tool.

    :param bitmap dest_bitmap: Destination bitmap that will be written into
    :param int x: x-pixel position of the first pixel to check and fill if needed
    :param int y: y-pixel position of the first pixel to check and fill if needed
    :param int fill_color_value: Bitmap palette index that will be written into the
           enclosed area in the destination bitmap
    :param int replaced_color_value: Bitmap palette index that will filled with the
           value color in the enclosed area in the destination bitmap"""
    ...

def draw_line(
    dest_bitmap: displayio.Bitmap, x1: int, y1: int, x2: int, y2: int, value: int
) -> None:
    """Draws a line into a bitmap specified two endpoints (x1,y1) and (x2,y2).

    :param bitmap dest_bitmap: Destination bitmap that will be written into
    :param int x1: x-pixel position of the line's first endpoint
    :param int y1: y-pixel position of the line's first endpoint
    :param int x2: x-pixel position of the line's second endpoint
    :param int y2: y-pixel position of the line's second endpoint
    :param int value: Bitmap palette index that will be written into the
           line in the destination bitmap"""
    ...

def draw_polygon(
    dest_bitmap: displayio.Bitmap,
    xs: ReadableBuffer,
    ys: ReadableBuffer,
    value: int,
    close: Optional[bool] = True,
) -> None:
    """Draw a polygon connecting points on provided bitmap with provided value

    :param bitmap dest_bitmap: Destination bitmap that will be written into
    :param ReadableBuffer xs: x-pixel position of the polygon's vertices
    :param ReadableBuffer ys: y-pixel position of the polygon's vertices
    :param int value: Bitmap palette index that will be written into the
           line in the destination bitmap
    :param bool close: (Optional) Whether to connect first and last point. (True)

    .. code-block:: Python

       import board
       import displayio
       import bitmaptools

       display = board.DISPLAY
       main_group = displayio.Group()
       display.root_group = main_group

       palette = displayio.Palette(3)
       palette[0] = 0xffffff
       palette[1] = 0x0000ff
       palette[2] = 0xff0000

       bmp = displayio.Bitmap(128,128, 3)
       bmp.fill(0)

       xs = bytes([4, 101, 101, 19])
       ys = bytes([4, 19,  121, 101])
       bitmaptools.draw_polygon(bmp, xs, ys, 1)

       xs = bytes([14, 60, 110])
       ys = bytes([14, 24,  90])
       bitmaptools.draw_polygon(bmp, xs, ys, 2)

       tilegrid = displayio.TileGrid(bitmap=bmp, pixel_shader=palette)
       main_group.append(tilegrid)

       while True:
           pass
    """
    ...

def arrayblit(
    bitmap: displayio.Bitmap,
    data: ReadableBuffer,
    x1: int = 0,
    y1: int = 0,
    x2: Optional[int] = None,
    y2: Optional[int] = None,
    skip_index: Optional[int] = None,
) -> None:
    """Inserts pixels from ``data`` into the rectangle of width×height pixels with the upper left corner at ``(x,y)``

    The values from ``data`` are taken modulo the number of color values
    available in the destination bitmap.

    If x1 or y1 are not specified, they are taken as 0.  If x2 or y2
    are not specified, or are given as -1, they are taken as the width
    and height of the image.

    The coordinates affected by the blit are ``x1 <= x < x2`` and ``y1 <= y < y2``.

    ``data`` must contain at least as many elements as required.  If it
    contains excess elements, they are ignored.

    The blit takes place by rows, so the first elements of ``data`` go
    to the first row, the next elements to the next row, and so on.

    :param displayio.Bitmap bitmap: A writable bitmap
    :param ReadableBuffer data: Buffer containing the source pixel values
    :param int x1: The left corner of the area to blit into (inclusive)
    :param int y1: The top corner of the area to blit into (inclusive)
    :param int x2: The right of the area to blit into (exclusive)
    :param int y2: The bottom corner of the area to blit into (exclusive)
    :param int skip_index: Bitmap palette index in the source that will not be copied,
            set to None to copy all pixels
    """
    ...

def readinto(
    bitmap: displayio.Bitmap,
    file: typing.BinaryIO,
    bits_per_pixel: int,
    element_size: int = 1,
    reverse_pixels_in_element: bool = False,
    swap_bytes_in_element: bool = False,
    reverse_rows: bool = False,
) -> None:
    """Reads from a binary file into a bitmap.

    The file must be positioned so that it consists of ``bitmap.height`` rows of pixel data, where each row is the smallest multiple of ``element_size`` bytes that can hold ``bitmap.width`` pixels.

    The bytes in an element can be optionally swapped, and the pixels in an element can be reversed.  Also, the
    row loading direction can be reversed, which may be requires for loading certain bitmap files.

    This function doesn't parse image headers, but is useful to speed up loading of uncompressed image formats such as PCF glyph data.

    :param displayio.Bitmap bitmap: A writable bitmap
    :param typing.BinaryIO file: A file opened in binary mode
    :param int bits_per_pixel: Number of bits per pixel.  Values 1, 2, 4, 8, 16, 24, and 32 are supported;
    :param int element_size: Number of bytes per element.  Values of 1, 2, and 4 are supported, except that 24 ``bits_per_pixel`` requires 1 byte per element.
    :param bool reverse_pixels_in_element: If set, the first pixel in a word is taken from the Most Significant Bits; otherwise, it is taken from the Least Significant Bits.
    :param bool swap_bytes_in_element: If the ``element_size`` is not 1, then reverse the byte order of each element read.
    :param bool reverse_rows: Reverse the direction of the row loading (required for some bitmap images).
    """
    ...

class DitherAlgorithm:
    """Identifies the algorithm for dither to use"""

    Atkinson: "DitherAlgorithm"
    """The classic Atkinson dither, often associated with the Hypercard esthetic"""

    FloydStenberg: "DitherAlgorithm"
    """The Floyd-Stenberg dither"""

def dither(
    dest_bitmap: displayio.Bitmap,
    source_bitmapp: displayio.Bitmap,
    source_colorspace: displayio.Colorspace,
    algorithm: DitherAlgorithm = DitherAlgorithm.Atkinson,
) -> None:
    """Convert the input image into a 2-level output image using the given dither algorithm.

    :param bitmap dest_bitmap: Destination bitmap.  It must have a value_count of 2 or 65536.  The stored values are 0 and the maximum pixel value.
    :param bitmap source_bitmap: Source bitmap that contains the graphical region to be dithered.  It must have a value_count of 65536.
    :param colorspace: The colorspace of the image.  The supported colorspaces are ``RGB565``, ``BGR565``, ``RGB565_SWAPPED``, and ``BGR565_SWAPPED``
    :param algorithm: The dither algorithm to use, one of the `DitherAlgorithm` values.
    """
    ...

def draw_circle(
    dest_bitmap: displayio.Bitmap, x: int, y: int, radius: int, value: int
) -> None:
    """Draws a circle into a bitmap specified using a center (x0,y0) and radius r.

    :param bitmap dest_bitmap: Destination bitmap that will be written into
    :param int x: x-pixel position of the circle's center
    :param int y: y-pixel position of the circle's center
    :param int radius: circle's radius
    :param int value: Bitmap palette index that will be written into the
           circle in the destination bitmap

    .. code-block:: Python

       import board
       import displayio
       import bitmaptools

       display = board.DISPLAY
       main_group = displayio.Group()
       display.root_group = main_group

       palette = displayio.Palette(2)
       palette[0] = 0xffffff
       palette[1] = 0x440044

       bmp = displayio.Bitmap(128,128, 2)
       bmp.fill(0)

       bitmaptools.circle(64,64, 32, 1)

       tilegrid = displayio.TileGrid(bitmap=bmp, pixel_shader=palette)
       main_group.append(tilegrid)

       while True:
           pass

    """

    ...

def blit(
    dest_bitmap: displayio.Bitmap,
    source_bitmap: displayio.Bitmap,
    x: int,
    y: int,
    *,
    x1: int = 0,
    y1: int = 0,
    x2: int | None = None,
    y2: int | None = None,
    skip_source_index: int | None = None,
    skip_dest_index: int | None = None,
) -> None:
    """Inserts the source_bitmap region defined by rectangular boundaries
    (x1,y1) and (x2,y2) into the bitmap at the specified (x,y) location.

    :param bitmap dest_bitmap: Destination bitmap that the area will be copied into.
    :param bitmap source_bitmap: Source bitmap that contains the graphical region to be copied
    :param int x: Horizontal pixel location in bitmap where source_bitmap upper-left
                  corner will be placed
    :param int y: Vertical pixel location in bitmap where source_bitmap upper-left
                  corner will be placed
    :param int x1: Minimum x-value for rectangular bounding box to be copied from the source bitmap
    :param int y1: Minimum y-value for rectangular bounding box to be copied from the source bitmap
    :param int x2: Maximum x-value (exclusive) for rectangular bounding box to be copied from the source bitmap. If unspecified or `None`, the source bitmap width is used.
    :param int y2: Maximum y-value (exclusive) for rectangular bounding box to be copied from the source bitmap. If unspecified or `None`, the source bitmap height is used.
    :param int skip_source_index: bitmap palette index in the source that will not be copied,
                           set to None to copy all pixels
    :param int skip_dest_index: bitmap palette index in the destination bitmap that will not get overwritten
                            by the pixels from the source"""
    ...
