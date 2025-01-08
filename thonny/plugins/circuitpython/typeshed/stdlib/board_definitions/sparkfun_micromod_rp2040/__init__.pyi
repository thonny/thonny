# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for SparkFun MicroMod RP2040 Processor
 - port: raspberrypi
 - board_id: sparkfun_micromod_rp2040
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
LED: microcontroller.Pin  # GPIO25
BATT_VIN3: microcontroller.Pin  # GPIO29
UART_TX1: microcontroller.Pin  # GPIO0
UART_RX1: microcontroller.Pin  # GPIO1
UART_RTS1: microcontroller.Pin  # GPIO3
UART_CTS1: microcontroller.Pin  # GPIO2
TX: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1
UART_TX2: microcontroller.Pin  # GPIO8
UART_RX2: microcontroller.Pin  # GPIO9
I2C_SDA: microcontroller.Pin  # GPIO4
I2C_SCL: microcontroller.Pin  # GPIO5
SDA: microcontroller.Pin  # GPIO4
SCL: microcontroller.Pin  # GPIO5
I2C_INT: microcontroller.Pin  # GPIO8
SPI_CIPO: microcontroller.Pin  # GPIO20
SPI_MISO: microcontroller.Pin  # GPIO20
SPI_COPI: microcontroller.Pin  # GPIO23
SPI_MOSI: microcontroller.Pin  # GPIO23
SPI_SCK: microcontroller.Pin  # GPIO22
SPI_CS: microcontroller.Pin  # GPIO21
CIPO: microcontroller.Pin  # GPIO20
MISO: microcontroller.Pin  # GPIO20
COPI: microcontroller.Pin  # GPIO23
MOSI: microcontroller.Pin  # GPIO23
SCK: microcontroller.Pin  # GPIO22
CS: microcontroller.Pin  # GPIO21
LED_DAT: microcontroller.Pin  # GPIO23
LED_CLK: microcontroller.Pin  # GPIO22
SDIO_CLK: microcontroller.Pin  # GPIO14
SDIO_CMD: microcontroller.Pin  # GPIO15
SDIO_DATA0: microcontroller.Pin  # GPIO12
SDIO_DATA1: microcontroller.Pin  # GPIO11
SDIO_DATA2: microcontroller.Pin  # GPIO10
SDIO_DATA3: microcontroller.Pin  # GPIO9
SPI_CIPO1: microcontroller.Pin  # GPIO12
SPI_MISO1: microcontroller.Pin  # GPIO12
SPI_COPI1: microcontroller.Pin  # GPIO15
SPI_MOSI1: microcontroller.Pin  # GPIO15
SPI_SCK1: microcontroller.Pin  # GPIO14
SPI_CS1: microcontroller.Pin  # GPIO9
AUD_MCLK: microcontroller.Pin  # GPIO24
AUD_OUT: microcontroller.Pin  # GPIO10
AUD_IN: microcontroller.Pin  # GPIO11
AUD_LRCLK: microcontroller.Pin  # GPIO2
AUD_BCLK: microcontroller.Pin  # GPIO3
I2S_OUT: microcontroller.Pin  # GPIO10
I2S_IN: microcontroller.Pin  # GPIO11
I2S_WS: microcontroller.Pin  # GPIO2
I2S_SCK: microcontroller.Pin  # GPIO3
PCM_OUT: microcontroller.Pin  # GPIO10
PCM_IN: microcontroller.Pin  # GPIO11
PCM_SYNC: microcontroller.Pin  # GPIO2
PCM_CLK: microcontroller.Pin  # GPIO3
PDM_DATA: microcontroller.Pin  # GPIO2
PDM_CLK: microcontroller.Pin  # GPIO3
A0: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO27
PWM0: microcontroller.Pin  # GPIO13
PWM1: microcontroller.Pin  # GPIO24
D0: microcontroller.Pin  # GPIO6
D1: microcontroller.Pin  # GPIO7
G0: microcontroller.Pin  # GPIO16
G1: microcontroller.Pin  # GPIO17
G2: microcontroller.Pin  # GPIO18
G3: microcontroller.Pin  # GPIO19
G4: microcontroller.Pin  # GPIO20
G5: microcontroller.Pin  # GPIO21
G6: microcontroller.Pin  # GPIO22
G7: microcontroller.Pin  # GPIO23
G9: microcontroller.Pin  # GPIO28
G10: microcontroller.Pin  # GPIO25
BUS0: microcontroller.Pin  # GPIO16
BUS1: microcontroller.Pin  # GPIO17
BUS2: microcontroller.Pin  # GPIO18
BUS3: microcontroller.Pin  # GPIO19
BUS4: microcontroller.Pin  # GPIO20
BUS5: microcontroller.Pin  # GPIO21
BUS6: microcontroller.Pin  # GPIO22
BUS7: microcontroller.Pin  # GPIO23
CAM_MCLK: microcontroller.Pin  # GPIO10
CAM_PCLK: microcontroller.Pin  # GPIO11
CAM_TRIG: microcontroller.Pin  # GPIO7
CAM_HSYNC: microcontroller.Pin  # GPIO28
CAM_VSYNC: microcontroller.Pin  # GPIO25


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
