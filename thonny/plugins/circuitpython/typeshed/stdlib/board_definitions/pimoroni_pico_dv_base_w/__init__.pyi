# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Pimoroni Pico DV Base W
 - port: raspberrypi
 - board_id: pimoroni_pico_dv_base_w
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, cyw43, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, picodvi, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, socketpool, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: adafruit_sdcard
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1
GP1: microcontroller.Pin  # GPIO1
GP2: microcontroller.Pin  # GPIO2
GP3: microcontroller.Pin  # GPIO3
GP4: microcontroller.Pin  # GPIO4
GP5: microcontroller.Pin  # GPIO5
GP6: microcontroller.Pin  # GPIO6
GP7: microcontroller.Pin  # GPIO7
GP8: microcontroller.Pin  # GPIO8
GP9: microcontroller.Pin  # GPIO9
GP10: microcontroller.Pin  # GPIO10
GP11: microcontroller.Pin  # GPIO11
GP12: microcontroller.Pin  # GPIO12
GP13: microcontroller.Pin  # GPIO13
BUTTON_A: microcontroller.Pin  # GPIO14
GP14: microcontroller.Pin  # GPIO14
BUTTON_B: microcontroller.Pin  # GPIO15
GP15: microcontroller.Pin  # GPIO15
BUTTON_C: microcontroller.Pin  # GPIO16
GP16: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
GP18: microcontroller.Pin  # GPIO18
GP19: microcontroller.Pin  # GPIO19
GP20: microcontroller.Pin  # GPIO20
GP21: microcontroller.Pin  # GPIO21
GP22: microcontroller.Pin  # GPIO22
SD_SCK: microcontroller.Pin  # GPIO5
SD_MOSI: microcontroller.Pin  # GPIO18
SD_MISO: microcontroller.Pin  # GPIO19
SD_CS: microcontroller.Pin  # GPIO22
SMPS_MODE: microcontroller.Pin  # CYW1
LED: microcontroller.Pin  # CYW0
VBUS_SENSE: microcontroller.Pin  # CYW2
I2S_DATA: microcontroller.Pin  # GPIO26
GP26_A0: microcontroller.Pin  # GPIO26
GP26: microcontroller.Pin  # GPIO26
A0: microcontroller.Pin  # GPIO26
I2S_BIT_CLOCK: microcontroller.Pin  # GPIO27
GP27_A1: microcontroller.Pin  # GPIO27
GP27: microcontroller.Pin  # GPIO27
A1: microcontroller.Pin  # GPIO27
I2S_WORD_SELECT: microcontroller.Pin  # GPIO28
GP28_A2: microcontroller.Pin  # GPIO28
GP28: microcontroller.Pin  # GPIO28
A2: microcontroller.Pin  # GPIO28
A3: microcontroller.Pin  # GPIO29
VOLTAGE_MONITOR: microcontroller.Pin  # GPIO29
DV_CEC: microcontroller.Pin  # GPIO2
DV_SCL: microcontroller.Pin  # GPIO3
DV_SDA: microcontroller.Pin  # GPIO4
CKN: microcontroller.Pin  # GPIO6
CKP: microcontroller.Pin  # GPIO7
D0N: microcontroller.Pin  # GPIO8
D0P: microcontroller.Pin  # GPIO9
D1N: microcontroller.Pin  # GPIO10
D1P: microcontroller.Pin  # GPIO11
D2N: microcontroller.Pin  # GPIO12
D2P: microcontroller.Pin  # GPIO13
DV_HPD: microcontroller.Pin  # GPIO17


# Members:

# Unmapped:
#   none
