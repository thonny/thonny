"""Low-level routines for interacting with PicoDVI Output"""

from __future__ import annotations

import microcontroller

class Framebuffer:
    def __init__(
        self,
        width: int,
        height: int,
        *,
        clk_dp: microcontroller.Pin,
        clk_dn: microcontroller.Pin,
        red_dp: microcontroller.Pin,
        red_dn: microcontroller.Pin,
        green_dp: microcontroller.Pin,
        green_dn: microcontroller.Pin,
        blue_dp: microcontroller.Pin,
        blue_dn: microcontroller.Pin,
        color_depth: int = 8,
    ) -> None:
        """Create a Framebuffer object with the given dimensions. Memory is
        allocated onto the heap and then moved outside on VM end.

        .. warning:: This may change the system clock speed to match the DVI signal.
           Make sure to initialize other objects after this one so they account
           for the changed clock.

        This allocates a very large framebuffer and is most likely to succeed
        the earlier it is attempted.

        On RP2040, each dp and dn pair of pins must be neighboring, such as
        19 and 20. They must also be ordered the same way. In other words,
        dp must be less than dn for all pairs or dp must be greater than dn
        for all pairs.

        On RP2350, all pins must be an HSTX output but can be in any order.

        The framebuffer pixel format varies depending on color_depth:

        * 1 - Each bit is a pixel. Either white (1) or black (0).
        * 2 - Each two bits is a pixel. Grayscale between white (0x3) and black (0x0).
        * 4 - Each nibble is a pixel in RGB format. The fourth bit is ignored. (RP2350 only)
        * 8 - Each byte is a pixel in RGB332 format.
        * 16 - Each two bytes is a pixel in RGB565 format.
        * 32 - Each four bytes is a pixel in RGB888 format. The top byte is ignored.

        Output resolution support varies between the RP2040 and RP2350.

        On RP2040, two output resolutions are currently supported, 640x480
        and 800x480. Monochrome framebuffers (color_depth=1 or 2) must be
        full resolution. Color framebuffers must be half resolution (320x240
        or 400x240) and pixels will be duplicated to create the signal.

        On RP2350, output resolution is either 640x480 or 720x400. Monochrome
        framebuffers (color_depth=1 or 2) must be full resolution. 4-bit
        color must also be full resolution. 8-bit color can be quarter, half
        or full resolution. 16-bit color and 32-bit color must be quarter or
        half resolution due to internal RAM limitations.

        A Framebuffer is often used in conjunction with a
        `framebufferio.FramebufferDisplay`.

        :param int width: the width of the source framebuffer. Support varies with chipset.
        :param int height: the height of the source framebuffer. Support varies with chipset.
        :param ~microcontroller.Pin clk_dp: the positive clock signal pin
        :param ~microcontroller.Pin clk_dn: the negative clock signal pin
        :param ~microcontroller.Pin red_dp: the positive red signal pin
        :param ~microcontroller.Pin red_dn: the negative red signal pin
        :param ~microcontroller.Pin green_dp: the positive green signal pin
        :param ~microcontroller.Pin green_dn: the negative green signal pin
        :param ~microcontroller.Pin blue_dp: the positive blue signal pin
        :param ~microcontroller.Pin blue_dn: the negative blue signal pin
        :param int color_depth: the color depth of the framebuffer in bits. 1, 2 for grayscale
          and 4 (RP2350 only), 8 or 16 for color, 32 for color (RP2350 only)
        """

    def deinit(self) -> None:
        """Free the resources (pins, timers, etc.) associated with this
        `picodvi.Framebuffer` instance.  After deinitialization, no further operations
        may be performed."""
        ...
    width: int
    """The width of the framebuffer, in pixels. It may be doubled for output."""
    height: int
    """The width of the framebuffer, in pixels. It may be doubled for output."""
