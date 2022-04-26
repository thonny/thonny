from pybricks.parameters import Port


class Ev3devSensor:
    """
    Read values of an ev3dev-compatible sensor.

    Args:
        port (Port): Port to which the device is connected.

    Attributes:
        sensor_index (int): Index of the ev3dev sysfs lego-sensor class.
        port_index (int): Index of the ev3dev sysfs lego-port class.
    """

    def __init__(self, port: Port):
        self.sensor_index = 0  # type: int
        self.port_index = 0  # type: int
        if port == Port.A or port == Port.B or port == Port.C or port == Port.D:
            raise ValueError("Sensors must use Port S1, S2, S3, or S4.")

    def read(self, mode: str) -> tuple:
        """
        Reads values at a given mode.

        Args:
            mode (str): Mode name.

        Returns:
            Values read from the sensor.
        """
        return ()
