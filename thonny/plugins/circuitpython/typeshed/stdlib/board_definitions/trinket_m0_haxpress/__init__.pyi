# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Trinket M0 Haxpress
 - port: atmel-samd
 - board_id: trinket_m0_haxpress
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, audiobusio, audiocore, audioio, board, builtins, busdisplay, busio, busio.SPI, busio.UART, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, i2cdisplaybus, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, paralleldisplaybus, pulseio, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, terminalio, time, touchio, usb_cdc, usb_hid, usb_midi, warnings
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # PA08
A2: microcontroller.Pin  # PA08
SDA: microcontroller.Pin  # PA08
D1: microcontroller.Pin  # PA02
A0: microcontroller.Pin  # PA02
D2: microcontroller.Pin  # PA09
A1: microcontroller.Pin  # PA09
SCL: microcontroller.Pin  # PA09
MISO: microcontroller.Pin  # PA09
D4: microcontroller.Pin  # PA06
A4: microcontroller.Pin  # PA06
TX: microcontroller.Pin  # PA06
MOSI: microcontroller.Pin  # PA06
D3: microcontroller.Pin  # PA07
A3: microcontroller.Pin  # PA07
RX: microcontroller.Pin  # PA07
SCK: microcontroller.Pin  # PA07
LED: microcontroller.Pin  # PA10
D13: microcontroller.Pin  # PA10
APA102_MOSI: microcontroller.Pin  # PA00
DOTSTAR_DATA: microcontroller.Pin  # PA00
APA102_SCK: microcontroller.Pin  # PA01
DOTSTAR_CLOCK: microcontroller.Pin  # PA01


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
