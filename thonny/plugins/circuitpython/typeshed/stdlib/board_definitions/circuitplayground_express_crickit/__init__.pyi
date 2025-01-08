# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit CircuitPlayground Express with Crickit libraries
 - port: atmel-samd
 - board_id: circuitplayground_express_crickit
 - NVM size: 256
 - Included modules: adafruit_bus_device, adafruit_pixelbuf, analogio, array, audiobusio, audiocore, audioio, board, builtins, busio, busio.SPI, busio.UART, codeop, collections, digitalio, errno, locale, math, microcontroller, neopixel_write, nvm, onewireio, os, pulseio, pwmio, rainbowio, random, rotaryio, rtc, storage, struct, supervisor, sys, time, touchio, usb_cdc, usb_hid, usb_midi, warnings
 - Frozen libraries: adafruit_circuitplayground, adafruit_crickit, adafruit_lis3dh, adafruit_motor, adafruit_seesaw, adafruit_thermistor, neopixel
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA02
D12: microcontroller.Pin  # PA02
SPEAKER: microcontroller.Pin  # PA02
A1: microcontroller.Pin  # PA05
D6: microcontroller.Pin  # PA05
A2: microcontroller.Pin  # PA06
D9: microcontroller.Pin  # PA06
A3: microcontroller.Pin  # PA07
D10: microcontroller.Pin  # PA07
A4: microcontroller.Pin  # PB03
D3: microcontroller.Pin  # PB03
SCL: microcontroller.Pin  # PB03
A5: microcontroller.Pin  # PB02
D2: microcontroller.Pin  # PB02
SDA: microcontroller.Pin  # PB02
A6: microcontroller.Pin  # PB09
D0: microcontroller.Pin  # PB09
RX: microcontroller.Pin  # PB09
A7: microcontroller.Pin  # PB08
D1: microcontroller.Pin  # PB08
TX: microcontroller.Pin  # PB08
LIGHT: microcontroller.Pin  # PA11
A8: microcontroller.Pin  # PA11
TEMPERATURE: microcontroller.Pin  # PA09
A9: microcontroller.Pin  # PA09
BUTTON_A: microcontroller.Pin  # PA28
D4: microcontroller.Pin  # PA28
BUTTON_B: microcontroller.Pin  # PA14
D5: microcontroller.Pin  # PA14
SLIDE_SWITCH: microcontroller.Pin  # PA15
D7: microcontroller.Pin  # PA15
NEOPIXEL: microcontroller.Pin  # PB23
D8: microcontroller.Pin  # PB23
LED: microcontroller.Pin  # PA17
D13: microcontroller.Pin  # PA17
REMOTEIN: microcontroller.Pin  # PA12
IR_RX: microcontroller.Pin  # PA12
REMOTEOUT: microcontroller.Pin  # PA23
IR_TX: microcontroller.Pin  # PA23
IR_PROXIMITY: microcontroller.Pin  # PA04
MICROPHONE_CLOCK: microcontroller.Pin  # PA10
MICROPHONE_DATA: microcontroller.Pin  # PA08
ACCELEROMETER_INTERRUPT: microcontroller.Pin  # PA13
ACCELEROMETER_SDA: microcontroller.Pin  # PA00
ACCELEROMETER_SCL: microcontroller.Pin  # PA01
SPEAKER_ENABLE: microcontroller.Pin  # PA30
SCK: microcontroller.Pin  # PA05
MOSI: microcontroller.Pin  # PA07
MISO: microcontroller.Pin  # PA06


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
