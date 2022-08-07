from pybricks.parameters import Color


class Light:
    """
    Built-in light of the NXT Color Sensor.

    Can be made red, green, blue or turned off.
    """

    def __init__(self):
        ...

    def on(self, color: Color):
        """
        Turns on the light at the specified color.

        Args:
            color (Color): Color of the light. The light turns off if you choose None or a color that is not available.
        """
        ...

    def off(self):
        """
        Turns off the light.
        """
        ...
