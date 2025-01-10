# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Pico Plus 2
 - port: raspberrypi
 - board_id: pimoroni_pico_plus2
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiodelays, audiofilters, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, picodvi, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
GP0: microcontroller.Pin  # GPIO0
GP1: microcontroller.Pin  # GPIO1
GP2: microcontroller.Pin  # GPIO2
GP3: microcontroller.Pin  # GPIO3
GP4: microcontroller.Pin  # GPIO4
GP5: microcontroller.Pin  # GPIO5
GP6: microcontroller.Pin  # GPIO6
GP7: microcontroller.Pin  # GPIO7
GP8: microcontroller.Pin  # GPIO8
GP9: microcontroller.Pin  # GPIO9
GP10: microcontroller.Pin  # GPIO10
GP11: microcontroller.Pin  # GPIO11
GP12: microcontroller.Pin  # GPIO12
GP13: microcontroller.Pin  # GPIO13
GP14: microcontroller.Pin  # GPIO14
GP15: microcontroller.Pin  # GPIO15
GP16: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
GP18: microcontroller.Pin  # GPIO18
GP19: microcontroller.Pin  # GPIO19
GP20: microcontroller.Pin  # GPIO20
GP21: microcontroller.Pin  # GPIO21
GP22: microcontroller.Pin  # GPIO22
VBUS_SENSE: microcontroller.Pin  # GPIO24
GP24: microcontroller.Pin  # GPIO24
LED: microcontroller.Pin  # GPIO25
GP25: microcontroller.Pin  # GPIO25
GP26: microcontroller.Pin  # GPIO26
GP27: microcontroller.Pin  # GPIO27
GP28: microcontroller.Pin  # GPIO28
GP40_A0: microcontroller.Pin  # GPIO40
GP40: microcontroller.Pin  # GPIO40
A0: microcontroller.Pin  # GPIO40
GP41_A1: microcontroller.Pin  # GPIO41
GP41: microcontroller.Pin  # GPIO41
A1: microcontroller.Pin  # GPIO41
GP42_A2: microcontroller.Pin  # GPIO42
GP42: microcontroller.Pin  # GPIO42
A2: microcontroller.Pin  # GPIO42
A3: microcontroller.Pin  # GPIO43
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO43
USER_SW: microcontroller.Pin  # GPIO45
BUTTON: microcontroller.Pin  # GPIO45
SPCE_CS: microcontroller.Pin  # GPIO33
GP33: microcontroller.Pin  # GPIO33
SPCE_SCK: microcontroller.Pin  # GPIO34
SCK: microcontroller.Pin  # GPIO34
GP34: microcontroller.Pin  # GPIO34
SPCE_MOSI: microcontroller.Pin  # GPIO35
MOSI: microcontroller.Pin  # GPIO35
GP35: microcontroller.Pin  # GPIO35
SPCE_MISO: microcontroller.Pin  # GPIO32
MISO: microcontroller.Pin  # GPIO32
GP32: microcontroller.Pin  # GPIO32
SPCE_BL: microcontroller.Pin  # GPIO36
GP36: microcontroller.Pin  # GPIO36
TFT_BACKLIGHT: microcontroller.Pin  # GPIO36


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