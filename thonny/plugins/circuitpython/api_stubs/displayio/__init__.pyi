"""Native helpers for driving displays

The `displayio` module contains classes to manage display output
including synchronizing with refresh rates and partial updating.

For more a more thorough explanation and guide for using `displayio`, please
refer to `this Learn guide
<https://learn.adafruit.com/circuitpython-display-support-using-displayio>`_.
"""

from __future__ import annotations

import typing
from typing import Optional, Tuple, Union

import busio
import circuitpython_typing
import microcontroller
import paralleldisplay
import vectorio
from circuitpython_typing import ReadableBuffer, WriteableBuffer

def release_displays() -> None:
    """Releases any actively used displays so their buses and pins can be used again. This will also
    release the builtin display on boards that have one. You will need to reinitialize it yourself
    afterwards. This may take seconds to complete if an active EPaperDisplay is refreshing.

    Use this once in your code.py if you initialize a display. Place it right before the
    initialization so the display is active as long as possible."""
    ...

class Colorspace:
    """The colorspace for a `ColorConverter` to operate in"""

    RGB888: Colorspace
    """The standard 24-bit colorspace.  Bits 0-7 are blue, 8-15 are green, and 16-24 are red. (0xRRGGBB)"""

    RGB565: Colorspace
    """The standard 16-bit colorspace.  Bits 0-4 are blue, bits 5-10 are green, and 11-15 are red (0bRRRRRGGGGGGBBBBB)"""

    RGB565_SWAPPED: Colorspace
    """The swapped 16-bit colorspace.  First, the high and low 8 bits of the number are swapped, then they are interpreted as for RGB565"""

    RGB555: Colorspace
    """The standard 15-bit colorspace.  Bits 0-4 are blue, bits 5-9 are green, and 11-14 are red.  The top bit is ignored. (0bxRRRRRGGGGGBBBBB)"""

    RGB555_SWAPPED: Colorspace
    """The swapped 15-bit colorspace.  First, the high and low 8 bits of the number are swapped, then they are interpreted as for RGB555"""

class Bitmap:
    """Stores values of a certain size in a 2D array

    Bitmaps can be treated as read-only buffers. If the number of bits in a pixel is 8, 16, or 32; and the number of bytes
    per row is a multiple of 4, then the resulting memoryview will correspond directly with the bitmap's contents. Otherwise,
    the bitmap data is packed into the memoryview with unspecified padding.

    A Bitmap can be treated as a buffer, allowing its content to be
    viewed and modified using e.g., with ``ulab.numpy.frombuffer``,
    but the `displayio.Bitmap.dirty` method must be used to inform
    displayio when a bitmap was modified through the buffer interface.

    `bitmaptools.arrayblit` can also be useful to move data efficiently
    into a Bitmap."""

    def __init__(self, width: int, height: int, value_count: int) -> None:
        """Create a Bitmap object with the given fixed size. Each pixel stores a value that is used to
        index into a corresponding palette. This enables differently colored sprites to share the
        underlying Bitmap. value_count is used to minimize the memory used to store the Bitmap.

        :param int width: The number of values wide
        :param int height: The number of values high
        :param int value_count: The number of possible pixel values."""
        ...
    width: int
    """Width of the bitmap. (read only)"""
    height: int
    """Height of the bitmap. (read only)"""
    def __getitem__(self, index: Union[Tuple[int, int], int]) -> int:
        """Returns the value at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          print(bitmap[0,1])"""
        ...
    def __setitem__(self, index: Union[Tuple[int, int], int], value: int) -> None:
        """Sets the value at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          bitmap[0,1] = 3"""
        ...
    def blit(
        self,
        x: int,
        y: int,
        source_bitmap: Bitmap,
        *,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        skip_index: int,
    ) -> None:
        """Inserts the source_bitmap region defined by rectangular boundaries
                    (x1,y1) and (x2,y2) into the bitmap at the specified (x,y) location.

        :param int x: Horizontal pixel location in bitmap where source_bitmap upper-left
                      corner will be placed
        :param int y: Vertical pixel location in bitmap where source_bitmap upper-left
                      corner will be placed
        :param bitmap source_bitmap: Source bitmap that contains the graphical region to be copied
        :param int x1: Minimum x-value for rectangular bounding box to be copied from the source bitmap
        :param int y1: Minimum y-value for rectangular bounding box to be copied from the source bitmap
        :param int x2: Maximum x-value (exclusive) for rectangular bounding box to be copied from the source bitmap
        :param int y2: Maximum y-value (exclusive) for rectangular bounding box to be copied from the source bitmap
        :param int skip_index: bitmap palette index in the source that will not be copied,
                               set to None to copy all pixels"""
        ...
    def fill(self, value: int) -> None:
        """Fills the bitmap with the supplied palette index value."""
        ...
    def dirty(self, x1: int = 0, y1: int = 0, x2: int = -1, y2: int = -1) -> None:
        """Inform displayio of bitmap updates done via the buffer
        protocol.

        :param int x1: Minimum x-value for rectangular bounding box to be considered as modified
        :param int y1: Minimum y-value for rectangular bounding box to be considered as modified
        :param int x2: Maximum x-value (exclusive) for rectangular bounding box to be considered as modified
        :param int y2: Maximum y-value (exclusive) for rectangular bounding box to be considered as modified

        If x1 or y1 are not specified, they are taken as 0.  If x2 or y2
        are not specified, or are given as -1, they are taken as the width
        and height of the image.  Thus, calling dirty() with the
        default arguments treats the whole bitmap as modified.

        When a bitmap is modified through the buffer protocol, the
        display will not be properly updated unless the bitmap is
        notified of the "dirty rectangle" that encloses all modified
        pixels."""
        ...
    def deinit(self) -> None:
        """Release resources allocated by Bitmap."""
        ...

