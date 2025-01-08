# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for senseBox MCU-S2 ESP32S2
 - port: espressif
 - board_id: sensebox_mcu_esp32s2
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
SDA: microcontroller.Pin  # GPIO39
SCL: microcontroller.Pin  # GPIO40
SDA1: microcontroller.Pin  # GPIO45
SCL1: microcontroller.Pin  # GPIO42
D0: microcontroller.Pin  # GPIO0
D1: microcontroller.Pin  # GPIO1
D2: microcontroller.Pin  # GPIO2
D3: microcontroller.Pin  # GPIO3
D4: microcontroller.Pin  # GPIO4
D5: microcontroller.Pin  # GPIO5
D6: microcontroller.Pin  # GPIO6
D7: microcontroller.Pin  # GPIO7
A2: microcontroller.Pin  # GPIO2
A3: microcontroller.Pin  # GPIO3
A4: microcontroller.Pin  # GPIO4
A5: microcontroller.Pin  # GPIO5
A6: microcontroller.Pin  # GPIO6
A7: microcontroller.Pin  # GPIO7
IO_POWER: microcontroller.Pin  # GPIO8
SD_POWER: microcontroller.Pin  # GPIO9
PD_POWER: microcontroller.Pin  # GPIO21
UART_POWER: microcontroller.Pin  # GPIO26
XBEE_POWER: microcontroller.Pin  # GPIO41
PD_PIN: microcontroller.Pin  # GPIO14
SD_CS: microcontroller.Pin  # GPIO10
SD_MOSI: microcontroller.Pin  # GPIO11
SD_SCLK: microcontroller.Pin  # GPIO12
SD_MISO: microcontroller.Pin  # GPIO13
XB_INT: microcontroller.Pin  # GPIO33
XB_CS: microcontroller.Pin  # GPIO34
XB_MOSI: microcontroller.Pin  # GPIO35
XB_SCLK: microcontroller.Pin  # GPIO36
XB_MISO: microcontroller.Pin  # GPIO37
XB_RESET: microcontroller.Pin  # GPIO38
XB_TX: microcontroller.Pin  # GPIO17
XB_RX: microcontroller.Pin  # GPIO18
NEOPIXEL: microcontroller.Pin  # GPIO1
MOSI: microcontroller.Pin  # GPIO35
D35: microcontroller.Pin  # GPIO35
SCK: microcontroller.Pin  # GPIO36
D36: microcontroller.Pin  # GPIO36
MISO: microcontroller.Pin  # GPIO37
D37: microcontroller.Pin  # GPIO37
RX: microcontroller.Pin  # GPIO44
RX1: microcontroller.Pin  # GPIO17
D38: microcontroller.Pin  # GPIO38
TX: microcontroller.Pin  # GPIO43
TX1: microcontroller.Pin  # GPIO18
D39: microcontroller.Pin  # GPIO39


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
