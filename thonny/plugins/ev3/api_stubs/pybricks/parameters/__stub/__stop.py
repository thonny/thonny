from enum import Enum


class Stop(Enum):
    """
    Action after the motor stops: coast, brake, or hold.

    Note:
        COAST: Let the motor move freely.
        BRAKE: Passively resist small external forces.
        HOLD: Keep controlling the motor to hold it at the commanded angle. This is only available on motors with encoders.
    """
    COAST = "COAST"
    BRAKE = "BRAKE"
    HOLD = "HOLD"
