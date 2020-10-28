"""Support for edge counting

The `countio` module contains logic to read and count edge transistions

.. warning:: This module is not available in some SAMD21 (aka M0) builds. See the
  :ref:`module-support-matrix` for more info.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info."""

class Counter:
    """Counter will keep track of the number of falling edge transistions (pulses) on a
       given pin"""

    def __init__(self, pin_a):
        """Create a Counter object associated with the given pin. It tracks the number of
           falling pulses relative when the object is constructed.

           :param ~microcontroller.Pin pin_a: Pin to read pulses from.


           For example::

               import countio
               import time
               from board import *

               pin_counter = countio.Counter(board.D1)
               #reset the count after 100 counts
               while True:
                   if pin_counter.count == 100:
                       pin_counter.reset()
                   print(pin_counter.count)"""

    def deinit(self):
        """Deinitializes the Counter and releases any hardware resources for reuse."""

    def __enter__(self):
        """No-op used by Context Managers."""

    def __exit__(self):
        """Automatically deinitializes the hardware when exiting a context. See
           :ref:`lifetime-and-contextmanagers` for more info."""

    count: int = ...
    """The current count in terms of pulses."""

    def reset(self):
        """Resets the count back to 0."""

