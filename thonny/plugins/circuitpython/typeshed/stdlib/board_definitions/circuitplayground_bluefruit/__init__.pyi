# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Circuit Playground Bluefruit
 - port: nordic
 - board_id: circuitplayground_bluefruit
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
AUDIO: microcontroller.Pin  # P0_26
D12: microcontroller.Pin  # P0_26
SPEAKER: microcontroller.Pin  # P0_26
A1: microcontroller.Pin  # P0_02
D6: microcontroller.Pin  # P0_02
SCK: microcontroller.Pin  # P0_02
A2: microcontroller.Pin  # P0_29
D9: microcontroller.Pin  # P0_29
MISO: microcontroller.Pin  # P0_29
A3: microcontroller.Pin  # P0_03
D10: microcontroller.Pin  # P0_03
MOSI: microcontroller.Pin  # P0_03
A4: microcontroller.Pin  # P0_04
D3: microcontroller.Pin  # P0_04
SCL: microcontroller.Pin  # P0_04
A5: microcontroller.Pin  # P0_05
D2: microcontroller.Pin  # P0_05
SDA: microcontroller.Pin  # P0_05
A6: microcontroller.Pin  # P0_30
D0: microcontroller.Pin  # P0_30
RX: microcontroller.Pin  # P0_30
D1: microcontroller.Pin  # P0_14
TX: microcontroller.Pin  # P0_14
LIGHT: microcontroller.Pin  # P0_28
A8: microcontroller.Pin  # P0_28
TEMPERATURE: microcontroller.Pin  # P0_31
A9: microcontroller.Pin  # P0_31
BUTTON_A: microcontroller.Pin  # P1_02
D4: microcontroller.Pin  # P1_02
BUTTON_B: microcontroller.Pin  # P1_15
D5: microcontroller.Pin  # P1_15
SLIDE_SWITCH: microcontroller.Pin  # P1_06
D7: microcontroller.Pin  # P1_06
POWER_SWITCH: microcontroller.Pin  # P0_06
D35: microcontroller.Pin  # P0_06
LED: microcontroller.Pin  # P1_14
L: microcontroller.Pin  # P1_14
D13: microcontroller.Pin  # P1_14
NEOPIXEL: microcontroller.Pin  # P0_13
D8: microcontroller.Pin  # P0_13
MICROPHONE_CLOCK: microcontroller.Pin  # P0_17
MICROPHONE_DATA: microcontroller.Pin  # P0_16
ACCELEROMETER_INTERRUPT: microcontroller.Pin  # P1_13
ACCELEROMETER_SDA: microcontroller.Pin  # P1_10
ACCELEROMETER_SCL: microcontroller.Pin  # P1_12
SPEAKER_ENABLE: microcontroller.Pin  # P1_04


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


# Unmapped:
#   none
