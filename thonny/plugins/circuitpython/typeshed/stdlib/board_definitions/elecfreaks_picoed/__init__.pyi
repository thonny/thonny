# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ELECFREAKS PICO:ED
 - port: raspberrypi
 - board_id: elecfreaks_picoed
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: adafruit_is31fl3731, adafruit_motor, adafruit_ticks, asyncio, elecfreaks_music, neopixel, picoed
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
BUZZER_GP0: microcontroller.Pin  # GPIO0
I2C0_SDA: microcontroller.Pin  # GPIO0
I2C0_SCL: microcontroller.Pin  # GPIO1
BUZZER: microcontroller.Pin  # GPIO3
BUZZER_GP3: microcontroller.Pin  # GPIO3
P4: microcontroller.Pin  # GPIO4
P5: microcontroller.Pin  # GPIO5
P6: microcontroller.Pin  # GPIO6
P7: microcontroller.Pin  # GPIO7
P8: microcontroller.Pin  # GPIO8
P9: microcontroller.Pin  # GPIO9
P10: microcontroller.Pin  # GPIO10
P11: microcontroller.Pin  # GPIO11
P12: microcontroller.Pin  # GPIO12
P13: microcontroller.Pin  # GPIO13
P14: microcontroller.Pin  # GPIO14
P15: microcontroller.Pin  # GPIO15
P16: microcontroller.Pin  # GPIO16
SDA: microcontroller.Pin  # GPIO18
P20: microcontroller.Pin  # GPIO18
SCL: microcontroller.Pin  # GPIO19
P19: microcontroller.Pin  # GPIO19
BUTTON_A: microcontroller.Pin  # GPIO20
BUTTON_B: microcontroller.Pin  # GPIO21
SMPS_MODE: microcontroller.Pin  # GPIO23
VBUS_SENSE: microcontroller.Pin  # GPIO24
LED: microcontroller.Pin  # GPIO25
P0_A0: microcontroller.Pin  # GPIO26
P0: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
P1_A1: microcontroller.Pin  # GPIO27
P1: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
P2_A2: microcontroller.Pin  # GPIO28
P2: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
P3_A3: microcontroller.Pin  # GPIO29
P3: microcontroller.Pin  # GPIO29
A3: microcontroller.Pin  # GPIO29


# Members:

# Unmapped:
#   none
