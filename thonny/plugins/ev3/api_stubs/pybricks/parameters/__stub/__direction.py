from enum import Enum


class Direction(Enum):
    """
    Rotational direction for positive speed or angle values.

    Note:
        CLOCKWISE: A positive speed value should make the motor move clockwise.
        COUNTERCLOCKWISE: A positive speed value should make the motor move counterclockwise.

        By default, the positive direction is set as clockwise.

    """
    CLOCKWISE = "CLOCKWISE"
    COUNTERCLOCKWISE = "COUNTERCLOCKWISE"
