# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for DynOSSAT-EDU-EPS
 - port: atmel-samd
 - board_id: dynossat_edu_eps
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, audiobusio, audiocore, audioio, board, builtins, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, i2cdisplaybus, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, paralleldisplaybus, pulseio, pwmio, rainbowio, random, rtc, storage, struct, supervisor, sys, terminalio, time, usb_cdc, usb_hid, usb_midi, warnings
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
SCK: microcontroller.Pin  # PB11
MOSI: microcontroller.Pin  # PA12
MISO: microcontroller.Pin  # PB10
D26: microcontroller.Pin  # PA30
D27: microcontroller.Pin  # PA31
RX: microcontroller.Pin  # PA17
D0: microcontroller.Pin  # PA07
OVTEMP: microcontroller.Pin  # PA07
TX: microcontroller.Pin  # PA16
SDA: microcontroller.Pin  # PA08
SCL: microcontroller.Pin  # PA09
D2: microcontroller.Pin  # PA11
SAT_RESET: microcontroller.Pin  # PA11
D1: microcontroller.Pin  # PA10
SAT_PWR_ENABLE: microcontroller.Pin  # PA10
D3: microcontroller.Pin  # PA19
INT_IMU_OBC: microcontroller.Pin  # PA19
D4: microcontroller.Pin  # PB03
PWRMON_SDA: microcontroller.Pin  # PA04
PWRMON_SCL: microcontroller.Pin  # PA05
PWRMON_ALERT: microcontroller.Pin  # PB03
A0: microcontroller.Pin  # PB09
A1: microcontroller.Pin  # PB02
V_3V3_MEAS: microcontroller.Pin  # PB09
V_5V_MEAS: microcontroller.Pin  # PB02
FLASH_SCK: microcontroller.Pin  # PA23
FLASH_MOSI: microcontroller.Pin  # PA22
FLASH_MISO: microcontroller.Pin  # PA21
FLASH_CS: microcontroller.Pin  # PA20
D13: microcontroller.Pin  # PA06
NEOPIXEL: microcontroller.Pin  # PA06


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
