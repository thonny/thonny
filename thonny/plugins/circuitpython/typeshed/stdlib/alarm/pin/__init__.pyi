from __future__ import annotations

import microcontroller

class PinAlarm:
    """Trigger an alarm when a pin changes state."""

    def __init__(
        self,
        pin: microcontroller.Pin,
        value: bool,
        edge: bool = False,
        pull: bool = False,
    ) -> None:
        """Create an alarm triggered by a `microcontroller.Pin` level. The alarm is not active
        until it is passed to an `alarm`-enabling function, such as `alarm.light_sleep_until_alarms()` or
        `alarm.exit_and_deep_sleep_until_alarms()`.

        :param microcontroller.Pin pin: The pin to monitor. On some ports, the choice of pin
          may be limited due to hardware restrictions, particularly for deep-sleep alarms.
        :param bool value: When active, trigger when the pin value is high (``True``) or low (``False``).
          On some ports, multiple `PinAlarm` objects may need to have coordinated values
          for deep-sleep alarms.
        :param bool edge: If ``True``, trigger only when there is a transition to the specified
          value of ``value``. If ``True``, if the alarm becomes active when the pin value already
          matches ``value``, the alarm is not triggered: the pin must transition from ``not value``
          to ``value`` to trigger the alarm. On some ports, edge-triggering may not be available,
          particularly for deep-sleep alarms.
        :param bool pull: Enable a pull-up or pull-down which pulls the pin to the level opposite
          that of ``value``. For instance, if ``value`` is set to ``True``, setting ``pull``
          to ``True`` will enable a pull-down, to hold the pin low normally until an outside signal
          pulls it high.
        """
        ...
    pin: microcontroller.Pin
    """The trigger pin."""
    value: bool
    """The value on which to trigger."""
