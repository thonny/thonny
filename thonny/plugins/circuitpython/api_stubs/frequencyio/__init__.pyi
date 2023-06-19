"""Support for frequency based protocols

.. warning:: This module is not available in SAMD21 builds. See the
  :ref:`module-support-matrix` for more info.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

For example::

  import time
  import frequencyio
  import board

  frequency = frequencyio.FrequencyIn(board.D11)
  frequency.capture_period = 15
  time.sleep(0.1)

This example will initialize the the device, set
:py:data:`~frequencyio.FrequencyIn.capture_period`, and then sleep 0.1 seconds.
CircuitPython will automatically turn off FrequencyIn capture when it resets all
hardware after program completion. Use ``deinit()`` or a ``with`` statement
to do it yourself."""

from __future__ import annotations

import microcontroller

class FrequencyIn:
    """Read a frequency signal

    FrequencyIn is used to measure the frequency, in hertz, of a digital signal
    on an incoming pin. Accuracy has shown to be within 10%, if not better. It
    is recommended to utilize an average of multiple samples to smooth out readings.

    Frequencies below 1KHz are not currently detectable.

    FrequencyIn will not determine pulse width (use ``PulseIn``)."""

    def __init__(self, pin: microcontroller.Pin, capture_period: int = 10) -> None:
        """Create a FrequencyIn object associated with the given pin.

        :param ~microcontroller.Pin pin: Pin to read frequency from.
        :param int capture_period: Keyword argument to set the measurement period, in
                                   milliseconds. Default is 10ms; range is 1ms - 500ms.

        Read the incoming frequency from a pin::

          import frequencyio
          import board

          frequency = frequencyio.FrequencyIn(board.D11)

          # Loop while printing the detected frequency
          while True:
              print(frequency.value)

              # Optional clear() will reset the value
              # to zero. Without this, if the incoming
              # signal stops, the last reading will remain
              # as the value.
              frequency.clear()"""
        ...
    def deinit(self) -> None:
        """Deinitialises the FrequencyIn and releases any hardware resources for reuse."""
        ...
    def __enter__(self) -> FrequencyIn:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    def pause(self) -> None:
        """Pause frequency capture."""
        ...
    def resume(self) -> None:
        """Resumes frequency capture."""
        ...
    def clear(self) -> None:
        """Clears the last detected frequency capture value."""
        ...
    capture_period: int
    """The capture measurement period. Lower incoming frequencies will be measured
    more accurately with longer capture periods. Higher frequencies are more
    accurate with shorter capture periods.

    .. note:: When setting a new ``capture_period``, all previous capture information is
              cleared with a call to ``clear()``."""
    def __get__(self, index: int) -> int:
        """Returns the value of the last frequency captured."""
        ...
