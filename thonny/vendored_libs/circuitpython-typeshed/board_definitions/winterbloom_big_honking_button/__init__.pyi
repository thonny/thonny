# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Winterbloom Big Honking Button
 - port: atmel-samd
 - board_id: winterbloom_big_honking_button
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, audiocore, audioio, board, builtins, busio, busio.SPI, busio.UART, codeop, collections, digitalio, errno, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, pulseio, pwmio, rainbowio, random, rotaryio, storage, struct, supervisor, sys, time, usb_cdc, warnings
 - Frozen libraries: 
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
BUTTON: microcontroller.Pin  # PA07
HONK_OUT: microcontroller.Pin  # PA02
GATE_OUT: microcontroller.Pin  # PA11
GATE_IN: microcontroller.Pin  # PA14
PITCH_IN: microcontroller.Pin  # PB08
V5: microcontroller.Pin  # PB10


# Members:

# Unmapped:
#   none
