# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit TRRS Trinkey M0
 - port: atmel-samd
 - board_id: adafruit_trrs_trinkey_m0
 - NVM size: 256
 - Included modules: analogio, array, board, builtins, busio, collections, digitalio, keypad, keypad.Keys, math, microcontroller, neopixel_write, nvm, os, random, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: adafruit_hid
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
NEOPIXEL: microcontroller.Pin  # PA01
TIP: microcontroller.Pin  # PA02
TIP_SWITCH: microcontroller.Pin  # PA03
RING_2: microcontroller.Pin  # PA04
SLEEVE: microcontroller.Pin  # PA05
RING_1: microcontroller.Pin  # PA06
RING_1_SWITCH: microcontroller.Pin  # PA07
SCL: microcontroller.Pin  # PA09
SDA: microcontroller.Pin  # PA08


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
