# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for WK-50 Trackball Keyboard
 - port: raspberrypi
 - board_id: wk-50
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, picodvi, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: neopixel
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
NEOPIXEL: microcontroller.Pin  # GPIO0
COL13: microcontroller.Pin  # GPIO1
COL12: microcontroller.Pin  # GPIO4
COL11: microcontroller.Pin  # GPIO5
COL10: microcontroller.Pin  # GPIO6
COL9: microcontroller.Pin  # GPIO7
COL8: microcontroller.Pin  # GPIO8
COL7: microcontroller.Pin  # GPIO9
COL6: microcontroller.Pin  # GPIO10
ROW1: microcontroller.Pin  # GPIO13
ROW0: microcontroller.Pin  # GPIO14
ENC1: microcontroller.Pin  # GPIO15
ENC0: microcontroller.Pin  # GPIO17
ROW2: microcontroller.Pin  # GPIO18
ROW3: microcontroller.Pin  # GPIO19
XY_NCS: microcontroller.Pin  # GPIO21
XY_SCLK: microcontroller.Pin  # GPIO22
XY_SDIO: microcontroller.Pin  # GPIO23
COL5: microcontroller.Pin  # GPIO24
COL4: microcontroller.Pin  # GPIO25
COL3: microcontroller.Pin  # GPIO26
COL2: microcontroller.Pin  # GPIO27
COL1: microcontroller.Pin  # GPIO28
COL0: microcontroller.Pin  # GPIO29


# Members:

# Unmapped:
#   none
