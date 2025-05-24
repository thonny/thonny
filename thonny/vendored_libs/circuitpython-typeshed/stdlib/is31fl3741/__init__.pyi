from __future__ import annotations

from typing import Optional, Tuple

import busio
import is31fl3741
from circuitpython_typing import ReadableBuffer, WriteableBuffer

class IS31FL3741_FrameBuffer:
    """Creates an in-memory framebuffer for a IS31FL3741 device."""

    def __init__(
        self,
        is31: is31fl3741.IS31FL3741,
        width: int,
        height: int,
        mapping: Tuple[int, ...],
        *,
        framebuffer: Optional[WriteableBuffer] = None,
        scale: bool = False,
        gamma: bool = False,
    ) -> None:
        """Create a IS31FL3741_FrameBuffer object with the given attributes.

        The framebuffer is in "RGB888" format using 4 bytes per pixel.
        Bits 24-31 are ignored. The format is in RGB order.

        If a framebuffer is not passed in, one is allocated and initialized
        to all black.  In any case, the framebuffer can be retrieved
        by passing the Is31fl3741 object to memoryview().

        A Is31fl3741 is often used in conjunction with a
        `framebufferio.FramebufferDisplay`.

        :param is31fl3741.IS31FL3741 is31: base IS31FL3741 instance to drive the framebuffer
        :param int width: width of the display
        :param int height: height of the display
        :param Tuple[int, ...] mapping: mapping of matrix locations to LEDs
        :param Optional[WriteableBuffer] framebuffer: Optional buffer to hold the display
        :param bool scale: if True display is scaled down by 3 when displayed
        :param bool gamma: if True apply gamma correction to all LEDs"""
        ...

    def deinit(self) -> None:
        """Free the resources associated with this
        IS31FL3741 instance.  After deinitialization, no further operations
        may be performed."""
        ...
    brightness: float
    """In the current implementation, 0.0 turns the display off entirely
    and any other value up to 1.0 turns the display on fully."""

    def refresh(self) -> None:
        """Transmits the color data in the buffer to the pixels so that
        they are shown."""
        ...
    width: int
    """The width of the display, in pixels"""
    height: int
    """The height of the display, in pixels"""

class IS31FL3741:
    """Driver for an IS31FL3741 device."""

    def __init__(self, i2c: busio.I2C, *, addr: int = 0x30) -> None:
        """Create a IS31FL3741 object with the given attributes.

        Designed to work low level or passed to and object such as
        :class:`~is31fl3741.IS31FL3741_FrameBuffer`.

        :param ~busio.I2C i2c: I2C bus the IS31FL3741 is on
        :param int addr: device address"""
        ...

    def deinit(self) -> None:
        """Free the resources associated with this
        IS31FL3741 instance.  After deinitialization, no further operations
        may be performed."""
        ...

def reset(self) -> None:
    """Resets the IS31FL3741 chip."""
    ...

def enable(self) -> None:
    """Enables the IS31FL3741 chip."""
    ...

def set_global_current(self, current: int) -> None:
    """Sets the global current of the IS31FL3741 chip.

    :param int current: global current value 0x00 to 0xFF"""
    ...

def set_led(self, led: int, value: int, page: int) -> None:
    """Resets the IS31FL3741 chip.

    :param int led: which LED to set
    :param int value: value to set the LED to 0x00 to 0xFF
    :param int page: page to write to 0 or 2. If the LED is a >= 180
      the routine will automatically write to page 1 or 3 (instead
      of 0 or 2)"""
    ...

def write(mapping: Tuple[int, ...], buf: ReadableBuffer) -> None:
    """Write buf out on the I2C bus to the IS31FL3741.

    :param ~Tuple[int, ...] mapping: map the pixels in the buffer to the order addressed by the driver chip
    :param ~_typing.ReadableBuffer buf: The bytes to clock out. No assumption is made about color order
    """
    ...
