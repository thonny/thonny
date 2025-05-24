"""Low-level routines for interacting with the Broadcom VideoCore GPU"""

from __future__ import annotations

class Framebuffer:
    """A VideoCore managed frame buffer."""

    def __init__(self, width: int, height: int) -> None:
        """Create a Framebuffer object with the given dimensions. Memory is
           allocated outside of the heap in GPU memory.

        The framebuffer is in "ARGB8888" format.

        A Framebuffer is often used in conjunction with a
        `framebufferio.FramebufferDisplay`."""

    def deinit(self) -> None:
        """Free the resources (pins, timers, etc.) associated with this
        rgbmatrix instance.  After deinitialization, no further operations
        may be performed."""
        ...
    width: int
    """The width of the display, in pixels"""
    height: int
    """The height of the display, in pixels"""
