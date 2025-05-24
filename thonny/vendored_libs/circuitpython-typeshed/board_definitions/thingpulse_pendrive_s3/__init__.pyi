# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ThingPulse Pendrive S3
 - port: espressif
 - board_id: thingpulse_pendrive_s3
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
D1: microcontroller.Pin  # GPIO1
TouchIn: microcontroller.Pin  # GPIO1
D5: microcontroller.Pin  # GPIO5
NEOPIXEL: microcontroller.Pin  # GPIO5
D33: microcontroller.Pin  # GPIO33
D34: microcontroller.Pin  # GPIO34
CS: microcontroller.Pin  # GPIO34
D35: microcontroller.Pin  # GPIO35
MISO: microcontroller.Pin  # GPIO35
D36: microcontroller.Pin  # GPIO36
SCLK: microcontroller.Pin  # GPIO36
D37: microcontroller.Pin  # GPIO37
MOSI: microcontroller.Pin  # GPIO37
D38: microcontroller.Pin  # GPIO38
TX: microcontroller.Pin  # GPIO39
D39: microcontroller.Pin  # GPIO39


# Members:

# Unmapped:
#   none
