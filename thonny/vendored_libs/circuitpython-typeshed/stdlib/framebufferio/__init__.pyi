"""Native framebuffer display driving

The `framebufferio` module contains classes to manage display output
including synchronizing with refresh rates and partial updating.
It is used in conjunction with classes from `displayio` to actually
place items on the display; and classes like `RGBMatrix` to actually
drive the display."""

from __future__ import annotations

from typing import Optional

import circuitpython_typing
import displayio
from circuitpython_typing import WriteableBuffer

class FramebufferDisplay:
    """Manage updating a display with framebuffer in RAM

    This initializes a display and connects it into CircuitPython. Unlike other
    objects in CircuitPython, Display objects live until `displayio.release_displays()`
    is called. This is done so that CircuitPython can use the display itself."""

    def __init__(
        self,
        framebuffer: circuitpython_typing.FrameBuffer,
        *,
        rotation: int = 0,
        auto_refresh: bool = True,
    ) -> None:
        """Create a Display object with the given framebuffer (a buffer, array, ulab.array, etc)

        :param ~circuitpython_typing.FrameBuffer framebuffer: The framebuffer that the display is connected to
        :param bool auto_refresh: Automatically refresh the screen
        :param int rotation: The rotation of the display in degrees clockwise. Must be in 90 degree increments (0, 90, 180, 270)
        """
        ...

    def refresh(
        self,
        *,
        target_frames_per_second: Optional[int] = None,
        minimum_frames_per_second: int = 0,
    ) -> bool:
        """When auto_refresh is off, and :py:attr:`target_frames_per_second` is not `None` this waits
        for the target frame rate and then refreshes the display,
        returning `True`. If the call has taken too long since the last refresh call for the given
        target frame rate, then the refresh returns `False` immediately without updating the screen to
        hopefully help getting caught up.

        If the time since the last successful refresh is below the minimum frame rate, then an
        exception will be raised. The default :py:attr:`minimum_frames_per_second` of 0 disables this behavior.

        When auto_refresh is off, and :py:attr:`target_frames_per_second` is `None` this
        will update the display immediately.

        When auto_refresh is on, updates the display immediately. (The display will also update
        without calls to this.)

        :param Optional[int] target_frames_per_second: The target frame rate that :py:func:`refresh` should try to
            achieve. Set to `None` for immediate refresh.
        :param int minimum_frames_per_second: The minimum number of times the screen should be updated per second.
        """
        ...
    auto_refresh: bool
    """True when the display is refreshed automatically."""
    brightness: float
    """The brightness of the display as a float. 0.0 is off and 1.0 is full brightness."""
    width: int
    """Gets the width of the framebuffer"""
    height: int
    """Gets the height of the framebuffer"""
    rotation: int
    """The rotation of the display as an int in degrees."""
    framebuffer: circuitpython_typing.FrameBuffer
    """The framebuffer being used by the display"""

    def fill_row(self, y: int, buffer: WriteableBuffer) -> WriteableBuffer:
        """Extract the pixels from a single row

        :param int y: The top edge of the area
        :param ~circuitpython_typing.WriteableBuffer buffer: The buffer in which to place the pixel data
        """
        ...
    root_group: displayio.Group
    """The root group on the display.
    If the root group is set to `displayio.CIRCUITPYTHON_TERMINAL`, the default CircuitPython terminal will be shown.
    If the root group is set to ``None``, no output will be shown.
    """
