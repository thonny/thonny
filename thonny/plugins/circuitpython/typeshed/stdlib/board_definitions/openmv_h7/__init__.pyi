# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for OPENMV-H7 R1
 - port: stm
 - board_id: openmv_h7
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, array, atexit, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, onewireio, os, os.getenv, rainbowio, random, re, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
P0: microcontroller.Pin  # PB15
P1: microcontroller.Pin  # PB14
P2: microcontroller.Pin  # PB13
P3: microcontroller.Pin  # PB12
P4: microcontroller.Pin  # PB10
P5: microcontroller.Pin  # PB11
P6: microcontroller.Pin  # PA05
P7: microcontroller.Pin  # PD12
P8: microcontroller.Pin  # PD13
P9: microcontroller.Pin  # PD14
LED1: microcontroller.Pin  # PC00
LED2: microcontroller.Pin  # PC01
LED3: microcontroller.Pin  # PC02
LED4: microcontroller.Pin  # PE02
LED_RED: microcontroller.Pin  # PC00
LED_GREEN: microcontroller.Pin  # PC01
LED_BLUE: microcontroller.Pin  # PC02
LED_IR: microcontroller.Pin  # PE02
UART1_TX: microcontroller.Pin  # PB14
UART1_RX: microcontroller.Pin  # PB15
UART3_TX: microcontroller.Pin  # PB10
UART3_RX: microcontroller.Pin  # PB11
I2C2_SCL: microcontroller.Pin  # PB10
I2C2_SDA: microcontroller.Pin  # PB11
I2C4_SCL: microcontroller.Pin  # PD12
I2C4_SDA: microcontroller.Pin  # PD13
SPI2_NSS: microcontroller.Pin  # PB12
SPI2_SCK: microcontroller.Pin  # PB13
SPI2_MISO: microcontroller.Pin  # PB14
SPI2_MOSI: microcontroller.Pin  # PB15


# Members:

# Unmapped:
#   none
