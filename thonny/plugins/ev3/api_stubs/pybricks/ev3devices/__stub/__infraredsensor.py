from pybricks.parameters import Button, Port
from typing import List, Tuple


class InfraredSensor:
    """
    LEGO® MINDSTORMS® EV3 Infrared Sensor and Beacon.

    Args:
        port (Port): Port to which the sensor is connected.
    """

    def __init__(self, port: Port):
        if port == Port.A or port == Port.B or port == Port.C or port == Port.D:
            raise ValueError("Sensors must use Port S1, S2, S3, or S4.")

    def distance(self) -> int:
        """
        Measures the relative distance between the sensor and an object using infrared light.

        Returns:
            Relative distance ranging from 0 (closest) to 100 (farthest).
        """
        return 0

    def beacon(self, channel: int) -> Tuple[int, int]:
        """
        Measures the relative distance and angle between the remote and the infrared sensor.

        Args:
            channel (int): Channel number of the remote.

        Returns:
            Tuple of relative distance (0 to 100) and approximate angle (-75 to 75 degrees) between remote and infrared sensor or (None,None) if no remote is detected.
        """
        if not channel in range(1,5):
            raise ValueError('Channel must be 1, 2, 3, or 4.')
        return (0, 0)

    def buttons(self, channel: int) -> List[Button]:
        """
        Checks which buttons on the infrared remote are pressed.

        This method can detect up to two buttons at once. If you press more buttons, you may not get useful data.

        Args:
            channel (int): Channel number of the remote.

        Returns:
            List of pressed buttons on the remote on the specified channel.
        """
        if not channel in range(1,5):
            raise ValueError('Channel must be 1, 2, 3, or 4.') 
        return []

    def keypad(self) -> List[Button]:
        """
        Checks which buttons on the infrared remote are pressed.

        This method can independently detect all 4 up/down buttons, but it cannot detect the beacon button.

        This method only works with the remote in channel 1.

        Returns:
            List of pressed buttons on the remote on selected channel.
        """
        return []
