"""Analog Buffered IO Hardware Support

The `analogbufio` module contains classes to provide access to analog-to-digital
conversion and digital-to-analog (DAC) for multiple value transfer.

All classes change hardware state and should be deinitialized when they
are no longer needed if the program continues after use. To do so, either
call :py:meth:`!deinit` or use a context manager. See
:ref:`lifetime-and-contextmanagers` for more info.

TODO: For the essentials of `analogbufio`, see the `CircuitPython Essentials
Learn guide <https://learn.adafruit.com/circuitpython-essentials/circuitpython-analogbufio>`_

TODO: For more information on using `analogbufio`, see `this additional Learn guide
<https://learn.adafruit.com/circuitpython-advanced-analog-inputs-and-outputs>`_
"""

from __future__ import annotations

import microcontroller
from circuitpython_typing import WriteableBuffer

class BufferedIn:
    """Capture multiple analog voltage levels to the supplied buffer

    Usage::

        import board
        import analogbufio
        import array

        length = 1000
        mybuffer = array.array("H", [0x0000] * length)
        rate = 500000
        adcbuf = analogbufio.BufferedIn(board.GP26, sample_rate=rate)
        adcbuf.readinto(mybuffer)
        adcbuf.deinit()
        for i in range(length):
            print(i, mybuffer[i])

        (TODO) The reference voltage varies by platform so use
        ``reference_voltage`` to read the configured setting.
        (TODO) Provide mechanism to read CPU Temperature."""

    def __init__(self, pin: microcontroller.Pin, *, sample_rate: int) -> None:
        """Create a `BufferedIn` on the given pin and given sample rate.

        :param ~microcontroller.Pin pin: the pin to read from
        :param ~int sample_rate: rate: sampling frequency, in samples per second"""
        ...
    def deinit(self) -> None:
        """Shut down the `BufferedIn` and release the pin for other use."""
        ...
    def __enter__(self) -> BufferedIn:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    def readinto(self, buffer: WriteableBuffer) -> int:
        """Fills the provided buffer with ADC voltage values.

        ADC values will be read into the given buffer at the supplied sample_rate.
        Depending on the buffer typecode, 'B', 'H', samples are 8-bit byte-arrays or
        16-bit half-words and are always unsigned.
        The ADC most significant bits of the ADC are kept. (See
        https://docs.circuitpython.org/en/latest/docs/library/array.html)

        :param ~circuitpython_typing.WriteableBuffer buffer: buffer: A buffer for samples
        """
        ...
