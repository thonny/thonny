from pybricks.parameters import Port


class TouchSensor:
    """
    LEGO® MINDSTORMS® EV3 Touch Sensor.

    Args:
        port (Port): Port to which the sensor is connected.
    """

    def __init__(self, port: Port):
        if port == Port.A or port == Port.B or port == Port.C or port == Port.D:
            raise ValueError("Sensors must use Port S1, S2, S3, or S4.")

    def pressed(self) -> bool:
        """
        Checks if the sensor is pressed.

        Return:
            True if the sensor is pressed, False if it is not pressed.
        """
        return False
