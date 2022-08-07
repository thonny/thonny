"""Real Time Clock

The `rtc` module provides support for a Real Time Clock. You can access and manage the
RTC using :class:`rtc.RTC`. It also backs the :func:`time.time` and :func:`time.localtime`
functions using the onboard RTC if present."""

from __future__ import annotations

import time

def set_time_source(rtc: RTC) -> None:
    """Sets the RTC time source used by :func:`time.localtime`.
    The default is :class:`rtc.RTC`, but it's useful to use this to override the
    time source for testing purposes. For example::

      import rtc
      import time

      class RTC(object):
          @property
          def datetime(self):
              return time.struct_time((2018, 3, 17, 21, 1, 47, 0, 0, 0))

      r = RTC()
      rtc.set_time_source(r)"""
    ...

class RTC:
    """Real Time Clock"""

    def __init__(self) -> None:
        """This class represents the onboard Real Time Clock. It is a singleton and will always return the same instance."""
        ...
    datetime: time.struct_time
    """The current date and time of the RTC as a `time.struct_time`.

    This must be set to the current date and time whenever the board loses power::

      import rtc
      import time

      r = rtc.RTC()
      r.datetime = time.struct_time((2019, 5, 29, 15, 14, 15, 0, -1, -1))


    Once set, the RTC will automatically update this value as time passes. You can read this
    property to get a snapshot of the current time::

      current_time = r.datetime
      print(current_time)
      # struct_time(tm_year=2019, tm_month=5, ...)"""

    calibration: int
    """The RTC calibration value as an `int`.

    A positive value speeds up the clock and a negative value slows it down.
    Range and value is hardware specific, but one step is often approximately 1 ppm::

      import rtc
      import time

      r = rtc.RTC()
      r.calibration = 1"""
