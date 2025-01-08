# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Core Basic
 - port: espressif
 - board_id: m5stack_core_basic
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
MOSI: microcontroller.Pin  # GPIO23
D23: microcontroller.Pin  # GPIO23
MISO: microcontroller.Pin  # GPIO19
D19: microcontroller.Pin  # GPIO19
SCK: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
D3: microcontroller.Pin  # GPIO3
RX2: microcontroller.Pin  # GPIO16
D16: microcontroller.Pin  # GPIO16
PORTC_RX: microcontroller.Pin  # GPIO16
SDA: microcontroller.Pin  # GPIO21
PORTA_SDA: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
A2: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
A12: microcontroller.Pin  # GPIO12
D12: microcontroller.Pin  # GPIO12
A15: microcontroller.Pin  # GPIO15
D15: microcontroller.Pin  # GPIO15
A35: microcontroller.Pin  # GPIO35
D35: microcontroller.Pin  # GPIO35
A36: microcontroller.Pin  # GPIO36
D36: microcontroller.Pin  # GPIO36
PORTB_IN: microcontroller.Pin  # GPIO36
A25: microcontroller.Pin  # GPIO25
D25: microcontroller.Pin  # GPIO25
SPEAKER: microcontroller.Pin  # GPIO25
A26: microcontroller.Pin  # GPIO26
D26: microcontroller.Pin  # GPIO26
PORTB_OUT: microcontroller.Pin  # GPIO26
D1: microcontroller.Pin  # GPIO1
TX2: microcontroller.Pin  # GPIO17
D17: microcontroller.Pin  # GPIO17
PORTC_TX: microcontroller.Pin  # GPIO17
SCL: microcontroller.Pin  # GPIO22
PORTA_SCL: microcontroller.Pin  # GPIO22
D22: microcontroller.Pin  # GPIO22
D5: microcontroller.Pin  # GPIO5
A13: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
A0: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
A34: microcontroller.Pin  # GPIO34
D34: microcontroller.Pin  # GPIO34
BTN_A: microcontroller.Pin  # GPIO39
BTN_B: microcontroller.Pin  # GPIO38
BTN_C: microcontroller.Pin  # GPIO37
SD_CS: microcontroller.Pin  # GPIO4
TFT_CS: microcontroller.Pin  # GPIO14
TFT_DC: microcontroller.Pin  # GPIO27
TFT_RESET: microcontroller.Pin  # GPIO33
TFT_BACKLIGHT: microcontroller.Pin  # GPIO32


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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
