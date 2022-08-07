from pybricks.parameters import Color


class Light:
    """
    A stub class to represent the light member of the EV3Brick class.
    """

    def __init__(self):
        ...

    def on(self, color: Color):
        """
        Turns on the light at the specified color.

        Args:
            color (Color): Color of the light. The light turns off if you choose None or a color that is not available. The brick status light supports Color.RED, Color.ORANGE, and Color.GREEN.
        """
        ...

    def off(self):
        """
        Turns off the light.
        """
        ...
