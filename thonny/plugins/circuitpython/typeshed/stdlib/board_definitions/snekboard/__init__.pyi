# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for keithp.com snekboard
 - port: atmel-samd
 - board_id: snekboard
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, audiobusio, audiocore, audioio, board, builtins, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, i2cdisplaybus, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, paralleldisplaybus, pulseio, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, terminalio, time, touchio, usb_cdc, usb_hid, usb_midi, warnings
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A1: microcontroller.Pin  # PB08
RX: microcontroller.Pin  # PB08
A2: microcontroller.Pin  # PB09
TX: microcontroller.Pin  # PB09
A3: microcontroller.Pin  # PA06
A4: microcontroller.Pin  # PA07
A5: microcontroller.Pin  # PA08
SCL: microcontroller.Pin  # PA08
A6: microcontroller.Pin  # PA09
SDA: microcontroller.Pin  # PA09
A7: microcontroller.Pin  # PA10
A8: microcontroller.Pin  # PA11
POWER1: microcontroller.Pin  # PA12
DIR1: microcontroller.Pin  # PA16
POWER2: microcontroller.Pin  # PA13
DIR2: microcontroller.Pin  # PA17
POWER3: microcontroller.Pin  # PA18
DIR3: microcontroller.Pin  # PA20
POWER4: microcontroller.Pin  # PA19
DIR4: microcontroller.Pin  # PA21
NEOPIXEL: microcontroller.Pin  # PB11


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
