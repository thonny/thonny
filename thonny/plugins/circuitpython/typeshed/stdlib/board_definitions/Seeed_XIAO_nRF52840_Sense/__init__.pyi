# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Seeed XIAO nRF52840 Sense
 - port: nordic
 - board_id: Seeed_XIAO_nRF52840_Sense
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
A0: microcontroller.Pin  # P0_02
A1: microcontroller.Pin  # P0_03
A2: microcontroller.Pin  # P0_28
A3: microcontroller.Pin  # P0_29
A4: microcontroller.Pin  # P0_04
A5: microcontroller.Pin  # P0_05
NFC1: microcontroller.Pin  # P0_09
NFC2: microcontroller.Pin  # P0_10
D0: microcontroller.Pin  # P0_02
D1: microcontroller.Pin  # P0_03
D2: microcontroller.Pin  # P0_28
D3: microcontroller.Pin  # P0_29
D4: microcontroller.Pin  # P0_04
D5: microcontroller.Pin  # P0_05
D6: microcontroller.Pin  # P1_11
D7: microcontroller.Pin  # P1_12
D8: microcontroller.Pin  # P1_13
D9: microcontroller.Pin  # P1_14
D10: microcontroller.Pin  # P1_15
SCK: microcontroller.Pin  # P1_13
MOSI: microcontroller.Pin  # P1_15
MISO: microcontroller.Pin  # P1_14
TX: microcontroller.Pin  # P1_11
RX: microcontroller.Pin  # P1_12
SCL: microcontroller.Pin  # P0_05
SDA: microcontroller.Pin  # P0_04
LED: microcontroller.Pin  # P0_26
LED_RED: microcontroller.Pin  # P0_26
LED_BLUE: microcontroller.Pin  # P0_06
LED_GREEN: microcontroller.Pin  # P0_30
IMU_PWR: microcontroller.Pin  # P1_08
IMU_SCL: microcontroller.Pin  # P0_27
IMU_SDA: microcontroller.Pin  # P0_07
IMU_INT1: microcontroller.Pin  # P0_11
MIC_PWR: microcontroller.Pin  # P1_10
PDM_CLK: microcontroller.Pin  # P1_00
PDM_DATA: microcontroller.Pin  # P0_16
READ_BATT_ENABLE: microcontroller.Pin  # P0_14
VBATT: microcontroller.Pin  # P0_31
CHARGE_STATUS: microcontroller.Pin  # P0_17
CHARGE_RATE: microcontroller.Pin  # P0_13


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
