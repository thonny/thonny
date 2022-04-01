"""Displays text in a TileGrid

The `terminalio` module contains classes to display a character stream on a display. The built
in font is available as ``terminalio.FONT``."""

from __future__ import annotations

from typing import Optional

import displayio
import fontio
from circuitpython_typing import ReadableBuffer

FONT: fontio.BuiltinFont
"""The built in font"""

class Terminal:
    """Display a character stream with a TileGrid"""

    def __init__(self, tilegrid: displayio.TileGrid, font: fontio.BuiltinFont) -> None:
        """Terminal manages tile indices and cursor position based on VT100 commands. The font should be
        a `fontio.BuiltinFont` and the TileGrid's bitmap should match the font's bitmap."""
        ...
    def write(self, buf: ReadableBuffer) -> Optional[int]:
        """Write the buffer of bytes to the bus.

        :return: the number of bytes written
        :rtype: int or None"""
        ...
