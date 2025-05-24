# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Music Thing Modular Workshop Computer
 - port: raspberrypi
 - board_id: mtm_computer
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiodelays, audiofilters, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
UART_TX: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
UART_RX: microcontroller.Pin  # GPIO1
GP1: microcontroller.Pin  # GPIO1
PULSE_1_IN: microcontroller.Pin  # GPIO2
GP2: microcontroller.Pin  # GPIO2
PULSE_2_IN: microcontroller.Pin  # GPIO3
GP3: microcontroller.Pin  # GPIO3
NORM_PROBE: microcontroller.Pin  # GPIO4
GP4: microcontroller.Pin  # GPIO4
ID0: microcontroller.Pin  # GPIO5
GP5: microcontroller.Pin  # GPIO5
ID1: microcontroller.Pin  # GPIO6
GP6: microcontroller.Pin  # GPIO6
ID2: microcontroller.Pin  # GPIO7
GP7: microcontroller.Pin  # GPIO7
PULSE_1_OUT: microcontroller.Pin  # GPIO8
GP8: microcontroller.Pin  # GPIO8
PULSE_2_OUT: microcontroller.Pin  # GPIO9
GP9: microcontroller.Pin  # GPIO9
LED1: microcontroller.Pin  # GPIO10
GP10: microcontroller.Pin  # GPIO10
LED2: microcontroller.Pin  # GPIO11
GP11: microcontroller.Pin  # GPIO11
LED3: microcontroller.Pin  # GPIO12
GP12: microcontroller.Pin  # GPIO12
LED4: microcontroller.Pin  # GPIO13
GP13: microcontroller.Pin  # GPIO13
LED5: microcontroller.Pin  # GPIO14
GP14: microcontroller.Pin  # GPIO14
LED6: microcontroller.Pin  # GPIO15
GP15: microcontroller.Pin  # GPIO15
EEPROM_SDA: microcontroller.Pin  # GPIO16
GP16: microcontroller.Pin  # GPIO16
EEPROM_SCL: microcontroller.Pin  # GPIO17
GP17: microcontroller.Pin  # GPIO17
DAC_SCK: microcontroller.Pin  # GPIO18
GP18: microcontroller.Pin  # GPIO18
DAC_SDI: microcontroller.Pin  # GPIO19
GP19: microcontroller.Pin  # GPIO19
DAC_CS: microcontroller.Pin  # GPIO21
GP21: microcontroller.Pin  # GPIO21
CV_2_OUT: microcontroller.Pin  # GPIO22
GP22: microcontroller.Pin  # GPIO22
CV_1_OUT: microcontroller.Pin  # GPIO23
GP23: microcontroller.Pin  # GPIO23
MUX_A: microcontroller.Pin  # GPIO24
GP24: microcontroller.Pin  # GPIO24
MUX_B: microcontroller.Pin  # GPIO25
GP25: microcontroller.Pin  # GPIO25
AUDIO_R_IN: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
AUDIO_L_IN: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
MUX_1: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
MUX_2: microcontroller.Pin  # GPIO29
A3: microcontroller.Pin  # GPIO29
GP29: microcontroller.Pin  # GPIO29


# Members:

# Unmapped:
#   none
