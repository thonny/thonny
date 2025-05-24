"""Support for JPEG image decoding"""

from __future__ import annotations

import io
from typing import Tuple, overload

import displayio
from circuitpython_typing import ReadableBuffer

class JpegDecoder:
    """A JPEG decoder

    A JpegDecoder allocates a few thousand bytes of memory. To reduce memory fragmentation,
    create a single JpegDecoder object and use it anytime a JPEG image needs to be decoded.

    Example::

        from jpegio import JpegDecoder
        from displayio import Bitmap

        decoder = JpegDecoder()
        width, height = decoder.open("/sd/example.jpg")
        bitmap = Bitmap(width, height, 65535)
        decoder.decode(bitmap)
        # .. do something with bitmap
    """

    def __init__(self) -> None:
        """Create a JpegDecoder"""
        ...

    @overload
    def open(self, filename: str) -> Tuple[int, int]: ...
    @overload
    def open(self, buffer: ReadableBuffer) -> Tuple[int, int]: ...
    @overload
    def open(self, bytesio: io.BytesIO) -> Tuple[int, int]:
        """Use the specified object  as the JPEG data source.

        The source may be a filename, a binary buffer in memory, or an opened binary stream.

        The single parameter is positional-only (write ``open(f)``, not
        ``open(filename=f)`` but due to technical limitations this is
        not shown in the function signature in the documentation.

        Returns the image size as the tuple ``(width, height)``."""

    def decode(
        self,
        bitmap: displayio.Bitmap,
        scale: int = 0,
        x: int = 0,
        y: int = 0,
        *,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        skip_source_index: int,
        skip_dest_index: int,
    ) -> None:
        """Decode JPEG data

        The bitmap must be large enough to contain the decoded image.
        The pixel data is stored in the `displayio.Colorspace.RGB565_SWAPPED` colorspace.

        The image is optionally downscaled by a factor of ``2**scale``.
        Scaling by a factor of 8 (scale=3) is particularly efficient in terms of decoding time.

        The remaining parameters are as for `bitmaptools.blit`.
        Because JPEG is a lossy data format, chroma keying based on the "source
        index" is not reliable, because the same original RGB value might end
        up being decompressed as a similar but not equal color value. Using a
        higher JPEG encoding quality can help, but ultimately it will not be
        perfect.

        After a call to ``decode``, you must ``open`` a new JPEG. It is not
        possible to repeatedly ``decode`` the same jpeg data, even if it is to
        select different scales or crop regions from it.

        :param Bitmap bitmap: Optional output buffer
        :param int scale: Scale factor from 0 to 3, inclusive.
        :param int x: Horizontal pixel location in bitmap where source_bitmap upper-left
                      corner will be placed
        :param int y: Vertical pixel location in bitmap where source_bitmap upper-left
                      corner will be placed
        :param int x1: Minimum x-value for rectangular bounding box to be copied from the source bitmap
        :param int y1: Minimum y-value for rectangular bounding box to be copied from the source bitmap
        :param int x2: Maximum x-value (exclusive) for rectangular bounding box to be copied from the source bitmap
        :param int y2: Maximum y-value (exclusive) for rectangular bounding box to be copied from the source bitmap
        :param int skip_source_index: bitmap palette index in the source that will not be copied,
                               set to None to copy all pixels
        :param int skip_dest_index: bitmap palette index in the destination bitmap that will not get overwritten
                                by the pixels from the source
        """
