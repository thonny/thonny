# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Interstate 75
 - port: raspberrypi
 - board_id: pimoroni_interstate75
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
R0: microcontroller.Pin  # GPIO0
G0: microcontroller.Pin  # GPIO1
B0: microcontroller.Pin  # GPIO2
R1: microcontroller.Pin  # GPIO3
G1: microcontroller.Pin  # GPIO4
B1: microcontroller.Pin  # GPIO5
ROW_A: microcontroller.Pin  # GPIO6
ROW_B: microcontroller.Pin  # GPIO7
ROW_C: microcontroller.Pin  # GPIO8
ROW_D: microcontroller.Pin  # GPIO9
ROW_E: microcontroller.Pin  # GPIO10
CLK: microcontroller.Pin  # GPIO11
LAT: microcontroller.Pin  # GPIO12
OE: microcontroller.Pin  # GPIO13
SW_A: microcontroller.Pin  # GPIO14
LED: microcontroller.Pin  # GPIO16
LED_R: microcontroller.Pin  # GPIO16
LED_G: microcontroller.Pin  # GPIO17
LED_B: microcontroller.Pin  # GPIO18
INT: microcontroller.Pin  # GPIO19
GP19: microcontroller.Pin  # GPIO19
SDA: microcontroller.Pin  # GPIO20
GP20: microcontroller.Pin  # GPIO20
SCL: microcontroller.Pin  # GPIO21
GP21: microcontroller.Pin  # GPIO21
USER_SW: microcontroller.Pin  # GPIO23
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
CURRENT_SENSE: microcontroller.Pin  # GPIO29


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
