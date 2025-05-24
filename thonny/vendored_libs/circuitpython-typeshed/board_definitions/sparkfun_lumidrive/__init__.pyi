# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SparkFun LUMIDrive
 - port: atmel-samd
 - board_id: sparkfun_lumidrive
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, board, builtins, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, i2cdisplaybus, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, paralleldisplaybus, pulseio, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, terminalio, time, touchio, usb_cdc, usb_hid, usb_midi, warnings
 - Frozen libraries: adafruit_dotstar
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A3: microcontroller.Pin  # PA04
A4: microcontroller.Pin  # PA05
SCK: microcontroller.Pin  # PA19
MOSI: microcontroller.Pin  # PA18
D6: microcontroller.Pin  # PA20
D8: microcontroller.Pin  # PA06
D9: microcontroller.Pin  # PA07
D10: microcontroller.Pin  # PA18
D13: microcontroller.Pin  # PA17
LED: microcontroller.Pin  # PA17


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
