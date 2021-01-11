"""Support for reading rotation sensors

The `rotaryio` module contains classes to read different rotation encoding schemes. See
`Wikipedia's Rotary Encoder page <https://en.wikipedia.org/wiki/Rotary_encoder>`_ for more
background.
.. warning:: This module is not available in some SAMD21 (aka M0) builds. See the :ref:`module-support-matrix` for more info.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info."""

class IncrementalEncoder:
    """IncrementalEncoder determines the relative rotational position based on two series of pulses."""

    def __init__(self, pin_a: microcontroller.Pin, pin_b: microcontroller.Pin):
        """Create an IncrementalEncoder object associated with the given pins. It tracks the positional
        state of an incremental rotary encoder (also known as a quadrature encoder.) Position is
        relative to the position when the object is constructed.

        :param ~microcontroller.Pin pin_a: First pin to read pulses from.
        :param ~microcontroller.Pin pin_b: Second pin to read pulses from.

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

    def deinit(self, ) -> Any:
        """Deinitializes the IncrementalEncoder and releases any hardware resources for reuse."""
        ...

    def __enter__(self, ) -> Any:
        """No-op used by Context Managers."""
        ...

    def __exit__(self, ) -> Any:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...

    position: Any = ...
    """The current position in terms of pulses. The number of pulses per rotation is defined by the
    specific hardware."""

