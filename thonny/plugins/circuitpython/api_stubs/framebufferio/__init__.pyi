"""Native framebuffer display driving

The `framebufferio` module contains classes to manage display output
including synchronizing with refresh rates and partial updating.
It is used in conjunction with classes from `displayio` to actually
place items on the display; and classes like `RGBMatrix` to actually
drive the display."""

class FramebufferDisplay:
    """Manage updating a display with framebuffer in RAM

    This initializes a display and connects it into CircuitPython. Unlike other
    objects in CircuitPython, Display objects live until `displayio.release_displays()`
    is called. This is done so that CircuitPython can use the display itself."""

    def __init__(self, framebuffer: Any, *, rotation: int = 0, auto_refresh: bool = True):
        """Create a Display object with the given framebuffer (a buffer, array, ulab.array, etc)

        :param framebuffer: The framebuffer that the display is connected to
        :type framebuffer: any core object implementing the framebuffer protocol
        :param bool auto_refresh: Automatically refresh the screen
        :param int rotation: The rotation of the display in degrees clockwise. Must be in 90 degree increments (0, 90, 180, 270)"""
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

    framebuffer: Any = ...


    def fill_row(self, y: int, buffer: bytearray) -> Any:
        """Extract the pixels from a single row

        :param int y: The top edge of the area
        :param bytearray buffer: The buffer in which to place the pixel data"""
        ...

