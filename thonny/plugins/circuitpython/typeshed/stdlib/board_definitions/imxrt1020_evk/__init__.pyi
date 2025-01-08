# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for iMX RT 1020 EVK
 - port: mimxrt10xx
 - board_id: imxrt1020_evk
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
D0: microcontroller.Pin  # GPIO_AD_B1_09
RX: microcontroller.Pin  # GPIO_AD_B1_09
D1: microcontroller.Pin  # GPIO_AD_B1_08
TX: microcontroller.Pin  # GPIO_AD_B1_08
D2: microcontroller.Pin  # GPIO_AD_B0_09
D3: microcontroller.Pin  # GPIO_AD_B0_07
D4: microcontroller.Pin  # GPIO_AD_B0_05
D5: microcontroller.Pin  # GPIO_AD_B0_06
D6: microcontroller.Pin  # GPIO_AD_B0_14
D7: microcontroller.Pin  # GPIO_AD_B1_06
D8: microcontroller.Pin  # GPIO_AD_B1_07
D9: microcontroller.Pin  # GPIO_AD_B0_15
D10: microcontroller.Pin  # GPIO_AD_B0_11
D11: microcontroller.Pin  # GPIO_AD_B0_12
D12: microcontroller.Pin  # GPIO_AD_B0_13
D13: microcontroller.Pin  # GPIO_AD_B0_10
D14: microcontroller.Pin  # GPIO_SD_B1_03
SDA: microcontroller.Pin  # GPIO_SD_B1_03
D15: microcontroller.Pin  # GPIO_SD_B1_02
SCL: microcontroller.Pin  # GPIO_SD_B1_02
A0: microcontroller.Pin  # GPIO_AD_B1_10
A1: microcontroller.Pin  # GPIO_AD_B1_11
A2: microcontroller.Pin  # GPIO_AD_B1_12
A3: microcontroller.Pin  # GPIO_AD_B1_13
A4: microcontroller.Pin  # GPIO_AD_B1_15
A5: microcontroller.Pin  # GPIO_AD_B1_14
USER_LED: microcontroller.Pin  # GPIO_AD_B0_05
LED: microcontroller.Pin  # GPIO_AD_B0_05
SD_CLK: microcontroller.Pin  # GPIO_SD_B0_03
SD_SW: microcontroller.Pin  # GPIO_SD_B0_06
SD_CMD: microcontroller.Pin  # GPIO_SD_B0_02
SD_D0: microcontroller.Pin  # GPIO_SD_B0_04
SD_D1: microcontroller.Pin  # GPIO_SD_B0_05
SD_D2: microcontroller.Pin  # GPIO_SD_B0_00
SD_D3: microcontroller.Pin  # GPIO_SD_B0_01
SD_PWREN: microcontroller.Pin  # GPIO_SD_B1_04
AUDIO_INT: microcontroller.Pin  # GPIO_AD_B1_04
AUDIO_SYNC: microcontroller.Pin  # GPIO_AD_B1_02
AUDIO_BCLK: microcontroller.Pin  # GPIO_AD_B1_01
AUDIO_RXD: microcontroller.Pin  # GPIO_AD_B1_05
AUDIO_TXD: microcontroller.Pin  # GPIO_AD_B1_03
AUDIO_MCLK: microcontroller.Pin  # GPIO_AD_B1_00
ETHERNET_MDIO: microcontroller.Pin  # GPIO_EMC_40
ETHERNET_MDC: microcontroller.Pin  # GPIO_EMC_41
ETHERNET_RXD0: microcontroller.Pin  # GPIO_AD_B0_10
ETHERNET_RXD1: microcontroller.Pin  # GPIO_AD_B0_09
ETHERNET_CRS_DV: microcontroller.Pin  # GPIO_AD_B0_11
ETHERNET_TXD0: microcontroller.Pin  # GPIO_AD_B0_14
ETHERNET_TXD1: microcontroller.Pin  # GPIO_AD_B0_15
ETHERNET_TXEN: microcontroller.Pin  # GPIO_AD_B0_13
ETHERNET_INT: microcontroller.Pin  # GPIO_AD_B1_06
ETHERNET_RST: microcontroller.Pin  # GPIO_AD_B0_04
ETHERNET_CLK: microcontroller.Pin  # GPIO_AD_B0_08
ETHERNET_RXER: microcontroller.Pin  # GPIO_AD_B0_12
FREELINK_TX: microcontroller.Pin  # GPIO_AD_B0_06
FREELINK_RX: microcontroller.Pin  # GPIO_AD_B0_07
CAN_TX: microcontroller.Pin  # GPIO_SD_B1_00
CAN_RX: microcontroller.Pin  # GPIO_SD_B1_01
CAN_STBY: microcontroller.Pin  # GPIO_AD_B1_13
ACCELEROMETER_SDA: microcontroller.Pin  # GPIO_SD_B1_03
ACCELEROMETER_SCL: microcontroller.Pin  # GPIO_SD_B1_02


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
