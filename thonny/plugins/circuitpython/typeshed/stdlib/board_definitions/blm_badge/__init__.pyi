# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit BLM Badge
 - port: atmel-samd
 - board_id: blm_badge
 - NVM size: 256
 - Included modules: analogio, array, audiobusio, audiocore, audioio, board, builtins, busio, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, rainbowio, random, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
RX: microcontroller.Pin  # PA01
SCL: microcontroller.Pin  # PA01
D6: microcontroller.Pin  # PA01
TX: microcontroller.Pin  # PA00
SDA: microcontroller.Pin  # PA00
D5: microcontroller.Pin  # PA00
CAP1: microcontroller.Pin  # PA02
D1: microcontroller.Pin  # PA02
A0: microcontroller.Pin  # PA02
CAP2: microcontroller.Pin  # PA04
D2: microcontroller.Pin  # PA04
A1: microcontroller.Pin  # PA04
CAP3: microcontroller.Pin  # PA06
D3: microcontroller.Pin  # PA06
A2: microcontroller.Pin  # PA06
CAP4: microcontroller.Pin  # PA07
D4: microcontroller.Pin  # PA07
A3: microcontroller.Pin  # PA07
NEOPIXEL: microcontroller.Pin  # PA05
D14: microcontroller.Pin  # PA05
MICROPHONE_CLOCK: microcontroller.Pin  # PA10
D7: microcontroller.Pin  # PA10
MICROPHONE_DATA: microcontroller.Pin  # PA08
D0: microcontroller.Pin  # PA08
LIGHT: microcontroller.Pin  # PA11
A4: microcontroller.Pin  # PA11
LED: microcontroller.Pin  # PA03
L: microcontroller.Pin  # PA03
D13: microcontroller.Pin  # PA03


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
