"""Basic digital pin support

The `digitalio` module contains classes to provide access to basic digital IO.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

For example::

  import digitalio
  import board

  pin = digitalio.DigitalInOut(board.LED)
  print(pin.value)

This example will initialize the the device, read
:py:data:`~digitalio.DigitalInOut.value` and then
:py:meth:`~digitalio.DigitalInOut.deinit` the hardware.

Here is blinky::

  import time
  import digitalio
  import board

  led = digitalio.DigitalInOut(board.LED)
  led.direction = digitalio.Direction.OUTPUT
  while True:
      led.value = True
      time.sleep(0.1)
      led.value = False
      time.sleep(0.1)

For the essentials of `digitalio`, see the `CircuitPython Essentials
Learn guide <https://learn.adafruit.com/circuitpython-essentials/circuitpython-digital-in-out>`_

For more information on using `digitalio`, see `this additional Learn guide
<https://learn.adafruit.com/circuitpython-digital-inputs-and-outputs>`_

.. warning:: `digitalio.DigitalInOut` on Raspberry Pi RP2350 A2 stepping has some limitations
   due to a GPIO hardware issue that causes excessive leakage current (~120uA).
   A pin can read as high even when driven or pulled low, if the input signal is high
   impedance or if an attached pull-down resistor is too weak (has too high a value).

   To prevent this problem, drive the the input pin with a strong signal that can overcome
   the leakage current. If you need to use a pull-down,
   connect a strong external pull-down resistor that is 8.2k ohms or less.

   The internal pull-down resistor (``digitalio.DigitalInOut.pull = digitalio.Pull.DOWN``)
   is not strong enough, and is not useful.

   Typical push-pull outputs from attached peripherals or other microcontrollers will drive
   input pins adequately, with no resistor needed.

   There is no problem when pull-ups are used, even weak ones. Using the internal pull-up resistor
   (``digitalioDigitalInOut.pull = digitalio.Pull.UP``) will work fine.

   For more information, see the RP2350-E9 erratum in the
   `RP2350 datasheet <https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf>`_
"""

from __future__ import annotations

from typing import Optional

import microcontroller

class DriveMode:
    """Defines the drive mode of a digital pin"""

    def __init__(self) -> None:
        """Enum-like class to define the drive mode used when outputting
        digital values."""
        ...
    PUSH_PULL: DriveMode
    """Output both high and low digital values"""

    OPEN_DRAIN: DriveMode
    """Output low digital values but go into high z for digital high. This is
    useful for i2c and other protocols that share a digital line."""

class DigitalInOut:
    """Digital input and output

    A DigitalInOut is used to digitally control I/O pins. For analog control of
    a pin, see the :py:class:`analogio.AnalogIn` and
    :py:class:`analogio.AnalogOut` classes."""

    def __init__(self, pin: microcontroller.Pin) -> None:
        """Create a new DigitalInOut object associated with the pin. Defaults to input
        with no pull. Use :py:meth:`switch_to_input` and
        :py:meth:`switch_to_output` to change the direction.

        :param ~microcontroller.Pin pin: The pin to control"""
        ...

    def deinit(self) -> None:
        """Turn off the DigitalInOut and release the pin for other use."""
        ...

    def __enter__(self) -> DigitalInOut:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    def switch_to_output(
        self, value: bool = False, drive_mode: DriveMode = DriveMode.PUSH_PULL
    ) -> None:
        """Set the drive mode and value and then switch to writing out digital
        values.

        :param bool value: default value to set upon switching
        :param ~digitalio.DriveMode drive_mode: drive mode for the output
        """
        ...

    def switch_to_input(self, pull: Optional[Pull] = None) -> None:
        """Set the pull and then switch to read in digital values.

        :param Pull pull: pull configuration for the input

        Example usage::

          import digitalio
          import board

          switch = digitalio.DigitalInOut(board.SLIDE_SWITCH)
          switch.switch_to_input(pull=digitalio.Pull.UP)
          # Or, after switch_to_input
          switch.pull = digitalio.Pull.UP
          print(switch.value)"""
        ...
    direction: Direction
    """The direction of the pin.

    Setting this will use the defaults from the corresponding
    :py:meth:`switch_to_input` or :py:meth:`switch_to_output` method. If
    you want to set pull, value or drive mode prior to switching, then use
    those methods instead."""
    value: bool
    """The digital logic level of the pin."""
    drive_mode: DriveMode
    """The pin drive mode. One of:

    - `digitalio.DriveMode.PUSH_PULL`
    - `digitalio.DriveMode.OPEN_DRAIN`"""
    pull: Optional[Pull]
    """The pin pull direction. One of:

    - `digitalio.Pull.UP`
    - `digitalio.Pull.DOWN`
    - `None`

    :raises AttributeError: if `direction` is :py:data:`~digitalio.Direction.OUTPUT`."""

class Direction:
    """Defines the direction of a digital pin"""

    def __init__(self) -> None:
        """Enum-like class to define which direction the digital values are
        going."""
        ...
    INPUT: Direction
    """Read digital data in"""

    OUTPUT: Direction
    """Write digital data out"""

class Pull:
    """Defines the pull of a digital input pin"""

    def __init__(self) -> None:
        """Enum-like class to define the pull value, if any, used while reading
        digital values in."""
        ...
    UP: Pull
    """When the input line isn't being driven the pull up can pull the state
    of the line high so it reads as true."""

    DOWN: Pull
    """When the input line isn't being driven the pull down can pull the
    state of the line low so it reads as false."""
