from pybricks.parameters import Port
from typing import Callable


class VernierAdapter:
    """
    LEGO® MINDSTORMS® Education NXT/EV3 Adapter for Vernier Sensors.

    Args:
        port (Port): Port to which the sensor is connected.
        conversion (callable): Function of the format conversion(). This function is used to convert the raw analog voltage to the sensor-specific output value. Each Vernier Sensor has its own conversion function. The example given below demonstrates the conversion for the Surface Temperature Sensor.
    """

    def __init__(self, port: Port, conversion: Callable = None):
        if port == Port.A or port == Port.B or port == Port.C or port == Port.D:
            raise ValueError("Sensors must use Port S1, S2, S3, or S4.")

    def voltage(self) -> int:
        """
        Measures the raw analog sensor voltage.

        Returns:
            Analog voltage in millivolts.
        """
        return 0

    def conversion(self, voltage: int) -> int:
        """
        Converts the raw voltage (mV) to a sensor value.

        If you did not provide a conversion function earlier, no conversion will be applied.

        Args:
            voltage (int): Analog sensor voltage in millivolts.

        Returns:
            Converted sensor value.
        """
        return 0

    def value(self) -> int:
        """
        Measures the sensor voltage() and then applies your conversion() to give you the sensor value.

        Returns:
            Converted sensor value.
        """
        return 0
