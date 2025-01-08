# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Artisense Reference Design RD00
 - port: espressif
 - board_id: artisense_rd00
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO1
IO1: microcontroller.Pin  # GPIO2
IO2: microcontroller.Pin  # GPIO6
IO3: microcontroller.Pin  # GPIO7
IO4: microcontroller.Pin  # GPIO8
CAM: microcontroller.Pin  # GPIO9
HVIO0: microcontroller.Pin  # GPIO1
HVIO1: microcontroller.Pin  # GPIO2
HVIO2: microcontroller.Pin  # GPIO6
HVIO3: microcontroller.Pin  # GPIO7
HVIO4: microcontroller.Pin  # GPIO8
HVCAM: microcontroller.Pin  # GPIO9
LVIO0: microcontroller.Pin  # GPIO34
LVIO1: microcontroller.Pin  # GPIO33
LVIO2: microcontroller.Pin  # GPIO21
LVIO3: microcontroller.Pin  # GPIO5
LVIO4: microcontroller.Pin  # GPIO13
LVCAM: microcontroller.Pin  # GPIO12
DIRIO0: microcontroller.Pin  # GPIO4
DIRIO1: microcontroller.Pin  # GPIO3
DIRIO2: microcontroller.Pin  # GPIO14
DIRIO3: microcontroller.Pin  # GPIO15
DIRIO4: microcontroller.Pin  # GPIO10
DIRCAM: microcontroller.Pin  # GPIO11
D1: microcontroller.Pin  # GPIO42
D2: microcontroller.Pin  # GPIO41
D3: microcontroller.Pin  # GPIO40
D4: microcontroller.Pin  # GPIO39
D5: microcontroller.Pin  # GPIO38
D6: microcontroller.Pin  # GPIO37
D7: microcontroller.Pin  # GPIO36
D8: microcontroller.Pin  # GPIO35
DBG_TX: microcontroller.Pin  # GPIO43
DBG_RX: microcontroller.Pin  # GPIO44
TX: microcontroller.Pin  # GPIO17
RX: microcontroller.Pin  # GPIO18
RS232_TX: microcontroller.Pin  # GPIO17
RS232_RX: microcontroller.Pin  # GPIO18
RS232_EN: microcontroller.Pin  # GPIO16
DFU: microcontroller.Pin  # GPIO0
SW1: microcontroller.Pin  # GPIO0
BOOT: microcontroller.Pin  # GPIO0
NEOPIXEL: microcontroller.Pin  # GPIO45


# Members:

# Unmapped:
#   none
