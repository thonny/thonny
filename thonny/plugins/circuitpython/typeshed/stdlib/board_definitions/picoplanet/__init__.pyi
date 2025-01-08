# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PicoPlanet
 - port: atmel-samd
 - board_id: picoplanet
 - NVM size: 256
 - Included modules: analogio, array, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A1: microcontroller.Pin  # PA02
A0: microcontroller.Pin  # PA03
A2: microcontroller.Pin  # PA04
D5: microcontroller.Pin  # PA05
GREEN_LED: microcontroller.Pin  # PA05
D6: microcontroller.Pin  # PA06
RED_LED: microcontroller.Pin  # PA06
LED: microcontroller.Pin  # PA06
D7: microcontroller.Pin  # PA07
BLUE_LED: microcontroller.Pin  # PA07
D1: microcontroller.Pin  # PA08
A3: microcontroller.Pin  # PA08
SDA: microcontroller.Pin  # PA08
D2: microcontroller.Pin  # PA09
A4: microcontroller.Pin  # PA09
SCL: microcontroller.Pin  # PA09
D3: microcontroller.Pin  # PA16
MOSI: microcontroller.Pin  # PA16
D4: microcontroller.Pin  # PA17
SCK: microcontroller.Pin  # PA17
D8: microcontroller.Pin  # PA30
MISO: microcontroller.Pin  # PA30


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
