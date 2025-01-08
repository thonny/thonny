# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Deneyap Kart
 - port: espressif
 - board_id: deneyap_kart
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # GPIO23
PWM0: microcontroller.Pin  # GPIO23
CAMD4: microcontroller.Pin  # GPIO23
D1: microcontroller.Pin  # GPIO22
PWM1: microcontroller.Pin  # GPIO22
CAMD3: microcontroller.Pin  # GPIO22
TX: microcontroller.Pin  # GPIO1
D2: microcontroller.Pin  # GPIO1
LEDG: microcontroller.Pin  # GPIO1
RX: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
LEDR: microcontroller.Pin  # GPIO3
D4: microcontroller.Pin  # GPIO21
SS: microcontroller.Pin  # GPIO21
CAMD5: microcontroller.Pin  # GPIO21
SCK: microcontroller.Pin  # GPIO19
D5: microcontroller.Pin  # GPIO19
CAMD2: microcontroller.Pin  # GPIO19
MISO: microcontroller.Pin  # GPIO18
D6: microcontroller.Pin  # GPIO18
CAMD6: microcontroller.Pin  # GPIO18
MOSI: microcontroller.Pin  # GPIO5
D7: microcontroller.Pin  # GPIO5
CAMPC: microcontroller.Pin  # GPIO5
D8: microcontroller.Pin  # GPIO0
BOOT: microcontroller.Pin  # GPIO0
GPKEY: microcontroller.Pin  # GPIO0
D9: microcontroller.Pin  # GPIO2
SDA: microcontroller.Pin  # GPIO4
D10: microcontroller.Pin  # GPIO4
IMUSD: microcontroller.Pin  # GPIO4
LEDB: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO15
D11: microcontroller.Pin  # GPIO15
IMUSC: microcontroller.Pin  # GPIO15
D12: microcontroller.Pin  # GPIO13
T5: microcontroller.Pin  # GPIO13
MICC: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO12
T4: microcontroller.Pin  # GPIO12
MICD: microcontroller.Pin  # GPIO12
D14: microcontroller.Pin  # GPIO14
T3: microcontroller.Pin  # GPIO14
D15: microcontroller.Pin  # GPIO27
T2: microcontroller.Pin  # GPIO27
A0: microcontroller.Pin  # GPIO36
CAMV: microcontroller.Pin  # GPIO36
A1: microcontroller.Pin  # GPIO39
CAMH: microcontroller.Pin  # GPIO39
A2: microcontroller.Pin  # GPIO34
CAMD9: microcontroller.Pin  # GPIO34
A3: microcontroller.Pin  # GPIO35
CAMD8: microcontroller.Pin  # GPIO35
A4: microcontroller.Pin  # GPIO32
T0: microcontroller.Pin  # GPIO32
CAMXC: microcontroller.Pin  # GPIO32
A5: microcontroller.Pin  # GPIO33
T1: microcontroller.Pin  # GPIO33
CAMSD: microcontroller.Pin  # GPIO33
DAC1: microcontroller.Pin  # GPIO25
CAMSC: microcontroller.Pin  # GPIO25
DAC2: microcontroller.Pin  # GPIO26
CAMD7: microcontroller.Pin  # GPIO26


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


# Unmapped:
#   none
