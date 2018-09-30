DEEPSLEEP_RESET = 4
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


PWRON_RESET = 1


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


SOFT_RESET = 0


class SPI:
    ""
    LSB = 128
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


class WDT:
    ""

    def feed():
        pass


WDT_RESET = 3


def bootloader():
    pass


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


def info():
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


def soft_reset():
    pass


def time_pulse_us():
    pass


def unique_id():
    pass
