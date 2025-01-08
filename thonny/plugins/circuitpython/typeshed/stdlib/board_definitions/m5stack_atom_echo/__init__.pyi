# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Atom Echo
 - port: espressif
 - board_id: m5stack_atom_echo
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SPK_I2S_SDO: microcontroller.Pin  # GPIO22
SPK_I2S_SCK: microcontroller.Pin  # GPIO19
SPK_I2S_LRC: microcontroller.Pin  # GPIO33
PDM_MIC_CLK: microcontroller.Pin  # GPIO33
PDM_MIC_DATA: microcontroller.Pin  # GPIO23
SCL: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
SDA: microcontroller.Pin  # GPIO25
A25: microcontroller.Pin  # GPIO25
D25: microcontroller.Pin  # GPIO25
DAC1: microcontroller.Pin  # GPIO25
PORTA_SDA: microcontroller.Pin  # GPIO26
A26: microcontroller.Pin  # GPIO26
D26: microcontroller.Pin  # GPIO26
DAC2: microcontroller.Pin  # GPIO25
PORTA_SCL: microcontroller.Pin  # GPIO32
A32: microcontroller.Pin  # GPIO32
D32: microcontroller.Pin  # GPIO32
NEOPIXEL: microcontroller.Pin  # GPIO27
BTN: microcontroller.Pin  # GPIO39
IR_LED: microcontroller.Pin  # GPIO12


# Members:
def PORTA_I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