class ColorConverter:
    """Converts one color format to another."""

    def __init__(
        self, *, input_colorspace: Colorspace = Colorspace.RGB888, dither: bool = False
    ) -> None:
        """Create a ColorConverter object to convert color formats.

        :param Colorspace colorspace: The source colorspace, one of the Colorspace constants
        :param bool dither: Adds random noise to dither the output image"""
        ...
    def convert(self, color: int) -> int:
        """Converts the given color to RGB565 according to the Colorspace"""
        ...
    dither: bool
    """When `True` the ColorConverter dithers the output by adding random noise when
    truncating to display bitdepth"""
    def make_transparent(self, color: int) -> None:
        """Set the transparent color or index for the ColorConverter. This will
        raise an Exception if there is already a selected transparent index.

        :param int color: The color to be transparent"""
    def make_opaque(self, color: int) -> None:
        """Make the ColorConverter be opaque and have no transparent pixels.

        :param int color: [IGNORED] Use any value"""

_DisplayBus = Union["FourWire", "paralleldisplay.ParallelBus", "I2CDisplay"]
""":py:class:`FourWire`, :py:class:`paralleldisplay.ParallelBus` or :py:class:`I2CDisplay`"""

class Display:
    """Manage updating a display over a display bus

    This initializes a display and connects it into CircuitPython. Unlike other
    objects in CircuitPython, Display objects live until `displayio.release_displays()`
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
        r"""Create a Display object on the given display bus (`FourWire`, `ParallelBus` or `I2CDisplay`).

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
           display = displayio.Display(display_bus, init_sequence, width=320, height=240)

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
        :param int colstart: The index if the first visible column
        :param int rowstart: The index if the first visible row
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
    def show(self, group: Group) -> None:
        """
        .. note:: `show()` is deprecated and will be removed in CircuitPython 9.0.0.
          Use ``.root_group = group`` instead.

        Switches to displaying the given group of layers. When group is None, the default
        CircuitPython terminal will be shown.

        :param Group group: The group to show.

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
    root_group: Group
    """The root group on the display.
    If the root group is set to ``None``, the default CircuitPython terminal will be shown.
    """
    def fill_row(self, y: int, buffer: WriteableBuffer) -> WriteableBuffer:
        """Extract the pixels from a single row

        :param int y: The top edge of the area
        :param ~circuitpython_typing.WriteableBuffer buffer: The buffer in which to place the pixel data
        """
        ...

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
    ) -> None:
        """Create a EPaperDisplay object on the given display bus (`displayio.FourWire` or `paralleldisplay.ParallelBus`).

        The ``start_sequence`` and ``stop_sequence`` are bitpacked to minimize the ram impact. Every
        command begins with a command byte followed by a byte to determine the parameter count and
        delay. When the top bit of the second byte is 1 (0x80), a delay will occur after the command
        parameters are sent. The remaining 7 bits are the parameter count excluding any delay
        byte. The bytes following are the parameters. When the delay bit is set, a single byte after
        the parameters specifies the delay duration in milliseconds. The value 0xff will lead to an
        extra long 500 ms delay instead of 255 ms. The next byte will begin a new command definition.

        :param display_bus: The bus that the display is connected to
        :type _DisplayBus: displayio.FourWire or paralleldisplay.ParallelBus
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
        """
        ...
    def show(self, group: Group) -> None:
        """
        .. note:: `show()` is deprecated and will be removed in CircuitPython 9.0.0.
          Use ``.root_group = group`` instead.

        Switches to displaying the given group of layers. When group is None, the default
        CircuitPython terminal will be shown.

        :param Group group: The group to show."""
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

    root_group: Group
    """The root group on the epaper display.
    If the root group is set to ``None``, the default CircuitPython terminal will be shown.
    """

class FourWire:
    """Manage updating a display over SPI four wire protocol in the background while Python code runs.
    It doesn't handle display initialization."""

    def __init__(
        self,
        spi_bus: busio.SPI,
        *,
        command: Optional[microcontroller.Pin],
        chip_select: microcontroller.Pin,
        reset: Optional[microcontroller.Pin] = None,
        baudrate: int = 24000000,
        polarity: int = 0,
        phase: int = 0,
    ) -> None:
        """Create a FourWire object associated with the given pins.

        The SPI bus and pins are then in use by the display until `displayio.release_displays()` is
        called even after a reload. (It does this so CircuitPython can use the display after your code
        is done.) So, the first time you initialize a display bus in code.py you should call
        :py:func:`displayio.release_displays` first, otherwise it will error after the first code.py run.

        If the ``command`` pin is not specified, a 9-bit SPI mode will be simulated by adding a
        data/command bit to every bit being transmitted, and splitting the resulting data back
        into 8-bit bytes for transmission. The extra bits that this creates at the end are ignored
        by the receiving device.

        :param busio.SPI spi_bus: The SPI bus that make up the clock and data lines
        :param microcontroller.Pin command: Data or command pin. When None, 9-bit SPI is simulated.
        :param microcontroller.Pin chip_select: Chip select pin
        :param microcontroller.Pin reset: Reset pin. When None only software reset can be used
        :param int baudrate: Maximum baudrate in Hz for the display on the bus
        :param int polarity: the base state of the clock line (0 or 1)
        :param int phase: the edge of the clock that data is captured. First (0)
            or second (1). Rising or falling depends on clock polarity."""
        ...
    def reset(self) -> None:
        """Performs a hardware reset via the reset pin. Raises an exception if called when no reset pin
        is available."""
        ...
    def send(
        self, command: int, data: ReadableBuffer, *, toggle_every_byte: bool = False
    ) -> None:
        """Sends the given command value followed by the full set of data. Display state, such as
        vertical scroll, set via ``send`` may or may not be reset once the code is done.
        """
        ...

