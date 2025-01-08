# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Makerdiary nRF52840 M.2 Developer Kit
 - port: nordic
 - board_id: makerdiary_nrf52840_m2_devkit
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
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
P18: microcontroller.Pin  # P0_18
P19: microcontroller.Pin  # P0_19
P20: microcontroller.Pin  # P0_20
P21: microcontroller.Pin  # P0_21
P25: microcontroller.Pin  # P0_25
P26: microcontroller.Pin  # P0_26
P27: microcontroller.Pin  # P0_27
P28: microcontroller.Pin  # P0_28
P29: microcontroller.Pin  # P0_29
P30: microcontroller.Pin  # P0_30
P31: microcontroller.Pin  # P0_31
P1_0: microcontroller.Pin  # P1_00
P1_1: microcontroller.Pin  # P1_01
P1_2: microcontroller.Pin  # P1_02
P1_3: microcontroller.Pin  # P1_03
P1_4: microcontroller.Pin  # P1_04
P1_5: microcontroller.Pin  # P1_05
P1_6: microcontroller.Pin  # P1_06
P1_7: microcontroller.Pin  # P1_07
P1_8: microcontroller.Pin  # P1_08
P1_9: microcontroller.Pin  # P1_09
D0: microcontroller.Pin  # P0_15
RX: microcontroller.Pin  # P0_15
D1: microcontroller.Pin  # P0_16
TX: microcontroller.Pin  # P0_16
D2: microcontroller.Pin  # P0_19
D3: microcontroller.Pin  # P0_20
D4: microcontroller.Pin  # P0_21
D5: microcontroller.Pin  # P0_22
D6: microcontroller.Pin  # P0_23
D7: microcontroller.Pin  # P0_24
D8: microcontroller.Pin  # P1_00
D9: microcontroller.Pin  # P1_01
D10: microcontroller.Pin  # P1_02
D11: microcontroller.Pin  # P1_03
D12: microcontroller.Pin  # P1_04
D13: microcontroller.Pin  # P1_07
D14: microcontroller.Pin  # P1_05
SDA: microcontroller.Pin  # P1_05
D15: microcontroller.Pin  # P1_06
SCL: microcontroller.Pin  # P1_06
A0: microcontroller.Pin  # P0_02
A1: microcontroller.Pin  # P0_03
A2: microcontroller.Pin  # P0_28
A3: microcontroller.Pin  # P0_27
A4: microcontroller.Pin  # P0_26
A5: microcontroller.Pin  # P0_04
SCK: microcontroller.Pin  # P0_11
MOSI: microcontroller.Pin  # P0_12
MISO: microcontroller.Pin  # P1_08
LCD_DC: microcontroller.Pin  # P0_08
LCD_CS: microcontroller.Pin  # P0_06
LCD_BL: microcontroller.Pin  # P0_20
LCD_RST: microcontroller.Pin  # P1_09
LED_R: microcontroller.Pin  # P0_30
LED_G: microcontroller.Pin  # P0_29
LED_B: microcontroller.Pin  # P0_31
BUTTON_USR: microcontroller.Pin  # P0_19


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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
