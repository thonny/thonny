"""`qrio` module.

Provides the `QRDecoder` object."""

from __future__ import annotations

from typing import List, Union

from circuitpython_typing import ReadableBuffer

class PixelPolicy:
    EVERY_BYTE: PixelPolicy
    """The input buffer to `QRDecoder.decode` consists of greyscale values in every byte"""

    EVEN_BYTES: PixelPolicy
    """The input buffer to `QRDecoder.decode` consists of greyscale values in positions 0, 2, …, and ignored bytes in positions 1, 3, ….  This can decode directly from YUV images where the even bytes hold the Y (luminance) data."""

    ODD_BYTES: PixelPolicy
    """The input buffer to `QRDecoder.decode` consists of greyscale values in positions 1, 3, …, and ignored bytes in positions 0, 2, ….  This can decode directly from YUV images where the odd bytes hold the Y (luminance) data"""

class QRDecoder:
    def __init__(self, width: int, height: int) -> None:
        """Construct a QRDecoder object

        :param int width: The pixel width of the image to decode
        :param int height: The pixel height of the image to decode
        """
        ...
    def decode(
        self, buffer: ReadableBuffer, pixel_policy: PixelPolicy = PixelPolicy.EVERY_BYTE
    ) -> List[QRInfo]:
        """Decode zero or more QR codes from the given image.  The size of the buffer must be at least ``length``×``width`` bytes for `EVERY_BYTE`, and 2×``length``×``width`` bytes for `EVEN_BYTES` or `ODD_BYTES`."""
    width: int
    """The width of image the decoder expects"""

    height: int
    """The height of image the decoder expects"""

class QRInfo:
    """Information about a decoded QR code"""

    payload: bytes
    """The content of the QR code"""

    data_type: Union[str, int]
    """The encoding of the payload as a string (if a standard encoding) or int (if not standard)"""
