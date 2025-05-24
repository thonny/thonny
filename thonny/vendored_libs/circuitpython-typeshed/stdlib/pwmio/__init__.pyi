"""Support for PWM based protocols

The `pwmio` module contains classes to provide access to basic pulse IO.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

For example::

  import time
  import pwmio
  import board

  pwm = pwmio.PWMOut(board.LED)
  pwm.duty_cycle = 2 ** 15
  time.sleep(0.1)

This example will initialize the the device, set
:py:data:`~pwmio.PWMOut.duty_cycle`, and then sleep 0.1 seconds.
CircuitPython will automatically turn off the PWM when it resets all
hardware after program completion. Use ``deinit()`` or a ``with`` statement
to do it yourself.

For the essentials of `pwmio`, see the `CircuitPython Essentials
Learn guide <https://learn.adafruit.com/circuitpython-essentials/circuitpython-pwm>`_.
"""

from __future__ import annotations

import microcontroller

class PWMOut:
    """Output a Pulse Width Modulated signal on a given pin.

    .. note:: The exact frequencies possible depend on the specific microcontroller.
      If the requested frequency is within the available range, one of the two
      nearest possible frequencies to the requested one is selected.

      If the requested frequency is outside the range, either (A) a ValueError
      may be raised or (B) the highest or lowest frequency is selected. This
      behavior is microcontroller-dependent, and may depend on whether it's the
      upper or lower bound that is exceeded.

      In any case, the actual frequency (rounded to 1Hz) is available in the
      ``frequency`` property after construction.

    .. note:: The frequency is calculated based on a nominal CPU frequency.
      However, depending on the board, the error between the nominal and
      actual CPU frequency can be large (several hundred PPM in the case of
      crystal oscillators and up to ten percent in the case of RC
      oscillators)

    """

    def __init__(
        self,
        pin: microcontroller.Pin,
        *,
        duty_cycle: int = 0,
        frequency: int = 500,
        variable_frequency: bool = False,
    ) -> None:
        """Create a PWM object associated with the given pin. This allows you to
        write PWM signals out on the given pin. Frequency is fixed after init
        unless ``variable_frequency`` is True.

        .. note:: When ``variable_frequency`` is True, further PWM outputs may be
          limited because it may take more internal resources to be flexible. So,
          when outputting both fixed and flexible frequency signals construct the
          fixed outputs first.

        :param ~microcontroller.Pin pin: The pin to output to
        :param int duty_cycle: The fraction of each pulse which is high. 16-bit
        :param int frequency: The target frequency in Hertz (32-bit)
        :param bool variable_frequency: True if the frequency will change over time


        Simple LED on::

          import pwmio
          import board

          pwm = pwmio.PWMOut(board.LED)

          while True:
              pwm.duty_cycle = 2 ** 15  # Cycles the pin with 50% duty cycle (half of 2 ** 16) at the default 500hz

        PWM LED fade::

          import pwmio
          import board

          pwm = pwmio.PWMOut(board.LED)  # output on LED pin with default of 500Hz

          while True:
              for cycle in range(0, 65535):  # Cycles through the full PWM range from 0 to 65535
                  pwm.duty_cycle = cycle  # Cycles the LED pin duty cycle through the range of values
              for cycle in range(65534, 0, -1):  # Cycles through the PWM range backwards from 65534 to 0
                  pwm.duty_cycle = cycle  # Cycles the LED pin duty cycle through the range of values

        PWM at specific frequency (servos and motors)::

          import pwmio
          import board

          pwm = pwmio.PWMOut(board.D13, frequency=50)
          pwm.duty_cycle = 2 ** 15  # Cycles the pin with 50% duty cycle (half of 2 ** 16) at 50hz

        Variable frequency (usually tones)::

          import pwmio
          import board
          import time

          pwm = pwmio.PWMOut(board.D13, duty_cycle=2 ** 15, frequency=440, variable_frequency=True)
          time.sleep(0.2)
          pwm.frequency = 880
          time.sleep(0.1)

        """
        ...

    def deinit(self) -> None:
        """Deinitialises the PWMOut and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> PWMOut:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    duty_cycle: int
    """16 bit value that dictates how much of one cycle is high (1) versus low
    (0). 0xffff will always be high, 0 will always be low and 0x7fff will
    be half high and then half low.

    Depending on how PWM is implemented on a specific board, the internal
    representation for duty cycle might have less than 16 bits of resolution.
    Reading this property will return the value from the internal representation,
    so it may differ from the value set."""
    frequency: int
    """32 bit value that dictates the PWM frequency in Hertz (cycles per
    second). Only writeable when constructed with ``variable_frequency=True``.

    Depending on how PWM is implemented on a specific board, the internal value
    for the PWM's duty cycle may need to be recalculated when the frequency
    changes. In these cases, the duty cycle is automatically recalculated
    from the original duty cycle value. This should happen without any need
    to manually re-set the duty cycle. However, an output glitch may occur during the adjustment.
    """
