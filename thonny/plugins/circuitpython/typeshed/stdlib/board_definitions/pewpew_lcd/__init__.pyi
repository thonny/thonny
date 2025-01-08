# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PewPew LCD
 - port: atmel-samd
 - board_id: pewpew_lcd
 - NVM size: 256
 - Included modules: analogio, array, board, builtins, busdisplay, busio, busio.SPI, busio.UART, collections, digitalio, displayio, fontio, fourwire, keypad, keypad.Keys, math, microcontroller, neopixel_write, os, random, storage, struct, supervisor, sys, terminalio, time, usb_cdc
 - Frozen libraries: pew
"""

# Imports
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
SCK: microcontroller.Pin  # PA23
MOSI: microcontroller.Pin  # PA22
CS: microcontroller.Pin  # PA17
RST: microcontroller.Pin  # PA18
DC: microcontroller.Pin  # PA19
UP: microcontroller.Pin  # PA14
DOWN: microcontroller.Pin  # PA10
LEFT: microcontroller.Pin  # PA11
RIGHT: microcontroller.Pin  # PA09
O: microcontroller.Pin  # PA16
X: microcontroller.Pin  # PA15
P1: microcontroller.Pin  # PA30
P2: microcontroller.Pin  # PA31
P3: microcontroller.Pin  # PA00
P4: microcontroller.Pin  # PA01
P5: microcontroller.Pin  # PA02
P6: microcontroller.Pin  # PA03
P7: microcontroller.Pin  # PA04


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
