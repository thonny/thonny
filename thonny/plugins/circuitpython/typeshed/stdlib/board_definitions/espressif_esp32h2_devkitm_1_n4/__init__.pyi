# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ESP32-H2-DevKitM-1
 - port: espressif
 - board_id: espressif_esp32h2_devkitm_1_n4
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool.socketpool.AF_INET6, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, vectorio, warnings, watchdog, zlib
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
IO8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
IO10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO22: microcontroller.Pin  # GPIO22
RX: microcontroller.Pin  # GPIO23
TX: microcontroller.Pin  # GPIO24
IO25: microcontroller.Pin  # GPIO25
MTMS: microcontroller.Pin  # GPIO2
MTDO: microcontroller.Pin  # GPIO3
MTCK: microcontroller.Pin  # GPIO4
MTDI: microcontroller.Pin  # GPIO5
BUTTON: microcontroller.Pin  # GPIO9
NEOPIXEL: microcontroller.Pin  # GPIO8


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
