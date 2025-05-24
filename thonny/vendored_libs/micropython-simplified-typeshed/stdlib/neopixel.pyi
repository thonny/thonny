"""Individually addressable RGB and RGBW LED strips.
"""
from .microbit import MicroBitDigitalPin
from typing import Tuple

class NeoPixel:
    def __init__(self, pin: MicroBitDigitalPin, n: int, bpp: int = 3) -> None:
        """Initialise a new strip of neopixel LEDs controlled via a pin.

        Example: ``np = neopixel.NeoPixel(pin0, 8)``

        To support RGBW neopixels, a third argument can be passed to
        ``NeoPixel`` to indicate the number of bytes per pixel (``bpp``).
        For RGBW, this is is 4 rather than the default of 3 for RGB and GRB.

        Each pixel is addressed by a position (starting from 0). Neopixels are
        given RGB (red, green, blue) / RGBW (red, green, blue, white) values
        between 0-255 as a tuple. For example, in RGB, ``(255,255,255)`` is
        white. In RGBW, ``(255,255,255,0)`` or ``(0,0,0,255)`` is white.

        See `the online docs <https://microbit-micropython.readthedocs.io/en/v2-docs/neopixel.html>`_ for warnings and other advice.

        :param pin: The pin controlling the neopixel strip.
        :param n: The number of neopixels in the strip.
        :param bpp: Bytes per pixel. For RGBW neopixel support, pass 4 rather than the default of 3 for RGB and GRB.
        """
        ...
    def clear(self) -> None:
        """Clear all the pixels.

        Example: ``np.clear()``
        """
        ...
    def show(self) -> None:
        """Show the pixels.

        Example: ``np.show()``

        Must be called for any updates to become visible.
        """
        ...
    def write(self) -> None:
        """Show the pixels (micro:bit V2 only).

        Example: ``np.write()``

        Must be called for any updates to become visible.

        Equivalent to ``show``.
        """
        ...
    def fill(self, colour: Tuple[int, ...]) -> None:
        """Colour all pixels a given RGB/RGBW value (micro:bit V2 only).

        Example: ``np.fill((0, 0, 255))``

        :param colour: A tuple of the same length as the number of bytes per pixel (bpp).

        Use in conjunction with ``show()`` to update the neopixels.
        """
        ...
    def __setitem__(self, key: int, value: Tuple[int, ...]) -> None:
        """Set a pixel colour.

        Example: ``np[0] = (255, 0, 0)``

        :param key: The pixel number.
        :param value: The colour.
        """
    def __getitem__(self, key: int) -> Tuple[int, ...]:
        """Get a pixel colour.

        Example: ``r, g, b = np[0]``

        :param key: The pixel number.
        :return: The colour tuple.
        """
    def __len__(self) -> int:
        """Get length of this pixel strip.

        Example: ``len(np)``
        """
