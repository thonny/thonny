"""Native helpers for driving displays

The `displayio` module contains classes to manage display output
including synchronizing with refresh rates and partial updating."""

def release_displays() -> Any:
    """Releases any actively used displays so their busses and pins can be used again. This will also
    release the builtin display on boards that have one. You will need to reinitialize it yourself
    afterwards. This may take seconds to complete if an active EPaperDisplay is refreshing.

    Use this once in your code.py if you initialize a display. Place it right before the
    initialization so the display is active as long as possible."""
    ...

class Bitmap:
    """Stores values of a certain size in a 2D array"""

    def __init__(self, width: int, height: int, value_count: int):
        """Create a Bitmap object with the given fixed size. Each pixel stores a value that is used to
        index into a corresponding palette. This enables differently colored sprites to share the
        underlying Bitmap. value_count is used to minimize the memory used to store the Bitmap.

        :param int width: The number of values wide
        :param int height: The number of values high
        :param int value_count: The number of possible pixel values."""
        ...

    width: Any = ...
    """Width of the bitmap. (read only)"""

    height: Any = ...
    """Height of the bitmap. (read only)"""

    def __getitem__(self, index: Any) -> Any:
        """Returns the value at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          print(bitmap[0,1])"""
        ...

    def __setitem__(self, index: Any, value: Any) -> Any:
        """Sets the value at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          bitmap[0,1] = 3"""
        ...

    def fill(self, value: Any) -> Any:
        """Fills the bitmap with the supplied palette index value."""
        ...

class ColorConverter:
    """Converts one color format to another."""

    def __init__(self, *, dither: bool = False):
        """Create a ColorConverter object to convert color formats. Only supports RGB888 to RGB565
        currently.
        :param bool dither: Adds random noise to dither the output image"""
        ...


    def convert(self, color: Any) -> Any:
        """Converts the given RGB888 color to RGB565"""
        ...

    dither: Any = ...
    """When true the color converter dithers the output by adding random noise when
    truncating to display bitdepth"""

