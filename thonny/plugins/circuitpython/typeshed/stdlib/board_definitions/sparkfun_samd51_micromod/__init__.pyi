# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SparkFun MicroMod SAMD51 Processor
 - port: atmel-samd
 - board_id: sparkfun_samd51_micromod
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, max3421e, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
LED: microcontroller.Pin  # PA23
P3V3_EN: microcontroller.Pin  # PA19
BATT_VIN3: microcontroller.Pin  # PB03
CAN_RX: microcontroller.Pin  # PB15
CAN_TX: microcontroller.Pin  # PB14
UART_TX1: microcontroller.Pin  # PB31
UART_RX1: microcontroller.Pin  # PB30
UART_RTS1: microcontroller.Pin  # PB00
UART_CTS1: microcontroller.Pin  # PB01
TX: microcontroller.Pin  # PB31
RX: microcontroller.Pin  # PB30
UART_TX2: microcontroller.Pin  # PA12
UART_RX2: microcontroller.Pin  # PA13
I2C_SDA: microcontroller.Pin  # PA17
I2C_SCL: microcontroller.Pin  # PA16
SDA: microcontroller.Pin  # PA17
SCL: microcontroller.Pin  # PA16
I2C_INT: microcontroller.Pin  # PA18
I2C_SDA1: microcontroller.Pin  # PA13
I2C_SCL1: microcontroller.Pin  # PA12
SPI_CIPO: microcontroller.Pin  # PA06
SPI_MISO: microcontroller.Pin  # PA06
SPI_COPI: microcontroller.Pin  # PA04
SPI_MOSI: microcontroller.Pin  # PA04
SPI_SCK: microcontroller.Pin  # PA05
SPI_CS: microcontroller.Pin  # PA07
CIPO: microcontroller.Pin  # PA06
MISO: microcontroller.Pin  # PA06
COPI: microcontroller.Pin  # PA04
MOSI: microcontroller.Pin  # PA04
SCK: microcontroller.Pin  # PA05
CS: microcontroller.Pin  # PA07
LED_DAT: microcontroller.Pin  # PA04
LED_CLK: microcontroller.Pin  # PA05
AUD_MCLK: microcontroller.Pin  # PB17
AUD_OUT: microcontroller.Pin  # PA21
AUD_IN: microcontroller.Pin  # PA22
AUD_LRCLK: microcontroller.Pin  # PA20
AUD_BCLK: microcontroller.Pin  # PB16
I2S_OUT: microcontroller.Pin  # PA21
I2S_IN: microcontroller.Pin  # PA22
I2S_WS: microcontroller.Pin  # PA20
I2S_SCK: microcontroller.Pin  # PB16
PCM_OUT: microcontroller.Pin  # PA21
PCM_IN: microcontroller.Pin  # PA22
PCM_SYNC: microcontroller.Pin  # PA20
PCM_CLK: microcontroller.Pin  # PB16
PDM_DATA: microcontroller.Pin  # PA20
PDM_CLK: microcontroller.Pin  # PB16
SWDIO: microcontroller.Pin  # PA31
SWCLK: microcontroller.Pin  # PA30
A0: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PB00
PWM0: microcontroller.Pin  # PB01
PWM1: microcontroller.Pin  # PB02
D0: microcontroller.Pin  # PB04
D1: microcontroller.Pin  # PB05
G0: microcontroller.Pin  # PB06
G1: microcontroller.Pin  # PB07
G2: microcontroller.Pin  # PB08
G3: microcontroller.Pin  # PB09
G4: microcontroller.Pin  # PB10
G5: microcontroller.Pin  # PB11
G6: microcontroller.Pin  # PB12
G7: microcontroller.Pin  # PB13
G8: microcontroller.Pin  # PA14
G9: microcontroller.Pin  # PA15
G11: microcontroller.Pin  # PA27
BUS0: microcontroller.Pin  # PB06
BUS1: microcontroller.Pin  # PB07
BUS2: microcontroller.Pin  # PB08
BUS3: microcontroller.Pin  # PB09
BUS4: microcontroller.Pin  # PB10
BUS5: microcontroller.Pin  # PB11
BUS6: microcontroller.Pin  # PB12
BUS7: microcontroller.Pin  # PB13
HOST_ENABLE: microcontroller.Pin  # PA27


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
