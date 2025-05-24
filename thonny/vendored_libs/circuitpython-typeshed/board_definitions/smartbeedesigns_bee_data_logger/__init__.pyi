# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Bee-Data-Logger
 - port: espressif
 - board_id: smartbeedesigns_bee_data_logger
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_bus_device, adafruit_ds3231, adafruit_register, adafruit_sdcard, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO3: microcontroller.Pin  # GPIO3
A3: microcontroller.Pin  # GPIO3
D3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
A4: microcontroller.Pin  # GPIO4
D4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
A5: microcontroller.Pin  # GPIO5
D5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
A6: microcontroller.Pin  # GPIO6
D6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
A7: microcontroller.Pin  # GPIO7
D7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
A8: microcontroller.Pin  # GPIO8
D8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
A9: microcontroller.Pin  # GPIO9
D9: microcontroller.Pin  # GPIO9
IO38: microcontroller.Pin  # GPIO38
D38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
D39: microcontroller.Pin  # GPIO39
IO41: microcontroller.Pin  # GPIO41
D41: microcontroller.Pin  # GPIO41
IO42: microcontroller.Pin  # GPIO42
D42: microcontroller.Pin  # GPIO42
IO36: microcontroller.Pin  # GPIO36
SCL: microcontroller.Pin  # GPIO36
D36: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
SDA: microcontroller.Pin  # GPIO37
D37: microcontroller.Pin  # GPIO37
MISO: microcontroller.Pin  # GPIO45
MOSI: microcontroller.Pin  # GPIO46
SD_CS: microcontroller.Pin  # GPIO47
SCK: microcontroller.Pin  # GPIO48
IO48: microcontroller.Pin  # GPIO48
NEOPIXEL: microcontroller.Pin  # GPIO40
NEOPIXEL_POWER: microcontroller.Pin  # GPIO34
TX: microcontroller.Pin  # GPIO43
D43: microcontroller.Pin  # GPIO43
IO43: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
IO44: microcontroller.Pin  # GPIO44
D44: microcontroller.Pin  # GPIO44
BOOT_BTN: microcontroller.Pin  # GPIO0
BATTERY: microcontroller.Pin  # GPIO1
VBAT: microcontroller.Pin  # GPIO1
VBAT_SENSE: microcontroller.Pin  # GPIO1
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO1
VBUS_SENSE: microcontroller.Pin  # GPIO2
LDO2: microcontroller.Pin  # GPIO34


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
