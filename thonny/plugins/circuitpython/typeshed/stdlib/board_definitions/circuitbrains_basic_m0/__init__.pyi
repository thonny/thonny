# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for CircuitBrains Basic
 - port: atmel-samd
 - board_id: circuitbrains_basic_m0
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
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA06
TX: microcontroller.Pin  # PA06
A2: microcontroller.Pin  # PA07
RX: microcontroller.Pin  # PA07
A3: microcontroller.Pin  # PA08
D0: microcontroller.Pin  # PA00
D1: microcontroller.Pin  # PA01
D2: microcontroller.Pin  # PA28
D3: microcontroller.Pin  # PA27
D4: microcontroller.Pin  # PA23
D5: microcontroller.Pin  # PA22
D6: microcontroller.Pin  # PA15
D7: microcontroller.Pin  # PA14
LED: microcontroller.Pin  # PA14
STATUS_LED: microcontroller.Pin  # PA14
SDA: microcontroller.Pin  # PA04
SCL: microcontroller.Pin  # PA05
SCK: microcontroller.Pin  # PA11
MOSI: microcontroller.Pin  # PA10
MISO: microcontroller.Pin  # PA09


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
