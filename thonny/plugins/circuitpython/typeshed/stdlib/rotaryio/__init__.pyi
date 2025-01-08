"""Support for reading rotation sensors

The `rotaryio` module contains classes to read different rotation encoding schemes. See
`Wikipedia's Rotary Encoder page <https://en.wikipedia.org/wiki/Rotary_encoder>`_ for more
background.

For more information on working with rotary encoders using this library, see
`this Learn Guide <https://learn.adafruit.com/rotary-encoder>`_.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info."""

from __future__ import annotations

import microcontroller

class IncrementalEncoder:
    """IncrementalEncoder determines the relative rotational position based on two series of pulses.
    It assumes that the encoder's common pin(s) are connected to ground,and enables pull-ups on
    pin_a and pin_b."""

    def __init__(
        self, pin_a: microcontroller.Pin, pin_b: microcontroller.Pin, divisor: int = 4
    ) -> None:
        """Create an IncrementalEncoder object associated with the given pins. It tracks the positional
        state of an incremental rotary encoder (also known as a quadrature encoder.) Position is
        relative to the position when the object is constructed.

        :param ~microcontroller.Pin pin_a: First pin to read pulses from.
        :param ~microcontroller.Pin pin_b: Second pin to read pulses from.
        :param int divisor: The divisor of the quadrature signal.

        For example::

          import rotaryio
          import time
          from board import *

          enc = rotaryio.IncrementalEncoder(D1, D2)
          last_position = None
          while True:
              position = enc.position
              if last_position == None or position != last_position:
                  print(position)
              last_position = position"""
        ...

    def deinit(self) -> None:
        """Deinitializes the IncrementalEncoder and releases any hardware resources for reuse."""
        ...

    def __enter__(self) -> IncrementalEncoder:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    divisor: int
    """The divisor of the quadrature signal.  Use 1 for encoders without
    detents, or encoders with 4 detents per cycle.  Use 2 for encoders with 2
    detents per cycle.  Use 4 for encoders with 1 detent per cycle."""
    position: int
    """The current position in terms of pulses. The number of pulses per rotation is defined by the
    specific hardware and by the divisor."""
