# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack CoreS3
 - port: espressif
 - board_id: m5stack_cores3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_connection_manager, adafruit_display_shapes, adafruit_display_text, adafruit_fakerequests, adafruit_requests, neopixel
"""

# Imports
import busio
import displayio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
MOSI: microcontroller.Pin  # GPIO37
MISO: microcontroller.Pin  # GPIO35
SCK: microcontroller.Pin  # GPIO36
RX: microcontroller.Pin  # GPIO44
D44: microcontroller.Pin  # GPIO44
PORTC_RX: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
SDA: microcontroller.Pin  # GPIO12
D12: microcontroller.Pin  # GPIO12
PORTA_SDA: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
A2: microcontroller.Pin  # GPIO2
D6: microcontroller.Pin  # GPIO6
A6: microcontroller.Pin  # GPIO6
D5: microcontroller.Pin  # GPIO6
TX: microcontroller.Pin  # GPIO43
D43: microcontroller.Pin  # GPIO43
PORTC_TX: microcontroller.Pin  # GPIO17
D17: microcontroller.Pin  # GPIO17
SCL: microcontroller.Pin  # GPIO11
PORTA_SCL: microcontroller.Pin  # GPIO1
D7: microcontroller.Pin  # GPIO7
A7: microcontroller.Pin  # GPIO7
PORTB_IN: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
PORTB_OUT: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
I2S_BIT_CLOCK: microcontroller.Pin  # GPIO34
I2S_WORD_SELECT: microcontroller.Pin  # GPIO33
IS2_DATA: microcontroller.Pin  # GPIO13
IS2_MASTER_CLOCK: microcontroller.Pin  # GPIO0
CAMERA_DATA9: microcontroller.Pin  # GPIO47
CAMERA_DATA8: microcontroller.Pin  # GPIO48
CAMERA_DATA7: microcontroller.Pin  # GPIO16
CAMERA_DATA6: microcontroller.Pin  # GPIO15
CAMERA_DATA5: microcontroller.Pin  # GPIO42
CAMERA_DATA4: microcontroller.Pin  # GPIO41
CAMERA_DATA3: microcontroller.Pin  # GPIO40
CAMERA_DATA2: microcontroller.Pin  # GPIO39
CAMERA_VSYNC: microcontroller.Pin  # GPIO46
CAMERA_HREF: microcontroller.Pin  # GPIO38
CAMERA_PCLK: microcontroller.Pin  # GPIO45
CAMERA_XCLK: microcontroller.Pin  # GPIO2
TFT_CS: microcontroller.Pin  # GPIO3
TFT_DC: microcontroller.Pin  # GPIO35
I2C_INTERRUPT: microcontroller.Pin  # GPIO21
SDCARD_CS: microcontroller.Pin  # GPIO4
BOOT0: microcontroller.Pin  # GPIO0


# Members:
CAMERA_DATA: Tuple[Any]

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
