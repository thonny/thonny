# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ARAMCON Badge 2019
 - port: nordic
 - board_id: aramcon_badge_2019
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
LEFT_BUTTON: microcontroller.Pin  # P0_02
MIDDLE_BUTTON: microcontroller.Pin  # P0_29
RIGHT_BUTTON: microcontroller.Pin  # P0_31
LED: microcontroller.Pin  # P1_11
SCL: microcontroller.Pin  # P0_28
SDA: microcontroller.Pin  # P0_03
SCK: microcontroller.Pin  # P0_01
MOSI: microcontroller.Pin  # P1_10
MISO: microcontroller.Pin  # P1_09
SND_CS: microcontroller.Pin  # P1_13
SND_DREQ: microcontroller.Pin  # P0_13
SND_RESET: microcontroller.Pin  # P0_00
SND_XDCS: microcontroller.Pin  # P0_24
DISP_BUSY: microcontroller.Pin  # P0_26
DISP_CS: microcontroller.Pin  # P0_07
DISP_DC: microcontroller.Pin  # P0_12
DISP_RESET: microcontroller.Pin  # P0_06
NEOPIXEL: microcontroller.Pin  # P0_08
VIBRATION_MOTOR: microcontroller.Pin  # P0_17
BATTERY_SENSE: microcontroller.Pin  # P0_30


# Members:

# Unmapped:
#   none
