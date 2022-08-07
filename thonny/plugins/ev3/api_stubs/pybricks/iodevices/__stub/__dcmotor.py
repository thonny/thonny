from pybricks.parameters import Direction, Port


class DCMotor:
    """
    Generic class to control simple motors without rotation sensors, such as train motors.

    Args:
        port (Port): Port to which the motor is connected.
        positive_direction (Direction): Which direction the motor should turn when you give a positive duty cycle value.
    """

    def __init__(self, port: Port, positive_direction: Direction = Direction.CLOCKWISE):
        if port == Port.S1 or port == Port.S2 or port == Port.S3 or port == Port.S4:
            raise ValueError("Motors must use Port A, B, C, or D.")

    def dc(self, duty: int):
        """
        Rotates the motor at a given duty cycle (also known as “power”).

        Args:
            duty (int): The duty cycle as a percentage (-100 to 100).
        """
        ...

    def stop(self):
        """
        Stops the motor and lets it spin freely.

        The motor gradually stops due to friction.
        """
        ...
