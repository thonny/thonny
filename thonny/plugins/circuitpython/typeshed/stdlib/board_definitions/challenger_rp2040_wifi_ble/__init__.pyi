# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Challenger RP2040 WiFi/BLE
 - port: raspberrypi
 - board_id: challenger_rp2040_wifi_ble
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SDA: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
SCL: microcontroller.Pin  # GPIO1
GP1: microcontroller.Pin  # GPIO1
D5: microcontroller.Pin  # GPIO2
GP2: microcontroller.Pin  # GPIO2
D6: microcontroller.Pin  # GPIO3
GP3: microcontroller.Pin  # GPIO3
ESP_TX: microcontroller.Pin  # GPIO4
GP4: microcontroller.Pin  # GPIO4
ESP_RX: microcontroller.Pin  # GPIO5
GP5: microcontroller.Pin  # GPIO5
D9: microcontroller.Pin  # GPIO6
GP6: microcontroller.Pin  # GPIO6
D10: microcontroller.Pin  # GPIO7
GP7: microcontroller.Pin  # GPIO7
D11: microcontroller.Pin  # GPIO8
GP8: microcontroller.Pin  # GPIO8
D12: microcontroller.Pin  # GPIO9
GP9: microcontroller.Pin  # GPIO9
D13: microcontroller.Pin  # GPIO10
LED: microcontroller.Pin  # GPIO10
GP10: microcontroller.Pin  # GPIO10
NEOPIXEL: microcontroller.Pin  # GPIO11
GP11: microcontroller.Pin  # GPIO11
WIFI_MODE: microcontroller.Pin  # GPIO24
WIFI_RESET: microcontroller.Pin  # GPIO19
D0: microcontroller.Pin  # GPIO16
TX: microcontroller.Pin  # GPIO16
GP16: microcontroller.Pin  # GPIO16
D1: microcontroller.Pin  # GPIO17
RX: microcontroller.Pin  # GPIO17
GP17: microcontroller.Pin  # GPIO17
SCK: microcontroller.Pin  # GPIO22
GP22: microcontroller.Pin  # GPIO22
MOSI: microcontroller.Pin  # GPIO23
GP23: microcontroller.Pin  # GPIO23
MISO: microcontroller.Pin  # GPIO20
GP20: microcontroller.Pin  # GPIO20
A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A3: microcontroller.Pin  # GPIO29
GP29: microcontroller.Pin  # GPIO29
A4: microcontroller.Pin  # GPIO25
GP25: microcontroller.Pin  # GPIO25
A5: microcontroller.Pin  # GPIO21
GP21: microcontroller.Pin  # GPIO21


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
