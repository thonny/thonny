# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Teensy 4.1
 - port: mimxrt10xx
 - board_id: teensy41
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # GPIO_AD_B0_03
RX: microcontroller.Pin  # GPIO_AD_B0_03
RX1: microcontroller.Pin  # GPIO_AD_B0_03
D1: microcontroller.Pin  # GPIO_AD_B0_02
TX: microcontroller.Pin  # GPIO_AD_B0_02
TX1: microcontroller.Pin  # GPIO_AD_B0_02
D2: microcontroller.Pin  # GPIO_EMC_04
D3: microcontroller.Pin  # GPIO_EMC_05
D4: microcontroller.Pin  # GPIO_EMC_06
D5: microcontroller.Pin  # GPIO_EMC_08
D6: microcontroller.Pin  # GPIO_B0_10
D7: microcontroller.Pin  # GPIO_B1_01
D8: microcontroller.Pin  # GPIO_B1_00
D9: microcontroller.Pin  # GPIO_B0_11
D10: microcontroller.Pin  # GPIO_B0_00
D11: microcontroller.Pin  # GPIO_B0_02
MOSI: microcontroller.Pin  # GPIO_B0_02
D12: microcontroller.Pin  # GPIO_B0_01
MISO: microcontroller.Pin  # GPIO_B0_01
D24: microcontroller.Pin  # GPIO_AD_B0_12
A10: microcontroller.Pin  # GPIO_AD_B0_12
D25: microcontroller.Pin  # GPIO_AD_B0_13
A11: microcontroller.Pin  # GPIO_AD_B0_13
D26: microcontroller.Pin  # GPIO_AD_B1_14
A12: microcontroller.Pin  # GPIO_AD_B1_14
D27: microcontroller.Pin  # GPIO_AD_B1_15
A13: microcontroller.Pin  # GPIO_AD_B1_15
D28: microcontroller.Pin  # GPIO_EMC_32
D29: microcontroller.Pin  # GPIO_EMC_31
D30: microcontroller.Pin  # GPIO_EMC_37
D31: microcontroller.Pin  # GPIO_EMC_36
D32: microcontroller.Pin  # GPIO_B0_12
D13: microcontroller.Pin  # GPIO_B0_03
LED: microcontroller.Pin  # GPIO_B0_03
SCK: microcontroller.Pin  # GPIO_B0_03
D14: microcontroller.Pin  # GPIO_AD_B1_02
A0: microcontroller.Pin  # GPIO_AD_B1_02
D15: microcontroller.Pin  # GPIO_AD_B1_03
A1: microcontroller.Pin  # GPIO_AD_B1_03
D16: microcontroller.Pin  # GPIO_AD_B1_07
A2: microcontroller.Pin  # GPIO_AD_B1_07
D17: microcontroller.Pin  # GPIO_AD_B1_06
A3: microcontroller.Pin  # GPIO_AD_B1_06
D18: microcontroller.Pin  # GPIO_AD_B1_01
A4: microcontroller.Pin  # GPIO_AD_B1_01
SDA: microcontroller.Pin  # GPIO_AD_B1_01
SDA0: microcontroller.Pin  # GPIO_AD_B1_01
D19: microcontroller.Pin  # GPIO_AD_B1_00
A5: microcontroller.Pin  # GPIO_AD_B1_00
SCL: microcontroller.Pin  # GPIO_AD_B1_00
SCL0: microcontroller.Pin  # GPIO_AD_B1_00
D20: microcontroller.Pin  # GPIO_AD_B1_10
A6: microcontroller.Pin  # GPIO_AD_B1_10
D21: microcontroller.Pin  # GPIO_AD_B1_11
A7: microcontroller.Pin  # GPIO_AD_B1_11
D22: microcontroller.Pin  # GPIO_AD_B1_08
A8: microcontroller.Pin  # GPIO_AD_B1_08
D23: microcontroller.Pin  # GPIO_AD_B1_09
A9: microcontroller.Pin  # GPIO_AD_B1_09
D33: microcontroller.Pin  # GPIO_EMC_07
D34: microcontroller.Pin  # GPIO_B1_13
D35: microcontroller.Pin  # GPIO_B1_12
D36: microcontroller.Pin  # GPIO_B1_02
D37: microcontroller.Pin  # GPIO_B1_03
D38: microcontroller.Pin  # GPIO_AD_B1_12
D39: microcontroller.Pin  # GPIO_AD_B1_13
D40: microcontroller.Pin  # GPIO_AD_B1_04
D41: microcontroller.Pin  # GPIO_AD_B1_05
DAT1: microcontroller.Pin  # GPIO_SD_B0_03
D42: microcontroller.Pin  # GPIO_SD_B0_03
DAT0: microcontroller.Pin  # GPIO_SD_B0_02
D43: microcontroller.Pin  # GPIO_SD_B0_02
CLK: microcontroller.Pin  # GPIO_SD_B0_01
D44: microcontroller.Pin  # GPIO_SD_B0_01
CMD: microcontroller.Pin  # GPIO_SD_B0_00
D45: microcontroller.Pin  # GPIO_SD_B0_00
DAT3: microcontroller.Pin  # GPIO_SD_B0_05
D46: microcontroller.Pin  # GPIO_SD_B0_05
DAT2: microcontroller.Pin  # GPIO_SD_B0_04
D47: microcontroller.Pin  # GPIO_SD_B0_04
D48: microcontroller.Pin  # GPIO_EMC_24
PSRAM_CS: microcontroller.Pin  # GPIO_EMC_24
D49: microcontroller.Pin  # GPIO_EMC_27
QSPI_IO1: microcontroller.Pin  # GPIO_EMC_27
D50: microcontroller.Pin  # GPIO_EMC_28
QSPI_IO2: microcontroller.Pin  # GPIO_EMC_28
D51: microcontroller.Pin  # GPIO_EMC_22
FLASH_CS: microcontroller.Pin  # GPIO_EMC_22
D52: microcontroller.Pin  # GPIO_EMC_26
QSPI_IO0: microcontroller.Pin  # GPIO_EMC_26
D53: microcontroller.Pin  # GPIO_EMC_25
QSPI_CLK: microcontroller.Pin  # GPIO_EMC_25
D54: microcontroller.Pin  # GPIO_EMC_29
QSPI_IO3: microcontroller.Pin  # GPIO_EMC_29
USB_HOST_POWER: microcontroller.Pin  # GPIO_EMC_40
USB_HOST_DP: microcontroller.Pin  # USB_OTG2_DP
USB_HOST_DM: microcontroller.Pin  # USB_OTG2_DN
SDA1: microcontroller.Pin  # GPIO_AD_B1_06
SCL1: microcontroller.Pin  # GPIO_AD_B1_07
SDA2: microcontroller.Pin  # GPIO_AD_B0_13
SCL2: microcontroller.Pin  # GPIO_AD_B0_12
RX2: microcontroller.Pin  # GPIO_B1_01
TX2: microcontroller.Pin  # GPIO_B1_00
RX3: microcontroller.Pin  # GPIO_AD_B1_03
TX3: microcontroller.Pin  # GPIO_AD_B1_02
RX4: microcontroller.Pin  # GPIO_AD_B1_07
TX4: microcontroller.Pin  # GPIO_AD_B1_06
RX5: microcontroller.Pin  # GPIO_AD_B1_11
TX5: microcontroller.Pin  # GPIO_AD_B1_10
RX6: microcontroller.Pin  # GPIO_AD_B0_13
TX6: microcontroller.Pin  # GPIO_AD_B0_12
RX7: microcontroller.Pin  # GPIO_EMC_32
TX7: microcontroller.Pin  # GPIO_EMC_31
RX8: microcontroller.Pin  # GPIO_B1_13
TX8: microcontroller.Pin  # GPIO_B1_12


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
