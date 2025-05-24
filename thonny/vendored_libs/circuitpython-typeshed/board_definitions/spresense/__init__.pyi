# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SPRESENSE
 - port: cxd56
 - board_id: spresense
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, binascii, bitbangio, board, builtins, builtins.pow3, busio, busio.SPI, busio.UART, camera, codeop, collections, digitalio, errno, getpass, gnss, io, json, locale, math, microcontroller, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rtc, sdcardio, sdioio, select, storage, struct, supervisor, sys, time, traceback, ulab, usb_cdc, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # UART2_RXD
D1: microcontroller.Pin  # UART2_TXD
D2: microcontroller.Pin  # HIF_IRQ_OUT
D3: microcontroller.Pin  # PWM3
D4: microcontroller.Pin  # SPI2_MOSI
D5: microcontroller.Pin  # PWM1
D6: microcontroller.Pin  # PWM0
D7: microcontroller.Pin  # SPI3_CS1_X
D8: microcontroller.Pin  # SPI2_MISO
D9: microcontroller.Pin  # PWM2
D10: microcontroller.Pin  # SPI4_CS_X
D11: microcontroller.Pin  # SPI4_MOSI
D12: microcontroller.Pin  # SPI4_MISO
D13: microcontroller.Pin  # SPI4_SCK
D14: microcontroller.Pin  # I2C0_BDT
D15: microcontroller.Pin  # I2C0_BCK
D16: microcontroller.Pin  # EMMC_DATA0
D17: microcontroller.Pin  # EMMC_DATA1
D18: microcontroller.Pin  # I2S0_DATA_OUT
D19: microcontroller.Pin  # I2S0_DATA_IN
D20: microcontroller.Pin  # EMMC_DATA2
D21: microcontroller.Pin  # EMMC_DATA3
D22: microcontroller.Pin  # SEN_IRQ_IN
D23: microcontroller.Pin  # EMMC_CLK
D24: microcontroller.Pin  # EMMC_CMD
D25: microcontroller.Pin  # I2S0_LRCK
D26: microcontroller.Pin  # I2S0_BCK
D27: microcontroller.Pin  # UART2_CTS
D28: microcontroller.Pin  # UART2_RTS
LED0: microcontroller.Pin  # I2S1_BCK
LED1: microcontroller.Pin  # I2S1_LRCK
LED2: microcontroller.Pin  # I2S1_DATA_IN
LED3: microcontroller.Pin  # I2S1_DATA_OUT
A0: microcontroller.Pin  # LPADC0
A1: microcontroller.Pin  # LPADC1
A2: microcontroller.Pin  # LPADC2
A3: microcontroller.Pin  # LPADC3
A4: microcontroller.Pin  # HPADC0
A5: microcontroller.Pin  # HPADC1
SDA: microcontroller.Pin  # I2C0_BDT
SCL: microcontroller.Pin  # I2C0_BCK
SCK: microcontroller.Pin  # SPI4_SCK
MISO: microcontroller.Pin  # SPI4_MISO
MOSI: microcontroller.Pin  # SPI4_MOSI
RX: microcontroller.Pin  # UART2_RXD
TX: microcontroller.Pin  # UART2_TXD
SDIO_CLOCK: microcontroller.Pin  # SDIO_CLK
SDIO_COMMAND: microcontroller.Pin  # SDIO_CMD


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

SDIO_DATA: Tuple[Any]


# Unmapped:
#   none
