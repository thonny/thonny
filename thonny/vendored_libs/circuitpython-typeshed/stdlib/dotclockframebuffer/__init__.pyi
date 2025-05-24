"""Native helpers for driving parallel displays"""

from __future__ import annotations

import typing
from typing import Optional, Tuple

import busio
import microcontroller
from circuitpython_typing import ReadableBuffer

Length = typing.Literal[1, 2]

def ioexpander_send_init_sequence(
    bus: busio.I2C,
    init_sequence: ReadableBuffer,
    *,
    i2c_init_sequence: ReadableBuffer,
    i2c_address: int,
    gpio_address: int,
    gpio_data_len: Length,
    gpio_data: int,
    cs_bit: int,
    mosi_bit: int,
    clk_bit: int,
    reset_bit: Optional[int],
) -> None:
    """Send a displayio-style initialization sequence over an I2C I/O expander

    This function is highly generic in order to support various I/O expanders.
    What's assumed is that all the GPIO can be updated by writing to a single I2C register.
    Normal output polarity is assumed (CS and CLK are active low, data is not inverted).
    Only 8-bit I2C addresses are supported.
    8- and 16-bit I2C addresses and data registers are supported.
    The Data/Command bit is sent as part of the serial data.

    Normally this function is used via a convenience library that is specific to the display & I/O expander in use.

    If the board has an integrated I/O expander, ``**board.TFT_IO_EXPANDER`` expands to the proper arguments starting with ``gpio_address``.
    Note that this may include the ``i2c_init_sequence`` argument which can change the direction & value of I/O expander pins.
    If this is undesirable, take a copy of ``TFT_IO_EXPANDER`` and change or remove the ``i2c_init_sequence`` key.

    If the board has an integrated display that requires an initialization sequence, ``board.TFT_INIT_SEQUENCE`` is the initialization string for the display.

    :param busio.I2C bus: The I2C bus where the I/O expander resides
    :param int busio.i2c_address: The I2C bus address of the I/O expander
    :param ReadableBuffer init_sequence: The initialization sequence to send to the display
    :param int gpio_address: The address portion of the I2C transaction (1 byte)
    :param int gpio_data_len: The size of the data portion of the I2C transaction, 1 or 2 bytes
    :param int gpio_data: The output value for all GPIO bits other than cs, mosi, and clk (needed because GPIO expanders may be unable to read back the current output value)
    :param int cs_bit: The bit number (from 0 to 7, or from 0 to 15) of the chip select bit in the GPIO register
    :param int mosi_value: The bit number (from 0 to 7, or from 0 to 15) of the data out bit in the GPIO register
    :param int clk_value: The bit number (from 0 to 7, or from 0 to 15) of the clock out bit in the GPIO register
    :param Optional[int] reset_value: The bit number (from 0 to 7, or from 0 to 15) of the display reset bit in the GPIO register
    :param Optional[ReadableBuffer] i2c_init_sequence: An initialization sequence to send to the I2C expander
    """

