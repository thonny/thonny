# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Deneyap Mini v2
 - port: espressif
 - board_id: deneyap_mini_v2
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
RX: microcontroller.Pin  # GPIO44
D0: microcontroller.Pin  # GPIO44
TX: microcontroller.Pin  # GPIO43
D1: microcontroller.Pin  # GPIO43
D2: microcontroller.Pin  # GPIO42
PWM0: microcontroller.Pin  # GPIO42
D3: microcontroller.Pin  # GPIO41
PWM1: microcontroller.Pin  # GPIO41
MO: microcontroller.Pin  # GPIO40
D4: microcontroller.Pin  # GPIO40
MOSI: microcontroller.Pin  # GPIO40
MI: microcontroller.Pin  # GPIO39
D5: microcontroller.Pin  # GPIO39
MISO: microcontroller.Pin  # GPIO39
MC: microcontroller.Pin  # GPIO38
D6: microcontroller.Pin  # GPIO38
SCK: microcontroller.Pin  # GPIO38
SC: microcontroller.Pin  # GPIO37
D7: microcontroller.Pin  # GPIO37
SCL: microcontroller.Pin  # GPIO37
SD: microcontroller.Pin  # GPIO36
D8: microcontroller.Pin  # GPIO36
SDA: microcontroller.Pin  # GPIO36
D9: microcontroller.Pin  # GPIO26
D10: microcontroller.Pin  # GPIO21
SS: microcontroller.Pin  # GPIO21
DA1: microcontroller.Pin  # GPIO18
D11: microcontroller.Pin  # GPIO18
DAC1: microcontroller.Pin  # GPIO18
DA0: microcontroller.Pin  # GPIO17
D12: microcontroller.Pin  # GPIO17
DAC0: microcontroller.Pin  # GPIO17
D13: microcontroller.Pin  # GPIO0
GPKEY: microcontroller.Pin  # GPIO0
D14: microcontroller.Pin  # GPIO33
RGBLED: microcontroller.Pin  # GPIO33
A0: microcontroller.Pin  # GPIO7
T0: microcontroller.Pin  # GPIO7
A1: microcontroller.Pin  # GPIO8
T1: microcontroller.Pin  # GPIO8
A2: microcontroller.Pin  # GPIO9
T2: microcontroller.Pin  # GPIO9
A3: microcontroller.Pin  # GPIO10
T3: microcontroller.Pin  # GPIO10
A4: microcontroller.Pin  # GPIO11
T4: microcontroller.Pin  # GPIO11
A5: microcontroller.Pin  # GPIO12
T5: microcontroller.Pin  # GPIO12
A6: microcontroller.Pin  # GPIO13
T6: microcontroller.Pin  # GPIO13
A7: microcontroller.Pin  # GPIO16


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
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
