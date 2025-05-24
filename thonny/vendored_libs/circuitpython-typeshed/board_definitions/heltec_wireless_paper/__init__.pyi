# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Heltec Wireless Paper
 - port: espressif
 - board_id: heltec_wireless_paper
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
BUTTON0: microcontroller.Pin  # GPIO0
LED0: microcontroller.Pin  # GPIO18
ADC_CTRL: microcontroller.Pin  # GPIO19
ADC_IN: microcontroller.Pin  # GPIO20
BATTERY: microcontroller.Pin  # GPIO20
VEXT_CTRL: microcontroller.Pin  # GPIO45
DEBUG_TX: microcontroller.Pin  # GPIO43
DEBUG_RX: microcontroller.Pin  # GPIO44
LORA_CS: microcontroller.Pin  # GPIO8
LORA_SCK: microcontroller.Pin  # GPIO9
LORA_MOSI: microcontroller.Pin  # GPIO10
LORA_MISO: microcontroller.Pin  # GPIO11
LORA_RESET: microcontroller.Pin  # GPIO12
LORA_BUSY: microcontroller.Pin  # GPIO13
LORA_DIO1: microcontroller.Pin  # GPIO14
EPD_MOSI: microcontroller.Pin  # GPIO2
EPD_SCK: microcontroller.Pin  # GPIO3
EPD_CS: microcontroller.Pin  # GPIO4
EPD_DC: microcontroller.Pin  # GPIO5
EPD_RES: microcontroller.Pin  # GPIO6
EPD_BUSY: microcontroller.Pin  # GPIO7


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

"""Returns the `displayio.EPaperDisplay` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.EPaperDisplay`.
"""
DISPLAY: displayio.EPaperDisplay


# Unmapped:
#   none
