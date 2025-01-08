# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Makerdiary M60 Keyboard
 - port: nordic
 - board_id: makerdiary_m60_keyboard
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
R1: microcontroller.Pin  # P0_05
R2: microcontroller.Pin  # P0_06
R3: microcontroller.Pin  # P0_07
R4: microcontroller.Pin  # P0_08
R5: microcontroller.Pin  # P1_09
R6: microcontroller.Pin  # P1_08
R7: microcontroller.Pin  # P0_12
R8: microcontroller.Pin  # P0_11
C1: microcontroller.Pin  # P0_19
C2: microcontroller.Pin  # P0_20
C3: microcontroller.Pin  # P0_21
C4: microcontroller.Pin  # P0_22
C5: microcontroller.Pin  # P0_23
C6: microcontroller.Pin  # P0_24
C7: microcontroller.Pin  # P0_25
C8: microcontroller.Pin  # P0_26
TXD: microcontroller.Pin  # P0_16
RXD: microcontroller.Pin  # P0_15
SCL: microcontroller.Pin  # P1_06
SDA: microcontroller.Pin  # P1_05
LED_R: microcontroller.Pin  # P0_30
LED_G: microcontroller.Pin  # P0_29
LED_B: microcontroller.Pin  # P0_31
BTN: microcontroller.Pin  # P0_27
CHARGING: microcontroller.Pin  # P0_03
VOLTAGE_MONITOR: microcontroller.Pin  # P0_02
BATTERY: microcontroller.Pin  # P0_02
BATTERY_ENABLE: microcontroller.Pin  # P0_28
RGB_POWER: microcontroller.Pin  # P1_04


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
