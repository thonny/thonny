"""Button handling in the background"""

class GamePad:
    """Scan buttons for presses

    Usage::

        import board
        import digitalio
        import gamepad
        import time

        B_UP = 1 << 0
        B_DOWN = 1 << 1


        pad = gamepad.GamePad(
            digitalio.DigitalInOut(board.D10),
            digitalio.DigitalInOut(board.D11),
        )

        y = 0
        while True:
            buttons = pad.get_pressed()
            if buttons & B_UP:
                y -= 1
                print(y)
            elif buttons & B_DOWN:
                y += 1
                print(y)
            time.sleep(0.1)
            while buttons:
                # Wait for all buttons to be released.
                buttons = pad.get_pressed()
                time.sleep(0.1)"""

    def __init__(self, b1: Any, b2: Any, b3: Any, b4: Any, b5: Any, b6: Any, b7: Any, b8: Any):
        """Initializes button scanning routines.

        The ``b1``-``b8`` parameters are ``DigitalInOut`` objects, which
        immediately get switched to input with a pull-up, (unless they already
        were set to pull-down, in which case they remain so), and then scanned
        regularly for button presses. The order is the same as the order of
        bits returned by the ``get_pressed`` function. You can re-initialize
        it with different keys, then the new object will replace the previous
        one.

        The basic feature required here is the ability to poll the keys at
        regular intervals (so that de-bouncing is consistent) and fast enough
        (so that we don't miss short button presses) while at the same time
        letting the user code run normally, call blocking functions and wait
        on delays.

        They button presses are accumulated, until the ``get_pressed`` method
        is called, at which point the button state is cleared, and the new
        button presses start to be recorded."""
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

