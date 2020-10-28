"""Tracks button presses read through a shift register"""

class GamePadShift:
    """Scan buttons for presses through a shift register"""

    def __init__(self, clock: Any, data: Any, latch: Any):
        """Initializes button scanning routines.

        The ``clock``, ``data`` and ``latch`` parameters are ``DigitalInOut``
        objects connected to the shift register controlling the buttons.

        They button presses are accumulated, until the ``get_pressed`` method
        is called, at which point the button state is cleared, and the new
        button presses start to be recorded.

        Only one gamepad (`gamepad.GamePad` or `gamepadshift.GamePadShift`)
        may be used at a time."""
        ...

    def get_pressed(self, ) -> Any:
        """Get the status of buttons pressed since the last call and clear it.

        Returns an 8-bit number, with bits that correspond to buttons,
        which have been pressed (or held down) since the last call to this
        function set to 1, and the remaining bits set to 0. Then it clears
        the button state, so that new button presses (or buttons that are
        held down) can be recorded for the next call."""
        ...

    def deinit(self, ) -> Any:
        """Disable button scanning."""
        ...

