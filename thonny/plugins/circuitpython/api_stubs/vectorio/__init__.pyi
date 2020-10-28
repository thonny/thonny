"""Lightweight 2d shapes for displays"""

class Circle:

    def __init__(self, radius: int):
        """Circle is positioned on screen by its center point.

           :param radius: The radius of the circle in pixels"""

    radius : int = ...
    """The radius of the circle in pixels."""

from typing import List, Tuple

class Polygon:
    def __init__(self, points: List[ Tuple[ x, y ], ... ] ):
        """Represents a closed shape by ordered vertices

           :param points: Vertices for the polygon"""

    points: List[ Tuple[ x, y ], ... ] = ...
    """Set a new look and shape for this polygon"""

class Rectangle:
    def __init__(self, width: int, height: int):
        """Represents a rectangle by defining its bounds

           :param width: The number of pixels wide
           :param height: The number of pixels high"""

class VectorShape:
    def __init__(self, shape: vectorio.Polygon, pixel_shader: displayio.Palette, x: int=0, y: int=0):
        """Binds a vector shape to a location and pixel color

           :param shape: The shape to draw.
           :param pixel_shader: The pixel shader that produces colors from values
           :param x: Initial x position of the center axis of the shape within the parent.
           :param y: Initial y position of the center axis of the shape within the parent."""
        ...

    x: int = ...
    """X position of the center point of the shape in the parent."""

    y: int = ...
    """Y position of the center point of the shape in the parent."""

    pixel_shader: displayio.Palette = ...
    """The pixel shader of the shape."""

