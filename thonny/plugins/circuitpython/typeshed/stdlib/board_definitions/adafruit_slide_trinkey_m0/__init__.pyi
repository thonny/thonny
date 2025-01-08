# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Slide Trinkey M0
 - port: atmel-samd
 - board_id: adafruit_slide_trinkey_m0
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, board, builtins, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, rainbowio, random, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: adafruit_hid, adafruit_simplemath, neopixel
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
NEOPIXEL: microcontroller.Pin  # PA04
POTENTIOMETER: microcontroller.Pin  # PA02
A0: microcontroller.Pin  # PA02
TOUCH: microcontroller.Pin  # PA07


# Members:

# Unmapped:
#   none
