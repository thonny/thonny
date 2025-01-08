# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Core2
 - port: espressif
 - board_id: m5stack_core2
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_connection_manager, adafruit_display_text, adafruit_fakerequests, adafruit_requests, neopixel
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
MOSI: microcontroller.Pin  # GPIO23
D23: microcontroller.Pin  # GPIO23
MISO: microcontroller.Pin  # GPIO38
D38: microcontroller.Pin  # GPIO38
SCK: microcontroller.Pin  # GPIO18
D18: microcontroller.Pin  # GPIO18
D3: microcontroller.Pin  # GPIO3
PORTC_RX: microcontroller.Pin  # GPIO13
RX2: microcontroller.Pin  # GPIO13
D13: microcontroller.Pin  # GPIO13
SDA: microcontroller.Pin  # GPIO21
D21: microcontroller.Pin  # GPIO21
PORTA_SDA: microcontroller.Pin  # GPIO32
D32: microcontroller.Pin  # GPIO32
D27: microcontroller.Pin  # GPIO27
A27: microcontroller.Pin  # GPIO27
I2S_SDO: microcontroller.Pin  # GPIO2
D2: microcontroller.Pin  # GPIO2
A35: microcontroller.Pin  # GPIO35
D35: microcontroller.Pin  # GPIO35
PORTB_IN: microcontroller.Pin  # GPIO36
A36: microcontroller.Pin  # GPIO36
D36: microcontroller.Pin  # GPIO36
A25: microcontroller.Pin  # GPIO25
D25: microcontroller.Pin  # GPIO25
PORTB_OUT: microcontroller.Pin  # GPIO26
A26: microcontroller.Pin  # GPIO26
D26: microcontroller.Pin  # GPIO26
D1: microcontroller.Pin  # GPIO1
PORTC_TX: microcontroller.Pin  # GPIO14
TX2: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
SCL: microcontroller.Pin  # GPIO22
D22: microcontroller.Pin  # GPIO22
PORTA_SCL: microcontroller.Pin  # GPIO33
D33: microcontroller.Pin  # GPIO33
D19: microcontroller.Pin  # GPIO19
I2S_LRC: microcontroller.Pin  # GPIO0
I2S_PDM_MIC_CLOCK: microcontroller.Pin  # GPIO0
D0: microcontroller.Pin  # GPIO0
I2S_PDM_MIC_DATA: microcontroller.Pin  # GPIO34
D34: microcontroller.Pin  # GPIO34
A34: microcontroller.Pin  # GPIO34
I2S_SCK: microcontroller.Pin  # GPIO12
TFT_CS: microcontroller.Pin  # GPIO5
TFT_DC: microcontroller.Pin  # GPIO15
SD_CS: microcontroller.Pin  # GPIO4
TOUCH_INT: microcontroller.Pin  # GPIO39


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
