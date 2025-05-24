# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for BPI-PicoW-S3
 - port: espressif
 - board_id: bpi_picow_s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
GP0: microcontroller.Pin  # GPIO43
GP1: microcontroller.Pin  # GPIO44
GP2: microcontroller.Pin  # GPIO47
GP3: microcontroller.Pin  # GPIO17
GP4: microcontroller.Pin  # GPIO15
GP5: microcontroller.Pin  # GPIO13
GP6: microcontroller.Pin  # GPIO12
GP7: microcontroller.Pin  # GPIO14
GP8: microcontroller.Pin  # GPIO18
GP9: microcontroller.Pin  # GPIO16
GP10: microcontroller.Pin  # GPIO21
GP11: microcontroller.Pin  # GPIO38
GP12: microcontroller.Pin  # GPIO39
GP13: microcontroller.Pin  # GPIO40
GP14: microcontroller.Pin  # GPIO41
GP15: microcontroller.Pin  # GPIO42
GP16: microcontroller.Pin  # GPIO1
GP17: microcontroller.Pin  # GPIO2
GP18: microcontroller.Pin  # GPIO3
GP19: microcontroller.Pin  # GPIO4
GP20: microcontroller.Pin  # GPIO5
GP21: microcontroller.Pin  # GPIO6
GP22: microcontroller.Pin  # GPIO7
GP25: microcontroller.Pin  # GPIO46
LED: microcontroller.Pin  # GPIO46
GP26: microcontroller.Pin  # GPIO8
GP26_A0: microcontroller.Pin  # GPIO8
A0: microcontroller.Pin  # GPIO8
GP27: microcontroller.Pin  # GPIO9
GP27_A1: microcontroller.Pin  # GPIO9
A1: microcontroller.Pin  # GPIO9
GP28: microcontroller.Pin  # GPIO10
GP28_A2: microcontroller.Pin  # GPIO10
A2: microcontroller.Pin  # GPIO10
GP29: microcontroller.Pin  # GPIO11
GP29_A3: microcontroller.Pin  # GPIO11
A3: microcontroller.Pin  # GPIO11
NEOPIXEL: microcontroller.Pin  # GPIO48
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
BOOT0: microcontroller.Pin  # GPIO0


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
