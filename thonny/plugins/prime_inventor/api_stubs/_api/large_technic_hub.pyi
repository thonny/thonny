"""
This module defines the base class for `mindstorms.MSHub` and `spike.PrimeHub`.
The module appears only after you have imported either `mindstorms` or `spike`.
"""
from .button import Button
from .lightmatrix import LightMatrix
from .motionsensor import MotionSensor
from .speaker import Speaker
from .statuslight import StatusLight


class LargeTechnicHub():
    def __init__(self, *argv, **kwargs) -> None:
        """"""

    PORT_A:str = 'A'
    PORT_B:str = 'B'
    PORT_C:str = 'C'
    PORT_D:str = 'D'
    PORT_E:str = 'E'
    PORT_F:str = 'F'

    left_button : Button
    light_matrix : LightMatrix
    motion_sensor : MotionSensor
    right_button : Button
    speaker : Speaker
    status_light : StatusLight