class Display:
    """Manage updating a display over a display bus

    This initializes a display and connects it into CircuitPython. Unlike other
    objects in CircuitPython, Display objects live until `displayio.release_displays()`
    is called. This is done so that CircuitPython can use the display itself.

    Most people should not use this class directly. Use a specific display driver instead that will
    contain the initialization sequence at minimum."""

    def __init__(self, display_bus: Any, init_sequence: buffer, *, width: int, height: int, colstart: int = 0, rowstart: int = 0, rotation: int = 0, color_depth: int = 16, grayscale: bool = False, pixels_in_byte_share_row: bool = True, bytes_per_cell: int = 1, reverse_pixels_in_byte: bool = False, set_column_command: int = 0x2a, set_row_command: int = 0x2b, write_ram_command: int = 0x2c, set_vertical_scroll: int = 0, backlight_pin: microcontroller.Pin = None, brightness_command: int = None, brightness: bool = 1.0, auto_brightness: bool = False, single_byte_bounds: bool = False, data_as_commands: bool = False, auto_refresh: bool = True, native_frames_per_second: int = 60):
        """Create a Display object on the given display bus (`displayio.FourWire` or `displayio.ParallelBus`).

        The ``init_sequence`` is bitpacked to minimize the ram impact. Every command begins with a
        command byte followed by a byte to determine the parameter count and if a delay is need after.
        When the top bit of the second byte is 1, the next byte will be the delay time in milliseconds.
        The remaining 7 bits are the parameter count excluding any delay byte. The third through final
        bytes are the remaining command parameters. The next byte will begin a new command definition.
        Here is a portion of ILI9341 init code:

        .. code-block:: python

          init_sequence = (b"\xe1\x0f\x00\x0E\x14\x03\x11\x07\x31\xC1\x48\x08\x0F\x0C\x31\x36\x0F" # Set Gamma
                           b"\x11\x80\x78"# Exit Sleep then delay 0x78 (120ms)
                           b"\x29\x80\x78"# Display on then delay 0x78 (120ms)
                          )
           display = displayio.Display(display_bus, init_sequence, width=320, height=240)

        The first command is 0xe1 with 15 (0xf) parameters following. The second and third are 0x11 and
        0x29 respectively with delays (0x80) of 120ms (0x78) and no parameters. Multiple byte literals
        (b"") are merged together on load. The parens are needed to allow byte literals on subsequent
        lines.

        The initialization sequence should always leave the display memory access inline with the scan
        of the display to minimize tearing artifacts.

        :param display_bus: The bus that the display is connected to
        :type display_bus: displayio.FourWire or displayio.ParallelBus
        :param buffer init_sequence: Byte-packed initialization sequence.
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
        :param int set_vertical_scroll: Command used to set the first row to show
        :param microcontroller.Pin backlight_pin: Pin connected to the display's backlight
        :param int brightness_command: Command to set display brightness. Usually available in OLED controllers.
        :param bool brightness: Initial display brightness. This value is ignored if auto_brightness is True.
        :param bool auto_brightness: If True, brightness is controlled via an ambient light sensor or other mechanism.
        :param bool single_byte_bounds: Display column and row commands use single bytes
        :param bool data_as_commands: Treat all init and boundary data as SPI commands. Certain displays require this.
        :param bool auto_refresh: Automatically refresh the screen
        :param int native_frames_per_second: Number of display refreshes per second that occur with the given init_sequence.
        :param bool backlight_on_high: If True, pulling the backlight pin high turns the backlight on."""
        ...

    def show(self, group: Group) -> Any:
        """Switches to displaying the given group of layers. When group is None, the default
        CircuitPython terminal will be shown.

        :param Group group: The group to show."""
        ...

    def refresh(self, *, target_frames_per_second: int = 60, minimum_frames_per_second: int = 1) -> Any:
        """When auto refresh is off, waits for the target frame rate and then refreshes the display,
        returning True. If the call has taken too long since the last refresh call for the given
        target frame rate, then the refresh returns False immediately without updating the screen to
        hopefully help getting caught up.

        If the time since the last successful refresh is below the minimum frame rate, then an
        exception will be raised. Set minimum_frames_per_second to 0 to disable.

        When auto refresh is on, updates the display immediately. (The display will also update
        without calls to this.)

        :param int target_frames_per_second: How many times a second `refresh` should be called and the screen updated.
        :param int minimum_frames_per_second: The minimum number of times the screen should be updated per second."""
        ...

    auto_refresh: Any = ...
    """True when the display is refreshed automatically."""

    brightness: Any = ...
    """The brightness of the display as a float. 0.0 is off and 1.0 is full brightness. When
    `auto_brightness` is True, the value of `brightness` will change automatically.
    If `brightness` is set, `auto_brightness` will be disabled and will be set to False."""

    auto_brightness: Any = ...
    """True when the display brightness is adjusted automatically, based on an ambient
    light sensor or other method. Note that some displays may have this set to True by default,
    but not actually implement automatic brightness adjustment. `auto_brightness` is set to False
    if `brightness` is set manually."""

    width: Any = ...


    height: Any = ...


    rotation: Any = ...
    """The rotation of the display as an int in degrees."""

    bus: Any = ...


    def fill_row(self, y: int, buffer: bytearray) -> Any:
        """Extract the pixels from a single row

        :param int y: The top edge of the area
        :param bytearray buffer: The buffer in which to place the pixel data"""
        ...

