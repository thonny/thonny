"""Board specific pin names

Common container for board base pin names. These will vary from board to
board so don't expect portability when using this module.

Another common use of this module is to use serial communication buses with
the default pins and settings.  For more information about serial communcication
in CircuitPython, see the :mod:`busio`.

For more information regarding the typical usage of :py:mod:`board`, refer to the `CircuitPython
Essentials Learn guide
<https://learn.adafruit.com/circuitpython-essentials/circuitpython-pins-and-modules>`_

.. warning:: The board module varies by board. The APIs documented here may or may not be
             available on a specific board."""

from __future__ import annotations

import busio

board_id: str
"""Board ID string. The unique identifier for the board model in
circuitpython, as well as on circuitpython.org.
Example: "hallowing_m0_express"."""

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """
    ...

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """
    ...

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """
    ...


from microcontroller import Pin

A: Pin
A0: Pin
A0_D26: Pin
A1: Pin
A10: Pin
A11: Pin
A12: Pin
A13: Pin
A14: Pin
A15: Pin
A16: Pin
A17: Pin
A18: Pin
A19: Pin
A1_4: Pin
A1_5: Pin
A1_6: Pin
A1_7: Pin
A1_D27: Pin
A2: Pin
A20: Pin
A25: Pin
A26: Pin
A27: Pin
A29: Pin
A3: Pin
A32: Pin
A33: Pin
A34: Pin
A35: Pin
A36: Pin
A37: Pin
A38: Pin
A39: Pin
A4: Pin
A5: Pin
A6: Pin
A7: Pin
A8: Pin
A9: Pin
ACCELEROMETER_GYRO_INTERRUPT: Pin
ACCELEROMETER_INTERRUPT: Pin
ACCELEROMETER_SCL: Pin
ACCELEROMETER_SDA: Pin
ACCEL_INT1: Pin
ACCEL_INT2: Pin
ACCEL_SCL: Pin
ACCEL_SDA: Pin
ACC_INT: Pin
ACC_INT1: Pin
ACC_INT2: Pin
ACC_INT_1: Pin
ACC_INT_2: Pin
ACC_SCL: Pin
ACC_SDA: Pin
ACTION_BUTTON: Pin
AD1: Pin
ADC: Pin
ADC0: Pin
ADC1: Pin
ADC1_CH0: Pin
ADC1_CH1: Pin
ADC1_CH2: Pin
ADC1_CH3: Pin
ADC1_CH4: Pin
ADC1_CH5: Pin
ADC1_CH6: Pin
ADC1_CH7: Pin
ADC1_CH8: Pin
ADC1_CH9: Pin
ADC1_CH9B: Pin
ADC2: Pin
ADC2_CH0: Pin
ADC2_CH1: Pin
ADC2_CH2: Pin
ADC2_CH3: Pin
ADC2_CH4: Pin
ADC2_CH5: Pin
ADC2_CH6: Pin
ADC2_CH7: Pin
ADC2_CH8: Pin
ADC2_CH9: Pin
ADC2_CH9A: Pin
ADC3: Pin
ADCDAC: Pin
ADC_ADDR_0: Pin
ADC_ADDR_1: Pin
ADC_ADDR_2: Pin
ADC_BAT: Pin
ADC_CS: Pin
ADC_MISO: Pin
ADC_MOSI: Pin
ADC_SCK: Pin
ADC_VBUS_IN: Pin
ADC_VBUS_OUT: Pin
ADDON_SCL: Pin
ADDON_SDA: Pin
AIN0: Pin
AIN1: Pin
AIN2: Pin
AIN3: Pin
AIN4: Pin
AIN5: Pin
AIN6: Pin
AIN7: Pin
AIN_0: Pin
AIN_1: Pin
AIN_2: Pin
AIN_3: Pin
AIN_4: Pin
AIN_5: Pin
AIN_6: Pin
AIN_7: Pin
ALERT: Pin
AMB: Pin
AMB_INT: Pin
AMP_BCLK: Pin
AMP_DATA: Pin
AMP_EN: Pin
AMP_LRCLK: Pin
AMP_SD: Pin
AN0: Pin
AN1: Pin
AN5V: Pin
ANMB: Pin
ANTENNA_EXTERNAL: Pin
ANTENNA_PCB: Pin
ANTENNA_SWITCH: Pin
ANVLIM: Pin
APA102_CLK: Pin
APA102_DI: Pin
APA102_MOSI: Pin
APA102_PWR: Pin
APA102_SCK: Pin
AREF: Pin
ATMAC_SCL: Pin
ATMAC_SDA: Pin
ATW01_EN: Pin
ATW01_GPIO_1: Pin
ATW01_GPIO_3: Pin
ATW01_IRQ: Pin
ATW01_MISO: Pin
ATW01_MOSI: Pin
ATW01_RESET: Pin
ATW01_SCK: Pin
ATW01_SS: Pin
ATW01_WAKE: Pin
AUDIO: Pin
AUDIO_BCK: Pin
AUDIO_BCLK: Pin
AUDIO_BT_ADC: Pin
AUDIO_DATA: Pin
AUDIO_DIN: Pin
AUDIO_I2S0_BCLK: Pin
AUDIO_I2S0_LRCK: Pin
AUDIO_I2S0_MCLK: Pin
AUDIO_I2S0_SDI: Pin
AUDIO_I2S0_SDO: Pin
AUDIO_I2S1_BCLK_DAC2: Pin
AUDIO_I2S1_LRCK_DAC1: Pin
AUDIO_I2S1_MCLK: Pin
AUDIO_I2S1_SDI: Pin
AUDIO_I2S1_SDO: Pin
AUDIO_INT: Pin
AUDIO_LRCLK: Pin
AUDIO_MCLK: Pin
AUDIO_N: Pin
AUDIO_OUT: Pin
AUDIO_P: Pin
AUDIO_PA_CTRL: Pin
AUDIO_RST: Pin
AUDIO_RXD: Pin
AUDIO_RX_BCLK: Pin
AUDIO_RX_SYNC: Pin
AUDIO_SCL: Pin
AUDIO_SD: Pin
AUDIO_SDA: Pin
AUDIO_SPI_CS: Pin
AUDIO_SPI_MISO: Pin
AUDIO_SPI_MOSI: Pin
AUDIO_SPI_SCK: Pin
AUDIO_SYNC: Pin
AUDIO_TXD: Pin
AUDIO_TX_BCLK: Pin
AUDIO_TX_SYNC: Pin
AUDIO_WAKE_INT: Pin
AUDIO_WS: Pin
AUD_BCLK: Pin
AUD_IN: Pin
AUD_LRCLK: Pin
AUD_MCLK: Pin
AUD_OUT: Pin
AUX_1: Pin
AUX_10: Pin
AUX_11: Pin
AUX_12: Pin
AUX_3: Pin
AUX_4: Pin
AUX_5: Pin
AUX_6: Pin
AUX_8: Pin
AUX_9: Pin
AUX_I2C_SCL: Pin
AUX_I2C_SDA: Pin
AUX_SPI_MISO: Pin
AUX_SPI_MOSI: Pin
AUX_SPI_SCK: Pin
AUX_SPI_SS: Pin
AUX_UART_CTS: Pin
AUX_UART_RTS: Pin
AUX_UART_RX: Pin
AUX_UART_TX: Pin
AXIS_INT: Pin
AXP202_INT: Pin
B: Pin
B0: Pin
B1: Pin
B10: Pin
B12: Pin
B13: Pin
B14: Pin
B15: Pin
B2: Pin
B3: Pin
B4: Pin
B5: Pin
B6: Pin
B7: Pin
B8: Pin
B9: Pin
BACKLIGHT: Pin
BACKLIGHT_PWM: Pin
BAT: Pin
BATTERY: Pin
BATTERY_DIV: Pin
BATTERY_ENABLE: Pin
BATTERY_MONITOR: Pin
BATTERY_MONITOR_ENABLE: Pin
BATTERY_SENSE: Pin
BATTERY_VOLTAGE: Pin
BATT_VIN3: Pin
BAT_ADC: Pin
BAT_ADC_EN: Pin
BAT_HOLD: Pin
BAT_INT: Pin
BAT_SENSE: Pin
BAT_VOL: Pin
BAT_VOLT: Pin
BCS: Pin
BC_CS: Pin
BC_EN: Pin
BC_MISO: Pin
BC_MOSI: Pin
BC_READY: Pin
BC_SCK: Pin
BLUE: Pin
BLUELED: Pin
BLUE_LED: Pin
BLUE_LED1_INVERTED: Pin
BLUE_LED2_INVERTED: Pin
BM8563_SCL: Pin
BM8563_SDA: Pin
BMA423_INT: Pin
BMI_INT1: Pin
BMI_INT2: Pin
BOARD_ID: Pin
BOARD_ID_DISABLE: Pin
BOOST_EN: Pin
BOOST_ENABLE: Pin
BOOT: Pin
BOOT0: Pin
BOOTSEL: Pin
BOOT_BTN: Pin
BT: Pin
BT840_RESETN: Pin
BT840_SWO: Pin
BTN: Pin
BTN1: Pin
BTN2: Pin
BTN3: Pin
BTN4: Pin
BTN5: Pin
BTNA: Pin
BTNB: Pin
BTN_A: Pin
BTN_AXIS_X: Pin
BTN_AXIS_Y: Pin
BTN_B: Pin
BTN_C: Pin
BTN_CENTER: Pin
BTN_DOWN: Pin
BTN_L_R: Pin
BTN_MENU: Pin
BTN_SELECT: Pin
BTN_START: Pin
BTN_UP: Pin
BTN_UP_DOWN: Pin
BTN_VOLUME: Pin
BT_ARRAY_ADC: Pin
BURN1: Pin
BURN2: Pin
BUS0: Pin
BUS1: Pin
BUS2: Pin
BUS3: Pin
BUS4: Pin
BUS5: Pin
BUS6: Pin
BUS7: Pin
BUSY: Pin
BUTTON: Pin
BUTTON0: Pin
BUTTON1: Pin
BUTTON1_DEFAULT: Pin
BUTTON1_OPTIONAL: Pin
BUTTON2: Pin
BUTTON2_DEFAULT: Pin
BUTTON2_OPTIONAL: Pin
BUTTON3: Pin
BUTTON4: Pin
BUTTONS: Pin
BUTTON_1: Pin
BUTTON_2: Pin
BUTTON_3: Pin
BUTTON_A: Pin
BUTTON_B: Pin
BUTTON_C: Pin
BUTTON_CLK: Pin
BUTTON_CLOCK: Pin
BUTTON_D: Pin
BUTTON_DOWN: Pin
BUTTON_DW: Pin
BUTTON_I: Pin
BUTTON_J: Pin
BUTTON_K: Pin
BUTTON_L: Pin
BUTTON_LATCH: Pin
BUTTON_LEFT: Pin
BUTTON_MENU: Pin
BUTTON_O: Pin
BUTTON_OK: Pin
BUTTON_OUT: Pin
BUTTON_R: Pin
BUTTON_RIGHT: Pin
BUTTON_S: Pin
BUTTON_SELECT: Pin
BUTTON_SW1: Pin
BUTTON_SW2: Pin
BUTTON_SW3: Pin
BUTTON_SW4: Pin
BUTTON_UP: Pin
BUTTON_USER: Pin
BUTTON_USR: Pin
BUTTON_W: Pin
BUTTON_X: Pin
BUTTON_Z: Pin
BUZZER: Pin
BUZZER_GP0: Pin
BUZZER_GP3: Pin
C: Pin
C1: Pin
C13: Pin
C14: Pin
C15: Pin
C2: Pin
C3: Pin
C4: Pin
C5: Pin
C6: Pin
C7: Pin
C8: Pin
CAM: Pin
CAMD2: Pin
CAMD3: Pin
CAMD4: Pin
CAMD5: Pin
CAMD6: Pin
CAMD7: Pin
CAMD8: Pin
CAMD9: Pin
CAMERA_D2: Pin
CAMERA_D3: Pin
CAMERA_D4: Pin
CAMERA_D5: Pin
CAMERA_D6: Pin
CAMERA_D7: Pin
CAMERA_D8: Pin
CAMERA_D9: Pin
CAMERA_DATA2: Pin
CAMERA_DATA3: Pin
CAMERA_DATA4: Pin
CAMERA_DATA5: Pin
CAMERA_DATA6: Pin
CAMERA_DATA7: Pin
CAMERA_DATA8: Pin
CAMERA_DATA9: Pin
CAMERA_HREF: Pin
CAMERA_PCLK: Pin
CAMERA_PWDN: Pin
CAMERA_RESET: Pin
CAMERA_SIOC: Pin
CAMERA_SIOD: Pin
CAMERA_VSYNC: Pin
CAMERA_XCLK: Pin
CAMH: Pin
CAMPC: Pin
CAMSC: Pin
CAMSD: Pin
CAMV: Pin
CAMXC: Pin
CAM_D0: Pin
CAM_D1: Pin
CAM_D2: Pin
CAM_D3: Pin
CAM_D4: Pin
CAM_D5: Pin
CAM_D6: Pin
CAM_D7: Pin
CAM_HREF: Pin
CAM_HSYNC: Pin
CAM_LDO_EN: Pin
CAM_MCLK: Pin
CAM_PCLK: Pin
CAM_SCL: Pin
CAM_SDA: Pin
CAM_SIOC: Pin
CAM_SIOD: Pin
CAM_TRIG: Pin
CAM_VSYNC: Pin
CAM_XCLK: Pin
CAM_Y2: Pin
CAM_Y3: Pin
CAM_Y4: Pin
CAM_Y5: Pin
CAM_Y6: Pin
CAM_Y7: Pin
CAM_Y8: Pin
CAM_Y9: Pin
CAN_CS: Pin
CAN_INTERRUPT: Pin
CAN_RESET: Pin
CAN_RX: Pin
CAN_RX0_BF: Pin
CAN_STANDBY: Pin
CAN_STBY: Pin
CAN_TX: Pin
CAN_TX0_RTS: Pin
CAP0: Pin
CAP1: Pin
CAP10: Pin
CAP11: Pin
CAP12: Pin
CAP13: Pin
CAP2: Pin
CAP3: Pin
CAP4: Pin
CAP5: Pin
CAP6: Pin
CAP7: Pin
CAP8: Pin
CAP9: Pin
CAP_PIN: Pin
CARD_CS: Pin
CDONE: Pin
CE0: Pin
CE1: Pin
CEC: Pin
CELL_CTS: Pin
CELL_DCD: Pin
CELL_DSR: Pin
CELL_DTR: Pin
CELL_HW_SHUTDOWN: Pin
CELL_ON_OFF: Pin
CELL_POWER_ENABLE: Pin
CELL_PWRMON: Pin
CELL_RTS: Pin
CELL_RX: Pin
CELL_TX: Pin
CHARGE_COMPLETE: Pin
CHARGE_PORT: Pin
CHARGE_RATE: Pin
CHARGE_STAT: Pin
CHARGE_STATUS: Pin
CHARGING: Pin
CHRG: Pin
CHRG_EN: Pin
CHRG_STAT: Pin
CIPO: Pin
CKN: Pin
CKP: Pin
CLK: Pin
CLOCK: Pin
CMD: Pin
COL0: Pin
COL1: Pin
COL10: Pin
COL11: Pin
COL12: Pin
COL13: Pin
COL14: Pin
COL15: Pin
COL16: Pin
COL17: Pin
COL2: Pin
COL3: Pin
COL4: Pin
COL5: Pin
COL6: Pin
COL7: Pin
COL8: Pin
COL9: Pin
COMPASS_SCL: Pin
COMPASS_SDA: Pin
COPI: Pin
CS: Pin
CS0: Pin
CS1: Pin
CSI_D2: Pin
CSI_D3: Pin
CSI_D4: Pin
CSI_D5: Pin
CSI_D6: Pin
CSI_D7: Pin
CSI_D8: Pin
CSI_D9: Pin
CSI_HSYNC: Pin
CSI_MCLK: Pin
CSI_PIXCLK: Pin
CSI_PWDN: Pin
CSI_VSYNC: Pin
CSN: Pin
CS_2: Pin
CS_CNN: Pin
CS_SD: Pin
CTP_INT: Pin
CTP_RST: Pin
CTS: Pin
CTS0: Pin
CTS1: Pin
CTS2: Pin
CTS3: Pin
CURRENT_SENSE: Pin
D: Pin
D0: Pin
D00: Pin
D01: Pin
D02: Pin
D03: Pin
D04: Pin
D05: Pin
D06: Pin
D07: Pin
D08: Pin
D09: Pin
D0N: Pin
D0P: Pin
D1: Pin
D10: Pin
D10_GND: Pin
D11: Pin
D11_GND: Pin
D12: Pin
D13: Pin
D13_LED: Pin
D14: Pin
D15: Pin
D16: Pin
D17: Pin
D17_A17: Pin
D18: Pin
D18_A18: Pin
D19: Pin
D1N: Pin
D1P: Pin
D1_A1: Pin
D2: Pin
D20: Pin
D21: Pin
D22: Pin
D23: Pin
D24: Pin
D25: Pin
D26: Pin
D27: Pin
D28: Pin
D29: Pin
D2N: Pin
D2P: Pin
D2_A2: Pin
D3: Pin
D30: Pin
D31: Pin
D32: Pin
D33: Pin
D34: Pin
D35: Pin
D36: Pin
D37: Pin
D38: Pin
D39: Pin
D4: Pin
D40: Pin
D41: Pin
D42: Pin
D43: Pin
D44: Pin
D45: Pin
D46: Pin
D47: Pin
D48: Pin
D49: Pin
D5: Pin
D50: Pin
D51: Pin
D52: Pin
D53: Pin
D54: Pin
D55: Pin
D56: Pin
D57: Pin
D58: Pin
D59: Pin
D6: Pin
D60: Pin
D61: Pin
D62: Pin
D63: Pin
D64: Pin
D65: Pin
D66: Pin
D67: Pin
D68: Pin
D69: Pin
D7: Pin
D70: Pin
D71: Pin
D72: Pin
D8: Pin
D9: Pin
DA0: Pin
DA1: Pin
DAC: Pin
DAC0: Pin
DAC1: Pin
DAC2: Pin
DAC_CS: Pin
DAC_OUT: Pin
DAT0: Pin
DAT1: Pin
DAT2: Pin
DAT3: Pin
DATA: Pin
DBG_RX: Pin
DBG_TX: Pin
DC: Pin
DCDC_MODE: Pin
DD23: Pin
DE1: Pin
DE2: Pin
DEBUG_RX: Pin
DEBUG_TX: Pin
DENSITY: Pin
DEV_VBUS_EN: Pin
DFU: Pin
DI0: Pin
DI1: Pin
DI10: Pin
DI2: Pin
DI3: Pin
DI4: Pin
DI5: Pin
DI6: Pin
DI7: Pin
DI8: Pin
DI9: Pin
DIN: Pin
DIR1: Pin
DIR2: Pin
DIR3: Pin
DIR4: Pin
DIRCAM: Pin
DIRECTION: Pin
DIRIO0: Pin
DIRIO1: Pin
DIRIO2: Pin
DIRIO3: Pin
DIRIO4: Pin
DISPLAY_EN: Pin
DISP_BL: Pin
DISP_BUSY: Pin
DISP_CS: Pin
DISP_DC: Pin
DISP_MISO: Pin
DISP_MOSI: Pin
DISP_RESET: Pin
DISP_RST: Pin
DISP_SCK: Pin
DISP_SCL: Pin
DISP_SDA: Pin
DO0: Pin
DO1: Pin
DO2: Pin
DO3: Pin
DOTSTAR_CI: Pin
DOTSTAR_CLOCK: Pin
DOTSTAR_DATA: Pin
DOTSTAR_DI: Pin
DOWN: Pin
DOWN_BUTTON: Pin
DTR: Pin
DV_CEC: Pin
DV_HPD: Pin
DV_SCL: Pin
DV_SDA: Pin
E1: Pin
E2: Pin
E3: Pin
E4: Pin
E5: Pin
E6: Pin
EBSY: Pin
ECHO: Pin
ECS: Pin
EDC: Pin
EINK_EN: Pin
EN: Pin
ENC0: Pin
ENC1: Pin
ENCA: Pin
ENCB: Pin
ENCODER_A: Pin
ENCODER_A_A: Pin
ENCODER_A_B: Pin
ENCODER_B: Pin
ENCODER_BUTTON: Pin
ENCODER_B_A: Pin
ENCODER_B_B: Pin
ENCODER_C_A: Pin
ENCODER_C_B: Pin
ENCODER_D_A: Pin
ENCODER_D_B: Pin
ENCODER_SWITCH: Pin
ENC_A: Pin
ENC_B: Pin
EN_GPS: Pin
EN_RF: Pin
EPD_BUSY: Pin
EPD_CS: Pin
EPD_DC: Pin
EPD_MISO: Pin
EPD_MOSI: Pin
EPD_RES: Pin
EPD_RESET: Pin
EPD_SCK: Pin
EPD_SS: Pin
ERST: Pin
ESP01_CH_PD: Pin
ESP01_EN: Pin
ESP01_GPIO0: Pin
ESP01_GPIO2: Pin
ESP01_RESET: Pin
ESP01_RX: Pin
ESP01_TX: Pin
ESP_BOOT: Pin
ESP_BOOT_MODE: Pin
ESP_BUSY: Pin
ESP_CHPD: Pin
ESP_CS: Pin
ESP_CTS: Pin
ESP_DRDY: Pin
ESP_GPIO0: Pin
ESP_GPIO13: Pin
ESP_HOST_WK: Pin
ESP_HS: Pin
ESP_MISO: Pin
ESP_MOSI: Pin
ESP_RESET: Pin
ESP_RTS: Pin
ESP_RX: Pin
ESP_SCK: Pin
ESP_TX: Pin
ESP_WIFI_EN: Pin
ES_BCLK: Pin
ES_DIN: Pin
ES_LRCK: Pin
ES_MCLK: Pin
ETHERNET_CLK: Pin
ETHERNET_CRS_DV: Pin
ETHERNET_INT: Pin
ETHERNET_MDC: Pin
ETHERNET_MDIO: Pin
ETHERNET_RST: Pin
ETHERNET_RXD0: Pin
ETHERNET_RXD1: Pin
ETHERNET_RXER: Pin
ETHERNET_TXD0: Pin
ETHERNET_TXD1: Pin
ETHERNET_TXEN: Pin
ETH_MDC: Pin
ETH_MDIO: Pin
ETH_RMII_CRS_DV: Pin
ETH_RMII_REF_CLK: Pin
ETH_RMII_RXD0: Pin
ETH_RMII_RXD1: Pin
ETH_RMII_RXER: Pin
ETH_RMII_TXD0: Pin
ETH_RMII_TXD1: Pin
ETH_RMII_TX_EN: Pin
EXP10: Pin
EXP11: Pin
EXP12: Pin
EXP13: Pin
EXP14: Pin
EXP15: Pin
EXP16: Pin
EXP17: Pin
EXP18: Pin
EXP19: Pin
EXP20: Pin
EXP21: Pin
EXP22: Pin
EXP23: Pin
EXP24: Pin
EXP25: Pin
EXP26: Pin
EXP27: Pin
EXP28: Pin
EXP7: Pin
EXP8: Pin
EXP9: Pin
EXT2: Pin
EXT3: Pin
EXT4: Pin
EXT5: Pin
EXT7: Pin
EXT8: Pin
EXTERNAL_BUTTON: Pin
EXTERNAL_NEOPIXEL: Pin
EXTERNAL_NEOPIXELS: Pin
EXTERNAL_POWER: Pin
EXTERNAL_SERVO: Pin
EXT_FLASH_CS: Pin
EXT_HDR3: Pin
EXT_HDR4: Pin
EXT_HDR5: Pin
EXT_RST: Pin
EXT_SCL: Pin
EXT_SDA: Pin
EXT_SW6: Pin
F2: Pin
F3: Pin
F4: Pin
F45: Pin
F46: Pin
F47: Pin
F48: Pin
F6: Pin
FAN: Pin
FG_ALERT: Pin
FG_INT: Pin
FLASHLIGHT: Pin
FLASH_CLK: Pin
FLASH_CMD: Pin
FLASH_CS: Pin
FLASH_D0: Pin
FLASH_D1: Pin
FLASH_D2: Pin
FLASH_D3: Pin
FLASH_MISO: Pin
FLASH_MOSI: Pin
FLASH_SCK: Pin
FLOPPY_DIRECTION: Pin
FREELINK_RX: Pin
FREELINK_TX: Pin
FSYNC: Pin
F_CSN: Pin
F_MISO: Pin
F_MOSI: Pin
F_RST: Pin
F_SCK: Pin
G0: Pin
G1: Pin
G10: Pin
G11: Pin
G12: Pin
G13: Pin
G14: Pin
G18: Pin
G19: Pin
G2: Pin
G20: Pin
G21: Pin
G3: Pin
G38: Pin
G39: Pin
G4: Pin
G40: Pin
G41: Pin
G42: Pin
G43: Pin
G44: Pin
G5: Pin
G6: Pin
G7: Pin
G8: Pin
G9: Pin
GAIN: Pin
GATE_IN: Pin
GATE_OUT: Pin
GP0: Pin
GP02: Pin
GP03: Pin
GP04: Pin
GP05: Pin
GP06: Pin
GP07: Pin
GP08: Pin
GP09: Pin
GP1: Pin
GP10: Pin
GP11: Pin
GP12: Pin
GP13: Pin
GP14: Pin
GP15: Pin
GP16: Pin
GP17: Pin
GP18: Pin
GP19: Pin
GP2: Pin
GP20: Pin
GP21: Pin
GP22: Pin
GP23: Pin
GP24: Pin
GP25: Pin
GP26: Pin
GP26_A0: Pin
GP27: Pin
GP27_A1: Pin
GP28: Pin
GP28_A2: Pin
GP29: Pin
GP29_A3: Pin
GP3: Pin
GP30: Pin
GP31: Pin
GP32: Pin
GP33: Pin
GP34: Pin
GP35: Pin
GP36: Pin
GP37: Pin
GP38: Pin
GP39: Pin
GP4: Pin
GP40: Pin
GP40_A0: Pin
GP41: Pin
GP41_A1: Pin
GP42: Pin
GP42_A2: Pin
GP43: Pin
GP44: Pin
GP45: Pin
GP46: Pin
GP47: Pin
GP5: Pin
GP6: Pin
GP7: Pin
GP8: Pin
GP9: Pin
GPIO0: Pin
GPIO1: Pin
GPIO10: Pin
GPIO11: Pin
GPIO12: Pin
GPIO13: Pin
GPIO14: Pin
GPIO15: Pin
GPIO16: Pin
GPIO17: Pin
GPIO18: Pin
GPIO19: Pin
GPIO2: Pin
GPIO20: Pin
GPIO21: Pin
GPIO22: Pin
GPIO23: Pin
GPIO24: Pin
GPIO25: Pin
GPIO26: Pin
GPIO27: Pin
GPIO28: Pin
GPIO29: Pin
GPIO3: Pin
GPIO32: Pin
GPIO33: Pin
GPIO34: Pin
GPIO35: Pin
GPIO36: Pin
GPIO37: Pin
GPIO38: Pin
GPIO39: Pin
GPIO4: Pin
GPIO40: Pin
GPIO41: Pin
GPIO42: Pin
GPIO43: Pin
GPIO44: Pin
GPIO45: Pin
GPIO46: Pin
GPIO47: Pin
GPIO48: Pin
GPIO5: Pin
GPIO6: Pin
GPIO7: Pin
GPIO8: Pin
GPIO9: Pin
GPKEY: Pin
GPS_POWER: Pin
GPS_RX: Pin
GPS_TX: Pin
GREEN: Pin
GREEN_LED: Pin
GROVE_A0: Pin
GROVE_A1: Pin
GROVE_D0: Pin
GROVE_D1: Pin
GROVE_RX: Pin
GROVE_SCL: Pin
GROVE_SDA: Pin
GROVE_TX: Pin
GYROSCOPE_INT: Pin
GYROSCOPE_SCL: Pin
GYROSCOPE_SDA: Pin
HAPTIC_ENABLE: Pin
HAPTIC_INT: Pin
HEADPHONE_LEFT: Pin
HEADPHONE_RIGHT: Pin
HOLD_2: Pin
HOLD_SYS_EN: Pin
HONK_OUT: Pin
HOST_ENABLE: Pin
HOST_ID: Pin
HOST_VBUS: Pin
HOST_VOL: Pin
HREF: Pin
HRM_INT: Pin
HRM_POWER: Pin
HRM_SCL: Pin
HRM_SDA: Pin
HSPI_CLK: Pin
HSPI_CS: Pin
HSPI_MISO: Pin
HSPI_MOSI: Pin
HSYNC: Pin
HVCAM: Pin
HVIO0: Pin
HVIO1: Pin
HVIO2: Pin
HVIO3: Pin
HVIO4: Pin
HWD: Pin
I2C0_SCL: Pin
I2C0_SDA: Pin
I2C1_SCL: Pin
I2C1_SDA: Pin
I2C2_SCL: Pin
I2C2_SDA: Pin
I2C3_SCL: Pin
I2C3_SDA: Pin
I2C4_SCL: Pin
I2C4_SDA: Pin
I2C_INT: Pin
I2C_INTERRUPT: Pin
I2C_POWER: Pin
I2C_PWR: Pin
I2C_SCL: Pin
I2C_SCL1: Pin
I2C_SDA: Pin
I2C_SDA1: Pin
I2S: Pin
I2S_ADC_SDOUT: Pin
I2S_AMP_BCLK: Pin
I2S_AMP_DATA: Pin
I2S_AMP_LRCLK: Pin
I2S_AMP_SD: Pin
I2S_BCK: Pin
I2S_BCLK: Pin
I2S_BIT_CLOCK: Pin
I2S_CODEC_DSDIN: Pin
I2S_DATA: Pin
I2S_DEMP: Pin
I2S_DIN: Pin
I2S_DOUT: Pin
I2S_FS_0: Pin
I2S_IN: Pin
I2S_LCK: Pin
I2S_LRC: Pin
I2S_LRCK: Pin
I2S_LRCLK: Pin
I2S_MCK_0: Pin
I2S_MCLK: Pin
I2S_MIC_BCLK: Pin
I2S_MIC_DATA: Pin
I2S_MIC_SEL: Pin
I2S_MIC_WS: Pin
I2S_OUT: Pin
I2S_PDM_MIC_CLOCK: Pin
I2S_PDM_MIC_DATA: Pin
I2S_SCK: Pin
I2S_SCK_0: Pin
I2S_SCLK: Pin
I2S_SD: Pin
I2S_SDI: Pin
I2S_SDIN: Pin
I2S_SDO: Pin
I2S_SDOUT: Pin
I2S_WCLK: Pin
I2S_WORD_SELECT: Pin
I2S_WS: Pin
I2S_WSEL: Pin
I2S_XSMT: Pin
I34: Pin
I35: Pin
I36: Pin
I39: Pin
ICE_1V2_EN: Pin
ICE_3V3_EN: Pin
ICE_CDONE: Pin
ICE_CRESET: Pin
ICE_IOB_29B: Pin
ICE_IOB_31B: Pin
ICE_SPI_CLK: Pin
ICE_SPI_CS: Pin
ICE_SPI_SDI: Pin
ICE_SPI_SDO: Pin
ID_SC: Pin
ID_SCL: Pin
ID_SD: Pin
ID_SDA: Pin
IMUSC: Pin
IMUSD: Pin
IMU_INT1: Pin
IMU_INT2: Pin
IMU_IRQ: Pin
IMU_PWR: Pin
IMU_SCL: Pin
IMU_SDA: Pin
IN06: Pin
IN07: Pin
INDEX: Pin
INKY_BUSY: Pin
INKY_CS: Pin
INKY_DC: Pin
INKY_RES: Pin
INKY_RST: Pin
INT: Pin
INT1: Pin
INTERNAL_INTERRUPT: Pin
INTERNAL_SCL: Pin
INTERNAL_SDA: Pin
INTERRUPT: Pin
INT_ACCEL: Pin
INT_APDS: Pin
INT_BMI_1: Pin
INT_BMI_2: Pin
INT_COL: Pin
INT_IMU: Pin
INT_IMU_OBC: Pin
INT_LIGHT_TOF: Pin
INT_LPS: Pin
INT_ROW: Pin
INVERTED_LED: Pin
IO0: Pin
IO01: Pin
IO02: Pin
IO03: Pin
IO04: Pin
IO05: Pin
IO1: Pin
IO10: Pin
IO11: Pin
IO12: Pin
IO13: Pin
IO14: Pin
IO15: Pin
IO16: Pin
IO17: Pin
IO18: Pin
IO19: Pin
IO2: Pin
IO20: Pin
IO21: Pin
IO22: Pin
IO23: Pin
IO24: Pin
IO25: Pin
IO26: Pin
IO27: Pin
IO28: Pin
IO29: Pin
IO3: Pin
IO30: Pin
IO31: Pin
IO32: Pin
IO33: Pin
IO34: Pin
IO35: Pin
IO36: Pin
IO37: Pin
IO38: Pin
IO39: Pin
IO4: Pin
IO40: Pin
IO41: Pin
IO42: Pin
IO43: Pin
IO44: Pin
IO45: Pin
IO46: Pin
IO47: Pin
IO48: Pin
IO49: Pin
IO5: Pin
IO6: Pin
IO7: Pin
IO8: Pin
IO9: Pin
IOX: Pin
IO_POWER: Pin
IR: Pin
IRQ: Pin
IRRX: Pin
IRTX: Pin
IR_LED: Pin
IR_PROXIMITY: Pin
IR_RX: Pin
IR_TX: Pin
IS2_DATA: Pin
IS2_MASTER_CLOCK: Pin
IT8951_BUSY: Pin
IT8951_CS: Pin
IT8951_POWER: Pin
IT8951_RESET: Pin
J29_RX: Pin
J29_TX: Pin
J30_RX: Pin
J30_TX: Pin
JACK_PWREN: Pin
JACK_SND: Pin
JACK_TX: Pin
JOYSTICK_X: Pin
JOYSTICK_Y: Pin
K1: Pin
K2: Pin
K3: Pin
KB_A_0: Pin
KB_A_1: Pin
KB_A_2: Pin
KB_COL_0: Pin
KB_COL_1: Pin
KB_COL_2: Pin
KB_COL_3: Pin
KB_COL_4: Pin
KB_COL_5: Pin
KB_COL_6: Pin
KEY1: Pin
KEY10: Pin
KEY11: Pin
KEY12: Pin
KEY2: Pin
KEY3: Pin
KEY4: Pin
KEY5: Pin
KEY6: Pin
KEY7: Pin
KEY8: Pin
KEY9: Pin
KEYBOARD_INT: Pin
KNOB_BUTTON: Pin
L: Pin
L1PROG: Pin
LAT: Pin
LCD_BACKLIGHT: Pin
LCD_BCKL: Pin
LCD_BL: Pin
LCD_BL_CTR: Pin
LCD_BL_CTRL: Pin
LCD_BRIGHTNESS: Pin
LCD_CLK: Pin
LCD_CS: Pin
LCD_CTRL: Pin
LCD_D0: Pin
LCD_D1: Pin
LCD_D10: Pin
LCD_D11: Pin
LCD_D12: Pin
LCD_D13: Pin
LCD_D14: Pin
LCD_D15: Pin
LCD_D2: Pin
LCD_D3: Pin
LCD_D4: Pin
LCD_D5: Pin
LCD_D6: Pin
LCD_D7: Pin
LCD_D8: Pin
LCD_D9: Pin
LCD_DATA0: Pin
LCD_DATA1: Pin
LCD_DATA2: Pin
LCD_DATA3: Pin
LCD_DATA4: Pin
LCD_DATA5: Pin
LCD_DATA6: Pin
LCD_DATA7: Pin
LCD_DC: Pin
LCD_DIN: Pin
LCD_D_C: Pin
LCD_EN: Pin
LCD_ENABLE: Pin
LCD_HSYNC: Pin
LCD_INT: Pin
LCD_LED: Pin
LCD_MISO: Pin
LCD_MOSI: Pin
LCD_POWER_ON: Pin
LCD_RD: Pin
LCD_RESET: Pin
LCD_RS: Pin
LCD_RST: Pin
LCD_SCK: Pin
LCD_SCL: Pin
LCD_SCLK: Pin
LCD_SDA: Pin
LCD_TOUCH_INT: Pin
LCD_TP_BUSY: Pin
LCD_TP_CS: Pin
LCD_TP_IRQ: Pin
LCD_TP_MISO: Pin
LCD_TP_MOSI: Pin
LCD_TP_SCK: Pin
LCD_VSYNC: Pin
LCD_WR: Pin
LD3: Pin
LD4: Pin
LD5: Pin
LD6: Pin
LDO2: Pin
LDO_CONTROL: Pin
LDR: Pin
LED: Pin
LED0: Pin
LED1: Pin
LED10: Pin
LED11: Pin
LED12: Pin
LED13: Pin
LED1A: Pin
LED1B: Pin
LED2: Pin
LED20: Pin
LED21: Pin
LED2A: Pin
LED2B: Pin
LED2_B: Pin
LED2_G: Pin
LED2_R: Pin
LED3: Pin
LED3A: Pin
LED3B: Pin
LED4: Pin
LED4A: Pin
LED4B: Pin
LED5: Pin
LED6: Pin
LED7: Pin
LED8: Pin
LED9: Pin
LEDB: Pin
LEDG: Pin
LEDR: Pin
LED_1: Pin
LED_2: Pin
LED_3: Pin
LED_4: Pin
LED_5: Pin
LED_6: Pin
LED_A: Pin
LED_ACT: Pin
LED_AUX: Pin
LED_B: Pin
LED_BAR: Pin
LED_BLUE: Pin
LED_BOTTOM_AMBER: Pin
LED_BOTTOM_RED: Pin
LED_BUILTIN: Pin
LED_C: Pin
LED_CLK: Pin
LED_CONN: Pin
LED_D: Pin
LED_DAT: Pin
LED_DATA: Pin
LED_E: Pin
LED_G: Pin
LED_GREEN: Pin
LED_INVERTED: Pin
LED_IO2: Pin
LED_IR: Pin
LED_ORANGE: Pin
LED_QSPI: Pin
LED_R: Pin
LED_RED: Pin
LED_RX: Pin
LED_STATUS: Pin
LED_TOP_AMBER: Pin
LED_TOP_RED: Pin
LED_TX: Pin
LED_WHITE: Pin
LED_Y: Pin
LED_YELLOW: Pin
LED_nACT: Pin
LEFT: Pin
LEFT_BUTTON: Pin
LEFT_TFT_CS: Pin
LEFT_TFT_DC: Pin
LEFT_TFT_MOSI: Pin
LEFT_TFT_SCK: Pin
LIGHT: Pin
LIGHT_ENABLE: Pin
LIGHT_SENSOR: Pin
LIMIT_EN: Pin
LOCK_BUTTON: Pin
LOGO: Pin
LOG_SWITCH: Pin
LORA_BUSY: Pin
LORA_CS: Pin
LORA_DIO0: Pin
LORA_DIO1: Pin
LORA_DIO2: Pin
LORA_DIO3: Pin
LORA_DIO4: Pin
LORA_MISO: Pin
LORA_MOSI: Pin
LORA_NSS: Pin
LORA_RESETN: Pin
LORA_RST: Pin
LORA_SCK: Pin
LORA_SCLK: Pin
LORA_SSN: Pin
LP_I2C_SCL: Pin
LP_I2C_SDA: Pin
LP_UART_RXD: Pin
LP_UART_TXD: Pin
LUM1: Pin
LUM2: Pin
LVCAM: Pin
LVIO0: Pin
LVIO1: Pin
LVIO2: Pin
LVIO3: Pin
LVIO4: Pin
M1: Pin
M1A: Pin
M1B: Pin
M2: Pin
M2A: Pin
M2B: Pin
M3: Pin
M3A: Pin
M3B: Pin
M4: Pin
M4A: Pin
M4B: Pin
M5: Pin
M6: Pin
M7: Pin
M8: Pin
MATRIX_DATA: Pin
MATRIX_POWER: Pin
MAXTEMP_SCL: Pin
MAXTEMP_SDA: Pin
MBCS: Pin
MBINT: Pin
MBPWM: Pin
MBRST: Pin
MC: Pin
MD: Pin
MEAS_EN: Pin
MEMLCD_CS: Pin
MEMLCD_DISP: Pin
MEMLCD_EXTCOMIN: Pin
MEMLCD_MOSI: Pin
MEMLCD_SCK: Pin
MENU: Pin
MI: Pin
MIC: Pin
MICC: Pin
MICD: Pin
MICIN: Pin
MICOUT: Pin
MICROPHONE: Pin
MICROPHONE_CLOCK: Pin
MICROPHONE_DATA: Pin
MICROPHONE_DIN: Pin
MICROPHONE_ENABLE: Pin
MICROPHONE_MCK: Pin
MICROPHONE_SCK: Pin
MICROPHONE_WS: Pin
MIC_ADC_M: Pin
MIC_CLK: Pin
MIC_CLOCK: Pin
MIC_DATA: Pin
MIC_PWR: Pin
MIC_SCK: Pin
MIC_SCLK: Pin
MIC_SDO: Pin
MIC_SHUTDOWN: Pin
MIC_WS: Pin
MIDDLE_BUTTON: Pin
MIDI_RX: Pin
MISO: Pin
MISO0: Pin
MISO1: Pin
MISO2: Pin
MISO_1: Pin
MISO_2: Pin
MM_33V_EN: Pin
MM_A0: Pin
MM_A1: Pin
MM_BATT_VIN3: Pin
MM_CAN_RX: Pin
MM_CAN_TX: Pin
MM_CIPO: Pin
MM_CIPO1: Pin
MM_COPI: Pin
MM_COPI1: Pin
MM_CS: Pin
MM_CS1: Pin
MM_D0: Pin
MM_D1: Pin
MM_DAT0: Pin
MM_DAT1: Pin
MM_DAT2: Pin
MM_DAT3: Pin
MM_G0: Pin
MM_G1: Pin
MM_G10: Pin
MM_G11: Pin
MM_G2: Pin
MM_G3: Pin
MM_G4: Pin
MM_G5: Pin
MM_G6: Pin
MM_G7: Pin
MM_G8: Pin
MM_G9: Pin
MM_I2C_INT: Pin
MM_I2S_CLK: Pin
MM_I2S_FS: Pin
MM_I2S_SDI: Pin
MM_I2S_SDO: Pin
MM_MCLK: Pin
MM_PWM0: Pin
MM_PWM1: Pin
MM_RX: Pin
MM_RX2: Pin
MM_SCK: Pin
MM_SCK1: Pin
MM_SCL: Pin
MM_SCL1: Pin
MM_SDA: Pin
MM_SDA1: Pin
MM_TX: Pin
MM_TX2: Pin
MO: Pin
MODE: Pin
MOSI: Pin
MOSI0: Pin
MOSI1: Pin
MOSI2: Pin
MOSI_1: Pin
MOSI_2: Pin
MOTOR: Pin
MOTOR_A_N: Pin
MOTOR_A_P: Pin
MOTOR_B_N: Pin
MOTOR_B_P: Pin
MOTOR_C_N: Pin
MOTOR_C_P: Pin
MOTOR_D_N: Pin
MOTOR_D_P: Pin
MOTOR_OUT_1: Pin
MOTOR_OUT_2: Pin
MPU_SCL: Pin
MPU_SDA: Pin
MTCK: Pin
MTDI: Pin
MTDO: Pin
MTMS: Pin
MTX_ADDRA: Pin
MTX_ADDRB: Pin
MTX_ADDRC: Pin
MTX_ADDRD: Pin
MTX_ADDRE: Pin
MTX_B1: Pin
MTX_B2: Pin
MTX_CLK: Pin
MTX_G1: Pin
MTX_G2: Pin
MTX_LAT: Pin
MTX_OE: Pin
MTX_R1: Pin
MTX_R2: Pin
MUTE: Pin
MUTE_STATUS: Pin
NEOPIX: Pin
NEOPIXEL: Pin
NEOPIXEL0: Pin
NEOPIXEL1: Pin
NEOPIXEL2: Pin
NEOPIXEL3: Pin
NEOPIXEL4: Pin
NEOPIXEL5: Pin
NEOPIXEL6: Pin
NEOPIXEL7: Pin
NEOPIXEL_I2C_POWER: Pin
NEOPIXEL_MATRIX: Pin
NEOPIXEL_MATRIX_POWER: Pin
NEOPIXEL_POWER: Pin
NEOPIXEL_POWER_INVERTED: Pin
NEOPIX_POWER: Pin
NFC1: Pin
NFC2: Pin
NFC_1: Pin
NFC_2: Pin
NOSE: Pin
NSS: Pin
O: Pin
OE: Pin
OLED_CS: Pin
OLED_DC: Pin
OLED_RESET: Pin
OLED_RST: Pin
OLED_SCL: Pin
OLED_SDA: Pin
OTG_FS_OVER_CURRENT: Pin
OTG_FS_POWER: Pin
OTG_HS_OVER_CURRENT: Pin
OVER_CURRENT: Pin
OVTEMP: Pin
P0: Pin
P0_00: Pin
P0_01: Pin
P0_02: Pin
P0_03: Pin
P0_04: Pin
P0_05: Pin
P0_06: Pin
P0_07: Pin
P0_08: Pin
P0_09: Pin
P0_10: Pin
P0_11: Pin
P0_12: Pin
P0_13: Pin
P0_14: Pin
P0_15: Pin
P0_16: Pin
P0_17: Pin
P0_18: Pin
P0_19: Pin
P0_20: Pin
P0_21: Pin
P0_22: Pin
P0_23: Pin
P0_24: Pin
P0_25: Pin
P0_26: Pin
P0_27: Pin
P0_28: Pin
P0_29: Pin
P0_30: Pin
P0_31: Pin
P0_A0: Pin
P1: Pin
P10: Pin
P11: Pin
P12: Pin
P13: Pin
P14: Pin
P15: Pin
P16: Pin
P17: Pin
P18: Pin
P19: Pin
P1_0: Pin
P1_00: Pin
P1_01: Pin
P1_02: Pin
P1_03: Pin
P1_04: Pin
P1_05: Pin
P1_06: Pin
P1_07: Pin
P1_08: Pin
P1_09: Pin
P1_1: Pin
P1_10: Pin
P1_11: Pin
P1_12: Pin
P1_13: Pin
P1_14: Pin
P1_15: Pin
P1_2: Pin
P1_3: Pin
P1_4: Pin
P1_5: Pin
P1_6: Pin
P1_7: Pin
P1_8: Pin
P1_9: Pin
P1_A1: Pin
P2: Pin
P20: Pin
P21: Pin
P22: Pin
P23: Pin
P24: Pin
P24V: Pin
P25: Pin
P26: Pin
P27: Pin
P28: Pin
P29: Pin
P2_A2: Pin
P3: Pin
P30: Pin
P31: Pin
P32: Pin
P33: Pin
P34: Pin
P35: Pin
P36: Pin
P37: Pin
P38: Pin
P39: Pin
P3V3_EN: Pin
P3_A3: Pin
P4: Pin
P40: Pin
P41: Pin
P42: Pin
P43: Pin
P44: Pin
P45: Pin
P46: Pin
P47: Pin
P5: Pin
P6: Pin
P7: Pin
P8: Pin
P9: Pin
PA0: Pin
PA00: Pin
PA01: Pin
PA02: Pin
PA03: Pin
PA04: Pin
PA05: Pin
PA06: Pin
PA07: Pin
PA08: Pin
PA09: Pin
PA1: Pin
PA10: Pin
PA11: Pin
PA12: Pin
PA13: Pin
PA14: Pin
PA15: Pin
PA16: Pin
PA17: Pin
PA18: Pin
PA19: Pin
PA2: Pin
PA20: Pin
PA22: Pin
PA23: Pin
PA27: Pin
PA3: Pin
PA4: Pin
PA5: Pin
PA6: Pin
PA7: Pin
PA8: Pin
PA9: Pin
PA_CTRL: Pin
PB0: Pin
PB00: Pin
PB01: Pin
PB02: Pin
PB03: Pin
PB04: Pin
PB05: Pin
PB06: Pin
PB07: Pin
PB08: Pin
PB09: Pin
PB1: Pin
PB10: Pin
PB11: Pin
PB12: Pin
PB13: Pin
PB14: Pin
PB15: Pin
PB16: Pin
PB17: Pin
PB2: Pin
PB22: Pin
PB23: Pin
PB26: Pin
PB27: Pin
PB28: Pin
PB29: Pin
PB3: Pin
PB4: Pin
PB5: Pin
PB6: Pin
PB7: Pin
PB8: Pin
PB9: Pin
PC0: Pin
PC00: Pin
PC01: Pin
PC02: Pin
PC03: Pin
PC04: Pin
PC05: Pin
PC06: Pin
PC07: Pin
PC08: Pin
PC09: Pin
PC1: Pin
PC10: Pin
PC11: Pin
PC12: Pin
PC13: Pin
PC14: Pin
PC15: Pin
PC2: Pin
PC22: Pin
PC23: Pin
PC3: Pin
PC30: Pin
PC31: Pin
PC4: Pin
PC5: Pin
PC6: Pin
PC7: Pin
PC8: Pin
PC9: Pin
PCBREV: Pin
PCC_CLK: Pin
PCC_D0: Pin
PCC_D1: Pin
PCC_D10: Pin
PCC_D11: Pin
PCC_D12: Pin
PCC_D13: Pin
PCC_D2: Pin
PCC_D3: Pin
PCC_D4: Pin
PCC_D5: Pin
PCC_D6: Pin
PCC_D7: Pin
PCC_D8: Pin
PCC_D9: Pin
PCC_DEN1: Pin
PCC_DEN2: Pin
PCC_XCLK: Pin
PCF8563_INT: Pin
PCLK: Pin
PCM_CLK: Pin
PCM_IN: Pin
PCM_OUT: Pin
PCM_SYNC: Pin
PD00: Pin
PD01: Pin
PD02: Pin
PD03: Pin
PD04: Pin
PD05: Pin
PD06: Pin
PD07: Pin
PD08: Pin
PD09: Pin
PD10: Pin
PD11: Pin
PD12: Pin
PD13: Pin
PD14: Pin
PD15: Pin
PD2: Pin
PD5: Pin
PDEC_A: Pin
PDEC_B: Pin
PDEC_C: Pin
PDMCLK: Pin
PDMDIN: Pin
PDM_CLK: Pin
PDM_DATA: Pin
PDM_MIC_CLK: Pin
PDM_MIC_DATA: Pin
PD_PIN: Pin
PD_POWER: Pin
PE00: Pin
PE01: Pin
PE02: Pin
PE03: Pin
PE04: Pin
PE05: Pin
PE06: Pin
PE07: Pin
PE08: Pin
PE09: Pin
PE10: Pin
PE11: Pin
PE12: Pin
PE13: Pin
PE14: Pin
PE15: Pin
PERIPHERAL_SCL: Pin
PERIPHERAL_SDA: Pin
PE_POWER: Pin
PF02: Pin
PF03: Pin
PF10: Pin
PF11: Pin
PF13: Pin
PG02: Pin
PG09: Pin
PG10: Pin
PG11: Pin
PG12: Pin
PG13: Pin
PG14: Pin
PH0: Pin
PH1: Pin
PICO_LED: Pin
PIEZO: Pin
PIR: Pin
PIR_SENSE: Pin
PIR_SENSOR: Pin
PITCH_IN: Pin
PI_GP24: Pin
PI_GP25: Pin
PI_RX: Pin
PI_SCL: Pin
PI_SDA: Pin
PI_TX: Pin
PMU_INT: Pin
PMU_N_VBUSEN: Pin
PORTA1: Pin
PORTA2: Pin
PORTA_SCL: Pin
PORTA_SDA: Pin
PORTB_IN: Pin
PORTB_OUT: Pin
PORTC_RX: Pin
PORTC_TX: Pin
POTENTIOMETER: Pin
POWER1: Pin
POWER2: Pin
POWER3: Pin
POWER4: Pin
POWER_DISABLE: Pin
POWER_ENABLE: Pin
POWER_EXT: Pin
POWER_HOLD: Pin
POWER_I2C_SCL: Pin
POWER_I2C_SDA: Pin
POWER_INTERRUPT: Pin
POWER_LED: Pin
POWER_MAIN: Pin
POWER_OFF: Pin
POWER_ON: Pin
POWER_SWITCH: Pin
PRESSURE_SCL: Pin
PRESSURE_SDA: Pin
PROXIMITY_LIGHT_INTERRUPT: Pin
PSRAM_CS: Pin
PUSH_BUTTON: Pin
PWDN: Pin
PWDWN: Pin
PWM0: Pin
PWM1: Pin
PWM2: Pin
PWR: Pin
PWRMON_ALERT: Pin
PWRMON_SCL: Pin
PWRMON_SDA: Pin
PWR_SHUTDOWN: Pin
QCLK: Pin
QCS: Pin
QEN: Pin
QIO0: Pin
QIO1: Pin
QIO2: Pin
QIO3: Pin
QSPI_CLK: Pin
QSPI_CSN: Pin
QSPI_IO0: Pin
QSPI_IO1: Pin
QSPI_IO2: Pin
QSPI_IO3: Pin
QT: Pin
R0: Pin
R1: Pin
R10: Pin
R11: Pin
R12: Pin
R13: Pin
R14: Pin
R15: Pin
R16: Pin
R2: Pin
R3: Pin
R4: Pin
R5: Pin
R6: Pin
R7: Pin
R8: Pin
R9: Pin
RADIO_BUSY: Pin
RADIO_CS: Pin
RADIO_DIO1: Pin
RADIO_INT: Pin
RADIO_MISO: Pin
RADIO_MOSI: Pin
RADIO_RESET: Pin
RADIO_RST: Pin
RADIO_SCK: Pin
RADIO_SS: Pin
RCC1: Pin
RCC2: Pin
RCC3: Pin
RCC4: Pin
RDDATA: Pin
READY: Pin
READ_BATT_ENABLE: Pin
REC: Pin
RED: Pin
REDLED: Pin
RED_LED: Pin
REF_1V2: Pin
RELAY_A: Pin
REMOTEIN: Pin
REMOTEOUT: Pin
RES: Pin
RESET: Pin
RF1_CS: Pin
RF1_IO0: Pin
RF1_IO4: Pin
RF1_RST: Pin
RF2_BSY: Pin
RF2_CS: Pin
RF2_IO0: Pin
RF2_IO1: Pin
RF2_IO4: Pin
RF2_RST: Pin
RFID_IRQ: Pin
RFM69HCW_CS: Pin
RFM69HCW_DIO0: Pin
RFM69HCW_DIO1: Pin
RFM69HCW_DIO2: Pin
RFM69HCW_RST: Pin
RFM69HCW_SCK: Pin
RFM69HCW_SDI: Pin
RFM69HCW_SDO: Pin
RFM69_CS: Pin
RFM69_D0: Pin
RFM69_RST: Pin
RFM95W_CS: Pin
RFM95W_DIO0: Pin
RFM95W_DIO1: Pin
RFM95W_DIO2: Pin
RFM95W_RST: Pin
RFM95W_SCK: Pin
RFM95W_SDI: Pin
RFM95W_SDO: Pin
RFM9X_CS: Pin
RFM9X_D0: Pin
RFM9X_D1: Pin
RFM9X_D2: Pin
RFM9X_D5: Pin
RFM9X_RST: Pin
RFM_CS: Pin
RFM_IO0: Pin
RFM_IO1: Pin
RFM_IO2: Pin
RFM_IO3: Pin
RFM_IO4: Pin
RFM_IO5: Pin
RFM_RST: Pin
RGB: Pin
RGBLED: Pin
RGB_BUILTIN: Pin
RGB_LED: Pin
RGB_LED_B: Pin
RGB_LED_BLUE: Pin
RGB_LED_G: Pin
RGB_LED_GREEN: Pin
RGB_LED_R: Pin
RGB_LED_RED: Pin
RGB_POWER: Pin
RIGHT: Pin
RIGHT_BUTTON: Pin
RIGHT_TFT_CS: Pin
RIGHT_TFT_DC: Pin
RIGHT_TFT_LITE: Pin
RIGHT_TFT_MOSI: Pin
RIGHT_TFT_RST: Pin
RIGHT_TFT_SCK: Pin
RING_1: Pin
RING_1_SWITCH: Pin
RING_2: Pin
ROTA: Pin
ROTB: Pin
ROW0: Pin
ROW1: Pin
ROW2: Pin
ROW3: Pin
ROW4: Pin
ROW5: Pin
ROW6: Pin
ROW7: Pin
ROW8: Pin
ROW9: Pin
ROW_A: Pin
ROW_B: Pin
ROW_C: Pin
ROW_D: Pin
ROW_E: Pin
RS232_EN: Pin
RS232_RX: Pin
RS232_TX: Pin
RS485_RE: Pin
RS485_RX: Pin
RS485_TE: Pin
RS485_TX: Pin
RST: Pin
RTC_ALARM: Pin
RTC_INT: Pin
RTC_RST: Pin
RTC_SCL: Pin
RTC_SDA: Pin
RTL_CLK: Pin
RTL_CS: Pin
RTL_DIR: Pin
RTL_MISO: Pin
RTL_MOSI: Pin
RTL_PWR: Pin
RTL_READY: Pin
RTL_RXD: Pin
RTL_TXD: Pin
RTS: Pin
RTS0: Pin
RTS1: Pin
RTS2: Pin
RTS3: Pin
RV1: Pin
RV2: Pin
RV3: Pin
RX: Pin
RX0: Pin
RX1: Pin
RX2: Pin
RX3: Pin
RX4: Pin
RX5: Pin
RX6: Pin
RX7: Pin
RX8: Pin
RXD: Pin
RX_D0_SWITCH_LEFT: Pin
RX_D1_SWITCH_RIGHT: Pin
RX_LED: Pin
RX_LED_INVERTED: Pin
R_PULLUP: Pin
S1: Pin
S2: Pin
S3: Pin
S32K: Pin
S4: Pin
S5: Pin
S6: Pin
S7: Pin
SARA_BTN: Pin
SARA_CTS: Pin
SARA_PWR: Pin
SARA_RST: Pin
SARA_RTS: Pin
SARA_RX: Pin
SARA_TX: Pin
SAT_POWER: Pin
SAT_PWR_ENABLE: Pin
SAT_RESET: Pin
SC: Pin
SCK: Pin
SCK0: Pin
SCK1: Pin
SCK2: Pin
SCK_1: Pin
SCK_2: Pin
SCL: Pin
SCL0: Pin
SCL1: Pin
SCL2: Pin
SCL3: Pin
SCL4: Pin
SCL6: Pin
SCLK: Pin
SCLK_1: Pin
SCL_1: Pin
SCL_ALT: Pin
SD: Pin
SD0: Pin
SD1: Pin
SD13: Pin
SD2: Pin
SD3: Pin
SD4: Pin
SD5: Pin
SDA: Pin
SDA0: Pin
SDA1: Pin
SDA2: Pin
SDA3: Pin
SDA4: Pin
SDA6: Pin
SDA_1: Pin
SDA_ALT: Pin
SDCARD_CS: Pin
SDCK: Pin
SDCS: Pin
SDI: Pin
SDIO_CLK: Pin
SDIO_CLOCK: Pin
SDIO_CMD: Pin
SDIO_COMMAND: Pin
SDIO_D0: Pin
SDIO_D1: Pin
SDIO_D2: Pin
SDIO_D3: Pin
SDIO_DATA0: Pin
SDIO_DATA1: Pin
SDIO_DATA2: Pin
SDIO_DATA3: Pin
SDIO_SLAVE: Pin
SDMI: Pin
SDMO: Pin
SDO: Pin
SDRAM_A0: Pin
SDRAM_A1: Pin
SDRAM_A10: Pin
SDRAM_A11: Pin
SDRAM_A2: Pin
SDRAM_A3: Pin
SDRAM_A4: Pin
SDRAM_A5: Pin
SDRAM_A6: Pin
SDRAM_A7: Pin
SDRAM_A8: Pin
SDRAM_A9: Pin
SDRAM_BA0: Pin
SDRAM_BA1: Pin
SDRAM_D0: Pin
SDRAM_D1: Pin
SDRAM_D10: Pin
SDRAM_D11: Pin
SDRAM_D12: Pin
SDRAM_D13: Pin
SDRAM_D14: Pin
SDRAM_D15: Pin
SDRAM_D2: Pin
SDRAM_D3: Pin
SDRAM_D4: Pin
SDRAM_D5: Pin
SDRAM_D6: Pin
SDRAM_D7: Pin
SDRAM_D8: Pin
SDRAM_D9: Pin
SDRAM_NBL0: Pin
SDRAM_NBL1: Pin
SDRAM_SDCKE0: Pin
SDRAM_SDCLK: Pin
SDRAM_SDNCAS: Pin
SDRAM_SDNE0: Pin
SDRAM_SDNRAS: Pin
SDRAM_SDNWE: Pin
SD_CARD_DETECT: Pin
SD_CD: Pin
SD_CK: Pin
SD_CLK: Pin
SD_CMD: Pin
SD_CS: Pin
SD_D0: Pin
SD_D1: Pin
SD_D2: Pin
SD_D3: Pin
SD_DAT0: Pin
SD_DAT1: Pin
SD_DAT2: Pin
SD_DAT3: Pin
SD_DET: Pin
SD_DETECT: Pin
SD_MISO: Pin
SD_MOSI: Pin
SD_POWER: Pin
SD_PWREN: Pin
SD_SCK: Pin
SD_SCLK: Pin
SD_SDI: Pin
SD_SDO: Pin
SD_SW: Pin
SELECT: Pin
SENSE: Pin
SENSOR: Pin
SENSORS_SCL: Pin
SENSORS_SDA: Pin
SENSOR_IN: Pin
SENSOR_POWER_ENABLE: Pin
SENSOR_VN: Pin
SENSOR_VP: Pin
SERIAL_MODE1: Pin
SERIAL_MODE2: Pin
SERVO1: Pin
SERVO2: Pin
SERVO3: Pin
SERVO4: Pin
SERVO5: Pin
SERVO6: Pin
SERVO7: Pin
SERVO8: Pin
SERVO_1: Pin
SERVO_10: Pin
SERVO_11: Pin
SERVO_12: Pin
SERVO_13: Pin
SERVO_14: Pin
SERVO_15: Pin
SERVO_16: Pin
SERVO_17: Pin
SERVO_18: Pin
SERVO_2: Pin
SERVO_3: Pin
SERVO_4: Pin
SERVO_5: Pin
SERVO_6: Pin
SERVO_7: Pin
SERVO_8: Pin
SERVO_9: Pin
SHARED_ADC: Pin
SHDWN: Pin
SIDE: Pin
SLEEVE: Pin
SLIDE_SWITCH: Pin
SMC_RST: Pin
SMPS_MODE: Pin
SND_CS: Pin
SND_DREQ: Pin
SND_RESET: Pin
SND_XDCS: Pin
SPCE_BL: Pin
SPCE_CS: Pin
SPCE_MISO: Pin
SPCE_MOSI: Pin
SPCE_SCK: Pin
SPDIF_IN: Pin
SPDIF_OUT: Pin
SPEAKER: Pin
SPEAKER_DOUT: Pin
SPEAKER_EN: Pin
SPEAKER_ENABLE: Pin
SPEAKER_IN: Pin
SPEAKER_IN_M: Pin
SPEAKER_IN_P: Pin
SPEAKER_N: Pin
SPEAKER_P: Pin
SPEAKER_SCK: Pin
SPEAKER_WS: Pin
SPI0_CE0: Pin
SPI0_CE1: Pin
SPI0_MISO: Pin
SPI0_MOSI: Pin
SPI0_SCLK: Pin
SPI1_MISO: Pin
SPI1_MOSI: Pin
SPI1_SCK: Pin
SPI1_SS: Pin
SPI2_MISO: Pin
SPI2_MOSI: Pin
SPI2_NSS: Pin
SPI2_SCK: Pin
SPI3_MISO: Pin
SPI3_MOSI: Pin
SPI3_NSS: Pin
SPI3_SCK: Pin
SPICE_BL: Pin
SPICE_CS: Pin
SPICE_RX: Pin
SPICE_SCK: Pin
SPICE_TX: Pin
SPI_BUSY: Pin
SPI_B_MOSI: Pin
SPI_B_NSS: Pin
SPI_B_SCK: Pin
SPI_CIPO: Pin
SPI_CIPO1: Pin
SPI_COPI: Pin
SPI_COPI1: Pin
SPI_CS: Pin
SPI_CS1: Pin
SPI_CSN: Pin
SPI_DC: Pin
SPI_MISO: Pin
SPI_MISO1: Pin
SPI_MOSI: Pin
SPI_MOSI1: Pin
SPI_RESET: Pin
SPI_SCK: Pin
SPI_SCK1: Pin
SPI_SS: Pin
SPK_I2S_LRC: Pin
SPK_I2S_SCK: Pin
SPK_I2S_SDO: Pin
SS: Pin
SSCB_SCL: Pin
SSCB_SDA: Pin
START: Pin
STATUS: Pin
STATUS_LED: Pin
STEMMA_SCL: Pin
STEMMA_SDA: Pin
STEP: Pin
SW: Pin
SW0: Pin
SW1: Pin
SW10: Pin
SW11: Pin
SW12: Pin
SW13: Pin
SW14: Pin
SW15: Pin
SW1_2: Pin
SW2: Pin
SW3: Pin
SW36: Pin
SW38: Pin
SW39: Pin
SW3_4: Pin
SW4: Pin
SW5: Pin
SW6: Pin
SW7: Pin
SW8: Pin
SW9: Pin
SWCLK: Pin
SWDCLK: Pin
SWDIO: Pin
SWITCH: Pin
SWITCH_CLK: Pin
SWITCH_DOWN: Pin
SWITCH_LATCH: Pin
SWITCH_LEFT: Pin
SWITCH_OUT: Pin
SWITCH_PRESS: Pin
SWITCH_RIGHT: Pin
SWITCH_UP: Pin
SW_A: Pin
SW_B: Pin
SW_BOOT: Pin
SW_C: Pin
SW_DOWN: Pin
SW_LEFT: Pin
SW_MID: Pin
SW_RIGHT: Pin
SW_TOPL: Pin
SW_TOPR: Pin
SW_UP: Pin
SW_X: Pin
SW_Y: Pin
SYS_INT: Pin
SYS_SCL: Pin
SYS_SDA: Pin
T0: Pin
T1: Pin
T10: Pin
T14: Pin
T2: Pin
T3: Pin
T4: Pin
T5: Pin
T6: Pin
T7: Pin
T8: Pin
T9: Pin
TCK: Pin
TDI: Pin
TEMP: Pin
TEMPERATURE: Pin
TEMP_SCL: Pin
TEMP_SDA: Pin
TFTB1: Pin
TFTB2: Pin
TFTB3: Pin
TFTB4: Pin
TFTB5: Pin
TFTG1: Pin
TFTG2: Pin
TFTG3: Pin
TFTG4: Pin
TFTG5: Pin
TFTG6: Pin
TFTR1: Pin
TFTR2: Pin
TFTR3: Pin
TFTR4: Pin
TFTR5: Pin
TFT_BACKLIGHT: Pin
TFT_BKLT: Pin
TFT_BL: Pin
TFT_CS: Pin
TFT_DATA: Pin
TFT_DC: Pin
TFT_I2C_POWER: Pin
TFT_LED: Pin
TFT_LITE: Pin
TFT_MISO: Pin
TFT_MOSI: Pin
TFT_NSS: Pin
TFT_POWER: Pin
TFT_RD: Pin
TFT_RESET: Pin
TFT_RS: Pin
TFT_RST: Pin
TFT_SCK: Pin
TFT_SCLK: Pin
TFT_TE: Pin
TFT_WR: Pin
TF_CS: Pin
TIP: Pin
TIP_SWITCH: Pin
TMS: Pin
TOUCH: Pin
TOUCH0: Pin
TOUCH1: Pin
TOUCH10: Pin
TOUCH11: Pin
TOUCH12: Pin
TOUCH13: Pin
TOUCH14: Pin
TOUCH2: Pin
TOUCH3: Pin
TOUCH4: Pin
TOUCH5: Pin
TOUCH6: Pin
TOUCH7: Pin
TOUCH8: Pin
TOUCH9: Pin
TOUCH_CS: Pin
TOUCH_INT: Pin
TOUCH_IRQ: Pin
TOUCH_MISO: Pin
TOUCH_MOSI: Pin
TOUCH_RES: Pin
TOUCH_RESET: Pin
TOUCH_RST: Pin
TOUCH_SCK: Pin
TOUCH_SCL: Pin
TOUCH_SDA: Pin
TOUCH_XL: Pin
TOUCH_XR: Pin
TOUCH_YD: Pin
TOUCH_YU: Pin
TP1: Pin
TP2: Pin
TP3: Pin
TP_MOTION: Pin
TP_RESET: Pin
TP_SHUTDOWN: Pin
TRACK0: Pin
TRACKBALL_CLICK: Pin
TRACKBALL_DOWN: Pin
TRACKBALL_LEFT: Pin
TRACKBALL_RIGHT: Pin
TRACKBALL_UP: Pin
TRIG: Pin
TST: Pin
TS_CS: Pin
TX: Pin
TX0: Pin
TX1: Pin
TX2: Pin
TX3: Pin
TX4: Pin
TX5: Pin
TX6: Pin
TX7: Pin
TX8: Pin
TXD: Pin
TX_D0_SWITCH_RIGHT: Pin
TX_D1_SWITCH_LEFT: Pin
TX_LED: Pin
TX_LED_INVERTED: Pin
TouchIn: Pin
U0R: Pin
U0RXD: Pin
U0T: Pin
U0TXD: Pin
UART1_CTS: Pin
UART1_RTS: Pin
UART1_RX: Pin
UART1_TX: Pin
UART2_CTS: Pin
UART2_RTS: Pin
UART2_RX: Pin
UART2_TX: Pin
UART3_RX: Pin
UART3_TX: Pin
UART5_RX: Pin
UART5_TX: Pin
UART6_RX: Pin
UART6_TX: Pin
UART7_RX: Pin
UART7_TX: Pin
UART8_RX: Pin
UART8_TX: Pin
UART_CTS: Pin
UART_CTS1: Pin
UART_POWER: Pin
UART_PWR: Pin
UART_RTS: Pin
UART_RTS1: Pin
UART_RX: Pin
UART_RX1: Pin
UART_RX2: Pin
UART_TX: Pin
UART_TX1: Pin
UART_TX2: Pin
UBLOX_CTS: Pin
UBLOX_POWER_ENABLE: Pin
UBLOX_POWER_MONITOR: Pin
UBLOX_POWER_ON: Pin
UBLOX_RESET: Pin
UBLOX_RTS: Pin
UBLOX_RX: Pin
UBLOX_TX: Pin
UP: Pin
UP_BUTTON: Pin
USB: Pin
USBBCEN: Pin
USBHOSTEN: Pin
USBHOST_DM: Pin
USBHOST_DP: Pin
USBRESET: Pin
USB_DM: Pin
USB_DP: Pin
USB_HOST_5V_POWER: Pin
USB_HOST_DATA_MINUS: Pin
USB_HOST_DATA_PLUS: Pin
USB_HOST_DM: Pin
USB_HOST_DP: Pin
USB_HOST_POWER: Pin
USB_ID: Pin
USB_IN: Pin
USB_OVCUR: Pin
USB_RELAY: Pin
USB_SEL: Pin
USB_VBUS: Pin
USER: Pin
USER_BUTTON: Pin
USER_LED: Pin
USER_PWR_SHUTDOWN: Pin
USER_SW: Pin
USR_BTN: Pin
V5: Pin
VBAT: Pin
VBATT: Pin
VBAT_SENSE: Pin
VBAT_VOLTAGE: Pin
VBUS: Pin
VBUS_DETECT: Pin
VBUS_PRESENT: Pin
VBUS_RST: Pin
VBUS_SENSE: Pin
VCC_OFF: Pin
VCC_ON: Pin
VCLK: Pin
VCP_RX: Pin
VCP_TX: Pin
VDD_ENV: Pin
VDIV: Pin
VEXT_SELECT: Pin
VIB: Pin
VIBRATE: Pin
VIBRATION_MOTOR: Pin
VIN: Pin
VN: Pin
VOC_RST: Pin
VOLTAGE_MONITOR: Pin
VOLUME: Pin
VP: Pin
VP_EN: Pin
VREF_POWER: Pin
VSPI_CLK: Pin
VSPI_CS: Pin
VSPI_CS0: Pin
VSPI_CS1: Pin
VSPI_CS2: Pin
VSPI_MISO: Pin
VSPI_MOSI: Pin
VSPI_SCK: Pin
VSYNC: Pin
V_3V3_MEAS: Pin
V_5V_MEAS: Pin
W5500_CS: Pin
W5500_INT: Pin
W5500_RESET: Pin
W5500_RST: Pin
WAKE: Pin
WDT_WDI: Pin
WHITELED: Pin
WHITE_LED: Pin
WHITE_LEDS: Pin
WIFI_BUSY: Pin
WIFI_CS: Pin
WIFI_MISO: Pin
WIFI_MODE: Pin
WIFI_MOSI: Pin
WIFI_PWR: Pin
WIFI_RESET: Pin
WIFI_SCK: Pin
WP_2: Pin
WRDATA: Pin
WRGATE: Pin
WRPROT: Pin
X: Pin
X0: Pin
X1: Pin
X10: Pin
X11: Pin
X12: Pin
X13: Pin
X14: Pin
X15: Pin
X17: Pin
X18: Pin
X19: Pin
X2: Pin
X20: Pin
X21: Pin
X22: Pin
X3: Pin
X4: Pin
X5: Pin
X6: Pin
X7: Pin
X8: Pin
X9: Pin
XB1_CS: Pin
XB1_INT: Pin
XB1_PWR: Pin
XB1_RX: Pin
XB1_TX: Pin
XB2_CS: Pin
XB2_INT: Pin
XB2_PWR: Pin
XB2_RX: Pin
XB2_TX: Pin
XBEE_POWER: Pin
XB_CS: Pin
XB_INT: Pin
XB_MISO: Pin
XB_MOSI: Pin
XB_RESET: Pin
XB_RX: Pin
XB_SCLK: Pin
XB_TX: Pin
XCLK: Pin
XY_NCS: Pin
XY_SCLK: Pin
XY_SDIO: Pin
Y0: Pin
Y1: Pin
Y10: Pin
Y11: Pin
Y12: Pin
Y2: Pin
Y3: Pin
Y4: Pin
Y5: Pin
Y6: Pin
Y7: Pin
Y8: Pin
Y9: Pin
YELLOW_LED: Pin
YELLOW_LED_INVERTED: Pin
_A0: Pin
_A1: Pin
_A2: Pin
_A3: Pin
_A4: Pin
_A5: Pin
_BATTERY: Pin
_BUTTONS: Pin
_C1: Pin
_C2: Pin
_C3: Pin
_C4: Pin
_C5: Pin
_C6: Pin
_C7: Pin
_C8: Pin
_D10: Pin
_D11: Pin
_D12: Pin
_D13: Pin
_D2: Pin
_D5: Pin
_D6: Pin
_D9: Pin
_NEOPIXEL: Pin
_NFC1: Pin
_NFC2: Pin
_R1: Pin
_R2: Pin
_R3: Pin
_R4: Pin
_R5: Pin
_R6: Pin
_R7: Pin
_R8: Pin
_SWITCH: Pin
_VOLTAGE_MONITOR: Pin
clock_pin: Pin
dclk: Pin
de: Pin
hsync: Pin
latch_pin: Pin
output_enable_pin: Pin
radioCS: Pin
vsync: Pin
xSDCS: Pin