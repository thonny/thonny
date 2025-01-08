from __future__ import annotations

from typing import Optional

class TimeAlarm:
    """Trigger an alarm when the specified time is reached."""

    def __init__(
        self,
        *,
        monotonic_time: Optional[float] = None,
        epoch_time: Optional[int] = None,
    ) -> None:
        """Create an alarm that will be triggered when `time.monotonic()` would equal
        ``monotonic_time``, or when `time.time()` would equal ``epoch_time``.
        Only one of the two arguments can be given.
        The alarm is not active until it is passed to an
        `alarm`-enabling sleep function, such as `alarm.light_sleep_until_alarms()` or
        `alarm.exit_and_deep_sleep_until_alarms()`.

        If the given time is already in the past, then an exception is raised.
        If the sleep happens after the given time, then it will wake immediately
        due to this time alarm.
        """
        ...
    monotonic_time: float
    """When this time is reached, the alarm will trigger, based on the `time.monotonic()` clock.
       The time may be given as ``epoch_time`` in the constructor, but it is returned
       by this property only as a `time.monotonic()` time.
       """
