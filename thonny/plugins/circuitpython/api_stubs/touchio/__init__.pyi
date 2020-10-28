"""Touch related IO

The `touchio` module contains classes to provide access to touch IO typically
accelerated by hardware on the onboard microcontroller.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

For example::

  import touchio
  from board import *

  touch_pin = touchio.TouchIn(D6)
  print(touch_pin.value)

This example will initialize the the device, and print the
:py:data:`~touchio.TouchIn.value`."""

class TouchIn:
    """Read the state of a capacitive touch sensor

    Usage::

       import touchio
       from board import *

       touch = touchio.TouchIn(A1)
       while True:
           if touch.value:
               print("touched!")"""

    def __init__(self, pin: microcontroller.Pin):
        """Use the TouchIn on the given pin.

        :param ~microcontroller.Pin pin: the pin to read from"""
        ...

    def deinit(self, ) -> Any:
        """Deinitialises the TouchIn and releases any hardware resources for reuse."""
        ...

    def __enter__(self, ) -> Any:
        """No-op used by Context Managers."""
        ...

    def __exit__(self, ) -> Any:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    value: Any = ...
    """Whether the touch pad is being touched or not. (read-only)

    True when `raw_value` > `threshold`."""

    raw_value: Any = ...
    """The raw touch measurement as an `int`. (read-only)"""

    threshold: Any = ...
    """Minimum `raw_value` needed to detect a touch (and for `value` to be `True`).

    When the **TouchIn** object is created, an initial `raw_value` is read from the pin,
    and then `threshold` is set to be 100 + that value.

    You can adjust `threshold` to make the pin more or less sensitive."""

