# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SparkFun STM32 MicroMod Processor
 - port: stm
 - board_id: sparkfun_stm32f405_micromod
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rtc, sdcardio, sdioio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
LED: microcontroller.Pin  # PA15
BATT_VIN3: microcontroller.Pin  # PA01
USBHOST_DM: microcontroller.Pin  # PB14
USBHOST_DP: microcontroller.Pin  # PB15
CAN_RX: microcontroller.Pin  # PB08
CAN_TX: microcontroller.Pin  # PB09
UART_TX1: microcontroller.Pin  # PA02
UART_RX1: microcontroller.Pin  # PA03
TX: microcontroller.Pin  # PA02
RX: microcontroller.Pin  # PA03
I2C_SDA: microcontroller.Pin  # PB11
I2C_SCL: microcontroller.Pin  # PB10
SDA: microcontroller.Pin  # PB11
SCL: microcontroller.Pin  # PB10
I2C_INT: microcontroller.Pin  # PB01
I2C_SDA1: microcontroller.Pin  # PB07
I2C_SCL1: microcontroller.Pin  # PB06
SPI_CIPO: microcontroller.Pin  # PA06
SPI_MISO: microcontroller.Pin  # PA06
SPI_COPI: microcontroller.Pin  # PA07
SPI_MOSI: microcontroller.Pin  # PA07
SPI_SCK: microcontroller.Pin  # PA05
SPI_CS: microcontroller.Pin  # PA04
CIPO: microcontroller.Pin  # PA06
MISO: microcontroller.Pin  # PA06
COPI: microcontroller.Pin  # PA07
MOSI: microcontroller.Pin  # PA07
SCK: microcontroller.Pin  # PA05
CS: microcontroller.Pin  # PA04
LED_DAT: microcontroller.Pin  # PA07
LED_CLK: microcontroller.Pin  # PA05
I2S_OUT: microcontroller.Pin  # PB04
I2S_IN: microcontroller.Pin  # PB05
I2S_WS: microcontroller.Pin  # PA04
I2S_SCK: microcontroller.Pin  # PB03
PCM_OUT: microcontroller.Pin  # PB04
PCM_IN: microcontroller.Pin  # PB05
PCM_SYNC: microcontroller.Pin  # PA04
PCM_CLK: microcontroller.Pin  # PB03
PDM_DATA: microcontroller.Pin  # PA04
PDM_CLK: microcontroller.Pin  # PB03
SWDIO: microcontroller.Pin  # PA13
SWCLK: microcontroller.Pin  # PA14
A0: microcontroller.Pin  # PC05
A1: microcontroller.Pin  # PB00
PWM0: microcontroller.Pin  # PC06
PWM1: microcontroller.Pin  # PC07
D0: microcontroller.Pin  # PC00
D1: microcontroller.Pin  # PC01
G0: microcontroller.Pin  # PD02
G1: microcontroller.Pin  # PA08
G2: microcontroller.Pin  # PA00
G3: microcontroller.Pin  # PC08
G4: microcontroller.Pin  # PC09
G5: microcontroller.Pin  # PC13
G6: microcontroller.Pin  # PC02
G10: microcontroller.Pin  # PB13
G11: microcontroller.Pin  # PB12
BUS0: microcontroller.Pin  # PD02
BUS1: microcontroller.Pin  # PA08
BUS2: microcontroller.Pin  # PA00
BUS3: microcontroller.Pin  # PC08
BUS4: microcontroller.Pin  # PC09
BUS5: microcontroller.Pin  # PC13
BUS6: microcontroller.Pin  # PC02
HOST_VBUS: microcontroller.Pin  # PB13
HOST_ID: microcontroller.Pin  # PB12


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
