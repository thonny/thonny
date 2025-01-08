# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for BPI-Bit-S2
 - port: espressif
 - board_id: bpi_bit_s2
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO17
A0: microcontroller.Pin  # GPIO17
D0: microcontroller.Pin  # GPIO17
DAC1: microcontroller.Pin  # GPIO17
BUZZER: microcontroller.Pin  # GPIO17
IO1: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
A2: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
A3: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
A4: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
A6: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
A7: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
A8: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
A9: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
A10: microcontroller.Pin  # GPIO10
D10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
A11: microcontroller.Pin  # GPIO11
D11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO21
D12: microcontroller.Pin  # GPIO21
IO13: microcontroller.Pin  # GPIO36
SCK: microcontroller.Pin  # GPIO36
D13: microcontroller.Pin  # GPIO36
IO14: microcontroller.Pin  # GPIO37
MISO: microcontroller.Pin  # GPIO37
D14: microcontroller.Pin  # GPIO37
IO15: microcontroller.Pin  # GPIO35
MOSI: microcontroller.Pin  # GPIO35
D15: microcontroller.Pin  # GPIO35
IO16: microcontroller.Pin  # GPIO34
CS: microcontroller.Pin  # GPIO34
D16: microcontroller.Pin  # GPIO34
SCL: microcontroller.Pin  # GPIO16
IO19: microcontroller.Pin  # GPIO16
SDA: microcontroller.Pin  # GPIO15
IO20: microcontroller.Pin  # GPIO15
BOOT0: microcontroller.Pin  # GPIO0
LED: microcontroller.Pin  # GPIO0
BUTTON_A: microcontroller.Pin  # GPIO38
BUTTON_B: microcontroller.Pin  # GPIO33
LUM1: microcontroller.Pin  # GPIO12
LUM2: microcontroller.Pin  # GPIO13
TEMPERATURE: microcontroller.Pin  # GPIO14
NEOPIXEL: microcontroller.Pin  # GPIO18
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44


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
