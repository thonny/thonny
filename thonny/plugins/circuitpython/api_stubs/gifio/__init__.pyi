"""Access GIF-format images
"""

from __future__ import annotations

import typing
from typing import Union

import displayio
from circuitpython_typing import ReadableBuffer

class GifWriter:
    def __init__(
        self,
        file: Union[typing.BinaryIO, str],
        width: int,
        height: int,
        colorspace: displayio.Colorspace,
        loop: bool = True,
        dither: bool = False,
    ) -> None:
        """Construct a GifWriter object

        :param file: Either a file open in bytes mode, or the name of a file to open in bytes mode.
        :param width: The width of the image.  All frames must have the same width.
        :param height: The height of the image.  All frames must have the same height.
        :param colorspace: The colorspace of the image.  All frames must have the same colorspace.  The supported colorspaces are ``RGB565``, ``BGR565``, ``RGB565_SWAPPED``, ``BGR565_SWAPPED``, and ``L8`` (greyscale)
        :param loop: If True, the GIF is marked for looping playback
        :param dither: If True, and the image is in color, a simple ordered dither is applied.
        """
        ...
    def __enter__(self) -> GifWriter:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    def deinit(self) -> None:
        """Close the underlying file."""
        ...
    def add_frame(self, bitmap: ReadableBuffer, delay: float = 0.1) -> None:
        """Add a frame to the GIF.

        :param bitmap: The frame data
        :param delay: The frame delay in seconds.  The GIF format rounds this to the nearest 1/100 second, and the largest permitted value is 655 seconds.
        """
        ...
