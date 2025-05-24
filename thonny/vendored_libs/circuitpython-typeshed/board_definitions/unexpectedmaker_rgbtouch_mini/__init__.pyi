# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for RGBTouch Mini
 - port: espressif
 - board_id: unexpectedmaker_rgbtouch_mini
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, _stage, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO7: microcontroller.Pin  # GPIO7
INT_IMU: microcontroller.Pin  # GPIO7
SDA: microcontroller.Pin  # GPIO8
IO8: microcontroller.Pin  # GPIO8
SCL: microcontroller.Pin  # GPIO9
IO9: microcontroller.Pin  # GPIO9
IO15: microcontroller.Pin  # GPIO15
INT_ROW: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
INT_COL: microcontroller.Pin  # GPIO16
IO18: microcontroller.Pin  # GPIO18
VBAT_SENSE: microcontroller.Pin  # GPIO18
IO21: microcontroller.Pin  # GPIO21
PWR_SHUTDOWN: microcontroller.Pin  # GPIO21
IO34: microcontroller.Pin  # GPIO34
AMP_SD: microcontroller.Pin  # GPIO34
IO35: microcontroller.Pin  # GPIO35
AMP_DATA: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
AMP_BCLK: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
AMP_LRCLK: microcontroller.Pin  # GPIO37
IO48: microcontroller.Pin  # GPIO48
VBUS_SENSE: microcontroller.Pin  # GPIO48
MATRIX_POWER: microcontroller.Pin  # GPIO38
MATRIX_DATA: microcontroller.Pin  # GPIO39


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
