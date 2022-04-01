from __future__ import annotations

import microcontroller

class TouchAlarm:
    """Trigger an alarm when touch is detected."""

    def __init__(self, *pin: microcontroller.Pin) -> None:
        """Create an alarm that will be triggered when the given pin is touched.
        The alarm is not active until it is passed to an `alarm`-enabling function, such as
        `alarm.light_sleep_until_alarms()` or `alarm.exit_and_deep_sleep_until_alarms()`.

        :param microcontroller.Pin pin: The pin to monitor. On some ports, the choice of pin
          may be limited due to hardware restrictions, particularly for deep-sleep alarms.
        """
        ...
    pin: microcontroller.Pin
    """The trigger pin."""
