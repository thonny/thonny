# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Keybow 2040
 - port: raspberrypi
 - board_id: pimoroni_keybow2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1
GP1: microcontroller.Pin  # GPIO1
INT: microcontroller.Pin  # GPIO3
SDA: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO5
SW0: microcontroller.Pin  # GPIO21
SW1: microcontroller.Pin  # GPIO20
SW2: microcontroller.Pin  # GPIO19
SW3: microcontroller.Pin  # GPIO18
SW4: microcontroller.Pin  # GPIO17
SW5: microcontroller.Pin  # GPIO16
SW6: microcontroller.Pin  # GPIO15
SW7: microcontroller.Pin  # GPIO14
SW8: microcontroller.Pin  # GPIO13
SW9: microcontroller.Pin  # GPIO12
SW10: microcontroller.Pin  # GPIO11
SW11: microcontroller.Pin  # GPIO10
SW12: microcontroller.Pin  # GPIO9
SW13: microcontroller.Pin  # GPIO8
SW14: microcontroller.Pin  # GPIO7
SW15: microcontroller.Pin  # GPIO6
USER_SW: microcontroller.Pin  # GPIO23


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
