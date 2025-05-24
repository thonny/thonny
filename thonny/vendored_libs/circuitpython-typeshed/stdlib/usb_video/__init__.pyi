"""Allows streaming bitmaps to a host computer via USB

This makes your CircuitPython device identify to the host computer as a video camera.
This mode is also known as "USB UVC".

This mode requires 1 IN endpoint. Generally, microcontrollers have a limit on
the number of endpoints. If you exceed the number of endpoints, CircuitPython
will automatically enter Safe Mode. Even in this case, you may be able to
enable USB video by also disabling other USB functions, such as `usb_hid` or
`usb_midi`.

To enable this mode, you must configure the framebuffer size in ``boot.py`` and then
create a display in ``code.py``.

.. code-block:: py

    # boot.py
    import usb_video
    usb_video.enable_framebuffer(128, 96)

.. code-block:: py

    # code.py
    import usb_video
    import framebufferio
    import displayio

    displayio.release_displays()
    display = framebufferio.FramebufferDisplay(usb_video.USBFramebuffer())

    # ... use the display object with displayio Group and TileGrid objects

This interface is experimental and may change without notice even in stable
versions of CircuitPython."""

from __future__ import annotations

def enable_framebuffer(width: int, height: int) -> None:
    """Enable a USB video framebuffer, setting the given width & height

    This function may only be used from ``boot.py``.

    Width is rounded up to a multiple of 2.

    After boot.py completes, the framebuffer will be allocated. Total storage
    of 4×``width``×``height`` bytes is required, reducing the amount available
    for Python objects. If the allocation fails, a MemoryError is raised.
    This message can be seen in ``boot_out.txt``."""

class USBFramebuffer:
    """Displays to a USB connected computer using the UVC protocol

    The data in the framebuffer is in RGB565_SWAPPED format.

    This object is most often used with `framebufferio.FramebufferDisplay`. However,
    it also supports the ``WritableBuffer`` protocol and can be accessed
    as an array of ``H`` (unsigned 16-bit values)."""

    def __init__(self) -> None:
        """Returns the singleton framebuffer object, if USB video is enabled"""

    def refresh(self) -> None:
        """Transmits the color data in the buffer to the pixels so that
        they are shown."""
        ...
    width: int
    """The width of the display, in pixels"""
    height: int
    """The height of the display, in pixels"""
