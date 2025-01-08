# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for HMI-DevKit-1.1
 - port: espressif
 - board_id: espressif_hmi_devkit_1
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
NEOPIXEL: microcontroller.Pin  # GPIO21
LCD_RS: microcontroller.Pin  # GPIO38
LCD_WR: microcontroller.Pin  # GPIO33
LCD_RS: microcontroller.Pin  # GPIO38
CS_SD: microcontroller.Pin  # GPIO34
CS_CNN: microcontroller.Pin  # GPIO45
CAN_TX: microcontroller.Pin  # GPIO41
CAN_RX: microcontroller.Pin  # GPIO42
MIC_ADC_M: microcontroller.Pin  # GPIO9
DAC_OUT: microcontroller.Pin  # GPIO18
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
LCD_DATA: Tuple[Any]

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#     { MP_ROM_QSTR(MP_QSTR_MISO), MP_ROM_PTR(DEFAULT_SPI_BUS_MISO) },
#     { MP_ROM_QSTR(MP_QSTR_MOSI), MP_ROM_PTR(DEFAULT_SPI_BUS_MOSI) },
#     { MP_ROM_QSTR(MP_QSTR_SCK), MP_ROM_PTR(DEFAULT_SPI_BUS_SCK) },
#     { MP_ROM_QSTR(MP_QSTR_SCL), MP_ROM_PTR(DEFAULT_I2C_BUS_SCL) },
#     { MP_ROM_QSTR(MP_QSTR_SDA), MP_ROM_PTR(DEFAULT_I2C_BUS_SDA) },
