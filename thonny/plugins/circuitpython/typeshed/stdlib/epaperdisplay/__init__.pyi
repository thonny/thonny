"""Displays a `displayio` object tree on an e-paper display

"""

from __future__ import annotations

from typing import Optional, Union

import circuitpython_typing
import displayio
import microcontroller
from busdisplay import _DisplayBus
from circuitpython_typing import ReadableBuffer

class EPaperDisplay:
    """Manage updating an epaper display over a display bus

    This initializes an epaper display and connects it into CircuitPython. Unlike other
    objects in CircuitPython, EPaperDisplay objects live until `displayio.release_displays()`
    is called. This is done so that CircuitPython can use the display itself.

    Most people should not use this class directly. Use a specific display driver instead that will
    contain the startup and shutdown sequences at minimum."""

    def __init__(
        self,
        display_bus: _DisplayBus,
        start_sequence: ReadableBuffer,
        stop_sequence: ReadableBuffer,
        *,
        width: int,
        height: int,
        ram_width: int,
        ram_height: int,
        colstart: int = 0,
        rowstart: int = 0,
        rotation: int = 0,
        set_column_window_command: Optional[int] = None,
        set_row_window_command: Optional[int] = None,
        set_current_column_command: Optional[int] = None,
        set_current_row_command: Optional[int] = None,
        write_black_ram_command: int,
        black_bits_inverted: bool = False,
        write_color_ram_command: Optional[int] = None,
        color_bits_inverted: bool = False,
        highlight_color: int = 0x000000,
        refresh_display_command: Union[int, circuitpython_typing.ReadableBuffer],
        refresh_time: float = 40,
        busy_pin: Optional[microcontroller.Pin] = None,
        busy_state: bool = True,
        seconds_per_frame: float = 180,
        always_toggle_chip_select: bool = False,
        grayscale: bool = False,
        advanced_color_epaper: bool = False,
        two_byte_sequence_length: bool = False,
        start_up_time: float = 0,
        address_little_endian: bool = False,
    ) -> None:
        """Create a EPaperDisplay object on the given display bus (`fourwire.FourWire` or `paralleldisplaybus.ParallelBus`).

        The ``start_sequence`` and ``stop_sequence`` are bitpacked to minimize the ram impact. Every
        command begins with a command byte followed by a byte to determine the parameter count and
        delay. When the top bit of the second byte is 1 (0x80), a delay will occur after the command
        parameters are sent. The remaining 7 bits are the parameter count excluding any delay
        byte. The bytes following are the parameters. When the delay bit is set, a single byte after
        the parameters specifies the delay duration in milliseconds. The value 0xff will lead to an
        extra long 500 ms delay instead of 255 ms. The next byte will begin a new command definition.

        :param display_bus: The bus that the display is connected to
        :type _DisplayBus: fourwire.FourWire or paralleldisplaybus.ParallelBus
        :param ~circuitpython_typing.ReadableBuffer start_sequence: Byte-packed command sequence.
        :param ~circuitpython_typing.ReadableBuffer stop_sequence: Byte-packed command sequence.
        :param int width: Width in pixels
        :param int height: Height in pixels
        :param int ram_width: RAM width in pixels
        :param int ram_height: RAM height in pixels
        :param int colstart: The index if the first visible column
        :param int rowstart: The index if the first visible row
        :param int rotation: The rotation of the display in degrees clockwise. Must be in 90 degree increments (0, 90, 180, 270)
        :param int set_column_window_command: Command used to set the start and end columns to update
        :param int set_row_window_command: Command used so set the start and end rows to update
        :param int set_current_column_command: Command used to set the current column location
        :param int set_current_row_command: Command used to set the current row location
        :param int write_black_ram_command: Command used to write pixels values into the update region
        :param bool black_bits_inverted: True if 0 bits are used to show black pixels. Otherwise, 1 means to show black.
        :param int write_color_ram_command: Command used to write pixels values into the update region
        :param bool color_bits_inverted: True if 0 bits are used to show the color. Otherwise, 1 means to show color.
        :param int highlight_color: RGB888 of source color to highlight with third ePaper color.
        :param int refresh_display_command: Command used to start a display refresh. Single int or byte-packed command sequence
        :param float refresh_time: Time it takes to refresh the display before the stop_sequence should be sent. Ignored when busy_pin is provided.
        :param microcontroller.Pin busy_pin: Pin used to signify the display is busy
        :param bool busy_state: State of the busy pin when the display is busy
        :param float seconds_per_frame: Minimum number of seconds between screen refreshes
        :param bool always_toggle_chip_select: When True, chip select is toggled every byte
        :param bool grayscale: When true, the color ram is the low bit of 2-bit grayscale
        :param bool advanced_color_epaper: When true, the display is a 7-color advanced color epaper (ACeP)
        :param bool two_byte_sequence_length: When true, use two bytes to define sequence length
        :param float start_up_time: Time to wait after reset before sending commands
        :param bool address_little_endian: Send the least significant byte (not bit) of multi-byte addresses first. Ignored when ram is addressed with one byte
        """
        ...

    def update_refresh_mode(
        self, start_sequence: ReadableBuffer, seconds_per_frame: float = 180
    ) -> None:
        """Updates the ``start_sequence`` and ``seconds_per_frame`` parameters to enable
        varying the refresh mode of the display."""

    def refresh(self) -> None:
        """Refreshes the display immediately or raises an exception if too soon. Use
        ``time.sleep(display.time_to_refresh)`` to sleep until a refresh can occur."""
        ...
    time_to_refresh: float
    """Time, in fractional seconds, until the ePaper display can be refreshed."""
    busy: bool
    """True when the display is refreshing. This uses the ``busy_pin`` when available or the
       ``refresh_time`` otherwise."""
    width: int
    """Gets the width of the display in pixels"""
    height: int
    """Gets the height of the display in pixels"""
    rotation: int
    """The rotation of the display as an int in degrees."""
    bus: _DisplayBus
    """The bus being used by the display"""

    root_group: displayio.Group
    """The root group on the epaper display.
    If the root group is set to `displayio.CIRCUITPYTHON_TERMINAL`, the default CircuitPython terminal will be shown.
    If the root group is set to ``None``, no output will be shown.
    """
