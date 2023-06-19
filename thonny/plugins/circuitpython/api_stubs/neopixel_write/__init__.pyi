"""Low-level neopixel implementation

The `neopixel_write` module contains a helper method to write out bytes in
the 800khz neopixel protocol.

For example, to turn off a single neopixel (like the status pixel on Express
boards.)

.. code-block:: python

  import board
  import neopixel_write
  import digitalio

  pin = digitalio.DigitalInOut(board.NEOPIXEL)
  pin.direction = digitalio.Direction.OUTPUT
  pixel_off = bytearray([0, 0, 0])
  neopixel_write.neopixel_write(pin, pixel_off)

.. note::

    This module is typically not used by user level code.

    For more information on actually using NeoPixels, refer to the `CircuitPython
    Essentials Learn guide <https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel>`_

    For a much more thorough guide about using NeoPixels, refer to the `Adafruit NeoPixel Überguide
    <https://learn.adafruit.com/adafruit-neopixel-uberguide>`_.

"""

from __future__ import annotations

import digitalio
from circuitpython_typing import ReadableBuffer

def neopixel_write(digitalinout: digitalio.DigitalInOut, buf: ReadableBuffer) -> None:
    """Write buf out on the given DigitalInOut.

    :param ~digitalio.DigitalInOut digitalinout: the DigitalInOut to output with
    :param ~circuitpython_typing.ReadableBuffer buf: The bytes to clock out. No assumption is made about color order
    """
    ...
