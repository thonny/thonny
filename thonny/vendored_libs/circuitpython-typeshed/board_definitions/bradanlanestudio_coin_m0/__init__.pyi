# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Bradán Lane STUDIO Coin M0
 - port: atmel-samd
 - board_id: bradanlanestudio_coin_m0
 - NVM size: 256
 - Included modules: analogio, array, audiocore, audioio, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, neopixel_write, nvm, os, pwmio, rainbowio, random, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid
 - Frozen libraries: adafruit_hid, neopixel
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
D9: microcontroller.Pin  # PA07
NEOPIXEL: microcontroller.Pin  # PA07
D10: microcontroller.Pin  # PA18
D11: microcontroller.Pin  # PA16
D12: microcontroller.Pin  # PA19
LED: microcontroller.Pin  # PA17
D13: microcontroller.Pin  # PA17
A0: microcontroller.Pin  # PA02
SPEAKER: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PB08
TOUCH2: microcontroller.Pin  # PB08
A2: microcontroller.Pin  # PB09
TOUCH1: microcontroller.Pin  # PB09
A5: microcontroller.Pin  # PB02
TOUCH3: microcontroller.Pin  # PB02


# Members:

# Unmapped:
#   none
