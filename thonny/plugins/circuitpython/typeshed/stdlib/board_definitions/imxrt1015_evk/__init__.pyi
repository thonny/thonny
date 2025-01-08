# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for IMXRT1015-EVK
 - port: mimxrt10xx
 - board_id: imxrt1015_evk
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # GPIO_EMC_33
RX: microcontroller.Pin  # GPIO_EMC_33
D1: microcontroller.Pin  # GPIO_EMC_32
TX: microcontroller.Pin  # GPIO_EMC_32
D2: microcontroller.Pin  # GPIO_EMC_20
D3: microcontroller.Pin  # GPIO_EMC_26
D4: microcontroller.Pin  # GPIO_EMC_34
D5: microcontroller.Pin  # GPIO_EMC_27
D6: microcontroller.Pin  # GPIO_AD_B1_11
D7: microcontroller.Pin  # GPIO_AD_B0_15
D8: microcontroller.Pin  # GPIO_EMC_21
D9: microcontroller.Pin  # GPIO_EMC_22
D10: microcontroller.Pin  # GPIO_AD_B0_11
D11: microcontroller.Pin  # GPIO_AD_B0_12
MOSI: microcontroller.Pin  # GPIO_AD_B0_12
D12: microcontroller.Pin  # GPIO_AD_B0_13
MISO: microcontroller.Pin  # GPIO_AD_B0_13
D13: microcontroller.Pin  # GPIO_AD_B0_10
SCK: microcontroller.Pin  # GPIO_AD_B0_10
D14: microcontroller.Pin  # GPIO_AD_B1_15
D15: microcontroller.Pin  # GPIO_AD_B1_14
A0: microcontroller.Pin  # GPIO_AD_B1_13
A1: microcontroller.Pin  # GPIO_AD_B0_14
A2: microcontroller.Pin  # GPIO_AD_B1_12
A3: microcontroller.Pin  # GPIO_AD_B1_10
A4: microcontroller.Pin  # GPIO_AD_B1_15
SDA: microcontroller.Pin  # GPIO_AD_B1_15
A5: microcontroller.Pin  # GPIO_AD_B1_14
SCL: microcontroller.Pin  # GPIO_AD_B1_14
USER_LED: microcontroller.Pin  # GPIO_SD_B1_00
LED: microcontroller.Pin  # GPIO_SD_B1_00
LED1: microcontroller.Pin  # GPIO_SD_B1_00
LED2: microcontroller.Pin  # GPIO_SD_B1_01
LED3: microcontroller.Pin  # GPIO_SD_B1_02
USER_SW: microcontroller.Pin  # GPIO_EMC_09
AUDIO_INT: microcontroller.Pin  # GPIO_EMC_08
AUDIO_SYNC: microcontroller.Pin  # GPIO_EMC_27
AUDIO_BCLK: microcontroller.Pin  # GPIO_EMC_26
AUDIO_RXD: microcontroller.Pin  # GPIO_EMC_21
AUDIO_TXD: microcontroller.Pin  # GPIO_EMC_25
AUDIO_MCLK: microcontroller.Pin  # GPIO_EMC_20
SPDIF_IN: microcontroller.Pin  # GPIO_EMC_05
SPDIF_OUT: microcontroller.Pin  # GPIO_EMC_04
J29_TX: microcontroller.Pin  # GPIO_EMC_32
J29_RX: microcontroller.Pin  # GPIO_EMC_33
J30_TX: microcontroller.Pin  # GPIO_EMC_06
J30_RX: microcontroller.Pin  # GPIO_EMC_07
FREELINK_TX: microcontroller.Pin  # GPIO_AD_B0_06
FREELINK_RX: microcontroller.Pin  # GPIO_AD_B0_07


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
