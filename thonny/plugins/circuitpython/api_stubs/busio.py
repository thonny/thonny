class I2C:
    ""

    def deinit():
        pass

    def readfrom_into():
        pass

    def scan():
        pass

    def try_lock():
        pass

    def unlock():
        pass

    def writeto():
        pass


class OneWire:
    ""

    def deinit():
        pass

    def read_bit():
        pass

    def reset():
        pass

    def write_bit():
        pass


class SPI:
    ""

    def configure():
        pass

    def deinit():
        pass

    frequency = None

    def readinto():
        pass

    def try_lock():
        pass

    def unlock():
        pass

    def write():
        pass

    def write_readinto():
        pass


class UART:
    ""
    Parity = None
    baudrate = None

    def deinit():
        pass

    in_waiting = None

    def read():
        pass

    def readinto():
        pass

    def readline():
        pass

    def reset_input_buffer():
        pass

    def write():
        pass
