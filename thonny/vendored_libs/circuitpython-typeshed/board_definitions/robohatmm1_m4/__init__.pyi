# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Robo HAT MM1 M4
 - port: atmel-samd
 - board_id: robohatmm1_m4
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, board, builtins, builtins.pow3, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, errno, floppyio, getpass, i2ctarget, io, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, samd, sdcardio, select, spitarget, storage, struct, supervisor, synthio, sys, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, warnings, watchdog, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SERVO1: microcontroller.Pin  # PA18
SERVO2: microcontroller.Pin  # PA19
SERVO3: microcontroller.Pin  # PA20
SERVO4: microcontroller.Pin  # PA21
SERVO5: microcontroller.Pin  # PA11
SERVO6: microcontroller.Pin  # PA10
SERVO7: microcontroller.Pin  # PA09
SERVO8: microcontroller.Pin  # PA08
RCC1: microcontroller.Pin  # PA07
RCC2: microcontroller.Pin  # PA06
RCC3: microcontroller.Pin  # PA05
RCC4: microcontroller.Pin  # PA04
VOLTAGE_MONITOR: microcontroller.Pin  # PA02
BATTERY: microcontroller.Pin  # PA02
POWER_OFF: microcontroller.Pin  # PA03
POWER_DISABLE: microcontroller.Pin  # PA03
POWER_ON: microcontroller.Pin  # PA27
POWER_ENABLE: microcontroller.Pin  # PA27
BUTTON: microcontroller.Pin  # PA27
NEOPIXEL: microcontroller.Pin  # PB23
LED: microcontroller.Pin  # PB22
GROVE_SCL: microcontroller.Pin  # PA09
GROVE_SDA: microcontroller.Pin  # PA08
GROVE_RX: microcontroller.Pin  # PA09
GROVE_TX: microcontroller.Pin  # PA08
GROVE_D1: microcontroller.Pin  # PA09
GROVE_D0: microcontroller.Pin  # PA08
GROVE_A1: microcontroller.Pin  # PA09
GROVE_A0: microcontroller.Pin  # PA08
UART_TX: microcontroller.Pin  # PA04
UART_RX: microcontroller.Pin  # PA05
UART_CTS: microcontroller.Pin  # PA06
UART_RTS: microcontroller.Pin  # PA07
TX1: microcontroller.Pin  # PA16
RX1: microcontroller.Pin  # PA17
PI_TX: microcontroller.Pin  # PA16
PI_RX: microcontroller.Pin  # PA17
SDA1: microcontroller.Pin  # PA00
SCL1: microcontroller.Pin  # PA01
FLASH_SCK: microcontroller.Pin  # PA13
FLASH_MISO: microcontroller.Pin  # PA14
FLASH_MOSI: microcontroller.Pin  # PA12
FLASH_CS: microcontroller.Pin  # PA15
SDA: microcontroller.Pin  # PA22
SCL: microcontroller.Pin  # PA23
PI_SDA: microcontroller.Pin  # PA22
PI_SCL: microcontroller.Pin  # PA23
MOSI: microcontroller.Pin  # PB08
SCK: microcontroller.Pin  # PB09
SS: microcontroller.Pin  # PB10
MISO: microcontroller.Pin  # PB11
GPS_TX: microcontroller.Pin  # PB02
GPS_RX: microcontroller.Pin  # PB03
PI_GP25: microcontroller.Pin  # PA30
SWCLK: microcontroller.Pin  # PA30
PI_GP24: microcontroller.Pin  # PA31
SWDIO: microcontroller.Pin  # PA31


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
