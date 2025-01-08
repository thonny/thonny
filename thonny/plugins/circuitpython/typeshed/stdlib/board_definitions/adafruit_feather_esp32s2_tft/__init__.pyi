# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Feather ESP32-S2 TFT
 - port: espressif
 - board_id: adafruit_feather_esp32s2_tft
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
D5: microcontroller.Pin  # GPIO5
D6: microcontroller.Pin  # GPIO6
D9: microcontroller.Pin  # GPIO9
D10: microcontroller.Pin  # GPIO10
D11: microcontroller.Pin  # GPIO11
D12: microcontroller.Pin  # GPIO12
LED: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
L: microcontroller.Pin  # GPIO13
A5: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
A4: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
A3: microcontroller.Pin  # GPIO15
D15: microcontroller.Pin  # GPIO15
A2: microcontroller.Pin  # GPIO16
D16: microcontroller.Pin  # GPIO16
A1: microcontroller.Pin  # GPIO17
D17: microcontroller.Pin  # GPIO17
A0: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
NEOPIXEL: microcontroller.Pin  # GPIO33
NEOPIXEL_POWER: microcontroller.Pin  # GPIO34
TFT_I2C_POWER: microcontroller.Pin  # GPIO21
MOSI: microcontroller.Pin  # GPIO35
D35: microcontroller.Pin  # GPIO35
SCK: microcontroller.Pin  # GPIO36
D36: microcontroller.Pin  # GPIO36
MISO: microcontroller.Pin  # GPIO37
D37: microcontroller.Pin  # GPIO37
SCL: microcontroller.Pin  # GPIO41
D41: microcontroller.Pin  # GPIO41
SDA: microcontroller.Pin  # GPIO42
D42: microcontroller.Pin  # GPIO42
TFT_CS: microcontroller.Pin  # GPIO7
TFT_DC: microcontroller.Pin  # GPIO39
TFT_RESET: microcontroller.Pin  # GPIO40
TFT_BACKLIGHT: microcontroller.Pin  # GPIO45
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0


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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
