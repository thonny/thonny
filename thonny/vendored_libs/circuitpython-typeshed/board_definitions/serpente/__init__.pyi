# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Serpente
 - port: atmel-samd
 - board_id: serpente
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
D0: microcontroller.Pin  # PA04
D1: microcontroller.Pin  # PA05
D2: microcontroller.Pin  # PA06
D3: microcontroller.Pin  # PA07
D4: microcontroller.Pin  # PA08
D5: microcontroller.Pin  # PA09
A0: microcontroller.Pin  # PA04
A1: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PA06
A3: microcontroller.Pin  # PA07
A4: microcontroller.Pin  # PA08
A5: microcontroller.Pin  # PA09
LED_G: microcontroller.Pin  # PA19
LED_R: microcontroller.Pin  # PA22
LED_B: microcontroller.Pin  # PA23
MOSI: microcontroller.Pin  # PA04
MISO: microcontroller.Pin  # PA06
SCK: microcontroller.Pin  # PA05
SCL: microcontroller.Pin  # PA09
SDA: microcontroller.Pin  # PA08
RX: microcontroller.Pin  # PA09
TX: microcontroller.Pin  # PA08
RX2: microcontroller.Pin  # PA05
TX2: microcontroller.Pin  # PA04


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