class EPaperDisplay:
    """Manage updating an epaper display over a display bus

    This initializes an epaper display and connects it into CircuitPython. Unlike other
    objects in CircuitPython, EPaperDisplay objects live until `displayio.release_displays()`
    is called. This is done so that CircuitPython can use the display itself.

    Most people should not use this class directly. Use a specific display driver instead that will
    contain the startup and shutdown sequences at minimum."""

    def __init__(self, display_bus: Any, start_sequence: buffer, stop_sequence: buffer, *, width: int, height: int, ram_width: int, ram_height: int, colstart: int = 0, rowstart: int = 0, rotation: int = 0, set_column_window_command: int = None, set_row_window_command: int = None, single_byte_bounds: Any = False, write_black_ram_command: int, black_bits_inverted: bool = False, write_color_ram_command: int = None, color_bits_inverted: bool = False, highlight_color: int = 0x000000, refresh_display_command: int, refresh_time: float = 40, busy_pin: microcontroller.Pin = None, busy_state: bool = True, seconds_per_frame: float = 180, always_toggle_chip_select: bool = False):
        """Create a EPaperDisplay object on the given display bus (`displayio.FourWire` or `displayio.ParallelBus`).

        The ``start_sequence`` and ``stop_sequence`` are bitpacked to minimize the ram impact. Every
        command begins with a command byte followed by a byte to determine the parameter count and if
        a delay is need after. When the top bit of the second byte is 1, the next byte will be the
        delay time in milliseconds. The remaining 7 bits are the parameter count excluding any delay
        byte. The third through final bytes are the remaining command parameters. The next byte will
        begin a new command definition.

        :param display_bus: The bus that the display is connected to
        :type display_bus: displayio.FourWire or displayio.ParallelBus
        :param buffer start_sequence: Byte-packed initialization sequence.
        :param buffer stop_sequence: Byte-packed initialization sequence.
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
        :param int refresh_display_command: Command used to start a display refresh
        :param float refresh_time: Time it takes to refresh the display before the stop_sequence should be sent. Ignored when busy_pin is provided.
        :param microcontroller.Pin busy_pin: Pin used to signify the display is busy
        :param bool busy_state: State of the busy pin when the display is busy
        :param float seconds_per_frame: Minimum number of seconds between screen refreshes
        :param bool always_toggle_chip_select: When True, chip select is toggled every byte"""
        ...

    def show(self, group: Group) -> Any:
        """Switches to displaying the given group of layers. When group is None, the default
        CircuitPython terminal will be shown.

        :param Group group: The group to show."""
        ...

    def refresh(self, ) -> Any:
        """Refreshes the display immediately or raises an exception if too soon. Use
        ``time.sleep(display.time_to_refresh)`` to sleep until a refresh can occur."""
        ...

    time_to_refresh: Any = ...
    """Time, in fractional seconds, until the ePaper display can be refreshed."""

    width: Any = ...
    """Gets the width of the display in pixels"""

    height: Any = ...

    bus: Any = ...

class FourWire:
    """Manage updating a display over SPI four wire protocol in the background while Python code runs.
    It doesn't handle display initialization."""

    def __init__(self, spi_bus: busio.SPI, *, command: microcontroller.Pin, chip_select: microcontroller.Pin, reset: microcontroller.Pin = None, baudrate: int = 24000000, polarity: int = 0, phase: int = 0):
        """Create a FourWire object associated with the given pins.

        The SPI bus and pins are then in use by the display until `displayio.release_displays()` is
        called even after a reload. (It does this so CircuitPython can use the display after your code
        is done.) So, the first time you initialize a display bus in code.py you should call
        :py:func`displayio.release_displays` first, otherwise it will error after the first code.py run.

        :param busio.SPI spi_bus: The SPI bus that make up the clock and data lines
        :param microcontroller.Pin command: Data or command pin
        :param microcontroller.Pin chip_select: Chip select pin
        :param microcontroller.Pin reset: Reset pin. When None only software reset can be used
        :param int baudrate: Maximum baudrate in Hz for the display on the bus
        :param int polarity: the base state of the clock line (0 or 1)
        :param int phase: the edge of the clock that data is captured. First (0)
            or second (1). Rising or falling depends on clock polarity."""
        ...

    def reset(self, ) -> Any:
        """Performs a hardware reset via the reset pin. Raises an exception if called when no reset pin
        is available."""
        ...

    def send(self, command: Any, data: Any, *, toggle_every_byte: Any = False) -> Any:
        """Sends the given command value followed by the full set of data. Display state, such as
        vertical scroll, set via ``send`` may or may not be reset once the code is done."""
        ...

