# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for NodeMcu-ESP32-C2
 - port: espressif
 - board_id: nodemcu_esp32c2
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, espidf, espnow, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, microcontroller, msgpack, nvm, onewireio, os, os.getenv, ps2io, pwmio, rainbowio, random, re, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
IO18: microcontroller.Pin  # GPIO18
IO10: microcontroller.Pin  # GPIO10
IO9: microcontroller.Pin  # GPIO9
IO7: microcontroller.Pin  # GPIO7
IO6: microcontroller.Pin  # GPIO6
IO20: microcontroller.Pin  # GPIO20
TX0: microcontroller.Pin  # GPIO20
TX: microcontroller.Pin  # GPIO20
IO19: microcontroller.Pin  # GPIO19
RX0: microcontroller.Pin  # GPIO19
RX: microcontroller.Pin  # GPIO19


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