class Group:
    """Manage a group of sprites and groups and how they are inter-related."""

    def __init__(self, *, scale: int = 1, x: int = 0, y: int = 0) -> None:
        """Create a Group of a given size and scale. Scale is in one dimension. For example, scale=2
        leads to a layer's pixel being 2x2 pixels when in the group.

        :param int scale: Scale of layer pixels in one dimension.
        :param int x: Initial x position within the parent.
        :param int y: Initial y position within the parent."""
        ...
    hidden: bool
    """True when the Group and all of it's layers are not visible. When False, the Group's layers
    are visible if they haven't been hidden."""
    scale: int
    """Scales each pixel within the Group in both directions. For example, when scale=2 each pixel
    will be represented by 2x2 pixels."""
    x: int
    """X position of the Group in the parent."""
    y: int
    """Y position of the Group in the parent."""
    def append(
        self,
        layer: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> None:
        """Append a layer to the group. It will be drawn above other layers."""
        ...
    def insert(
        self,
        index: int,
        layer: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> None:
        """Insert a layer into the group."""
        ...
    def index(
        self,
        layer: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> int:
        """Returns the index of the first copy of layer. Raises ValueError if not found."""
        ...
    def pop(
        self, i: int = -1
    ) -> Union[vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid]:
        """Remove the ith item and return it."""
        ...
    def remove(
        self,
        layer: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> None:
        """Remove the first copy of layer. Raises ValueError if it is not present."""
        ...
    def __bool__(self) -> bool: ...
    def __len__(self) -> int:
        """Returns the number of layers in a Group"""
        ...
    def __getitem__(
        self, index: int
    ) -> Union[vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid]:
        """Returns the value at the given index.

        This allows you to::

          print(group[0])"""
        ...
    def __setitem__(
        self,
        index: int,
        value: Union[
            vectorio.Circle, vectorio.Rectangle, vectorio.Polygon, Group, TileGrid
        ],
    ) -> None:
        """Sets the value at the given index.

        This allows you to::

          group[0] = sprite"""
        ...
    def __delitem__(self, index: int) -> None:
        """Deletes the value at the given index.

        This allows you to::

          del group[0]"""
        ...
    def sort(self, key: function, reverse: bool) -> None:
        """Sort the members of the group."""
        ...

class I2CDisplay:
    """Manage updating a display over I2C in the background while Python code runs.
    It doesn't handle display initialization."""

    def __init__(
        self,
        i2c_bus: busio.I2C,
        *,
        device_address: int,
        reset: Optional[microcontroller.Pin] = None,
    ) -> None:
        """Create a I2CDisplay object associated with the given I2C bus and reset pin.

        The I2C bus and pins are then in use by the display until `displayio.release_displays()` is
        called even after a reload. (It does this so CircuitPython can use the display after your code
        is done.) So, the first time you initialize a display bus in code.py you should call
        :py:func:`displayio.release_displays` first, otherwise it will error after the first code.py run.

        :param busio.I2C i2c_bus: The I2C bus that make up the clock and data lines
        :param int device_address: The I2C address of the device
        :param microcontroller.Pin reset: Reset pin. When None only software reset can be used
        """
        ...
    def reset(self) -> None:
        """Performs a hardware reset via the reset pin. Raises an exception if called when no reset pin
        is available."""
        ...
    def send(self, command: int, data: ReadableBuffer) -> None:
        """Sends the given command value followed by the full set of data. Display state, such as
        vertical scroll, set via ``send`` may or may not be reset once the code is done.
        """
        ...

class OnDiskBitmap:
    """Loads values straight from disk. This minimizes memory use but can lead to
    much slower pixel load times. These load times may result in frame tearing where only part of
    the image is visible.

    It's easiest to use on a board with a built in display such as the `Hallowing M0 Express
    <https://www.adafruit.com/product/3900>`_.

    .. code-block:: Python

      import board
      import displayio
      import time
      import pulseio

      board.DISPLAY.brightness = 0
      splash = displayio.Group()
      board.DISPLAY.show(splash)

      odb = displayio.OnDiskBitmap('/sample.bmp')
      face = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader)
      splash.append(face)
      # Wait for the image to load.
      board.DISPLAY.refresh(target_frames_per_second=60)

      # Fade up the backlight
      for i in range(100):
          board.DISPLAY.brightness = 0.01 * i
          time.sleep(0.05)

      # Wait forever
      while True:
          pass"""

    def __init__(self, file: Union[str, typing.BinaryIO]) -> None:
        """Create an OnDiskBitmap object with the given file.

        :param file file: The name of the bitmap file.  For backwards compatibility, a file opened in binary mode may also be passed.

        Older versions of CircuitPython required a file opened in binary
        mode. CircuitPython 7.0 modified OnDiskBitmap so that it takes a
        filename instead, and opens the file internally.  A future version
        of CircuitPython will remove the ability to pass in an opened file.
        """
        ...
    width: int
    """Width of the bitmap. (read only)"""
    height: int
    """Height of the bitmap. (read only)"""
    pixel_shader: Union[ColorConverter, Palette]
    """The image's pixel_shader.  The type depends on the underlying
    bitmap's structure.  The pixel shader can be modified (e.g., to set the
    transparent pixel or, for palette shaded images, to update the palette.)"""

class Palette:
    """Map a pixel palette_index to a full color. Colors are transformed to the display's format internally to
    save memory."""

    def __init__(self, color_count: int, *, dither: bool = False) -> None:
        """Create a Palette object to store a set number of colors.

        :param int color_count: The number of colors in the Palette
        :param bool dither: When true, dither the RGB color before converting to the display's color space
        """
        ...
    dither: bool
    """When `True` the Palette dithers the output color by adding random
    noise when truncating to display bitdepth"""
    def __bool__(self) -> bool: ...
    def __len__(self) -> int:
        """Returns the number of colors in a Palette"""
        ...
    def __getitem__(self, index: int) -> Optional[int]:
        r"""Return the pixel color at the given index as an integer."""
        ...
    def __setitem__(
        self, index: int, value: Union[int, ReadableBuffer, Tuple[int, int, int]]
    ) -> None:
        r"""Sets the pixel color at the given index. The index should be an integer in the range 0 to color_count-1.

        The value argument represents a color, and can be from 0x000000 to 0xFFFFFF (to represent an RGB value).
        Value can be an int, bytes (3 bytes (RGB) or 4 bytes (RGB + pad byte)), bytearray,
        or a tuple or list of 3 integers.

        This allows you to::

          palette[0] = 0xFFFFFF                     # set using an integer
          palette[1] = b'\xff\xff\x00'              # set using 3 bytes
          palette[2] = b'\xff\xff\x00\x00'          # set using 4 bytes
          palette[3] = bytearray(b'\x00\x00\xFF')   # set using a bytearay of 3 or 4 bytes
          palette[4] = (10, 20, 30)                 # set using a tuple of 3 integers"""
        ...
    def make_transparent(self, palette_index: int) -> None: ...
    def make_opaque(self, palette_index: int) -> None: ...
    def is_transparent(self, palette_index: int) -> bool:
        """Returns `True` if the palette index is transparent.  Returns `False` if opaque."""
        ...

class Shape:
    """Represents a shape made by defining boundaries that may be mirrored."""

    def __init__(
        self, width: int, height: int, *, mirror_x: bool = False, mirror_y: bool = False
    ) -> None:
        """Create a Shape object with the given fixed size. Each pixel is one bit and is stored by the
        column boundaries of the shape on each row. Each row's boundary defaults to the full row.

        :param int width: The number of pixels wide
        :param int height: The number of pixels high
        :param bool mirror_x: When true the left boundary is mirrored to the right.
        :param bool mirror_y: When true the top boundary is mirrored to the bottom."""
        ...
    def set_boundary(self, y: int, start_x: int, end_x: int) -> None:
        """Loads pre-packed data into the given row."""
        ...

class TileGrid:
    """A grid of tiles sourced out of one bitmap

    Position a grid of tiles sourced from a bitmap and pixel_shader combination. Multiple grids
    can share bitmaps and pixel shaders.

    A single tile grid is also known as a Sprite."""

    def __init__(
        self,
        bitmap: Union[Bitmap, OnDiskBitmap, Shape],
        *,
        pixel_shader: Union[ColorConverter, Palette],
        width: int = 1,
        height: int = 1,
        tile_width: Optional[int] = None,
        tile_height: Optional[int] = None,
        default_tile: int = 0,
        x: int = 0,
        y: int = 0,
    ) -> None:
        """Create a TileGrid object. The bitmap is source for 2d pixels. The pixel_shader is used to
        convert the value and its location to a display native pixel color. This may be a simple color
        palette lookup, a gradient, a pattern or a color transformer.

        To save RAM usage, tile values are only allowed in the range from 0 to 255 inclusive (single byte values).

        tile_width and tile_height match the height of the bitmap by default.

        :param Bitmap,OnDiskBitmap,Shape bitmap: The bitmap storing one or more tiles.
        :param ColorConverter,Palette pixel_shader: The pixel shader that produces colors from values
        :param int width: Width of the grid in tiles.
        :param int height: Height of the grid in tiles.
        :param int tile_width: Width of a single tile in pixels. Defaults to the full Bitmap and must evenly divide into the Bitmap's dimensions.
        :param int tile_height: Height of a single tile in pixels. Defaults to the full Bitmap and must evenly divide into the Bitmap's dimensions.
        :param int default_tile: Default tile index to show.
        :param int x: Initial x position of the left edge within the parent.
        :param int y: Initial y position of the top edge within the parent."""
    hidden: bool
    """True when the TileGrid is hidden. This may be False even when a part of a hidden Group."""
    x: int
    """X position of the left edge in the parent."""
    y: int
    """Y position of the top edge in the parent."""
    width: int
    """Width of the tilegrid in tiles."""
    height: int
    """Height of the tilegrid in tiles."""
    tile_width: int
    """Width of a single tile in pixels."""
    tile_height: int
    """Height of a single tile in pixels."""
    flip_x: bool
    """If true, the left edge rendered will be the right edge of the right-most tile."""
    flip_y: bool
    """If true, the top edge rendered will be the bottom edge of the bottom-most tile."""
    transpose_xy: bool
    """If true, the TileGrid's axis will be swapped. When combined with mirroring, any 90 degree
    rotation can be achieved along with the corresponding mirrored version."""
    def contains(self, touch_tuple: tuple) -> bool:
        """Returns True if the first two values in ``touch_tuple`` represent an x,y coordinate
        inside the tilegrid rectangle bounds."""
    pixel_shader: Union[ColorConverter, Palette]
    """The pixel shader of the tilegrid."""
    bitmap: Union[Bitmap, OnDiskBitmap, Shape]
    """The bitmap of the tilegrid."""
    def __getitem__(self, index: Union[Tuple[int, int], int]) -> int:
        """Returns the tile index at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          print(grid[0])"""
        ...
    def __setitem__(self, index: Union[Tuple[int, int], int], value: int) -> None:
        """Sets the tile index at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          grid[0] = 10

        or::

          grid[0,0] = 10"""
        ...
