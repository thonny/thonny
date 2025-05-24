# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ESP32-S3-DevKitC-1-N8R8-with-HACKTABLET
 - port: espressif
 - board_id: espressif_esp32s3_devkitc_1_n8r8_hacktablet
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dotclockframebuffer, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller
from typing import Any, Dict


# Board Info:
board_id: str


# Pins:
de: microcontroller.Pin  # GPIO45
vsync: microcontroller.Pin  # GPIO48
hsync: microcontroller.Pin  # GPIO47
dclk: microcontroller.Pin  # GPIO21
TFT_BACKLIGHT: microcontroller.Pin  # GPIO39
IO0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
TFTB1: microcontroller.Pin  # GPIO3
TFTB2: microcontroller.Pin  # GPIO4
TFTB3: microcontroller.Pin  # GPIO5
TFTB4: microcontroller.Pin  # GPIO6
TFTB5: microcontroller.Pin  # GPIO7
TFTG1: microcontroller.Pin  # GPIO8
TFTG2: microcontroller.Pin  # GPIO9
TFTG3: microcontroller.Pin  # GPIO10
TFTG4: microcontroller.Pin  # GPIO11
TFTG5: microcontroller.Pin  # GPIO12
TFTG6: microcontroller.Pin  # GPIO13
TFTR1: microcontroller.Pin  # GPIO14
TFTR2: microcontroller.Pin  # GPIO15
TFTR3: microcontroller.Pin  # GPIO16
TFTR4: microcontroller.Pin  # GPIO17
TFTR5: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
IO20: microcontroller.Pin  # GPIO20
dclk: microcontroller.Pin  # GPIO21
IO35: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
IO38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
TOUCH_INT: microcontroller.Pin  # GPIO40
SCL: microcontroller.Pin  # GPIO41
SDA: microcontroller.Pin  # GPIO42
IO43: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44
de: microcontroller.Pin  # GPIO45
IO46: microcontroller.Pin  # GPIO46
hsync: microcontroller.Pin  # GPIO47
vsync: microcontroller.Pin  # GPIO48
NEOPIXEL: microcontroller.Pin  # GPIO48
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44


# Members:
TFT_PINS: Dict[str, Any]

TFT_TIMINGS: Dict[str, Any]

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
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
#     { MP_ROM_QSTR(MP_QSTR_red), MP_ROM_PTR(&tft_r_pins) },
#     { MP_ROM_QSTR(MP_QSTR_green), MP_ROM_PTR(&tft_g_pins) },
#     { MP_ROM_QSTR(MP_QSTR_blue), MP_ROM_PTR(&tft_b_pins) },
