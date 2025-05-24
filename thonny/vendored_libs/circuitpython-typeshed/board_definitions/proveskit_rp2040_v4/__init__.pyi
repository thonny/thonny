# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for PROVES Kit v4
 - port: raspberrypi
 - board_id: proveskit_rp2040_v4
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SPI0_CS1: microcontroller.Pin  # GPIO26
NEO_PWR: microcontroller.Pin  # GPIO27
SPI0_CS2: microcontroller.Pin  # GPIO28
D0: microcontroller.Pin  # GPIO29
D8: microcontroller.Pin  # GPIO18
D9: microcontroller.Pin  # GPIO19
D6: microcontroller.Pin  # GPIO16
TX: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1
I2C1_SDA: microcontroller.Pin  # GPIO2
I2C1_SCL: microcontroller.Pin  # GPIO3
I2C0_SDA: microcontroller.Pin  # GPIO4
I2C0_SCL: microcontroller.Pin  # GPIO5
PC: microcontroller.Pin  # GPIO6
VS: microcontroller.Pin  # GPIO7
SPI0_MISO: microcontroller.Pin  # GPIO8
SPI0_CS0: microcontroller.Pin  # GPIO9
SPI0_SCK: microcontroller.Pin  # GPIO10
SPI0_MOSI: microcontroller.Pin  # GPIO11
D2: microcontroller.Pin  # GPIO12
D3: microcontroller.Pin  # GPIO13
D4: microcontroller.Pin  # GPIO14
D5: microcontroller.Pin  # GPIO15
RF1_RST: microcontroller.Pin  # GPIO20
WDT_WDI: microcontroller.Pin  # GPIO21
RF1_IO4: microcontroller.Pin  # GPIO22
RF1_IO0: microcontroller.Pin  # GPIO23
NEOPIX: microcontroller.Pin  # GPIO24
HS: microcontroller.Pin  # GPIO25
D7: microcontroller.Pin  # GPIO17


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


# Unmapped:
#   none
