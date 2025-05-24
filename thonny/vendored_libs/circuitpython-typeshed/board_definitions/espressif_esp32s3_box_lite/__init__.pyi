# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ESP32-S3-Box-Lite
 - port: espressif
 - board_id: espressif_esp32s3_box_lite
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, dualbank, epaperdisplay, errno, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
G9: microcontroller.Pin  # GPIO9
U0TXD: microcontroller.Pin  # GPIO43
G43: microcontroller.Pin  # GPIO43
U0RXD: microcontroller.Pin  # GPIO44
G44: microcontroller.Pin  # GPIO44
CS: microcontroller.Pin  # GPIO10
G10: microcontroller.Pin  # GPIO10
MOSI: microcontroller.Pin  # GPIO11
G11: microcontroller.Pin  # GPIO11
MISO: microcontroller.Pin  # GPIO13
G13: microcontroller.Pin  # GPIO13
CLK: microcontroller.Pin  # GPIO12
G12: microcontroller.Pin  # GPIO12
G14: microcontroller.Pin  # GPIO14
G38: microcontroller.Pin  # GPIO38
G39: microcontroller.Pin  # GPIO39
SCL2: microcontroller.Pin  # GPIO40
G40: microcontroller.Pin  # GPIO40
SDA2: microcontroller.Pin  # GPIO41
G41: microcontroller.Pin  # GPIO41
G42: microcontroller.Pin  # GPIO42
G21: microcontroller.Pin  # GPIO21
LCD_DC: microcontroller.Pin  # GPIO4
LCD_CS: microcontroller.Pin  # GPIO5
LCD_MOSI: microcontroller.Pin  # GPIO6
LCD_SCK: microcontroller.Pin  # GPIO7
LCD_RST: microcontroller.Pin  # GPIO48
LCD_CTRL: microcontroller.Pin  # GPIO45
CTP_INT: microcontroller.Pin  # GPIO3
I2S_ADC_SDOUT: microcontroller.Pin  # GPIO16
I2S_MCLK: microcontroller.Pin  # GPIO2
I2S_SCLK: microcontroller.Pin  # GPIO17
I2S_LRCK: microcontroller.Pin  # GPIO47
I2S_CODEC_DSDIN: microcontroller.Pin  # GPIO15
PA_CTRL: microcontroller.Pin  # GPIO46
MUTE_STATUS: microcontroller.Pin  # GPIO1
SDA: microcontroller.Pin  # GPIO8
SCL: microcontroller.Pin  # GPIO18
BOOT: microcontroller.Pin  # GPIO0


# Members:
"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
