"""Analog hardware support

The `analogio` module contains classes to provide access to analog IO
typically implemented with digital-to-analog (DAC) and analog-to-digital
(ADC) converters.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

For example::

  import analogio
  from board import *

  pin = analogio.AnalogIn(A0)
  print(pin.value)
  pin.deinit()

This example will initialize the the device, read
:py:data:`~analogio.AnalogIn.value` and then
:py:meth:`~analogio.AnalogIn.deinit` the hardware. The last step is optional
because CircuitPython will do it automatically after the program finishes."""

from __future__ import annotations

import microcontroller

class AnalogIn:
    """Read analog voltage levels

    Usage::

       import analogio
       from board import *

       adc = analogio.AnalogIn(A1)
       val = adc.value"""

    def __init__(self, pin: microcontroller.Pin) -> None:
        """Use the AnalogIn on the given pin. The reference voltage varies by
        platform so use ``reference_voltage`` to read the configured setting.

        :param ~microcontroller.Pin pin: the pin to read from"""
        ...
    def deinit(self) -> None:
        """Turn off the AnalogIn and release the pin for other use."""
        ...
    def __enter__(self) -> AnalogIn:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    value: int
    """The value on the analog pin between 0 and 65535 inclusive (16-bit). (read-only)

    Even if the underlying analog to digital converter (ADC) is lower
    resolution, the value is 16-bit."""

    reference_voltage: float
    """The maximum voltage measurable (also known as the reference voltage) as a
    `float` in Volts.  Note the ADC value may not scale to the actual voltage linearly
    at ends of the analog range."""

class AnalogOut:
    """Output analog values (a specific voltage).

    Example usage::

        import analogio
        from board import *

        dac = analogio.AnalogOut(A2)                # output on pin A2
        dac.value = 32768                           # makes A2 1.65V"""

    def __init__(self, pin: microcontroller.Pin) -> None:
        """Use the AnalogOut on the given pin.

        :param ~microcontroller.Pin pin: the pin to output to"""
        ...
    def deinit(self) -> None:
        """Turn off the AnalogOut and release the pin for other use."""
        ...
    def __enter__(self) -> AnalogOut:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    value: int
    """The value on the analog pin between 0 and 65535 inclusive (16-bit). (write-only)

    Even if the underlying digital to analog converter (DAC) is lower
    resolution, the value is 16-bit."""
