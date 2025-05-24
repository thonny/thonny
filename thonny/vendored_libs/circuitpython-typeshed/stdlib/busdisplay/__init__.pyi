"""Displays a `displayio` object tree on an external device with a built-in
framebuffer

"""

from __future__ import annotations

from typing import Optional, Union

import displayio
import fourwire
import i2cdisplaybus
import microcontroller
import paralleldisplaybus
from circuitpython_typing import ReadableBuffer, WriteableBuffer

_DisplayBus = Union[
    "fourwire.FourWire", "paralleldisplaybus.ParallelBus", "i2cdisplaybus.I2CDisplayBus"
]
""":py:class:`fourwire.FourWire`, :py:class:`paralleldisplaybus.ParallelBus` or :py:class:`i2cdisplaybus.I2CDisplayBus`"""

class BusDisplay:
    """Manage updating a display over a display bus

    This initializes a display and connects it into CircuitPython. Unlike other
    objects in CircuitPython, display objects live until `displayio.release_displays()`
    is called. This is done so that CircuitPython can use the display itself.

    Most people should not use this class directly. Use a specific display driver instead that will
    contain the initialization sequence at minimum."""

    def __init__(
        self,
        display_bus: _DisplayBus,
        init_sequence: ReadableBuffer,
        *,
        width: int,
        height: int,
        colstart: int = 0,
        rowstart: int = 0,
        rotation: int = 0,
        color_depth: int = 16,
        grayscale: bool = False,
        pixels_in_byte_share_row: bool = True,
        bytes_per_cell: int = 1,
        reverse_pixels_in_byte: bool = False,
        set_column_command: int = 0x2A,
        set_row_command: int = 0x2B,
        write_ram_command: int = 0x2C,
        backlight_pin: Optional[microcontroller.Pin] = None,
        brightness_command: Optional[int] = None,
        brightness: float = 1.0,
        single_byte_bounds: bool = False,
        data_as_commands: bool = False,
        auto_refresh: bool = True,
        native_frames_per_second: int = 60,
        backlight_on_high: bool = True,
        SH1107_addressing: bool = False,
    ) -> None:
        r"""Create a Display object on the given display bus (`FourWire`, `paralleldisplaybus.ParallelBus` or `I2CDisplayBus`).

        The ``init_sequence`` is bitpacked to minimize the ram impact. Every command begins with a
        command byte followed by a byte to determine the parameter count and delay. When the top bit
        of the second byte is 1 (0x80), a delay will occur after the command parameters are sent.
        The remaining 7 bits are the parameter count excluding any delay byte. The bytes following
        are the parameters. When the delay bit is set, a single byte after the parameters specifies
        the delay duration in milliseconds. The value 0xff will lead to an extra long 500 ms delay
        instead of 255 ms. The next byte will begin a new command definition.
        Here is an example:

        .. code-block:: python

          init_sequence = (b"\xe1\x0f\x00\x0E\x14\x03\x11\x07\x31\xC1\x48\x08\x0F\x0C\x31\x36\x0F" # Set Gamma
                           b"\x11\x80\x78"# Exit Sleep then delay 0x78 (120ms)
                           b"\x29\x81\xaa\x78"# Display on then delay 0x78 (120ms)
                          )
           display = busdisplay.BusDisplay(display_bus, init_sequence, width=320, height=240)

        The first command is 0xe1 with 15 (0xf) parameters following. The second is 0x11 with 0
        parameters and a 120ms (0x78) delay. The third command is 0x29 with one parameter 0xaa and a
        120ms delay (0x78). Multiple byte literals (b"") are merged together on load. The parens
        are needed to allow byte literals on subsequent lines.

        The initialization sequence should always leave the display memory access inline with the scan
        of the display to minimize tearing artifacts.

        :param display_bus: The bus that the display is connected to
        :type _DisplayBus: FourWire, ParallelBus or I2CDisplay
        :param ~circuitpython_typing.ReadableBuffer init_sequence: Byte-packed initialization sequence.
        :param int width: Width in pixels
        :param int height: Height in pixels
        :param int colstart: The index of the first visible column
        :param int rowstart: The index of the first visible row
        :param int rotation: The rotation of the display in degrees clockwise. Must be in 90 degree increments (0, 90, 180, 270)
        :param int color_depth: The number of bits of color per pixel transmitted. (Some displays
            support 18 bit but 16 is easier to transmit. The last bit is extrapolated.)
        :param bool grayscale: True if the display only shows a single color.
        :param bool pixels_in_byte_share_row: True when pixels are less than a byte and a byte includes pixels from the same row of the display. When False, pixels share a column.
        :param int bytes_per_cell: Number of bytes per addressable memory location when color_depth < 8. When greater than one, bytes share a row or column according to pixels_in_byte_share_row.
        :param bool reverse_pixels_in_byte: Reverses the pixel order within each byte when color_depth < 8. Does not apply across multiple bytes even if there is more than one byte per cell (bytes_per_cell.)
        :param bool reverse_bytes_in_word: Reverses the order of bytes within a word when color_depth == 16
        :param int set_column_command: Command used to set the start and end columns to update
        :param int set_row_command: Command used so set the start and end rows to update
        :param int write_ram_command: Command used to write pixels values into the update region. Ignored if data_as_commands is set.
        :param microcontroller.Pin backlight_pin: Pin connected to the display's backlight
        :param int brightness_command: Command to set display brightness. Usually available in OLED controllers.
        :param float brightness: Initial display brightness.
        :param bool single_byte_bounds: Display column and row commands use single bytes
        :param bool data_as_commands: Treat all init and boundary data as SPI commands. Certain displays require this.
        :param bool auto_refresh: Automatically refresh the screen
        :param int native_frames_per_second: Number of display refreshes per second that occur with the given init_sequence.
        :param bool backlight_on_high: If True, pulling the backlight pin high turns the backlight on.
        :param bool SH1107_addressing: Special quirk for SH1107, use upper/lower column set and page set
        :param int set_vertical_scroll: This parameter is accepted but ignored for backwards compatibility. It will be removed in a future release.
        :param int backlight_pwm_frequency: The frequency to use to drive the PWM for backlight brightness control. Default is 50000.
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
    """Gets the width of the board"""
    height: int
    """Gets the height of the board"""
    rotation: int
    """The rotation of the display as an int in degrees."""
    bus: _DisplayBus
    """The bus being used by the display"""
    root_group: displayio.Group
    """The root group on the display.
    If the root group is set to `displayio.CIRCUITPYTHON_TERMINAL`, the default CircuitPython terminal will be shown.
    If the root group is set to ``None``, no output will be shown.
    """

    def fill_row(self, y: int, buffer: WriteableBuffer) -> WriteableBuffer:
        """Extract the pixels from a single row

        :param int y: The top edge of the area
        :param ~circuitpython_typing.WriteableBuffer buffer: The buffer in which to place the pixel data
        """
        ...
