# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit NeoKey Trinkey M0
 - port: atmel-samd
 - board_id: adafruit_neokey_trinkey_m0
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, array, board, builtins, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, rainbowio, random, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi
 - Frozen libraries: adafruit_hid, neopixel
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
TOUCH: microcontroller.Pin  # PA07
NEOPIXEL: microcontroller.Pin  # PA15
SWITCH: microcontroller.Pin  # PA28


# Members:

# Unmapped:
#   none
