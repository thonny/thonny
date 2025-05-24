"""Core font related data structures

.. note:: This module is intended only for low-level usage.  For working with
    fonts in CircuitPython see the `adafruit_bitmap_font library
    <https://github.com/adafruit/Adafruit_CircuitPython_Bitmap_Font>`_.
    For information on creating custom fonts for use in CircuitPython, see
    `this Learn guide <https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display>`_

"""

from __future__ import annotations

from typing import Optional, Tuple, Union

import displayio
from typing_extensions import Protocol  # for compat with python < 3.8

class FontProtocol(Protocol):
    """A protocol shared by `BuiltinFont` and classes in ``adafruit_bitmap_font``"""

    def get_bounding_box(self) -> Union[Tuple[int, int], Tuple[int, int, int, int]]:
        """Retrieve the maximum bounding box of any glyph in the font.

        The four element version is ``(width, height, x_offset, y_offset)``.
        The two element version is ``(width, height)``, in which
        ``x_offset`` and ``y_offset`` are assumed to be zero."""
        pass

    def get_glyph(self, codepoint: int) -> Optional[Glyph]:
        """Retrieve the Glyph for a given code point

        If the code point is not present in the font, `None` is returned."""
        pass

class BuiltinFont:
    """A font built into CircuitPython"""

    def __init__(self) -> None:
        """Creation not supported. Available fonts are defined when CircuitPython is built. See the
        `Adafruit_CircuitPython_Bitmap_Font <https://github.com/adafruit/Adafruit_CircuitPython_Bitmap_Font>`_
        library for dynamically loaded fonts."""
        ...
    bitmap: displayio.Bitmap
    """Bitmap containing all font glyphs starting with ASCII and followed by unicode. Use
    `get_glyph` in most cases. This is useful for use with `displayio.TileGrid` and
    `terminalio.Terminal`."""

    def get_bounding_box(self) -> Tuple[int, int]:
        """Returns the maximum bounds of all glyphs in the font in a tuple of two values: width, height."""
        ...

    def get_glyph(self, codepoint: int) -> Glyph:
        """Returns a `fontio.Glyph` for the given codepoint or None if no glyph is available."""
        ...

class Glyph:
    """Storage of glyph info"""

    def __init__(
        self,
        bitmap: displayio.Bitmap,
        tile_index: int,
        width: int,
        height: int,
        dx: int,
        dy: int,
        shift_x: int,
        shift_y: int,
    ) -> None:
        """Named tuple used to capture a single glyph and its attributes.

        :param bitmap: the bitmap including the glyph
        :param tile_index: the tile index within the bitmap
        :param width: the width of the glyph's bitmap
        :param height: the height of the glyph's bitmap
        :param dx: x adjustment to the bitmap's position
        :param dy: y adjustment to the bitmap's position
        :param shift_x: the x difference to the next glyph
        :param shift_y: the y difference to the next glyph"""
        ...
