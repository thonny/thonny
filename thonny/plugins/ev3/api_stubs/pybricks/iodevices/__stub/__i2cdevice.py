from pybricks.parameters import Port


class I2CDevice:
    """
    Generic or custom I2C device.

    Args:
        port (Port): Port to which the device is connected.
        address (int): I2C address of the client device.
    """

    def __init__(self, port: Port, address: int):
        if port == Port.A or port == Port.B or port == Port.C or port == Port.D:
            raise ValueError("Sensors must use Port S1, S2, S3, or S4.")

    def read(self, reg: int, length: int) -> bytes:
        """
        Reads bytes, starting at a given register.

        Args:
            reg (int): Register at which to begin reading: 0–255 or 0x00–0xFF.
            length (int): How many bytes to read.

        Returns:	
            Bytes returned from the device.
        """
        return bytes.fromhex('00')

    def write(self, reg: int, data: bytes = None):
        """
        Writes bytes, starting at a given register.

        Args:
            reg (int): Register at which to begin writing: 0–255 or 0x00–0xFF.
            data (bytes): Bytes to be written.
        """
        ...
