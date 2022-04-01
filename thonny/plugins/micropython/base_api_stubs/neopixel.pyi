"""
control of WS2812 / NeoPixel LEDs.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/neopixel.rst.
=====================================================

.. module:: neopixel
   :synopsis: control of WS2812 / NeoPixel LEDs

This module provides a driver for WS2818 / NeoPixel LEDs.

.. note:: This module is only included by default on the ESP8266 and ESP32
   ports. On STM32 / Pyboard, you can `download the module
   <https://github.com/micropython/micropython/blob/master/drivers/neopixel/neopixel.py>`_
   and copy it to the filesystem.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Final

from machine import Pin

_Color: Final = tuple[int, int, int] | tuple[int, int, int, int]

class NeoPixel:
    """
   This class stores pixel data for a WS2812 LED strip connected to a pin. The
   application should set pixel data and then call :meth:`NeoPixel.write`
   when it is ready to update the strip.
   
   For example::
   
       import neopixel
   
       # 32 LED strip connected to X8.
       p = machine.Pin.board.X8
       n = neopixel.NeoPixel(p, 32)
   
       # Draw a red gradient.
       for i in range(32):
           n[i] = (i * 8, 0, 0)
   
       # Update the strip.
       n.write()
   """

    def __init__(self, pin: Pin, n: int, /, *, bpp: int = 3, timing: int = 1):
        """
       Construct an NeoPixel object.  The parameters are:
       
           - *pin* is a machine.Pin instance.
           - *n* is the number of LEDs in the strip.
           - *bpp* is 3 for RGB LEDs, and 4 for RGBW LEDs.
           - *timing* is 0 for 400KHz, and 1 for 800kHz LEDs (most are 800kHz).
      """
    def fill(self, pixel: _Color, /) -> None:
        """
       Sets the value of all pixels to the specified *pixel* value (i.e. an
       RGB/RGBW tuple).
      """
    def __len__(self) -> int:
        """
       Returns the number of LEDs in the strip.
      """
    def __setitem__(self, index: int, val: _Color, /) -> None:
        """
       Set the pixel at *index* to the value, which is an RGB/RGBW tuple.
      """
    def __getitem__(self, index: int, /) -> _Color:
        """
       Returns the pixel at *index* as an RGB/RGBW tuple.
      """
    def write(self) -> None:
        """
       Writes the current pixel data to the strip.
      """
