class ADC:
    ""

    def read():
        pass

    def read_timed():
        pass

    def read_timed_multi():
        pass


class ADCAll:
    ""

    def read_channel():
        pass

    def read_core_temp():
        pass

    def read_core_vbat():
        pass

    def read_core_vref():
        pass

    def read_vref():
        pass


class Accel:
    ""

    def filtered_xyz():
        pass

    def read():
        pass

    def tilt():
        pass

    def write():
        pass

    def x():
        pass

    def y():
        pass

    def z():
        pass


class ExtInt:
    ""
    EVT_FALLING = 270663680
    EVT_RISING = 269615104
    EVT_RISING_FALLING = 271712256
    IRQ_FALLING = 270598144
    IRQ_RISING = 269549568
    IRQ_RISING_FALLING = 271646720

    def disable():
        pass

    def enable():
        pass

    def line():
        pass

    def regs():
        pass

    def swint():
        pass


class Flash:
    ""

    def ioctl():
        pass

    def readblocks():
        pass

    def writeblocks():
        pass


class I2C:
    ""
    MASTER = 0
    SLAVE = 1

    def deinit():
        pass

    def init():
        pass

    def is_ready():
        pass

    def mem_read():
        pass

    def mem_write():
        pass

    def recv():
        pass

    def scan():
        pass

    def send():
        pass


class LCD:
    ""

    def command():
        pass

    def contrast():
        pass

    def fill():
        pass

    def get():
        pass

    def light():
        pass

    def pixel():
        pass

    def show():
        pass

    def text():
        pass

    def write():
        pass


class LED:
    ""

    def intensity():
        pass

    def off():
        pass

    def on():
        pass

    def toggle():
        pass


class Pin:
    ""
    AF1_TIM1 = 1
    AF1_TIM2 = 1
    AF2_TIM3 = 2
    AF2_TIM4 = 2
    AF2_TIM5 = 2
    AF3_TIM10 = 3
    AF3_TIM11 = 3
    AF3_TIM9 = 3
    AF4_I2C1 = 4
    AF4_I2C3 = 4
    AF5_SPI1 = 5
    AF5_SPI2 = 5
    AF7_USART1 = 7
    AF7_USART2 = 7
    AF8_USART6 = 8
    AF9_I2C3 = 9
    AF_OD = 18
    AF_PP = 2
    ALT = 2
    ALT_OPEN_DRAIN = 18
    ANALOG = 3
    IN = 0
    IRQ_FALLING = 270598144
    IRQ_RISING = 269549568
    OPEN_DRAIN = 17
    OUT = 1
    OUT_OD = 17
    OUT_PP = 1
    PULL_DOWN = 2
    PULL_NONE = 0
    PULL_UP = 1

    def af():
        pass

    def af_list():
        pass

    board = None
    cpu = None

    def debug():
        pass

    def dict():
        pass

    def gpio():
        pass

    def high():
        pass

    def init():
        pass

    def irq():
        pass

    def low():
        pass

    def mapper():
        pass

    def mode():
        pass

    def name():
        pass

    def names():
        pass

    def off():
        pass

    def on():
        pass

    def pin():
        pass

    def port():
        pass

    def pull():
        pass

    def value():
        pass


class RTC:
    ""

    def calibration():
        pass

    def datetime():
        pass

    def info():
        pass

    def init():
        pass

    def wakeup():
        pass


SD = None


class SDCard:
    ""

    def info():
        pass

    def ioctl():
        pass

    def power():
        pass

    def present():
        pass

    def read():
        pass

    def readblocks():
        pass

    def write():
        pass

    def writeblocks():
        pass


class SPI:
    ""
    LSB = 128
    MASTER = 260
    MSB = 0
    SLAVE = 0

    def deinit():
        pass

    def init():
        pass

    def read():
        pass

    def readinto():
        pass

    def recv():
        pass

    def send():
        pass

    def send_recv():
        pass

    def write():
        pass

    def write_readinto():
        pass


class Servo:
    ""

    def angle():
        pass

    def calibration():
        pass

    def pulse_width():
        pass

    def speed():
        pass


class Switch:
    ""

    def callback():
        pass

    def value():
        pass


class Timer:
    ""
    BOTH = 10
    CENTER = 32
    DOWN = 16
    ENC_A = 9
    ENC_AB = 11
    ENC_B = 10
    FALLING = 2
    HIGH = 0
    IC = 8
    LOW = 2
    OC_ACTIVE = 3
    OC_FORCED_ACTIVE = 6
    OC_FORCED_INACTIVE = 7
    OC_INACTIVE = 4
    OC_TIMING = 2
    OC_TOGGLE = 5
    PWM = 0
    PWM_INVERTED = 1
    RISING = 0
    UP = 0

    def callback():
        pass

    def channel():
        pass

    def counter():
        pass

    def deinit():
        pass

    def freq():
        pass

    def init():
        pass

    def period():
        pass

    def prescaler():
        pass

    def source_freq():
        pass


class UART:
    ""
    CTS = 512
    RTS = 256

    def any():
        pass

    def deinit():
        pass

    def init():
        pass

    def read():
        pass

    def readchar():
        pass

    def readinto():
        pass

    def readline():
        pass

    def sendbreak():
        pass

    def write():
        pass

    def writechar():
        pass


class USB_HID:
    ""

    def recv():
        pass

    def send():
        pass


class USB_VCP:
    ""

    def any():
        pass

    def close():
        pass

    def isconnected():
        pass

    def read():
        pass

    def readinto():
        pass

    def readline():
        pass

    def readlines():
        pass

    def recv():
        pass

    def send():
        pass

    def setinterrupt():
        pass

    def write():
        pass


def bootloader():
    pass


def delay():
    pass


def dht_readinto():
    pass


def disable_irq():
    pass


def elapsed_micros():
    pass


def elapsed_millis():
    pass


def enable_irq():
    pass


def fault_debug():
    pass


def freq():
    pass


def hard_reset():
    pass


def have_cdc():
    pass


def hid():
    pass


hid_keyboard = None
hid_mouse = None


def info():
    pass


def main():
    pass


def micros():
    pass


def millis():
    pass


def mount():
    pass


def pwm():
    pass


def repl_info():
    pass


def repl_uart():
    pass


def servo():
    pass


def standby():
    pass


def stop():
    pass


def sync():
    pass


def udelay():
    pass


def unique_id():
    pass


def usb_mode():
    pass


def wfi():
    pass
