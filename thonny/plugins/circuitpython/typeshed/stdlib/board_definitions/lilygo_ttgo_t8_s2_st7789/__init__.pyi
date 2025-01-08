# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for LILYGO TTGO T8 ESP32-S2 w/Display
 - port: espressif
 - board_id: lilygo_ttgo_t8_s2_st7789
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
IO0: microcontroller.Pin  # GPIO0
IO1: microcontroller.Pin  # GPIO1
IO2: microcontroller.Pin  # GPIO2
IO3: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
IO5: microcontroller.Pin  # GPIO5
IO6: microcontroller.Pin  # GPIO6
IO7: microcontroller.Pin  # GPIO7
IO8: microcontroller.Pin  # GPIO8
IO9: microcontroller.Pin  # GPIO9
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO15: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
IO17: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
IO20: microcontroller.Pin  # GPIO20
IO21: microcontroller.Pin  # GPIO21
IO39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
IO41: microcontroller.Pin  # GPIO41
IO42: microcontroller.Pin  # GPIO42
IO45: microcontroller.Pin  # GPIO45
IO46: microcontroller.Pin  # GPIO46
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
TX1: microcontroller.Pin  # GPIO17
RX1: microcontroller.Pin  # GPIO18
SD_MISO: microcontroller.Pin  # GPIO13
SD_MOSI: microcontroller.Pin  # GPIO11
SD_CLK: microcontroller.Pin  # GPIO12
SD_CS: microcontroller.Pin  # GPIO10
LCD_MOSI: microcontroller.Pin  # GPIO35
LCD_CLK: microcontroller.Pin  # GPIO36
LCD_CS: microcontroller.Pin  # GPIO34
LCD_RST: microcontroller.Pin  # GPIO38
LCD_BCKL: microcontroller.Pin  # GPIO33
LCD_D_C: microcontroller.Pin  # GPIO37
PE_POWER: microcontroller.Pin  # GPIO14
BATTERY: microcontroller.Pin  # GPIO9


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
