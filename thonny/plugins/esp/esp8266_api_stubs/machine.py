class ADC:
    ""

    def read():
        pass


DEEPSLEEP = 4
DEEPSLEEP_RESET = 5
HARD_RESET = 6


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


PWRON_RESET = 0


class Pin:
    ""
    IN = 0
    IRQ_FALLING = 2
    IRQ_RISING = 1
    OPEN_DRAIN = 2
    OUT = 1
    PULL_UP = 1

    def init():
        pass

    def irq():
        pass

    def off():
        pass

    def on():
        pass

    def value():
        pass


class RTC:
    ""
    ALARM0 = 0

    def alarm():
        pass

    def alarm_left():
        pass

    def datetime():
        pass

    def irq():
        pass

    def memory():
        pass


SOFT_RESET = 4


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


class Timer:
    ""
    ONE_SHOT = 0
    PERIODIC = 1

    def deinit():
        pass

    def init():
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


class WDT:
    ""

    def deinit():
        pass

    def feed():
        pass


WDT_RESET = 1


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
