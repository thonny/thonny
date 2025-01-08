"""C-level helpers for animation of sprites on a stage

The `_stage` module contains native code to speed-up the ```stage`` Library
<https://github.com/python-ugame/circuitpython-stage>`_."""

from __future__ import annotations

from typing import List

import busdisplay
from circuitpython_typing import ReadableBuffer, WriteableBuffer

def render(
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    layers: List[Layer],
    buffer: WriteableBuffer,
    display: busdisplay.BusDisplay,
    scale: int,
    background: int,
) -> None:
    """Render and send to the display a fragment of the screen.

    :param int x0: Left edge of the fragment.
    :param int y0: Top edge of the fragment.
    :param int x1: Right edge of the fragment.
    :param int y1: Bottom edge of the fragment.
    :param layers: A list of the :py:class:`~_stage.Layer` objects.
    :type layers: list[Layer]
    :param ~circuitpython_typing.WriteableBuffer buffer: A buffer to use for rendering.
    :param ~busdisplay.BusDisplay display: The display to use.
    :param int scale: How many times should the image be scaled up.
    :param int background: What color to display when nothing is there.

    There are also no sanity checks, outside of the basic overflow
    checking. The caller is responsible for making the passed parameters
    valid.

    This function is intended for internal use in the ``stage`` library
    and all the necessary checks are performed there."""

class Layer:
    """Keep information about a single layer of graphics"""

    def __init__(
        self,
        width: int,
        height: int,
        graphic: ReadableBuffer,
        palette: ReadableBuffer,
        grid: ReadableBuffer,
    ) -> None:
        """Keep internal information about a layer of graphics (either a
        ``Grid`` or a ``Sprite``) in a format suitable for fast rendering
        with the ``render()`` function.

        :param int width: The width of the grid in tiles, or 1 for sprites.
        :param int height: The height of the grid in tiles, or 1 for sprites.
        :param ~circuitpython_typing.ReadableBuffer graphic: The graphic data of the tiles.
        :param ~circuitpython_typing.ReadableBuffer palette: The color palette to be used.
        :param ~circuitpython_typing.ReadableBuffer grid: The contents of the grid map.

        This class is intended for internal use in the ``stage`` library and
        it shouldn't be used on its own."""
        ...

    def move(self, x: int, y: int) -> None:
        """Set the offset of the layer to the specified values."""
        ...

    def frame(self, frame: int, rotation: int) -> None:
        """Set the animation frame of the sprite, and optionally rotation its
        graphic."""
        ...

class Text:
    """Keep information about a single grid of text"""

    def __init__(
        self,
        width: int,
        height: int,
        font: ReadableBuffer,
        palette: ReadableBuffer,
        chars: ReadableBuffer,
    ) -> None:
        """Keep internal information about a grid of text
        in a format suitable for fast rendering
        with the ``render()`` function.

        :param int width: The width of the grid in tiles, or 1 for sprites.
        :param int height: The height of the grid in tiles, or 1 for sprites.
        :param ~circuitpython_typing.ReadableBuffer font: The font data of the characters.
        :param ~circuitpython_typing.ReadableBuffer palette: The color palette to be used.
        :param ~circuitpython_typing.ReadableBuffer chars: The contents of the character grid.

        This class is intended for internal use in the ``stage`` library and
        it shouldn't be used on its own."""
        ...

    def move(self, x: int, y: int) -> None:
        """Set the offset of the text to the specified values."""
        ...
