# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Arduino Nano 33 BLE Rev2
 - port: nordic
 - board_id: arduino_nano_33_ble_rev2
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D2: microcontroller.Pin  # P1_11
D3: microcontroller.Pin  # P1_12
D4: microcontroller.Pin  # P1_15
D5: microcontroller.Pin  # P1_13
D6: microcontroller.Pin  # P1_14
D7: microcontroller.Pin  # P0_23
D8: microcontroller.Pin  # P0_21
D9: microcontroller.Pin  # P0_27
D10: microcontroller.Pin  # P1_02
A0: microcontroller.Pin  # P0_04
A1: microcontroller.Pin  # P0_05
A2: microcontroller.Pin  # P0_30
A3: microcontroller.Pin  # P0_29
A4: microcontroller.Pin  # P0_31
SDA: microcontroller.Pin  # P0_31
A5: microcontroller.Pin  # P0_02
SCL: microcontroller.Pin  # P0_02
A6: microcontroller.Pin  # P0_28
A7: microcontroller.Pin  # P0_03
SDA1: microcontroller.Pin  # P0_14
SCL1: microcontroller.Pin  # P0_15
MOSI: microcontroller.Pin  # P1_01
MISO: microcontroller.Pin  # P1_08
SCK: microcontroller.Pin  # P0_13
LED_Y: microcontroller.Pin  # P0_13
LED_G: microcontroller.Pin  # P1_09
RGB_LED_R: microcontroller.Pin  # P0_24
RGB_LED_G: microcontroller.Pin  # P0_16
RGB_LED_B: microcontroller.Pin  # P0_06
VDD_ENV: microcontroller.Pin  # P0_22
R_PULLUP: microcontroller.Pin  # P1_00
MIC_PWR: microcontroller.Pin  # P0_17
PDMCLK: microcontroller.Pin  # P0_26
PDMDIN: microcontroller.Pin  # P0_25
INT_APDS: microcontroller.Pin  # P0_19
INT_BMI_1: microcontroller.Pin  # P0_11
INT_BMI_2: microcontroller.Pin  # P0_20
INT_LPS: microcontroller.Pin  # P0_12
TX: microcontroller.Pin  # P1_03
RX: microcontroller.Pin  # P1_10


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
