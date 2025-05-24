"""Alarms and sleep

Provides alarms that trigger based on time intervals or on external events, such as pin
changes.
The program can simply wait for these alarms, or go to sleep and be awoken when they trigger.

There are two supported levels of sleep: light sleep and deep sleep.

Light sleep keeps sufficient state so the program can resume after sleeping.
It does not shut down WiFi, BLE, or other communications, or ongoing activities such
as audio playback. It reduces power consumption to the extent possible that leaves
these continuing activities running. In some cases there may be no decrease in power consumption.

Deep sleep shuts down power to nearly all of the microcontroller including the CPU and RAM. This can save
a more significant amount of power, but CircuitPython must restart ``code.py`` from the beginning when
awakened.

For both light sleep and deep sleep, if CircuitPython is connected to a host computer,
maintaining the connection takes priority and power consumption may not be reduced.

For more information about working with alarms and light/deep sleep in CircuitPython,
see `this Learn guide <https://learn.adafruit.com/deep-sleep-with-circuitpython>`_.
"""

from __future__ import annotations

from typing import Optional, Sequence, overload

import circuitpython_typing
import digitalio
from circuitpython_typing import ReadableBuffer

sleep_memory: SleepMemory
"""Memory that persists during deep sleep.
This object is the sole instance of `alarm.SleepMemory`."""
wake_alarm: Optional[circuitpython_typing.Alarm]
"""The most recently triggered alarm. If CircuitPython was sleeping, the alarm that woke it from sleep.
If no alarm occurred since the last hard reset or soft restart, value is ``None``.
"""

def light_sleep_until_alarms(
    *alarms: circuitpython_typing.Alarm,
) -> circuitpython_typing.Alarm:
    """Go into a light sleep until awakened one of the alarms. The alarm causing the wake-up
    is returned, and is also available as `alarm.wake_alarm`.

    If no alarms are specified, return immediately.

    **If CircuitPython is connected to a host computer, the connection will be maintained,
    and the microcontroller may not actually go into a light sleep.**
    This allows the user to interrupt an existing program with ctrl-C,
    and to edit the files in CIRCUITPY, which would not be possible in true light sleep.
    Thus, to use light sleep and save significant power,
    it may be necessary to disconnect from the host.
    """
    ...

def exit_and_deep_sleep_until_alarms(
    *alarms: circuitpython_typing.Alarm,
    preserve_dios: Sequence[digitalio.DigitalInOut] = (),
) -> None:
    """Exit the program and go into a deep sleep, until awakened by one of the alarms.
    This function does not return.

    When awakened, the microcontroller will restart and will run ``boot.py`` and ``code.py``
    from the beginning.

    After restart, an alarm *equivalent* to the one that caused the wake-up
    will be available as `alarm.wake_alarm`.
    Its type and/or attributes may not correspond exactly to the original alarm.
    For time-base alarms, currently, an `alarm.time.TimeAlarm()` is created.

    If no alarms are specified, the microcontroller will deep sleep until reset.

    :param circuitpython_typing.Alarm alarms: the alarms that can wake the microcontroller.
    :param Sequence[digitalio.DigitalInOut] preserve_dios: A sequence of `DigitalInOut` objects
      whose state should be preserved during deep sleep.
      If a `DigitalInOut` in the sequence is set to be an output,
      its current `DigitalInOut.value` (``True`` or ``False``)
      will be preserved during the deep sleep.
      If a `DigitalInOut` in the sequence is set to be an input,
      its current `DigitalInOut.pull` value (``DOWN``, ``UP``, or ``None``)
      will be preserved during deep sleep.

    Preserving `DigitalInOut` states during deep sleep can be used to ensure that
    external or on-board devices are powered or unpowered during sleep, among other purposes.

    On some microcontrollers, some pins cannot remain in their original state for hardware reasons.

    **Limitations:** ``preserve_dios`` is currently only available on Espressif.

    .. note::
      On Espressif chips, preserving pin settings during deep sleep may consume extra current.
      On ESP32, this was measured to be 250 uA or more.
      Consider not preserving pins unless you need to.
      Measure power consumption carefully both with no pins preserved and with the pins you might want to
      preserve to achieve the lowest consumption.

    **If CircuitPython is connected to a host computer via USB or BLE
    the first time a deep sleep is requested,
    the connection will be maintained and the system will not go into deep sleep.**
    This allows the user to interrupt an existing program with ctrl-C,
    and to edit the files in CIRCUITPY, which would not be possible in true deep sleep.

    If CircuitPython goes into a true deep sleep, and USB or BLE is reconnected,
    the next deep sleep will still be a true deep sleep. You must do a hard reset
    or power-cycle to exit a true deep sleep loop.

    Here is a skeletal example:

    .. code-block:: python

        import alarm
        import time
        import board

        print("Waking up")

        # Create an alarm for 60 seconds from now, and also a pin alarm.
        time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60)
        pin_alarm = alarm.pin.PinAlarm(board.D7, False)

        # Deep sleep until one of the alarm goes off. Then restart the program.
        alarm.exit_and_deep_sleep_until_alarms(time_alarm, pin_alarm)
    """
    ...

class SleepMemory:
    """Store raw bytes in RAM that persists during deep sleep.
    The class acts as a ``bytearray``.
    If power is lost, the memory contents are lost.

    Note that this class can't be imported and used directly. The sole
    instance of :class:`SleepMemory` is available at
    :attr:`alarm.sleep_memory`.

    **Limitations:** Not supported on RP2040.

    Usage::

       import alarm
       alarm.sleep_memory[0] = True
       alarm.sleep_memory[1] = 12
    """

    def __init__(self) -> None:
        """Not used. Access the sole instance through `alarm.sleep_memory`."""
        ...

    def __bool__(self) -> bool:
        """``sleep_memory`` is ``True`` if its length is greater than zero.
        This is an easy way to check for its existence.
        """
        ...

    def __len__(self) -> int:
        """Return the length. This is used by (`len`)"""
        ...

    @overload
    def __getitem__(self, index: slice) -> bytearray: ...
    @overload
    def __getitem__(self, index: int) -> int:
        """Returns the value at the given index."""
        ...

    @overload
    def __setitem__(self, index: slice, value: ReadableBuffer) -> None: ...
    @overload
    def __setitem__(self, index: int, value: int) -> None:
        """Set the value at the given index."""
        ...
