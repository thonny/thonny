class ADC:
    ""
    ATTN_0DB = 0
    ATTN_11DB = 3
    ATTN_2_5DB = 1
    ATTN_6DB = 2
    WIDTH_10BIT = 1
    WIDTH_11BIT = 2
    WIDTH_12BIT = 3
    WIDTH_9BIT = 0

    def atten():
        pass

    def read():
        pass

    def width():
        pass


class DAC:
    ""

    def write():
        pass


DEEPSLEEP = 4
DEEPSLEEP_RESET = 4
EXT0_WAKE = 1
EXT1_WAKE = 2
HARD_RESET = 2


class I2C:
    ""

    def init():
        pass

    def readfrom():
        pass

    def readfrom_into():
        pass

    def readfrom_mem():
        pass

    def readfrom_mem_into():
        pass

    def readinto():
        pass

    def scan():
        pass

    def start():
        pass

    def stop():
        pass

    def write():
        pass

    def writeto():
        pass

    def writeto_mem():
        pass


PIN_WAKE = 1


class PWM:
    ""

    def deinit():
        pass

    def duty():
        pass

    def freq():
        pass

    def init():
        pass


PWRON_RESET = 1


class Pin:
    ""
    IN = 1
    IRQ_FALLING = 2
    IRQ_RISING = 1
    OPEN_DRAIN = 7
    OUT = 3
    PULL_DOWN = 1
    PULL_UP = 0
    WAKE_HIGH = 5
    WAKE_LOW = 4

    def init():
        pass

    def irq():
        pass

    def value():
        pass


class RTC:
    ""

    def datetime():
        pass

    def init():
        pass

    def memory():
        pass


SLEEP = 2
SOFT_RESET = 5


class SPI:
    ""
    LSB = 1
    MSB = 0

    def deinit():
        pass

    def init():
        pass

    def read():
        pass

    def readinto():
        pass

    def write():
        pass

    def write_readinto():
        pass


class Signal:
    ""

    def off():
        pass

    def on():
        pass

    def value():
        pass


TIMER_WAKE = 3
TOUCHPAD_WAKE = 4


class Timer:
    ""
    ONE_SHOT = 0
    PERIODIC = 1

    def deinit():
        pass

    def init():
        pass

    def value():
        pass


class TouchPad:
    ""

    def config():
        pass

    def read():
        pass


class UART:
    ""

    def any():
        pass

    def init():
        pass

    def read():
        pass

    def readinto():
        pass

    def readline():
        pass

    def write():
        pass


ULP_WAKE = 5


class WDT:
    ""

    def feed():
        pass


WDT_RESET = 3


def deepsleep():
    pass


def disable_irq():
    pass


def enable_irq():
    pass


def freq():
    pass


def idle():
    pass


mem16 = None
mem32 = None
mem8 = None


def reset():
    pass


def reset_cause():
    pass


def sleep():
    pass


def time_pulse_us():
    pass


def unique_id():
    pass


def wake_reason():
    pass
