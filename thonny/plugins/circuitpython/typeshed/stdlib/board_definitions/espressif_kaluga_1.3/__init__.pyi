# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Kaluga 1
 - port: espressif
 - board_id: espressif_kaluga_1.3
 - NVM size: 8192
 - Included modules: _asyncio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


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
IO10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
IO12: microcontroller.Pin  # GPIO12
IO13: microcontroller.Pin  # GPIO13
IO14: microcontroller.Pin  # GPIO14
IO15: microcontroller.Pin  # GPIO15
IO16: microcontroller.Pin  # GPIO16
IO17: microcontroller.Pin  # GPIO17
IO18: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
IO20: microcontroller.Pin  # GPIO20
IO21: microcontroller.Pin  # GPIO21
IO26: microcontroller.Pin  # GPIO26
IO33: microcontroller.Pin  # GPIO33
IO34: microcontroller.Pin  # GPIO34
IO35: microcontroller.Pin  # GPIO35
IO36: microcontroller.Pin  # GPIO36
IO37: microcontroller.Pin  # GPIO37
IO38: microcontroller.Pin  # GPIO38
IO39: microcontroller.Pin  # GPIO39
IO40: microcontroller.Pin  # GPIO40
IO41: microcontroller.Pin  # GPIO41
IO42: microcontroller.Pin  # GPIO42
TX: microcontroller.Pin  # GPIO43
IO43: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
IO44: microcontroller.Pin  # GPIO44
IO45: microcontroller.Pin  # GPIO45
IO46: microcontroller.Pin  # GPIO46
NEOPIXEL: microcontroller.Pin  # GPIO45
CAMERA_XCLK: microcontroller.Pin  # GPIO1
CAMERA_PCLK: microcontroller.Pin  # GPIO33
CAMERA_HREF: microcontroller.Pin  # GPIO3
CAMERA_VSYNC: microcontroller.Pin  # GPIO2
CAMERA_SIOD: microcontroller.Pin  # GPIO8
CAMERA_SIOC: microcontroller.Pin  # GPIO7
CAMERA_D2: microcontroller.Pin  # GPIO36
CAMERA_D3: microcontroller.Pin  # GPIO37
CAMERA_D4: microcontroller.Pin  # GPIO41
CAMERA_D5: microcontroller.Pin  # GPIO42
CAMERA_D6: microcontroller.Pin  # GPIO39
CAMERA_D7: microcontroller.Pin  # GPIO40
CAMERA_D8: microcontroller.Pin  # GPIO21
CAMERA_D9: microcontroller.Pin  # GPIO38
TOUCH1: microcontroller.Pin  # GPIO1
TOUCH2: microcontroller.Pin  # GPIO2
TOUCH3: microcontroller.Pin  # GPIO3
TOUCH4: microcontroller.Pin  # GPIO4
TOUCH5: microcontroller.Pin  # GPIO5
TOUCH6: microcontroller.Pin  # GPIO6
TOUCH7: microcontroller.Pin  # GPIO7
TOUCH8: microcontroller.Pin  # GPIO8
TOUCH9: microcontroller.Pin  # GPIO9
TOUCH10: microcontroller.Pin  # GPIO10
TOUCH11: microcontroller.Pin  # GPIO11
TOUCH12: microcontroller.Pin  # GPIO12
TOUCH13: microcontroller.Pin  # GPIO13
TOUCH14: microcontroller.Pin  # GPIO14
SCL: microcontroller.Pin  # GPIO7
SDA: microcontroller.Pin  # GPIO8
BT_ARRAY_ADC: microcontroller.Pin  # GPIO6
LCD_TP_MISO: microcontroller.Pin  # GPIO42
LCD_TP_MOSI: microcontroller.Pin  # GPIO40
LCD_TP_SCK: microcontroller.Pin  # GPIO38
LCD_TP_CS: microcontroller.Pin  # GPIO33
LCD_TP_IRQ: microcontroller.Pin  # GPIO2
LCD_TP_BUSY: microcontroller.Pin  # GPIO4
LCD_BL_CTR: microcontroller.Pin  # GPIO6
LCD_MISO: microcontroller.Pin  # GPIO8
LCD_MOSI: microcontroller.Pin  # GPIO9
LCD_CS: microcontroller.Pin  # GPIO11
LCD_D_C: microcontroller.Pin  # GPIO13
LCD_CLK: microcontroller.Pin  # GPIO15
LCD_RST: microcontroller.Pin  # GPIO16
AUDIO_SPI_MISO: microcontroller.Pin  # GPIO42
AUDIO_SPI_MOSI: microcontroller.Pin  # GPIO40
AUDIO_SPI_SCK: microcontroller.Pin  # GPIO38
AUDIO_SPI_CS: microcontroller.Pin  # GPIO33
AUDIO_BT_ADC: microcontroller.Pin  # GPIO6
AUDIO_SCL: microcontroller.Pin  # GPIO7
AUDIO_SDA: microcontroller.Pin  # GPIO8
AUDIO_I2S0_MCLK: microcontroller.Pin  # GPIO41
AUDIO_I2S0_BCLK: microcontroller.Pin  # GPIO39
AUDIO_I2S0_LRCK: microcontroller.Pin  # GPIO21
AUDIO_I2S0_SDI: microcontroller.Pin  # GPIO1
AUDIO_I2S0_SDO: microcontroller.Pin  # GPIO3
AUDIO_RST: microcontroller.Pin  # GPIO5
AUDIO_WAKE_INT: microcontroller.Pin  # GPIO46
AUDIO_I2S1_MCLK: microcontroller.Pin  # GPIO35
AUDIO_PA_CTRL: microcontroller.Pin  # GPIO10
AUDIO_I2S1_SDI: microcontroller.Pin  # GPIO34
AUDIO_I2S1_SDO: microcontroller.Pin  # GPIO12
AUDIO_I2S1_LRCK_DAC1: microcontroller.Pin  # GPIO17
AUDIO_I2S1_BCLK_DAC2: microcontroller.Pin  # GPIO18


# Members:
CAMERA_DATA: Tuple[Any]

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
