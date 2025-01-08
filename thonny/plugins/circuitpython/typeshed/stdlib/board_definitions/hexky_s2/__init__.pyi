# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for HexKyS2
 - port: espressif
 - board_id: hexky_s2
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO1
A1: microcontroller.Pin  # GPIO3
A2: microcontroller.Pin  # GPIO2
A3: microcontroller.Pin  # GPIO7
A4: microcontroller.Pin  # GPIO17
A5: microcontroller.Pin  # GPIO18
DAC1: microcontroller.Pin  # GPIO17
DAC2: microcontroller.Pin  # GPIO18
D2: microcontroller.Pin  # GPIO5
D3: microcontroller.Pin  # GPIO6
D4: microcontroller.Pin  # GPIO4
D5: microcontroller.Pin  # GPIO11
D6: microcontroller.Pin  # GPIO10
D7: microcontroller.Pin  # GPIO12
D8: microcontroller.Pin  # GPIO10
SW1: microcontroller.Pin  # GPIO21
SW2: microcontroller.Pin  # GPIO42
D13_LED: microcontroller.Pin  # GPIO39
NEOPIXEL: microcontroller.Pin  # GPIO40
VBAT_SENSE: microcontroller.Pin  # GPIO13
TFT_CS: microcontroller.Pin  # GPIO33
TFT_DC: microcontroller.Pin  # GPIO34
TFT_RST: microcontroller.Pin  # GPIO41
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
SCL: microcontroller.Pin  # GPIO9
SDA: microcontroller.Pin  # GPIO8
SCK: microcontroller.Pin  # GPIO36
MISO: microcontroller.Pin  # GPIO37
MOSI: microcontroller.Pin  # GPIO35
BOOT: microcontroller.Pin  # GPIO0


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
