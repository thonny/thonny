"""Displays text in a TileGrid

The `terminalio` module contains classes to display a character stream on a display. The built
in font is available as ``terminalio.FONT``.

.. note:: This module does not give access to the
    `REPL <https://learn.adafruit.com/welcome-to-circuitpython/interacting-with-the-serial-console>`_.

"""

from __future__ import annotations

from typing import Optional

import displayio
import fontio
from circuitpython_typing import ReadableBuffer

FONT: fontio.BuiltinFont
"""The built in font"""

class Terminal:
    """Display a character stream with a TileGrid

    ASCII control:
    * ``\\r`` - Move cursor to column 1
    * ``\\n`` - Move cursor down a row
    * ``\\b`` - Move cursor left one if possible

    OSC control sequences:
    * ``ESC ] 0; <s> ESC \\`` - Set title bar to <s>
    * ``ESC ] ####; <s> ESC \\`` - Ignored

    VT100 control sequences:
    * ``ESC [ K`` - Clear the remainder of the line
    * ``ESC [ 0 K`` - Clear the remainder of the line
    * ``ESC [ 1 K`` - Clear start of the line to cursor
    * ``ESC [ 2 K`` - Clear the entire line
    * ``ESC [ #### D`` - Move the cursor to the left by ####
    * ``ESC [ 2 J`` - Erase the entire display
    * ``ESC [ nnnn ; mmmm H`` - Move the cursor to mmmm, nnnn.
    * ``ESC [ H`` - Move the cursor to 0,0.
    * ``ESC M`` - Move the cursor up one line, scrolling if necessary.
    * ``ESC D`` - Move the cursor down one line, scrolling if necessary.
    * ``ESC [ r`` - Disable scrolling range (set to fullscreen).
    * ``ESC [ nnnn ; mmmm r`` - Set scrolling range between rows nnnn and mmmm.
    * ``ESC [ ## m`` - Set the terminal display attributes.
    * ``ESC [ ## ; ## m`` - Set the terminal display attributes.
    * ``ESC [ ## ; ## ; ## m`` - Set the terminal display attributes.

    Supported Display attributes:
    0 - Reset all attributes
    Foreground Colors    Background Colors
    30 - Black           40 - Black
    31 - Red             41 - Red
    32 - Green           42 - Green
    33 - Yellow          43 - Yellow
    34 - Blue            44 - Blue
    35 - Magenta         45 - Magenta
    36 - Cyan            46 - Cyan
    37 - White           47 - White
    """

    def __init__(
        self,
        scroll_area: displayio.TileGrid,
        font: fontio.BuiltinFont,
        *,
        status_bar: Optional[displayio.TileGrid] = None,
    ) -> None:
        """Terminal manages tile indices and cursor position based on VT100 commands. The font should be
        a `fontio.BuiltinFont` and the TileGrid's bitmap should match the font's bitmap.
        """
        ...

    def write(self, buf: ReadableBuffer) -> Optional[int]:
        """Write the buffer of bytes to the bus.

        :return: the number of bytes written
        :rtype: int or None"""
        ...
