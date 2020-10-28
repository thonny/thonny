"""Watchdog Timer

The `watchdog` module provides support for a Watchdog Timer. This timer will reset the device
if it hasn't been fed after a specified amount of time. This is useful to ensure the board
has not crashed or locked up. Note that on some platforms the watchdog timer cannot be disabled
once it has been enabled.

The `WatchDogTimer` is used to restart the system when the application crashes and ends
up into a non recoverable state. Once started it cannot be stopped or
reconfigured in any way. After enabling, the application must "feed" the
watchdog periodically to prevent it from expiring and resetting the system.

Example usage::

    from microcontroller import watchdog as w
    from watchdog import WatchDogMode
    w.timeout=2.5 # Set a timeout of 2.5 seconds
    w.mode = WatchDogMode.RAISE
    w.feed()"""

class WatchDogMode:
    """run state of the watchdog timer"""

    def __init__(self, ):
        """Enum-like class to define the run mode of the watchdog timer."""

    RAISE: Any = ...
    """Raise an exception when the WatchDogTimer expires.

    :type watchdog.WatchDogMode:"""

    RESET: Any = ...
    """Reset the system if the WatchDogTimer expires.

    :type watchdog.WatchDogMode:"""

class WatchDogTimer:
    """Timer that is used to detect code lock ups and automatically reset the microcontroller
       when one is detected.

       A lock up is detected when the watchdog hasn't been fed after a given duration. So, make
       sure to call `feed` within the timeout.
    """

    def __init__(self, ):
        """Not currently dynamically supported. Access the sole instance through `microcontroller.watchdog`."""
        ...

    def feed(self):
        """Feed the watchdog timer. This must be called regularly, otherwise
        the timer will expire."""
        ...

    def deinit(self):
        """Stop the watchdog timer. This may raise an error if the watchdog
        timer cannot be disabled on this platform."""
        ...

    timeout: float = ...
    """The maximum number of seconds that can elapse between calls
    to feed()"""

    mode: watchdog.WatchDogMode = ...
    """The current operating mode of the WatchDogTimer `watchdog.WatchDogMode`.

    Setting a WatchDogMode activates the WatchDog::

      import microcontroller
      import watchdog

      w = microcontroller.watchdog
      w.timeout = 5
      w.mode = watchdog.WatchDogMode.RAISE


    Once set, the WatchDogTimer will perform the specified action if the timer expires."""

