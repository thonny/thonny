"""Core font related data structures"""

class BuiltinFont:
    """A font built into CircuitPython"""

    def __init__(self, ):
        """Creation not supported. Available fonts are defined when CircuitPython is built. See the
        `Adafruit_CircuitPython_Bitmap_Font <https://github.com/adafruit/Adafruit_CircuitPython_Bitmap_Font>`_
        library for dynamically loaded fonts."""
        ...

    bitmap: Any = ...
    """Bitmap containing all font glyphs starting with ASCII and followed by unicode. Use
    `get_glyph` in most cases. This is useful for use with `displayio.TileGrid` and
    `terminalio.Terminal`."""

    def get_bounding_box(self, ) -> Any:
        """Returns the maximum bounds of all glyphs in the font in a tuple of two values: width, height."""
        ...

    def get_glyph(self, codepoint: Any) -> Any:
        """Returns a `fontio.Glyph` for the given codepoint or None if no glyph is available."""
        ...

class Glyph:
    """Storage of glyph info"""

    def __init__(self,
                 bitmap: displayio.Bitmap,
                 tile_index: int,
                 width: int,
                 height: int,
                 dx: int,
                 dy: int,
                 shift_x: int,
                 shift_y: int):
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

