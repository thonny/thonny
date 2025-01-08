# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Seeed Xiao ESP32-C6 4MB Flash 512KB SRAM
 - port: espressif
 - board_id: seeed_xiao_esp32c6
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # GPIO0
A0: microcontroller.Pin  # GPIO0
D1: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO1
D2: microcontroller.Pin  # GPIO2
A2: microcontroller.Pin  # GPIO2
D3: microcontroller.Pin  # GPIO21
D4: microcontroller.Pin  # GPIO22
SDA: microcontroller.Pin  # GPIO22
D5: microcontroller.Pin  # GPIO23
SCL: microcontroller.Pin  # GPIO23
D6: microcontroller.Pin  # GPIO16
TX: microcontroller.Pin  # GPIO16
D7: microcontroller.Pin  # GPIO17
RX: microcontroller.Pin  # GPIO17
D8: microcontroller.Pin  # GPIO19
SCK: microcontroller.Pin  # GPIO19
D9: microcontroller.Pin  # GPIO20
MISO: microcontroller.Pin  # GPIO20
D10: microcontroller.Pin  # GPIO18
MOSI: microcontroller.Pin  # GPIO18
A4: microcontroller.Pin  # GPIO4
MTMS: microcontroller.Pin  # GPIO4
LP_UART_RXD: microcontroller.Pin  # GPIO4
A5: microcontroller.Pin  # GPIO5
MTDI: microcontroller.Pin  # GPIO5
LP_UART_TXD: microcontroller.Pin  # GPIO5
A6: microcontroller.Pin  # GPIO6
MTCK: microcontroller.Pin  # GPIO6
LP_I2C_SDA: microcontroller.Pin  # GPIO6
MTDO: microcontroller.Pin  # GPIO7
LP_I2C_SCL: microcontroller.Pin  # GPIO7


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
