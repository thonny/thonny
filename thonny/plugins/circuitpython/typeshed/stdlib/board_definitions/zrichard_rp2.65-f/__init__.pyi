# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for RP2.65-F
 - port: raspberrypi
 - board_id: zrichard_rp2.65-f
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_midi, neopixel
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
ROW0: microcontroller.Pin  # GPIO0
COL0: microcontroller.Pin  # GPIO1
ROW1: microcontroller.Pin  # GPIO2
COL1: microcontroller.Pin  # GPIO3
ROW2: microcontroller.Pin  # GPIO4
COL2: microcontroller.Pin  # GPIO5
ROW3: microcontroller.Pin  # GPIO6
COL3: microcontroller.Pin  # GPIO7
ROW4: microcontroller.Pin  # GPIO8
COL4: microcontroller.Pin  # GPIO9
ROW5: microcontroller.Pin  # GPIO10
COL5: microcontroller.Pin  # GPIO11
ROW6: microcontroller.Pin  # GPIO12
COL6: microcontroller.Pin  # GPIO13
ROW7: microcontroller.Pin  # GPIO14
COL7: microcontroller.Pin  # GPIO15
ROW8: microcontroller.Pin  # GPIO16
ROW9: microcontroller.Pin  # GPIO17
LED: microcontroller.Pin  # GPIO25
RV1: microcontroller.Pin  # GPIO27
RV2: microcontroller.Pin  # GPIO28
RV3: microcontroller.Pin  # GPIO29


# Members:

# Unmapped:
#   none
