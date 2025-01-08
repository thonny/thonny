# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ST STM32F746G Discovery
 - port: stm
 - board_id: stm32f746g_discovery
 - NVM size: Unknown
 - Included modules: _asyncio, _bleio, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, array, atexit, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, math, microcontroller, msgpack, onewireio, os, os.getenv, pulseio, pwmio, rainbowio, random, re, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, sys, terminalio, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA00
A1: microcontroller.Pin  # PF10
A2: microcontroller.Pin  # PF09
A3: microcontroller.Pin  # PF08
A4: microcontroller.Pin  # PF07
A5: microcontroller.Pin  # PF06
D0: microcontroller.Pin  # PC07
D1: microcontroller.Pin  # PC06
D2: microcontroller.Pin  # PG06
D3: microcontroller.Pin  # PB04
D4: microcontroller.Pin  # PG07
D5: microcontroller.Pin  # PA08
D6: microcontroller.Pin  # PH06
D7: microcontroller.Pin  # PI03
D8: microcontroller.Pin  # PI02
D9: microcontroller.Pin  # PA15
D10: microcontroller.Pin  # PI00
D11: microcontroller.Pin  # PB15
D12: microcontroller.Pin  # PB14
D13: microcontroller.Pin  # PI01
D14: microcontroller.Pin  # PB09
D15: microcontroller.Pin  # PB08
LED: microcontroller.Pin  # PI01
SW: microcontroller.Pin  # PI11
TP1: microcontroller.Pin  # PH02
TP2: microcontroller.Pin  # PI08
TP3: microcontroller.Pin  # PH15
AUDIO_INT: microcontroller.Pin  # PD06
AUDIO_SDA: microcontroller.Pin  # PH08
AUDIO_SCL: microcontroller.Pin  # PH07
EXT_SDA: microcontroller.Pin  # PB09
EXT_SCL: microcontroller.Pin  # PB08
EXT_RST: microcontroller.Pin  # PG03
SD_D0: microcontroller.Pin  # PC08
SD_D1: microcontroller.Pin  # PC09
SD_D2: microcontroller.Pin  # PC10
SD_D3: microcontroller.Pin  # PC11
SD_CK: microcontroller.Pin  # PC12
SD_CMD: microcontroller.Pin  # PD02
SD_SW: microcontroller.Pin  # PC13
LCD_BL_CTRL: microcontroller.Pin  # PK03
LCD_INT: microcontroller.Pin  # PI13
LCD_SDA: microcontroller.Pin  # PH08
LCD_SCL: microcontroller.Pin  # PH07
OTG_FS_POWER: microcontroller.Pin  # PD05
OTG_FS_OVER_CURRENT: microcontroller.Pin  # PD04
OTG_HS_OVER_CURRENT: microcontroller.Pin  # PE03
USB_VBUS: microcontroller.Pin  # PJ12
USB_ID: microcontroller.Pin  # PA10
USB_DM: microcontroller.Pin  # PA11
USB_DP: microcontroller.Pin  # PA12
VCP_TX: microcontroller.Pin  # PA09
VCP_RX: microcontroller.Pin  # PB07
CAN_TX: microcontroller.Pin  # PB13
CAN_RX: microcontroller.Pin  # PB12
ETH_MDC: microcontroller.Pin  # PC01
ETH_MDIO: microcontroller.Pin  # PA02
ETH_RMII_REF_CLK: microcontroller.Pin  # PA01
ETH_RMII_CRS_DV: microcontroller.Pin  # PA07
ETH_RMII_RXD0: microcontroller.Pin  # PC04
ETH_RMII_RXD1: microcontroller.Pin  # PC05
ETH_RMII_RXER: microcontroller.Pin  # PG02
ETH_RMII_TX_EN: microcontroller.Pin  # PG11
ETH_RMII_TXD0: microcontroller.Pin  # PG13
ETH_RMII_TXD1: microcontroller.Pin  # PG14
SDRAM_SDCKE0: microcontroller.Pin  # PC03
SDRAM_SDNE0: microcontroller.Pin  # PH03
SDRAM_SDCLK: microcontroller.Pin  # PG08
SDRAM_SDNCAS: microcontroller.Pin  # PG15
SDRAM_SDNRAS: microcontroller.Pin  # PF11
SDRAM_SDNWE: microcontroller.Pin  # PH05
SDRAM_BA0: microcontroller.Pin  # PG04
SDRAM_BA1: microcontroller.Pin  # PG05
SDRAM_NBL0: microcontroller.Pin  # PE00
SDRAM_NBL1: microcontroller.Pin  # PE01
SDRAM_A0: microcontroller.Pin  # PF00
SDRAM_A1: microcontroller.Pin  # PF01
SDRAM_A2: microcontroller.Pin  # PF02
SDRAM_A3: microcontroller.Pin  # PF03
SDRAM_A4: microcontroller.Pin  # PF04
SDRAM_A5: microcontroller.Pin  # PF05
SDRAM_A6: microcontroller.Pin  # PF12
SDRAM_A7: microcontroller.Pin  # PF13
SDRAM_A8: microcontroller.Pin  # PF14
SDRAM_A9: microcontroller.Pin  # PF15
SDRAM_A10: microcontroller.Pin  # PG00
SDRAM_A11: microcontroller.Pin  # PG01
SDRAM_D0: microcontroller.Pin  # PD14
SDRAM_D1: microcontroller.Pin  # PD15
SDRAM_D2: microcontroller.Pin  # PD00
SDRAM_D3: microcontroller.Pin  # PD01
SDRAM_D4: microcontroller.Pin  # PE07
SDRAM_D5: microcontroller.Pin  # PE08
SDRAM_D6: microcontroller.Pin  # PE09
SDRAM_D7: microcontroller.Pin  # PE10
SDRAM_D8: microcontroller.Pin  # PE11
SDRAM_D9: microcontroller.Pin  # PE12
SDRAM_D10: microcontroller.Pin  # PE13
SDRAM_D11: microcontroller.Pin  # PE14
SDRAM_D12: microcontroller.Pin  # PE15
SDRAM_D13: microcontroller.Pin  # PD08
SDRAM_D14: microcontroller.Pin  # PD09
SDRAM_D15: microcontroller.Pin  # PD10
I2C3_SDA: microcontroller.Pin  # PH08
I2C3_SCL: microcontroller.Pin  # PH07


# Members:

# Unmapped:
#   none
