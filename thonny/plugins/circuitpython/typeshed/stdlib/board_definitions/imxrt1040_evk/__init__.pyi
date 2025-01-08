# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for iMX RT 1040 EVK
 - port: mimxrt10xx
 - board_id: imxrt1040_evk
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, neopixel_write, onewireio, os, os.getenv, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # GPIO_SD_B1_01
RX: microcontroller.Pin  # GPIO_SD_B1_01
D1: microcontroller.Pin  # GPIO_SD_B1_00
TX: microcontroller.Pin  # GPIO_SD_B1_00
D2: microcontroller.Pin  # GPIO_AD_B0_11
D3: microcontroller.Pin  # GPIO_SD_B1_02
D4: microcontroller.Pin  # GPIO_AD_B0_09
D5: microcontroller.Pin  # GPIO_AD_B0_10
D6: microcontroller.Pin  # GPIO_AD_B1_02
D7: microcontroller.Pin  # GPIO_AD_B1_03
D8: microcontroller.Pin  # GPIO_B1_14
D9: microcontroller.Pin  # GPIO_B1_15
D10: microcontroller.Pin  # GPIO_SD_B0_01
D11: microcontroller.Pin  # GPIO_SD_B0_02
D12: microcontroller.Pin  # GPIO_SD_B0_03
D13: microcontroller.Pin  # GPIO_SD_B0_00
D14: microcontroller.Pin  # GPIO_AD_B1_01
SDA: microcontroller.Pin  # GPIO_AD_B1_01
D15: microcontroller.Pin  # GPIO_AD_B1_00
SCL: microcontroller.Pin  # GPIO_AD_B1_00
A0: microcontroller.Pin  # GPIO_AD_B0_14
A1: microcontroller.Pin  # GPIO_AD_B0_15
A2: microcontroller.Pin  # GPIO_AD_B1_04
A3: microcontroller.Pin  # GPIO_AD_B1_05
A4: microcontroller.Pin  # GPIO_AD_B1_06
A5: microcontroller.Pin  # GPIO_AD_B1_07
USER_LED: microcontroller.Pin  # GPIO_AD_B0_08
LED: microcontroller.Pin  # GPIO_AD_B0_08
SDIO_CLK: microcontroller.Pin  # GPIO_SD_B0_01
SD_SW: microcontroller.Pin  # GPIO_B1_12
SDIO_CMD: microcontroller.Pin  # GPIO_SD_B0_00
SDIO_D0: microcontroller.Pin  # GPIO_SD_B0_02
SDIO_D1: microcontroller.Pin  # GPIO_SD_B0_03
SDIO_D2: microcontroller.Pin  # GPIO_SD_B0_04
SDIO_D3: microcontroller.Pin  # GPIO_SD_B0_05
SD_PWREN: microcontroller.Pin  # GPIO_AD_B1_04
LCD_BACKLIGHT: microcontroller.Pin  # GPIO_B1_15
LCD_RST: microcontroller.Pin  # GPIO_AD_B1_03
LCD_ENABLE: microcontroller.Pin  # GPIO_B0_01
LCD_VSYNC: microcontroller.Pin  # GPIO_B0_03
LCD_HSYNC: microcontroller.Pin  # GPIO_B0_02
LCD_CLK: microcontroller.Pin  # GPIO_B0_00
LCD_D0: microcontroller.Pin  # GPIO_B0_04
LCD_D1: microcontroller.Pin  # GPIO_B0_05
LCD_D2: microcontroller.Pin  # GPIO_B0_06
LCD_D3: microcontroller.Pin  # GPIO_B0_07
LCD_D4: microcontroller.Pin  # GPIO_B0_08
LCD_D5: microcontroller.Pin  # GPIO_B0_09
LCD_D6: microcontroller.Pin  # GPIO_B0_10
LCD_D7: microcontroller.Pin  # GPIO_B0_11
LCD_D8: microcontroller.Pin  # GPIO_B0_12
LCD_D9: microcontroller.Pin  # GPIO_B0_13
LCD_D10: microcontroller.Pin  # GPIO_B0_14
LCD_D11: microcontroller.Pin  # GPIO_B0_15
LCD_D12: microcontroller.Pin  # GPIO_B1_00
LCD_D13: microcontroller.Pin  # GPIO_B1_01
LCD_D14: microcontroller.Pin  # GPIO_B1_02
LCD_D15: microcontroller.Pin  # GPIO_B1_03
LCD_TOUCH_INT: microcontroller.Pin  # GPIO_AD_B0_11
AUDIO_INT: microcontroller.Pin  # GPIO_SD_B1_03
AUDIO_MCLK: microcontroller.Pin  # GPIO_B0_13
AUDIO_RX_SYNC: microcontroller.Pin  # GPIO_B0_14
AUDIO_RX_BCLK: microcontroller.Pin  # GPIO_B0_15
AUDIO_RXD: microcontroller.Pin  # GPIO_AD_B1_00
AUDIO_TXD: microcontroller.Pin  # GPIO_AD_B1_01
AUDIO_TX_BCLK: microcontroller.Pin  # GPIO_AD_B1_02
AUDIO_TX_SYNC: microcontroller.Pin  # GPIO_AD_B1_03
SPDIF_IN: microcontroller.Pin  # GPIO_AD_B1_03
SPDIF_OUT: microcontroller.Pin  # GPIO_AD_B1_02
ETHERNET_MDIO: microcontroller.Pin  # GPIO_EMC_41
ETHERNET_MDC: microcontroller.Pin  # GPIO_EMC_40
ETHERNET_RXD0: microcontroller.Pin  # GPIO_B1_04
ETHERNET_RXD1: microcontroller.Pin  # GPIO_B1_05
ETHERNET_CRS_DV: microcontroller.Pin  # GPIO_B1_06
ETHERNET_TXD0: microcontroller.Pin  # GPIO_B1_07
ETHERNET_TXD1: microcontroller.Pin  # GPIO_B1_08
ETHERNET_TXEN: microcontroller.Pin  # GPIO_B1_09
ETHERNET_INT: microcontroller.Pin  # GPIO_SD_B1_04
ETHERNET_RST: microcontroller.Pin  # GPIO_AD_B0_09
ETHERNET_CLK: microcontroller.Pin  # GPIO_B1_10
ETHERNET_RXER: microcontroller.Pin  # GPIO_B1_11
FREELINK_TX: microcontroller.Pin  # GPIO_AD_B0_12
FREELINK_RX: microcontroller.Pin  # GPIO_AD_B0_13
CAN_TX: microcontroller.Pin  # GPIO_AD_B0_14
CAN_RX: microcontroller.Pin  # GPIO_AD_B0_15
CAN_STBY: microcontroller.Pin  # GPIO_AD_B0_05
USB_HOST_DP: microcontroller.Pin  # USB_OTG1_DP
USB_HOST_DM: microcontroller.Pin  # USB_OTG1_DN


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
