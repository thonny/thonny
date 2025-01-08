# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for HalloWing M0 Express
 - port: atmel-samd
 - board_id: hallowing_m0_express
 - NVM size: 256
 - Included modules: adafruit_bus_device, adafruit_pixelbuf, analogio, array, audiocore, audioio, board, builtins, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, i2cdisplaybus, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, paralleldisplaybus, pulseio, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, terminalio, time, touchio, usb_cdc, usb_hid, usb_midi, warnings
 - Frozen libraries: adafruit_lis3dh, neopixel
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA02
SPEAKER: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PB08
LIGHT: microcontroller.Pin  # PB08
A2: microcontroller.Pin  # PB09
TOUCH4: microcontroller.Pin  # PB09
A3: microcontroller.Pin  # PA04
TOUCH3: microcontroller.Pin  # PA04
A4: microcontroller.Pin  # PA05
TOUCH2: microcontroller.Pin  # PA05
A5: microcontroller.Pin  # PA06
TOUCH1: microcontroller.Pin  # PA06
SCK: microcontroller.Pin  # PB23
MOSI: microcontroller.Pin  # PB22
MISO: microcontroller.Pin  # PB03
D0: microcontroller.Pin  # PA09
RX: microcontroller.Pin  # PA09
D1: microcontroller.Pin  # PA10
TX: microcontroller.Pin  # PA10
SDA: microcontroller.Pin  # PA16
SCL: microcontroller.Pin  # PA17
D5: microcontroller.Pin  # PA15
D6: microcontroller.Pin  # PA18
D9: microcontroller.Pin  # PA19
D10: microcontroller.Pin  # PA20
D11: microcontroller.Pin  # PA21
D12: microcontroller.Pin  # PA22
LED: microcontroller.Pin  # PA23
D13: microcontroller.Pin  # PA23
D4: microcontroller.Pin  # PA08
EXTERNAL_NEOPIXEL: microcontroller.Pin  # PA08
NEOPIXEL: microcontroller.Pin  # PA12
D3: microcontroller.Pin  # PA11
SENSE: microcontroller.Pin  # PA11
TFT_BACKLIGHT: microcontroller.Pin  # PA00
TFT_CS: microcontroller.Pin  # PA01
TFT_DC: microcontroller.Pin  # PA28
TFT_RESET: microcontroller.Pin  # PA27
BATTERY: microcontroller.Pin  # PB02
ACCELEROMETER_INTERRUPT: microcontroller.Pin  # PA14


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
