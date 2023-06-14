from __future__ import annotations

class CywPin:
    """A class that represents a GPIO pin attached to the wifi chip.

    Cannot be constructed at runtime, but may be the type of a pin object
    in :py:mod:`board`. A `CywPin` can be used as a DigitalInOut, but not with other
    peripherals such as `PWMOut`."""

PM_STANDARD: int
"""The standard power management mode"""
PM_AGGRESSIVE: int
"""Aggressive power management mode for optimal power usage at the cost of performance"""
PM_PERFORMANCE: int
"""Performance power management mode where more power is used to increase performance"""
PM_DISABLED: int
"""Disable power management and always use highest power mode. CircuitPython sets this value at reset time, because it provides the best connectivity reliability."""

def set_power_management(value: int) -> None:
    """Set the power management register

    For transmitter power, see ``wifi.Radio.txpower``.
    This controls software power saving features inside the cyw43 chip.
    it does not control transmitter power.

    The value is interpreted as a 24-bit hexadecimal number of the form
    ``0x00adbrrm``.

    The low 4 bits, ``m``, are the power management mode:
     * 0: disabled
     * 1: aggressive power saving which reduces wifi throughput
     * 2: Power saving with high throughput

    The next 8 bits, ``r``, specify "the maximum time to wait before going back to sleep" for power management mode 2. The units of ``r`` are 10ms.

    The next 4 bits, ``b``, are the "wake period is measured in beacon periods".

    The next 4 bits, ``d``, specify the "wake interval measured in DTIMs. If this is set to 0, the wake interval is measured in beacon periods".

    The top 4 bits, ``a``, specifies the "wake interval sent to the access point"

    Several ``PM_`` constants gathered from various sources are included
    in this module.  According to Raspberry Pi documentation, the value 0xa11140
    (called `cyw43.PM_DISABLED` here) increases responsiveness at the cost of higher power
    usage.
    """

def get_power_management() -> int:
    """Retrieve the power management register"""
