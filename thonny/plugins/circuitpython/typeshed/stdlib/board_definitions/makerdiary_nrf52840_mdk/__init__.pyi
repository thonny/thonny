# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for MakerDiary nRF52840 MDK
 - port: nordic
 - board_id: makerdiary_nrf52840_mdk
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
AIN0: microcontroller.Pin  # P0_02
AIN1: microcontroller.Pin  # P0_03
AIN2: microcontroller.Pin  # P0_04
AIN3: microcontroller.Pin  # P0_05
AIN4: microcontroller.Pin  # P0_28
AIN5: microcontroller.Pin  # P0_29
AIN6: microcontroller.Pin  # P0_30
AIN7: microcontroller.Pin  # P0_31
AREF: microcontroller.Pin  # P0_04
VDIV: microcontroller.Pin  # P0_05
NFC1: microcontroller.Pin  # P0_09
NFC2: microcontroller.Pin  # P0_10
P2: microcontroller.Pin  # P0_02
P3: microcontroller.Pin  # P0_03
P4: microcontroller.Pin  # P0_04
P5: microcontroller.Pin  # P0_05
P6: microcontroller.Pin  # P0_06
P7: microcontroller.Pin  # P0_07
P8: microcontroller.Pin  # P0_08
P9: microcontroller.Pin  # P0_09
P10: microcontroller.Pin  # P0_10
P11: microcontroller.Pin  # P0_11
P12: microcontroller.Pin  # P0_12
P13: microcontroller.Pin  # P0_13
P14: microcontroller.Pin  # P0_14
P15: microcontroller.Pin  # P0_15
P16: microcontroller.Pin  # P0_16
P17: microcontroller.Pin  # P0_17
P21: microcontroller.Pin  # P0_21
P25: microcontroller.Pin  # P0_25
P26: microcontroller.Pin  # P0_26
P27: microcontroller.Pin  # P0_27
P28: microcontroller.Pin  # P0_28
P29: microcontroller.Pin  # P0_29
P30: microcontroller.Pin  # P0_30
P31: microcontroller.Pin  # P0_31
SCK: microcontroller.Pin  # P1_03
CSN: microcontroller.Pin  # P1_06
IO0: microcontroller.Pin  # P1_05
IO1: microcontroller.Pin  # P1_04
IO2: microcontroller.Pin  # P1_02
IO3: microcontroller.Pin  # P1_01
TXD: microcontroller.Pin  # P0_20
RXD: microcontroller.Pin  # P0_19
LED_RED: microcontroller.Pin  # P0_23
LED_GREEN: microcontroller.Pin  # P0_22
LED_BLUE: microcontroller.Pin  # P0_24
BUTTON_USR: microcontroller.Pin  # P1_00


# Members:

# Unmapped:
#   none
