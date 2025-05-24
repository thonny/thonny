# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Cytron IRIV IO Controller
 - port: raspberrypi
 - board_id: cytron_iriv_io_controller
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiodelays, audiofilters, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, picodvi, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_connection_manager, adafruit_fakerequests, adafruit_register, adafruit_requests, adafruit_ticks, adafruit_wiznet5k, pcf85063a, simpleio
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
GP23: microcontroller.Pin  # GPIO23
GP24: microcontroller.Pin  # GPIO24
GP25: microcontroller.Pin  # GPIO25
GP26: microcontroller.Pin  # GPIO26
GP27: microcontroller.Pin  # GPIO27
GP28: microcontroller.Pin  # GPIO28
GP29: microcontroller.Pin  # GPIO29
DI0: microcontroller.Pin  # GPIO0
DI1: microcontroller.Pin  # GPIO1
DI2: microcontroller.Pin  # GPIO2
DI3: microcontroller.Pin  # GPIO3
DI4: microcontroller.Pin  # GPIO4
DI5: microcontroller.Pin  # GPIO5
DI6: microcontroller.Pin  # GPIO6
DI7: microcontroller.Pin  # GPIO7
DI8: microcontroller.Pin  # GPIO8
DI9: microcontroller.Pin  # GPIO9
DI10: microcontroller.Pin  # GPIO10
DO0: microcontroller.Pin  # GPIO12
DO1: microcontroller.Pin  # GPIO13
DO2: microcontroller.Pin  # GPIO14
DO3: microcontroller.Pin  # GPIO15
A0: microcontroller.Pin  # GPIO26
AN0: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO27
AN1: microcontroller.Pin  # GPIO27
BTN: microcontroller.Pin  # GPIO28
BUTTON: microcontroller.Pin  # GPIO28
LED: microcontroller.Pin  # GPIO29
BUZZER: microcontroller.Pin  # GPIO11
TX: microcontroller.Pin  # GPIO24
RX: microcontroller.Pin  # GPIO25
SDA: microcontroller.Pin  # GPIO16
SCL: microcontroller.Pin  # GPIO17
MOSI: microcontroller.Pin  # GPIO19
MISO: microcontroller.Pin  # GPIO20
SCK: microcontroller.Pin  # GPIO22
CS: microcontroller.Pin  # GPIO21
W5500_CS: microcontroller.Pin  # GPIO21
W5500_INT: microcontroller.Pin  # GPIO18
W5500_RST: microcontroller.Pin  # GPIO23
W5500_RESET: microcontroller.Pin  # GPIO23


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def RS485() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
