# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SparkFun MicroMod nRF52840 Processor
 - port: nordic
 - board_id: sparkfun_nrf52840_micromod
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
LED: microcontroller.Pin  # P0_13
P3V3_EN: microcontroller.Pin  # P1_15
BATT_VIN3: microcontroller.Pin  # P0_30
RESET: microcontroller.Pin  # P0_18
BOOT: microcontroller.Pin  # P0_07
UART_TX1: microcontroller.Pin  # P1_03
UART_RX1: microcontroller.Pin  # P1_10
UART_RTS1: microcontroller.Pin  # P1_02
UART_CTS1: microcontroller.Pin  # P1_09
TX: microcontroller.Pin  # P1_03
RX: microcontroller.Pin  # P1_10
UART_TX2: microcontroller.Pin  # P1_07
UART_RX2: microcontroller.Pin  # P1_05
I2C_SDA: microcontroller.Pin  # P0_08
I2C_SCL: microcontroller.Pin  # P0_11
SDA: microcontroller.Pin  # P0_08
SCL: microcontroller.Pin  # P0_11
I2C_INT: microcontroller.Pin  # P0_15
I2C_SDA1: microcontroller.Pin  # P1_01
I2C_SCL1: microcontroller.Pin  # P0_24
SPI_CIPO: microcontroller.Pin  # P0_02
SPI_MISO: microcontroller.Pin  # P0_02
SPI_COPI: microcontroller.Pin  # P0_31
SPI_MOSI: microcontroller.Pin  # P0_31
SPI_SCK: microcontroller.Pin  # P0_28
SPI_CS: microcontroller.Pin  # P0_20
CIPO: microcontroller.Pin  # P0_02
MISO: microcontroller.Pin  # P0_02
COPI: microcontroller.Pin  # P0_31
MOSI: microcontroller.Pin  # P0_31
SCK: microcontroller.Pin  # P0_28
CS: microcontroller.Pin  # P0_20
LED_DAT: microcontroller.Pin  # P0_31
LED_CLK: microcontroller.Pin  # P0_28
SDIO_CLK: microcontroller.Pin  # P0_19
SDIO_CMD: microcontroller.Pin  # P0_14
SDIO_DATA0: microcontroller.Pin  # P0_21
SDIO_DATA1: microcontroller.Pin  # P0_22
SDIO_DATA2: microcontroller.Pin  # P0_23
SDIO_DATA3: microcontroller.Pin  # P1_00
SPI_CIPO1: microcontroller.Pin  # P0_21
SPI_MISO1: microcontroller.Pin  # P0_21
SPI_COPI1: microcontroller.Pin  # P0_14
SPI_MOSI1: microcontroller.Pin  # P0_14
SPI_SCK1: microcontroller.Pin  # P0_19
SPI_CS1: microcontroller.Pin  # P1_00
PDM_DATA: microcontroller.Pin  # P0_26
PDM_CLK: microcontroller.Pin  # P0_25
A0: microcontroller.Pin  # P0_05
A1: microcontroller.Pin  # P0_04
PWM0: microcontroller.Pin  # P0_06
PWM1: microcontroller.Pin  # P0_16
D0: microcontroller.Pin  # P0_27
D1: microcontroller.Pin  # P1_08
G0: microcontroller.Pin  # P0_29
G1: microcontroller.Pin  # P0_03
G2: microcontroller.Pin  # P1_13
G3: microcontroller.Pin  # P1_12
G4: microcontroller.Pin  # P1_11
G5: microcontroller.Pin  # P0_17
G6: microcontroller.Pin  # P1_06
G7: microcontroller.Pin  # P1_04
G8: microcontroller.Pin  # P1_14
G9: microcontroller.Pin  # P0_09
G10: microcontroller.Pin  # P0_10
BUS0: microcontroller.Pin  # P0_29
BUS1: microcontroller.Pin  # P0_03
BUS2: microcontroller.Pin  # P1_13
BUS3: microcontroller.Pin  # P1_12
BUS4: microcontroller.Pin  # P1_11
BUS5: microcontroller.Pin  # P0_17
BUS6: microcontroller.Pin  # P1_06
BUS7: microcontroller.Pin  # P1_04


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
