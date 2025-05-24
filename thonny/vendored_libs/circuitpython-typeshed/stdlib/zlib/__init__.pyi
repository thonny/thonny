"""zlib decompression functionality

The `zlib` module allows limited functionality similar to the CPython zlib library.
This module allows to decompress binary data compressed with DEFLATE algorithm
(commonly used in zlib library and gzip archiver). Compression is not yet implemented.
"""

from __future__ import annotations

from typing import Optional

def decompress(
    data: bytes, wbits: Optional[int] = 0, bufsize: Optional[int] = 0
) -> bytes:
    """Return decompressed *data* as bytes. *wbits* is DEFLATE dictionary window
    size used during compression (8-15, the dictionary size is power of 2 of
    that value). Additionally, if value is positive, *data* is assumed to be
    zlib stream (with zlib header). Otherwise, if it's negative, it's assumed
    to be raw DEFLATE stream.

    The wbits parameter controls the size of the history buffer (or “window size”), and what header
    and trailer format is expected.

    Common wbits values:

    * To decompress deflate format, use wbits = -15
    * To decompress zlib format, use wbits = 15
    * To decompress gzip format, use wbits = 31

    :param bytes data: data to be decompressed
    :param int wbits: DEFLATE dictionary window size used during compression. See above.
    :param int bufsize: ignored for compatibility with CPython only
    """
    ...
