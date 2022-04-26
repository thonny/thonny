from pybricks.parameters import Port


class LUMPDevice:
    """
    Devices using the LEGO UART Messaging Protocol.

    Args:
        port (Port): Port to which the device is connected.
    """

    def __init__(self, port: Port):
        if port == Port.A or port == Port.B or port == Port.C or port == Port.D:
            raise ValueError("Sensors must use Port S1, S2, S3, or S4.")

    def read(self, mode: int) -> tuple:
        """
        Reads values from a given mode.

        Args:
            mode (int): Device mode.

        Returns:
            Values read from the sensor.
        """
        return ()

    def write(self, mode: int, data: tuple):
        """
        Writes values to the sensor. Only selected sensors and modes support this.

        Args:
            mode (int): Device mode.
            data (tuple): Values to be written.
        """
        ...
