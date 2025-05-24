# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Cedar Grove StringCar M0 Express
 - port: atmel-samd
 - board_id: stringcar_m0_express
 - NVM size: 256
 - Included modules: adafruit_pixelbuf, analogio, array, audiobusio, audiocore, audioio, board, builtins, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, i2cdisplaybus, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, paralleldisplaybus, pulseio, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, terminalio, time, touchio, usb_cdc, usb_hid, warnings
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
PIEZO: microcontroller.Pin  # PA08
VOLTAGE_MONITOR: microcontroller.Pin  # PA02
SENSOR_IN: microcontroller.Pin  # PA09
MOTOR_OUT_1: microcontroller.Pin  # PA06
MOTOR_OUT_2: microcontroller.Pin  # PA07
LED_STATUS: microcontroller.Pin  # PA10
SCL: microcontroller.Pin  # PA05
SDA: microcontroller.Pin  # PA04
DOTSTAR_DI: microcontroller.Pin  # PA00
DOTSTAR_CI: microcontroller.Pin  # PA01


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