class Group:
    """Manage a group of sprites and groups and how they are inter-related."""

    def __init__(self, *, max_size: int = 4, scale: int = 1, x: int = 0, y: int = 0):
        """Create a Group of a given size and scale. Scale is in one dimension. For example, scale=2
        leads to a layer's pixel being 2x2 pixels when in the group.

        :param int max_size: The maximum group size.
        :param int scale: Scale of layer pixels in one dimension.
        :param int x: Initial x position within the parent.
        :param int y: Initial y position within the parent."""
        ...

    hidden: Any = ...
    """True when the Group and all of it's layers are not visible. When False, the Group's layers
    are visible if they haven't been hidden."""

    scale: Any = ...
    """Scales each pixel within the Group in both directions. For example, when scale=2 each pixel
    will be represented by 2x2 pixels."""

    x: Any = ...
    """X position of the Group in the parent."""

    y: Any = ...
    """Y position of the Group in the parent."""

    def append(self, layer: Any) -> Any:
        """Append a layer to the group. It will be drawn above other layers."""
        ...

    def insert(self, index: Any, layer: Any) -> Any:
        """Insert a layer into the group."""
        ...

    def index(self, layer: Any) -> Any:
        """Returns the index of the first copy of layer. Raises ValueError if not found."""
        ...

    def pop(self, i: Any = -1) -> Any:
        """Remove the ith item and return it."""
        ...

    def remove(self, layer: Any) -> Any:
        """Remove the first copy of layer. Raises ValueError if it is not present."""
        ...

    def __len__(self, ) -> Any:
        """Returns the number of layers in a Group"""
        ...

    def __getitem__(self, index: Any) -> Any:
        """Returns the value at the given index.

        This allows you to::

          print(group[0])"""
        ...

    def __setitem__(self, index: Any, value: Any) -> Any:
        """Sets the value at the given index.

        This allows you to::

          group[0] = sprite"""
        ...

    def __delitem__(self, index: Any) -> Any:
        """Deletes the value at the given index.

        This allows you to::

          del group[0]"""
        ...

class I2CDisplay:
    """Manage updating a display over I2C in the background while Python code runs.
    It doesn't handle display initialization."""

    def __init__(self, i2c_bus: busio.I2C, *, device_address: int, reset: microcontroller.Pin = None):
        """Create a I2CDisplay object associated with the given I2C bus and reset pin.

        The I2C bus and pins are then in use by the display until `displayio.release_displays()` is
        called even after a reload. (It does this so CircuitPython can use the display after your code
        is done.) So, the first time you initialize a display bus in code.py you should call
        :py:func`displayio.release_displays` first, otherwise it will error after the first code.py run.

        :param busio.I2C i2c_bus: The I2C bus that make up the clock and data lines
        :param int device_address: The I2C address of the device
        :param microcontroller.Pin reset: Reset pin. When None only software reset can be used"""
        ...

    def reset(self, ) -> Any:
        """Performs a hardware reset via the reset pin. Raises an exception if called when no reset pin
        is available."""
        ...

    def send(self, command: Any, data: Any) -> Any:
        """Sends the given command value followed by the full set of data. Display state, such as
        vertical scroll, set via ``send`` may or may not be reset once the code is done."""
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

      board.DISPLAY.auto_brightness = False
      board.DISPLAY.brightness = 0
      splash = displayio.Group()
      board.DISPLAY.show(splash)

      with open("/sample.bmp", "rb") as f:
          odb = displayio.OnDiskBitmap(f)
          face = displayio.TileGrid(odb, pixel_shader=displayio.ColorConverter())
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

    def __init__(self, file: file):
        """Create an OnDiskBitmap object with the given file.

        :param file file: The open bitmap file"""
        ...

    width: Any = ...
    """Width of the bitmap. (read only)"""

    height: Any = ...
    """Height of the bitmap. (read only)"""

