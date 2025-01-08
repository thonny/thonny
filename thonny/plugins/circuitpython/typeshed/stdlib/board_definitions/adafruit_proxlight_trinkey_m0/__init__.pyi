# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit ProxLight Trinkey M0
 - port: atmel-samd
 - board_id: adafruit_proxlight_trinkey_m0
 - NVM size: 256
 - Included modules: adafruit_bus_device, adafruit_pixelbuf, array, board, builtins, busio, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, rainbowio, random, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: adafruit_apds9960, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
INTERRUPT: microcontroller.Pin  # PA00
TOUCH2: microcontroller.Pin  # PA03
TOUCH1: microcontroller.Pin  # PA07
NEOPIXEL: microcontroller.Pin  # PA15
SDA: microcontroller.Pin  # PA16
SCL: microcontroller.Pin  # PA17


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
