# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Particle Boron
 - port: nordic
 - board_id: particle_boron
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
A0: microcontroller.Pin  # P0_03
A1: microcontroller.Pin  # P0_04
A2: microcontroller.Pin  # P0_28
A3: microcontroller.Pin  # P0_29
A4: microcontroller.Pin  # P0_30
A5: microcontroller.Pin  # P0_31
MODE: microcontroller.Pin  # P0_11
POWER_I2C_SDA: microcontroller.Pin  # P0_24
POWER_I2C_SCL: microcontroller.Pin  # P1_09
POWER_INTERRUPT: microcontroller.Pin  # P0_05
NFC1: microcontroller.Pin  # P0_09
NFC2: microcontroller.Pin  # P0_10
D2: microcontroller.Pin  # P1_01
D3: microcontroller.Pin  # P1_02
D4: microcontroller.Pin  # P1_08
D5: microcontroller.Pin  # P1_10
D6: microcontroller.Pin  # P1_11
D7: microcontroller.Pin  # P1_12
BLUE_LED: microcontroller.Pin  # P1_12
LED: microcontroller.Pin  # P1_12
D8: microcontroller.Pin  # P1_03
RGB_LED_RED: microcontroller.Pin  # P0_13
RGB_LED_GREEN: microcontroller.Pin  # P0_14
RGB_LED_BLUE: microcontroller.Pin  # P0_15
D13: microcontroller.Pin  # P1_15
SCK: microcontroller.Pin  # P1_15
D12: microcontroller.Pin  # P1_13
MOSI: microcontroller.Pin  # P1_13
D11: microcontroller.Pin  # P1_14
MISO: microcontroller.Pin  # P1_14
D9: microcontroller.Pin  # P0_06
TX: microcontroller.Pin  # P0_06
D10: microcontroller.Pin  # P0_08
RX: microcontroller.Pin  # P0_08
D1: microcontroller.Pin  # P0_27
SCL: microcontroller.Pin  # P0_27
D0: microcontroller.Pin  # P0_26
SDA: microcontroller.Pin  # P0_26
ANTENNA_SWITCH: microcontroller.Pin  # P0_07
UBLOX_TX: microcontroller.Pin  # P1_05
UBLOX_RX: microcontroller.Pin  # P1_04
UBLOX_CTS: microcontroller.Pin  # P1_06
UBLOX_RTS: microcontroller.Pin  # P1_07
UBLOX_POWER_ENABLE: microcontroller.Pin  # P0_25
UBLOX_POWER_MONITOR: microcontroller.Pin  # P0_02
UBLOX_RESET: microcontroller.Pin  # P0_12
UBLOX_POWER_ON: microcontroller.Pin  # P0_16


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
