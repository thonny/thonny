# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Tiny FX
 - port: raspberrypi
 - board_id: pimoroni_tinyfx
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
LED_1: microcontroller.Pin  # GPIO3
LED_2: microcontroller.Pin  # GPIO2
LED_3: microcontroller.Pin  # GPIO4
LED_4: microcontroller.Pin  # GPIO5
LED_5: microcontroller.Pin  # GPIO8
LED_6: microcontroller.Pin  # GPIO9
LED_R: microcontroller.Pin  # GPIO13
LED_G: microcontroller.Pin  # GPIO14
LED_B: microcontroller.Pin  # GPIO15
SDA: microcontroller.Pin  # GPIO16
SCL: microcontroller.Pin  # GPIO17
I2S_DATA: microcontroller.Pin  # GPIO18
I2S_BCLK: microcontroller.Pin  # GPIO19
I2S_LRCLK: microcontroller.Pin  # GPIO20
AMP_EN: microcontroller.Pin  # GPIO21
USER_SW: microcontroller.Pin  # GPIO22
SENSOR: microcontroller.Pin  # GPIO26
CURRENT_SENSE: microcontroller.Pin  # GPIO28
GP16: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
GP26: microcontroller.Pin  # GPIO26
GP26_A0: microcontroller.Pin  # GPIO26


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