class Palette:
    """Map a pixel palette_index to a full color. Colors are transformed to the display's format internally to
    save memory."""

    def __init__(self, color_count: int):
        """Create a Palette object to store a set number of colors.

        :param int color_count: The number of colors in the Palette"""
        ...


    def __len__(self, ) -> Any:
        """Returns the number of colors in a Palette"""
        ...

    def __setitem__(self, index: Any, value: Any) -> Any:
        """Sets the pixel color at the given index. The index should be an integer in the range 0 to color_count-1.

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

    def make_transparent(self, palette_index: Any) -> Any: ...

    def make_opaque(self, palette_index: Any) -> Any: ...

class ParallelBus:
    """Manage updating a display over 8-bit parallel bus in the background while Python code runs. This
    protocol may be referred to as 8080-I Series Parallel Interface in datasheets. It doesn't handle
    display initialization."""

    def __init__(self, *, data0: microcontroller.Pin, command: microcontroller.Pin, chip_select: microcontroller.Pin, write: microcontroller.Pin, read: microcontroller.Pin, reset: microcontroller.Pin):
        """Create a ParallelBus object associated with the given pins. The bus is inferred from data0
        by implying the next 7 additional pins on a given GPIO port.

        The parallel bus and pins are then in use by the display until `displayio.release_displays()`
        is called even after a reload. (It does this so CircuitPython can use the display after your
        code is done.) So, the first time you initialize a display bus in code.py you should call
        :py:func`displayio.release_displays` first, otherwise it will error after the first code.py run.

        :param microcontroller.Pin data0: The first data pin. The rest are implied
        :param microcontroller.Pin command: Data or command pin
        :param microcontroller.Pin chip_select: Chip select pin
        :param microcontroller.Pin write: Write pin
        :param microcontroller.Pin read: Read pin
        :param microcontroller.Pin reset: Reset pin"""
        ...

    def reset(self, ) -> Any:
        """Performs a hardware reset via the reset pin. Raises an exception if called when no reset pin
        is available."""
        ...

    def send(self, command: Any, data: Any) -> Any:
        """Sends the given command value followed by the full set of data. Display state, such as
        vertical scroll, set via ``send`` may or may not be reset once the code is done."""
        ...

class Shape:
    """Represents a shape made by defining boundaries that may be mirrored."""

    def __init__(self, width: int, height: int, *, mirror_x: bool = False, mirror_y: bool = False):
        """Create a Shape object with the given fixed size. Each pixel is one bit and is stored by the
        column boundaries of the shape on each row. Each row's boundary defaults to the full row.

        :param int width: The number of pixels wide
        :param int height: The number of pixels high
        :param bool mirror_x: When true the left boundary is mirrored to the right.
        :param bool mirror_y: When true the top boundary is mirrored to the bottom."""
        ...

    def set_boundary(self, y: Any, start_x: Any, end_x: Any) -> Any:
        """Loads pre-packed data into the given row."""
        ...

class TileGrid:
    """A grid of tiles sourced out of one bitmap

    Position a grid of tiles sourced from a bitmap and pixel_shader combination. Multiple grids
    can share bitmaps and pixel shaders.

    A single tile grid is also known as a Sprite."""

    def __init__(self, bitmap: displayio.Bitmap, *, pixel_shader: displayio.Palette, width: int = 1, height: int = 1, tile_width: int = None, tile_height: int = None, default_tile: int = 0, x: int = 0, y: int = 0):
        """Create a TileGrid object. The bitmap is source for 2d pixels. The pixel_shader is used to
        convert the value and its location to a display native pixel color. This may be a simple color
        palette lookup, a gradient, a pattern or a color transformer.

        tile_width and tile_height match the height of the bitmap by default.

        :param displayio.Bitmap bitmap: The bitmap storing one or more tiles.
        :param displayio.Palette pixel_shader: The pixel shader that produces colors from values
        :param int width: Width of the grid in tiles.
        :param int height: Height of the grid in tiles.
        :param int tile_width: Width of a single tile in pixels. Defaults to the full Bitmap and must evenly divide into the Bitmap's dimensions.
        :param int tile_height: Height of a single tile in pixels. Defaults to the full Bitmap and must evenly divide into the Bitmap's dimensions.
        :param int default_tile: Default tile index to show.
        :param int x: Initial x position of the left edge within the parent.
        :param int y: Initial y position of the top edge within the parent."""

    hidden: Any = ...
    """True when the TileGrid is hidden. This may be False even when a part of a hidden Group."""

    x: Any = ...
    """X position of the left edge in the parent."""

    y: Any = ...
    """Y position of the top edge in the parent."""

    flip_x: Any = ...
    """If true, the left edge rendered will be the right edge of the right-most tile."""

    flip_y: Any = ...
    """If true, the top edge rendered will be the bottom edge of the bottom-most tile."""

    transpose_xy: Any = ...
    """If true, the TileGrid's axis will be swapped. When combined with mirroring, any 90 degree
    rotation can be achieved along with the corresponding mirrored version."""

    pixel_shader: Any = ...
    """The pixel shader of the tilegrid."""

    def __getitem__(self, index: Any) -> Any:
        """Returns the tile index at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          print(grid[0])"""
        ...

    def __setitem__(self, index: Any, tile_index: Any) -> Any:
        """Sets the tile index at the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          grid[0] = 10

        or::

          grid[0,0] = 10"""
        ...

