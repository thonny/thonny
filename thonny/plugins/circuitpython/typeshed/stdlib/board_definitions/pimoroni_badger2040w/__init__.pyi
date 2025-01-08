# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Badger 2040 W
 - port: raspberrypi
 - board_id: pimoroni_badger2040w
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, cyw43, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, socketpool, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, usb_video, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_register, pcf85063a
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1
GP1: microcontroller.Pin  # GPIO1
GP2: microcontroller.Pin  # GPIO2
GP3: microcontroller.Pin  # GPIO3
SDA: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO5
GP6: microcontroller.Pin  # GPIO6
GP7: microcontroller.Pin  # GPIO7
RTC_ALARM: microcontroller.Pin  # GPIO8
GP9: microcontroller.Pin  # GPIO9
SW_DOWN: microcontroller.Pin  # GPIO11
SW_A: microcontroller.Pin  # GPIO12
SW_B: microcontroller.Pin  # GPIO13
SW_C: microcontroller.Pin  # GPIO14
SW_UP: microcontroller.Pin  # GPIO15
MISO: microcontroller.Pin  # GPIO16
INKY_CS: microcontroller.Pin  # GPIO17
SCK: microcontroller.Pin  # GPIO18
MOSI: microcontroller.Pin  # GPIO19
INKY_DC: microcontroller.Pin  # GPIO20
INKY_RST: microcontroller.Pin  # GPIO21
USER_LED: microcontroller.Pin  # GPIO22
SMPS_MODE: microcontroller.Pin  # CYW1
LED: microcontroller.Pin  # CYW0
VBUS_SENSE: microcontroller.Pin  # CYW2
INKY_BUSY: microcontroller.Pin  # GPIO26
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO29
A3: microcontroller.Pin  # GPIO29


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

"""Returns the `displayio.EPaperDisplay` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.EPaperDisplay`.
"""
DISPLAY: displayio.EPaperDisplay


# Unmapped:
#   none
