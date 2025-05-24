# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Rotary Trinkey M0
 - port: atmel-samd
 - board_id: adafruit_rotary_trinkey_m0
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, array, board, builtins, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, rainbowio, random, rotaryio, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: adafruit_hid, neopixel
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
NEOPIXEL: microcontroller.Pin  # PA01
ROTA: microcontroller.Pin  # PA04
ROTB: microcontroller.Pin  # PA00
SWITCH: microcontroller.Pin  # PA27
TOUCH: microcontroller.Pin  # PA06


# Members:

# Unmapped:
#   none
