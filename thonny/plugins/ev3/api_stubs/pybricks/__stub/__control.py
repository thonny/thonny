from typing import Tuple

class Control:
    """
    Class to interact with PID controller and settings.

    Attributes:
        scale (float): Scaling factor between the controlled integer variable and the physical output. For example, for a single motor this is the number of encoder pulses per degree of rotation.
    """

    def __init__(self):
        self.scale = 1.0  # type: float

    def done(self) -> bool:
        """
        Checks if an ongoing command or maneuver is done.

        Returns:
            True if the command is done, False if not.
        """
        return False

    def stalled(self) -> bool:
        """
        Checks if the controller is currently stalled.

        A controller is stalled when it cannot reach the target speed or position, even with the maximum actuation signal.

        Returns:
            True if the controller is stalled, False if not.
        """
        return False

    def limits(self, speed: int = None, acceleration: int = None, actuation: int = None) -> Tuple[int, int, int]:
        """
        Configures the maximum speed, acceleration, and actuation.

        If no arguments are given, this will return the current values.

        Args:
            speed (int): Maximum speed. All speed commands will be capped to this value. Rotational (degrees/second) or Linear (millimeters/second).
            acceleration (int): Maximum acceleration. Rotational (degrees/second^2) or Linear (millimeters/second^2).
            actuation (int): Maximum actuation as percentage (0 - 100) of absolute maximum.

        Returns:
            Speed, acceleration, and actuation (if no arguments are provided). None, otherwise.
        """
        if speed is None and acceleration is None and actuation is None:
            return (0, 0, 0)
        else:
            return None

    def pid(self, kp: int = None, ki: int = None, kd: int = None, integral_range: int = None, integral_rate: int = None, feed_forward: int = None) -> Tuple[int, int, int, int, int, int]:
        """
        Gets or sets the PID values for position and speed control.

        If no arguments are given, this will return the current values.

        Args:	
            kp (int): Proportional position (or integral speed) control constant.
            ki (int): Integral position control constant.
            kd (int): Derivative position (or proportional speed) control constant.
            integral_range (int): Region around the target angle (degrees) or distance (millimeters), in which integral control errors are accumulated.
            integral_rate (int): Maximum rate at which the error integral is allowed to grow. Rotational (degrees/second) or Linear (millimeters/second).
            feed_forward (int): This adds a feed forward signal to the PID feedback signal, in the direction of the speed reference. This value is expressed as a percentage (0 - 100) of the absolute maximum duty cycle.

        Returns:
            kp, ki, kd, integral range, integral rate, and feed forward (if no arguments are provided), None otherwise.
        """
        if kp is None and ki is None and kd is None and integral_range is None and integral_rate is None and feed_forward is None:
            return (0, 0, 0, 0, 0, 0)
        else:
            return None

    def target_tolerances(self, speed: int = None, position: int = None) -> Tuple[int, int]:
        """
        Gets or sets the tolerances that say when a maneuver is done.

        If no arguments are given, this will return the current values.

        Args:	
            speed (int): Allowed deviation from zero speed before motion is considered complete. Linear (millimeters/second) or Rotational (degrees/second)
            position (init): Allowed deviation from the target before motion is considered complete. Linear (millimeters) or Rotational (degrees).

        Returns:
            Allowed deviation from zero speed and allowed deviation from the target (if no arguments are provided), None otherwise.
        """
        if speed is None and position is None:
            return (0, 0)
        else:
            return None

    def stall_tolerances(self, speed: int = None, time: int = None) -> Tuple[int, int]:
        """
        Gets or sets stalling tolerances.

        If no arguments are given, this will return the current values.

        Args:	
            speed (int): If the controller cannot reach this speed for some time even with maximum actuation, it is stalled. Rotational (degrees/second) or Linear (millimeters/second).
            time (int): How long the controller has to be below this minimum speed before we say it is stalled in milliseconds.

        Returns:
            Threshold speed and time limit (if no arguments are provided), None otherwise.
        """
        if speed is None and time is None:
            return (0, 0)
        else:
            return None
