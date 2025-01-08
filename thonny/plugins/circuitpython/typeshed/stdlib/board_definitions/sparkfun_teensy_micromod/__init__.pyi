# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SparkFun Teensy MicroMod Processor
 - port: mimxrt10xx
 - board_id: sparkfun_teensy_micromod
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
RX4: microcontroller.Pin  # GPIO_B1_01
D8: microcontroller.Pin  # GPIO_B1_00
TX4: microcontroller.Pin  # GPIO_B1_00
D9: microcontroller.Pin  # GPIO_B0_11
D10: microcontroller.Pin  # GPIO_B0_00
D11: microcontroller.Pin  # GPIO_B0_02
MOSI: microcontroller.Pin  # GPIO_B0_02
D12: microcontroller.Pin  # GPIO_B0_01
MISO: microcontroller.Pin  # GPIO_B0_01
D13: microcontroller.Pin  # GPIO_B0_03
LED: microcontroller.Pin  # GPIO_B0_03
SCK: microcontroller.Pin  # GPIO_B0_03
D14: microcontroller.Pin  # GPIO_AD_B1_02
A0: microcontroller.Pin  # GPIO_AD_B1_02
TX3: microcontroller.Pin  # GPIO_AD_B1_02
D15: microcontroller.Pin  # GPIO_AD_B1_03
A1: microcontroller.Pin  # GPIO_AD_B1_03
RX3: microcontroller.Pin  # GPIO_AD_B1_03
D16: microcontroller.Pin  # GPIO_AD_B1_07
A2: microcontroller.Pin  # GPIO_AD_B1_07
RX2: microcontroller.Pin  # GPIO_AD_B1_07
D17: microcontroller.Pin  # GPIO_AD_B1_06
A3: microcontroller.Pin  # GPIO_AD_B1_06
TX2: microcontroller.Pin  # GPIO_AD_B1_06
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
TX5: microcontroller.Pin  # GPIO_AD_B1_10
D21: microcontroller.Pin  # GPIO_AD_B1_11
A7: microcontroller.Pin  # GPIO_AD_B1_11
RX5: microcontroller.Pin  # GPIO_AD_B1_11
D22: microcontroller.Pin  # GPIO_AD_B1_08
A8: microcontroller.Pin  # GPIO_AD_B1_08
D23: microcontroller.Pin  # GPIO_AD_B1_09
A9: microcontroller.Pin  # GPIO_AD_B1_09
D24: microcontroller.Pin  # GPIO_AD_B0_12
A10: microcontroller.Pin  # GPIO_AD_B0_12
TX6: microcontroller.Pin  # GPIO_AD_B0_12
D25: microcontroller.Pin  # GPIO_AD_B0_13
A11: microcontroller.Pin  # GPIO_AD_B0_13
RX6: microcontroller.Pin  # GPIO_AD_B0_13
D26: microcontroller.Pin  # GPIO_AD_B1_14
A12: microcontroller.Pin  # GPIO_AD_B1_14
D27: microcontroller.Pin  # GPIO_AD_B1_15
A13: microcontroller.Pin  # GPIO_AD_B1_15
D28: microcontroller.Pin  # GPIO_EMC_32
RX7: microcontroller.Pin  # GPIO_EMC_32
D29: microcontroller.Pin  # GPIO_EMC_31
TX7: microcontroller.Pin  # GPIO_EMC_31
D30: microcontroller.Pin  # GPIO_EMC_37
D31: microcontroller.Pin  # GPIO_EMC_36
D32: microcontroller.Pin  # GPIO_B0_12
D33: microcontroller.Pin  # GPIO_EMC_07
D34: microcontroller.Pin  # GPIO_SD_B0_03
DAT1: microcontroller.Pin  # GPIO_SD_B0_03
D35: microcontroller.Pin  # GPIO_SD_B0_02
DAT0: microcontroller.Pin  # GPIO_SD_B0_02
D36: microcontroller.Pin  # GPIO_SD_B0_01
CLK: microcontroller.Pin  # GPIO_SD_B0_01
D37: microcontroller.Pin  # GPIO_SD_B0_00
CMD: microcontroller.Pin  # GPIO_SD_B0_00
D38: microcontroller.Pin  # GPIO_SD_B0_05
DAT3: microcontroller.Pin  # GPIO_SD_B0_05
D39: microcontroller.Pin  # GPIO_SD_B0_04
DAT2: microcontroller.Pin  # GPIO_SD_B0_04
D40: microcontroller.Pin  # GPIO_B0_04
BUS0: microcontroller.Pin  # GPIO_B0_04
D41: microcontroller.Pin  # GPIO_B0_05
BUS1: microcontroller.Pin  # GPIO_B0_05
D42: microcontroller.Pin  # GPIO_B0_06
BUS2: microcontroller.Pin  # GPIO_B0_06
D43: microcontroller.Pin  # GPIO_B0_07
BUS3: microcontroller.Pin  # GPIO_B0_07
D44: microcontroller.Pin  # GPIO_B0_08
BUS4: microcontroller.Pin  # GPIO_B0_08
D45: microcontroller.Pin  # GPIO_B0_09
BUS5: microcontroller.Pin  # GPIO_B0_09
USB_HOST_POWER: microcontroller.Pin  # GPIO_EMC_40
USB_HOST_DP: microcontroller.Pin  # USB_OTG2_DP
USB_HOST_DM: microcontroller.Pin  # USB_OTG2_DN
MM_RX: microcontroller.Pin  # GPIO_AD_B0_03
MM_TX: microcontroller.Pin  # GPIO_AD_B0_02
MM_PWM1: microcontroller.Pin  # GPIO_EMC_04
MM_PWM0: microcontroller.Pin  # GPIO_EMC_05
MM_D0: microcontroller.Pin  # GPIO_EMC_06
MM_D1: microcontroller.Pin  # GPIO_EMC_08
MM_G6: microcontroller.Pin  # GPIO_B0_10
MM_I2S_SDO: microcontroller.Pin  # GPIO_B1_01
MM_I2S_SDI: microcontroller.Pin  # GPIO_B1_00
MM_G7: microcontroller.Pin  # GPIO_B0_11
MM_CS: microcontroller.Pin  # GPIO_B0_00
MM_COPI: microcontroller.Pin  # GPIO_B0_02
MM_CIPO: microcontroller.Pin  # GPIO_B0_01
MM_SCK: microcontroller.Pin  # GPIO_B0_03
MM_A0: microcontroller.Pin  # GPIO_AD_B1_02
MM_A1: microcontroller.Pin  # GPIO_AD_B1_03
MM_RX2: microcontroller.Pin  # GPIO_AD_B1_07
MM_TX2: microcontroller.Pin  # GPIO_AD_B1_06
MM_SDA: microcontroller.Pin  # GPIO_AD_B1_01
MM_SCL: microcontroller.Pin  # GPIO_AD_B1_00
MM_I2S_FS: microcontroller.Pin  # GPIO_AD_B1_10
MM_I2S_CLK: microcontroller.Pin  # GPIO_AD_B1_11
MM_BATT_VIN3: microcontroller.Pin  # GPIO_AD_B1_08
MM_MCLK: microcontroller.Pin  # GPIO_AD_B1_09
MM_SCL1: microcontroller.Pin  # GPIO_AD_B0_12
MM_SDA1: microcontroller.Pin  # GPIO_AD_B0_13
MM_G8: microcontroller.Pin  # GPIO_AD_B1_14
MM_G11: microcontroller.Pin  # GPIO_AD_B1_15
MM_33V_EN: microcontroller.Pin  # GPIO_EMC_32
MM_I2C_INT: microcontroller.Pin  # GPIO_EMC_31
MM_CAN_RX: microcontroller.Pin  # GPIO_EMC_37
MM_CAN_TX: microcontroller.Pin  # GPIO_EMC_36
MM_G9: microcontroller.Pin  # GPIO_B0_12
MM_G10: microcontroller.Pin  # GPIO_EMC_07
MM_DAT1: microcontroller.Pin  # GPIO_SD_B0_03
MM_DAT0: microcontroller.Pin  # GPIO_SD_B0_02
MM_CIPO1: microcontroller.Pin  # GPIO_SD_B0_02
MM_SCK1: microcontroller.Pin  # GPIO_SD_B0_01
MM_COPI1: microcontroller.Pin  # GPIO_SD_B0_00
MM_CS1: microcontroller.Pin  # GPIO_SD_B0_05
MM_DAT3: microcontroller.Pin  # GPIO_SD_B0_05
MM_DAT2: microcontroller.Pin  # GPIO_SD_B0_04
MM_G0: microcontroller.Pin  # GPIO_B0_04
MM_G1: microcontroller.Pin  # GPIO_B0_05
MM_G2: microcontroller.Pin  # GPIO_B0_06
MM_G3: microcontroller.Pin  # GPIO_B0_07
MM_G4: microcontroller.Pin  # GPIO_B0_08
MM_G5: microcontroller.Pin  # GPIO_B0_09


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
