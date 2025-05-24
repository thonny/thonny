"""LED matrix driver"""

from __future__ import annotations

from typing import List

import digitalio
from circuitpython_typing import ReadableBuffer

class PewPew:
    """This is an internal module to be used by the ``pew.py`` library from
    https://github.com/pewpew-game/pew-pewpew-standalone-10.x to handle the
    LED matrix display and buttons on the ``pewpew10`` board.

    Usage::

        This singleton class is instantiated by the ``pew`` library, and
        used internally by it. All user-visible interactions are done through
        that library."""

    def __init__(
        self,
        buffer: ReadableBuffer,
        rows: List[digitalio.DigitalInOut],
        cols: List[digitalio.DigitalInOut],
        buttons: digitalio.DigitalInOut,
    ) -> None:
        """Initializes matrix scanning routines.

        The ``buffer`` is a 64 byte long ``bytearray`` that stores what should
        be displayed on the matrix. ``rows`` and ``cols`` are both lists of
        eight ``DigitalInputOutput`` objects that are connected to the matrix
        rows and columns. ``buttons`` is a ``DigitalInputOutput`` object that
        is connected to the common side of all buttons (the other sides of the
        buttons are connected to rows of the matrix)."""
        ...
