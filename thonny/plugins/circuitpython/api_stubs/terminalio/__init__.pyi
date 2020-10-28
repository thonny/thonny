"""Displays text in a TileGrid

The `terminalio` module contains classes to display a character stream on a display. The built
in font is available as ``terminalio.FONT``."""

class Terminal:
    """Display a character stream with a TileGrid"""

    def __init__(self, tilegrid: Any, font: Any):
        """Terminal manages tile indices and cursor position based on VT100 commands. The font should be
        a `fontio.BuiltinFont` and the TileGrid's bitmap should match the font's bitmap."""
        ...

    def write(self, buf: Any) -> Any:
        """Write the buffer of bytes to the bus.

        :return: the number of bytes written
        :rtype: int or None"""
        ...

