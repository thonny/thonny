from pybricks.parameters import Port


class UltrasonicSensor:
    """
    LEGO® MINDSTORMS® EV3 Ultrasonic Sensor.

    Args:
        port (Port): Port to which the sensor is connected.
    """

    def __init__(self, port: Port):
        if port == Port.A or port == Port.B or port == Port.C or port == Port.D:
            raise ValueError("Sensors must use Port S1, S2, S3, or S4.")

    def distance(self, silent: bool = False) -> int:
        """
        Measures the distance between the sensor and an object using ultrasonic sound waves.

        Args:
            silent (bool): Choose True to turn the sensor off after measuring the distance. This reduces interference with other ultrasonic sensors. If you do this too frequently, the sensor can freeze. If this happens, unplug it and plug it back in.

        Returns:
            Distance in millimeters.
        """
        return 0

    def presence(self) -> bool:
        """
        Check for the presence of other ultrasonic sensors by detecting ultrasonic sounds. 

        If the other ultrasonic sensor is operating in silent mode, you can only detect the presence of that sensor while it is taking a measurement.

        Returns:
            True if ultrasonic sounds are detected, False if not.
        """
        return False
