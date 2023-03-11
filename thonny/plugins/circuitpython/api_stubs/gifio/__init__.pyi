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

class OnDiskGif:
    """Loads one frame of a GIF into memory at a time.

    .. code-block:: Python

      import board
      import gifio
      import displayio
      import time

      display = board.DISPLAY
      splash = displayio.Group()
      display.root_group = splash

      odg = gifio.OnDiskGif('/sample.gif')

      start = time.monotonic()
      odg.next_frame() # Load the first frame
      end = time.monotonic()
      overhead = end - start

      face = displayio.TileGrid(
          odg.bitmap,
          pixel_shader=displayio.ColorConverter(
              input_colorspace=displayio.Colorspace.RGB565_SWAPPED
          ),
      )
      splash.append(face)
      board.DISPLAY.refresh()

      # Display repeatedly.
      while True:
          # Sleep for the frame delay specified by the GIF,
          # minus the overhead measured to advance between frames.
          time.sleep(max(0, next_delay - overhead))
          next_delay = odg.next_frame()
    """

    def __init__(self, file: str) -> None:
        """Create an `OnDiskGif` object with the given file.
        The GIF frames are decoded into RGB565 big-endian format.
        `displayio` expects little-endian, so the example above uses `Colorspace.RGB565_SWAPPED`.

        :param file file: The name of the GIF file.
        """
        ...
    width: int
    """Width of the gif. (read only)"""
    height: int
    """Height of the gif. (read only)"""
    bitmap: displayio.Bitmap
    """The bitmap used to hold the current frame."""
    def next_frame(self) -> float:
        """Loads the next frame. Returns expected delay before the next frame in seconds."""
    duration: float
    """Returns the total duration of the GIF in seconds. (read only)"""
    frame_count: int
    """Returns the number of frames in the GIF. (read only)"""
    min_delay: float
    """The minimum delay found between frames. (read only)"""
    max_delay: float
    """The maximum delay found between frames. (read only)"""