class DotClockFramebuffer:
    """Manage updating a 'dot-clock' framebuffer in the background while Python code runs.
    It doesn't handle display initialization."""

    def __init__(
        self,
        *,
        de: microcontroller.Pin,
        vsync: microcontroller.Pin,
        hsync: microcontroller.Pin,
        dclk: microcontroller.Pin,
        red: Tuple[microcontroller.Pin],
        green: Tuple[microcontroller.Pin],
        blue: Tuple[microcontroller.Pin],
        frequency: int,
        width: int,
        height: int,
        hsync_pulse_width: int,
        hsync_back_porch: int,
        hsync_front_porch: int,
        hsync_idle_low: bool,
        vsync_back_porch: int,
        vsync_front_porch: int,
        vsync_idle_low: bool,
        de_idle_high: bool,
        pclk_active_high: bool,
        pclk_idle_high: bool,
        overscan_left: int = 0,
    ) -> None:
        """Create a DotClockFramebuffer object associated with the given pins.

        The pins are then in use by the display until `displayio.release_displays()`
        is called even after a reload. (It does this so CircuitPython can use the display after your
        code is done.) So, the first time you initialize a display bus in code.py you should call
        :py:func:`displayio.release_displays` first, otherwise it will error after the first code.py run.

        When a board has dedicated dot clock framebuffer pins and/or timings, they are intended to be used in the constructor with ``**`` dictionary unpacking like so:
        ``DotClockFramebuffer(**board.TFT_PINS, **board.TFT_TIMINGS)``

        On Espressif-family microcontrollers, this driver requires that the
        ``CIRCUITPY_RESERVED_PSRAM`` in ``settings.toml`` be large enough to hold the
        framebuffer. Generally, boards with built-in displays or display connectors
        will have a default setting that is large enough for typical use. If the
        constructor raises a MemoryError or an IDFError, this probably indicates the
        setting is too small and should be increased.

        TFT connection parameters:

        :param microcontroller.Pin de: The "data enable" input to the display
        :param microcontroller.Pin vsync: The "vertical sync" input to the display
        :param microcontroller.Pin hsync: The "horizontal sync" input to the display
        :param microcontroller.Pin dclk: The "data clock" input to the display
        :param ~tuple red: The red data pins, most significant pin first.
        :param ~tuple green: The green data pins, most significant pin first.
        :param ~tuple blue: The blue data pins, most significant pin first.

        TFT timing parameters:

        :param int frequency: The requested data clock frequency in Hz.
        :param int width: The visible width of the display, in pixels
        :param int height: The visible height of the display, in pixels
        :param int hsync_pulse_width: Horizontal sync width in pixels
        :param int hsync_back_porch: Horizontal back porch, number of pixels between hsync and start of line active data
        :param int hsync_front_porch: Horizontal front porch, number of pixels between the end of active data and the next hsync
        :param int vsync_back_porch: Vertical back porch, number of lines between vsync and start of frame
        :param int vsync_front_porch: Vertical front porch, number of lines between the end of frame and the next vsync
        :param bool hsync_idle_low: True if the hsync signal is low in IDLE state
        :param bool vsync_idle_low: True if the vsync signal is low in IDLE state
        :param bool de_idle_high: True if the de signal is high in IDLE state
        :param bool pclk_active_high: True if the display data is clocked out at the rising edge of dclk
        :param bool pclk_idle_high: True if the dclk stays at high level in IDLE phase

        :param int overscan_left: Allocate additional non-visible columns left of the first display column
        """
        #:param int overscan_top: Allocate additional non-visible rows above the first display row
        #:param int overscan_right: Allocate additional non-visible columns right of the last display column
        #:param int overscan_bottom: Allocate additional non-visible rows below the last display row
        ...

    def refresh(self) -> None:
        """Transmits the color data in the buffer to the pixels so that
        they are shown.

        If this function is not called, the results are unpredictable; updates may be partially shown.
        """
        ...
    refresh_rate: float
    """The pixel refresh rate of the display, in Hz"""
    frequency: int
    """The pixel frequency of the display, in Hz"""
    width: int
    """The width of the display, in pixels"""
    height: int
    """The height of the display, in pixels"""

    row_stride: int
    """The row_stride of the display, in bytes

    Due to overscan or alignment requirements, the memory address for row N+1 may not be exactly ``2*width`` bytes after the memory address for row N.
    This property gives the stride in **bytes**.

    On Espressif this value is **guaranteed** to be a multiple of the 2 (i.e., it is a whole number of pixels)"""

    first_pixel_offset: int
    """The first_pixel_offset of the display, in bytes

    Due to overscan or alignment requirements, the memory address for row N+1 may not be exactly ``2*width`` bytes after the memory address for row N.
    This property gives the stride in **bytes**.

    On Espressif this value is **guaranteed** to be a multiple of the 2 (i.e., it is a whole number of pixels)"""
