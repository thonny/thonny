# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for CP Sapling M0 w/ SPI Flash
 - port: atmel-samd
 - board_id: cp_sapling_m0_spiflash
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, board, builtins, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, i2cdisplaybus, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, paralleldisplaybus, pulseio, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, terminalio, time, touchio, usb_cdc, usb_hid, usb_midi, warnings
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D5: microcontroller.Pin  # PA08
SDA: microcontroller.Pin  # PA08
D10: microcontroller.Pin  # PA00
A4: microcontroller.Pin  # PA00
D11: microcontroller.Pin  # PA01
A5: microcontroller.Pin  # PA01
D4: microcontroller.Pin  # PA09
SCL: microcontroller.Pin  # PA09
D0: microcontroller.Pin  # PA22
A0: microcontroller.Pin  # PA22
SS: microcontroller.Pin  # PA22
D3: microcontroller.Pin  # PA19
A3: microcontroller.Pin  # PA19
SCK: microcontroller.Pin  # PA19
D1: microcontroller.Pin  # PA17
A1: microcontroller.Pin  # PA17
MISO: microcontroller.Pin  # PA17
D2: microcontroller.Pin  # PA18
A2: microcontroller.Pin  # PA18
MOSI: microcontroller.Pin  # PA18
NEOPIXEL: microcontroller.Pin  # PA15


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
