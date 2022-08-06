from pybricks.parameters import Port


class UARTDevice:
    """
    Generic UART device.

    Args:
        port (Port): Port to which the device is connected.
        baudrate (int): Baudrate of the UART device.
        timeout (int): How long to wait during read() before giving up in milliseconds. If you choose None, it will wait forever.
    """

    def __init__(self, port: Port, baudrate: int, timeout: int):
        if port == Port.A or port == Port.B or port == Port.C or port == Port.D:
            raise ValueError("Sensors must use Port S1, S2, S3, or S4.")

    def read(self, length: int = 1) -> bytes:
        """
        Reads a given number of bytes from the buffer.

        Your program will wait until the requested number of bytes are received. If this takes longer than timeout, the ETIMEDOUT exception is raised.

        Args:
            length (int): How many bytes to read.

        Returns:
            Bytes returned from the device.
        """
        return bytes.fromhex('00')

    def read_all(self) -> bytes:
        """
        Reads all bytes from the buffer.

        Returns:
            Bytes returned from the device.
        """
        return bytes.fromhex('00')

    def write(self, data: bytes):
        """
        Writes bytes.

        Args:
            data (bytes): Bytes to be written.
        """
        ...

    def waiting(self) -> int:
        """
        Gets how many bytes are still waiting to be read.

        Returns:
            Number of bytes in the buffer.
        """
        return 0

    def clear(self):
        """
        Empties the buffer.
        """
        ...
