"""Lightweight 2D shapes for displays

The :py:attr:`vectorio` module provide simple filled drawing primitives for
use with `displayio`.

.. code-block:: python

    group = displayio.Group()

    palette = displayio.Palette(1)
    palette[0] = 0x125690

    circle = vectorio.Circle(pixel_shader=palette, radius=25, x=70, y=40)
    group.append(circle)

    rectangle = vectorio.Rectangle(pixel_shader=palette, width=40, height=30, x=55, y=45)
    group.append(rectangle)

    points=[(5, 5), (100, 20), (20, 20), (20, 100)]
    polygon = vectorio.Polygon(pixel_shader=palette, points=points, x=0, y=0)
    group.append(polygon)

"""

from __future__ import annotations

from typing import List, Tuple, Union

import displayio

class Circle:
    def __init__(
        self,
        pixel_shader: Union[displayio.ColorConverter, displayio.Palette],
        radius: int,
        x: int,
        y: int,
    ) -> None:
        """Circle is positioned on screen by its center point.

        :param Union[~displayio.ColorConverter,~displayio.Palette] pixel_shader: The pixel shader that produces colors from values
        :param int radius: The radius of the circle in pixels
        :param int x: Initial x position of the axis.
        :param int y: Initial y position of the axis.
        :param int color_index: Initial color_index to use when selecting color from the palette.
        """
    radius: int
    """The radius of the circle in pixels."""
    color_index: int
    """The color_index of the circle as 0 based index of the palette."""
    x: int
    """X position of the center point of the circle in the parent."""

    y: int
    """Y position of the center point of the circle in the parent."""

    hidden: bool
    """Hide the circle or not."""

    location: Tuple[int, int]
    """(X,Y) position of the center point of the circle in the parent."""

    pixel_shader: Union[displayio.ColorConverter, displayio.Palette]
    """The pixel shader of the circle."""

class Polygon:
    def __init__(
        self,
        pixel_shader: Union[displayio.ColorConverter, displayio.Palette],
        points: List[Tuple[int, int]],
        x: int,
        y: int,
    ) -> None:
        """Represents a closed shape by ordered vertices. The path will be treated as
        'closed', the last point will connect to the first point.

        :param Union[~displayio.ColorConverter,~displayio.Palette] pixel_shader: The pixel
            shader that produces colors from values
        :param List[Tuple[int,int]] points: Vertices for the polygon
        :param int x: Initial screen x position of the 0,0 origin in the points list.
        :param int y: Initial screen y position of the 0,0 origin in the points list.
        :param int color_index: Initial color_index to use when selecting color from the palette.
        """
    points: List[Tuple[int, int]]
    """Vertices for the polygon."""
    color_index: int
    """The color_index of the polygon as 0 based index of the palette."""
    x: int
    """X position of the 0,0 origin in the points list."""

    y: int
    """Y position of the 0,0 origin in the points list."""

    hidden: bool
    """Hide the polygon or not."""

    location: Tuple[int, int]
    """(X,Y) position of the 0,0 origin in the points list."""

    pixel_shader: Union[displayio.ColorConverter, displayio.Palette]
    """The pixel shader of the polygon."""

class Rectangle:
    def __init__(
        self,
        pixel_shader: Union[displayio.ColorConverter, displayio.Palette],
        width: int,
        height: int,
        x: int,
        y: int,
    ) -> None:
        """Represents a rectangle by defining its bounds

        :param Union[~displayio.ColorConverter,~displayio.Palette] pixel_shader: The pixel shader that produces colors from values
        :param int width: The number of pixels wide
        :param int height: The number of pixels high
        :param int x: Initial x position of the top left corner.
        :param int y: Initial y position of the top left corner.
        :param int color_index: Initial color_index to use when selecting color from the palette.
        """
    width: int
    """The width of the rectangle in pixels."""
    height: int
    """The height of the rectangle in pixels."""
    color_index: int
    """The color_index of the rectangle in 1 based index of the palette."""
    x: int
    """X position of the top left corner of the rectangle in the parent."""

    y: int
    """Y position of the top left corner of the rectangle in the parent."""

    hidden: bool
    """Hide the rectangle or not."""

    location: Tuple[int, int]
    """(X,Y) position of the top left corner of the rectangle in the parent."""

    pixel_shader: Union[displayio.ColorConverter, displayio.Palette]
    """The pixel shader of the rectangle."""
