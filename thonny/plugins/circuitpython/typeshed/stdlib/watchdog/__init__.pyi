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

from __future__ import annotations

from typing import Optional

class WatchDogTimeout(Exception):
    """Exception raised when the watchdog timer is set to
    ``WatchDogMode.RAISE`` and expires.

    Example::

        import microcontroller
        import watchdog
        import time

        wdt = microcontroller.watchdog
        wdt.timeout = 5

        while True:
            wdt.mode = watchdog.WatchDogMode.RAISE
            print("Starting loop -- should exit after five seconds")
            try:
                while True:
                    time.sleep(10)  # Also works with pass
            except watchdog.WatchDogTimeout as e:
                print("Watchdog expired")
            except Exception as e:
                print("Other exception")

        print("Exited loop")
    """

class WatchDogMode:
    """Run state of the watchdog timer."""

    RAISE: WatchDogMode
    """Raise an exception when the `WatchDogTimer` expires."""

    RESET: WatchDogMode
    """Reset the system when the `WatchDogTimer` expires."""

class WatchDogTimer:
    """Timer that is used to detect code lock ups and automatically reset the microcontroller
    when one is detected.

    A lock up is detected when the watchdog hasn't been fed after a given duration. So, make
    sure to call `feed` within the timeout.
    """

    def __init__(self) -> None:
        """Access the sole instance through `microcontroller.watchdog`."""
        ...

    def feed(self) -> None:
        """Feed the watchdog timer. This must be called regularly, otherwise
        the timer will expire. Silently does nothing if the watchdog isn't active."""
        ...

    def deinit(self) -> None:
        """Stop the watchdog timer.

        :raises RuntimeError: if the watchdog timer cannot be disabled on this platform.

        .. note:: This is deprecated in ``9.0.0`` and will be removed in ``10.0.0``.
            Set watchdog `mode` to `None` instead.

        """
        ...
    timeout: float
    """The maximum number of seconds that can elapse between calls
    to `feed()`. Setting the timeout will also feed the watchdog."""
    mode: Optional[WatchDogMode]
    """The current operating mode of the WatchDogTimer `watchdog.WatchDogMode` or `None` when
    the timer is disabled.

    Setting a `WatchDogMode` activates the WatchDog::

      from microcontroller import watchdog
      from watchdog import WatchDogMode

      watchdog.timeout = 5
      watchdog.mode = WatchDogMode.RESET


    Once set, the `WatchDogTimer` will perform the specified action if the timer expires."""
