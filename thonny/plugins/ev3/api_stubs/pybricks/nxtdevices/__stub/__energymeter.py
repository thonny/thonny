from pybricks.parameters import Port
from typing import Tuple


class EnergyMeter:
    """
    LEGO® MINDSTORMS® Education NXT Energy Meter.

    Args:
        port (Port): Port to which the sensor is connected.
    """

    def __init__(self, port: Port):
        if port == Port.A or port == Port.B or port == Port.C or port == Port.D:
            raise ValueError("Sensors must use Port S1, S2, S3, or S4.")

    def storage(self) -> int:
        """
        Gets the total available energy stored in the battery.

        Returns:
            Remaining stored energy in joules.
        """
        return 0

    def input(self) -> Tuple[int, int, int]:
        """
        Measures the electrical signals at the input (bottom) side of the energy meter. It measures the voltage applied to it and the current passing through it. The product of these two values is power. This power value is the rate at which the stored energy increases. This power is supplied by an energy source such as the provided solar panel or an externally driven motor.

        Returns:	
            Voltage (millivolts), current (milliamps), and power (milliwatts) measured at the input port.
        """
        return (0, 0, 0)

    def output(self) -> Tuple[int, int, int]:
        """
        Measures the electrical signals at the output (top) side of the energy meter. It measures the voltage applied to the external load and the current passing to it. The product of these two values is power. This power value is the rate at which the stored energy decreases. This power is consumed by the load, such as a light or a motor.

        Returns:
            Voltage (millivolts), current (milliamps), and power (milliwatts) measured at the output port.
        """
        return (0, 0, 0)
