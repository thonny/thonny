# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for VCC-GND YD-ESP32-S3 (N8R8)
 - port: espressif
 - board_id: yd_esp32_s3_n8r8
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
GPIO4: microcontroller.Pin  # GPIO4
GPIO5: microcontroller.Pin  # GPIO5
GPIO6: microcontroller.Pin  # GPIO6
GPIO7: microcontroller.Pin  # GPIO7
GPIO15: microcontroller.Pin  # GPIO15
GPIO16: microcontroller.Pin  # GPIO16
GPIO17: microcontroller.Pin  # GPIO17
GPIO18: microcontroller.Pin  # GPIO18
GPIO8: microcontroller.Pin  # GPIO8
GPIO3: microcontroller.Pin  # GPIO3
GPIO46: microcontroller.Pin  # GPIO46
GPIO9: microcontroller.Pin  # GPIO9
GPIO10: microcontroller.Pin  # GPIO10
GPIO11: microcontroller.Pin  # GPIO11
GPIO12: microcontroller.Pin  # GPIO12
GPIO13: microcontroller.Pin  # GPIO13
GPIO14: microcontroller.Pin  # GPIO14
GPIO43: microcontroller.Pin  # GPIO43
TX: microcontroller.Pin  # GPIO43
GPIO44: microcontroller.Pin  # GPIO44
RX: microcontroller.Pin  # GPIO44
GPIO1: microcontroller.Pin  # GPIO1
GPIO2: microcontroller.Pin  # GPIO2
GPIO14: microcontroller.Pin  # GPIO14
GPIO42: microcontroller.Pin  # GPIO42
GPIO41: microcontroller.Pin  # GPIO41
GPIO40: microcontroller.Pin  # GPIO40
GPIO39: microcontroller.Pin  # GPIO39
GPIO38: microcontroller.Pin  # GPIO38
GPIO37: microcontroller.Pin  # GPIO37
GPIO36: microcontroller.Pin  # GPIO36
GPIO35: microcontroller.Pin  # GPIO35
GPIO0: microcontroller.Pin  # GPIO0
BOOT: microcontroller.Pin  # GPIO0
GPIO45: microcontroller.Pin  # GPIO45
GPIO48: microcontroller.Pin  # GPIO48
NEOPIXEL: microcontroller.Pin  # GPIO48
GPIO47: microcontroller.Pin  # GPIO47
GPIO21: microcontroller.Pin  # GPIO21


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
