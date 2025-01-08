# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PCA10056 nRF52840-DK
 - port: nordic
 - board_id: pca10056
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
P0_00: microcontroller.Pin  # P0_00
P0_01: microcontroller.Pin  # P0_01
P0_02: microcontroller.Pin  # P0_02
P0_03: microcontroller.Pin  # P0_03
A0: microcontroller.Pin  # P0_03
P0_04: microcontroller.Pin  # P0_04
A1: microcontroller.Pin  # P0_04
P0_05: microcontroller.Pin  # P0_05
P0_06: microcontroller.Pin  # P0_06
P0_07: microcontroller.Pin  # P0_07
P0_08: microcontroller.Pin  # P0_08
P0_09: microcontroller.Pin  # P0_09
P0_10: microcontroller.Pin  # P0_10
P0_11: microcontroller.Pin  # P0_11
BUTTON1: microcontroller.Pin  # P0_11
P0_12: microcontroller.Pin  # P0_12
BUTTON2: microcontroller.Pin  # P0_12
P0_13: microcontroller.Pin  # P0_13
L: microcontroller.Pin  # P0_13
LED1: microcontroller.Pin  # P0_13
P0_14: microcontroller.Pin  # P0_14
LED2: microcontroller.Pin  # P0_14
P0_15: microcontroller.Pin  # P0_15
LED3: microcontroller.Pin  # P0_15
P0_16: microcontroller.Pin  # P0_16
LED4: microcontroller.Pin  # P0_16
P0_17: microcontroller.Pin  # P0_17
P0_19: microcontroller.Pin  # P0_19
P0_20: microcontroller.Pin  # P0_20
P0_21: microcontroller.Pin  # P0_21
P0_22: microcontroller.Pin  # P0_22
P0_23: microcontroller.Pin  # P0_23
P0_24: microcontroller.Pin  # P0_24
BUTTON3: microcontroller.Pin  # P0_24
P0_25: microcontroller.Pin  # P0_25
BUTTON4: microcontroller.Pin  # P0_25
P0_26: microcontroller.Pin  # P0_26
SDA: microcontroller.Pin  # P0_26
P0_27: microcontroller.Pin  # P0_27
SCL: microcontroller.Pin  # P0_27
P0_28: microcontroller.Pin  # P0_28
A2: microcontroller.Pin  # P0_28
P0_29: microcontroller.Pin  # P0_29
A3: microcontroller.Pin  # P0_29
P0_30: microcontroller.Pin  # P0_30
A4: microcontroller.Pin  # P0_30
P0_31: microcontroller.Pin  # P0_31
A5: microcontroller.Pin  # P0_31
P1_00: microcontroller.Pin  # P1_00
P1_01: microcontroller.Pin  # P1_01
D0: microcontroller.Pin  # P1_01
RX: microcontroller.Pin  # P1_01
P1_02: microcontroller.Pin  # P1_02
D1: microcontroller.Pin  # P1_02
TX: microcontroller.Pin  # P1_02
P1_03: microcontroller.Pin  # P1_03
D2: microcontroller.Pin  # P1_03
P1_04: microcontroller.Pin  # P1_04
D3: microcontroller.Pin  # P1_04
P1_05: microcontroller.Pin  # P1_05
D4: microcontroller.Pin  # P1_05
P1_06: microcontroller.Pin  # P1_06
D5: microcontroller.Pin  # P1_06
P1_07: microcontroller.Pin  # P1_07
D6: microcontroller.Pin  # P1_07
P1_08: microcontroller.Pin  # P1_08
D7: microcontroller.Pin  # P1_08
P1_09: microcontroller.Pin  # P1_09
P1_10: microcontroller.Pin  # P1_10
D8: microcontroller.Pin  # P1_10
P1_11: microcontroller.Pin  # P1_11
D9: microcontroller.Pin  # P1_11
P1_12: microcontroller.Pin  # P1_12
D10: microcontroller.Pin  # P1_12
P1_13: microcontroller.Pin  # P1_13
D11: microcontroller.Pin  # P1_13
MOSI: microcontroller.Pin  # P1_13
P1_14: microcontroller.Pin  # P1_14
D12: microcontroller.Pin  # P1_14
MISO: microcontroller.Pin  # P1_14
P1_15: microcontroller.Pin  # P1_15
D13: microcontroller.Pin  # P1_15
SCK: microcontroller.Pin  # P1_15


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
