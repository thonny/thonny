# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for THUNDERPACK_v12
 - port: stm
 - board_id: thunderpack_v12
 - NVM size: Unknown
 - Included modules: _asyncio, _pixelmap, adafruit_pixelbuf, analogio, array, atexit, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_midi, warnings
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
PA0: microcontroller.Pin  # PA00
PA1: microcontroller.Pin  # PA01
PA2: microcontroller.Pin  # PA02
PA3: microcontroller.Pin  # PA03
PA4: microcontroller.Pin  # PA04
PA5: microcontroller.Pin  # PA05
PA6: microcontroller.Pin  # PA06
PA7: microcontroller.Pin  # PA07
PA8: microcontroller.Pin  # PA08
PA9: microcontroller.Pin  # PA09
PA10: microcontroller.Pin  # PA10
PA13: microcontroller.Pin  # PA13
PA14: microcontroller.Pin  # PA14
PB0: microcontroller.Pin  # PB00
PB5: microcontroller.Pin  # PB05
PB6: microcontroller.Pin  # PB06
PB7: microcontroller.Pin  # PB07
PB8: microcontroller.Pin  # PB08
LED1: microcontroller.Pin  # PA00
LED2: microcontroller.Pin  # PA01
LED3: microcontroller.Pin  # PA02
LED4: microcontroller.Pin  # PA03
BUTTON: microcontroller.Pin  # PB04
SCL: microcontroller.Pin  # PB06
SDA: microcontroller.Pin  # PB07
APA102_MOSI: microcontroller.Pin  # PB08
APA102_SCK: microcontroller.Pin  # PB00


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
