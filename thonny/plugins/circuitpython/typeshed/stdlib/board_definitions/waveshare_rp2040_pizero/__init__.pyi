# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Waveshare RP2040-PiZero
 - port: raspberrypi
 - board_id: waveshare_rp2040_pizero
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, picodvi, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
GP2: microcontroller.Pin  # GPIO2
SDA: microcontroller.Pin  # GPIO2
GP3: microcontroller.Pin  # GPIO3
SCL: microcontroller.Pin  # GPIO3
GP14: microcontroller.Pin  # GPIO14
GP17: microcontroller.Pin  # GPIO17
GP27: microcontroller.Pin  # GPIO27
GP27_A1: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP22: microcontroller.Pin  # GPIO22
GP11: microcontroller.Pin  # GPIO11
MOSI: microcontroller.Pin  # GPIO11
GP12: microcontroller.Pin  # GPIO12
MISO: microcontroller.Pin  # GPIO12
GP10: microcontroller.Pin  # GPIO10
SCK: microcontroller.Pin  # GPIO10
GP0: microcontroller.Pin  # GPIO0
ID_SDA: microcontroller.Pin  # GPIO0
GP15: microcontroller.Pin  # GPIO15
GP6: microcontroller.Pin  # GPIO6
GP13: microcontroller.Pin  # GPIO13
GP19: microcontroller.Pin  # GPIO19
GP26: microcontroller.Pin  # GPIO26
GP26_A0: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
GP4: microcontroller.Pin  # GPIO4
TX: microcontroller.Pin  # GPIO4
GP5: microcontroller.Pin  # GPIO5
RX: microcontroller.Pin  # GPIO5
GP18: microcontroller.Pin  # GPIO18
GP23: microcontroller.Pin  # GPIO23
GP24: microcontroller.Pin  # GPIO24
GP25: microcontroller.Pin  # GPIO25
GP8: microcontroller.Pin  # GPIO8
CE0: microcontroller.Pin  # GPIO8
GP7: microcontroller.Pin  # GPIO7
CE1: microcontroller.Pin  # GPIO7
GP1: microcontroller.Pin  # GPIO1
ID_SCL: microcontroller.Pin  # GPIO1
GP9: microcontroller.Pin  # GPIO9
GP16: microcontroller.Pin  # GPIO16
GP20: microcontroller.Pin  # GPIO20
GP21: microcontroller.Pin  # GPIO21
CKN: microcontroller.Pin  # GPIO29
CKP: microcontroller.Pin  # GPIO28
D0N: microcontroller.Pin  # GPIO27
D0P: microcontroller.Pin  # GPIO26
D1N: microcontroller.Pin  # GPIO25
D1P: microcontroller.Pin  # GPIO24
D2N: microcontroller.Pin  # GPIO23
D2P: microcontroller.Pin  # GPIO22
CEC: microcontroller.Pin  # GPIO16
USB_HOST_DATA_PLUS: microcontroller.Pin  # GPIO6
USB_HOST_DATA_MINUS: microcontroller.Pin  # GPIO7
SD_SCK: microcontroller.Pin  # GPIO18
SD_MOSI: microcontroller.Pin  # GPIO19
SD_MISO: microcontroller.Pin  # GPIO20
SD_CS: microcontroller.Pin  # GPIO21


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
