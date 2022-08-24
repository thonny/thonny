"""
Module: '_api.motionsensor' on micropython-v1.14-893-lego learning system hub
"""
# MCU: {'machine': 'LEGO Technic Large Hub with STM32F413xx', 'sysname': 'LEGO Technic Large Hub', 'platform': 'LEGO Learning System Hub', 'nodename': 'LEGO Learning System Hub', 'ver': 'v1.14-893', 'release': '1.14.0', 'name': 'micropython', 'family': 'micropython', 'port': 'LEGO Learning System Hub', 'version': '1.14.0', 'mpy': 517, 'build': '893'}
# Stubber: 1.7.2
from typing import Any


class MotionSensor():
    def __init__(self, *argv, **kwargs) -> None:
        """"""

    BACK = 'back' # type: str
    DOUBLE_TAPPED = 'doubletapped' # type: str
    DOWN = 'down' # type: str
    FALLING = 'falling' # type: str
    FRONT = 'front' # type: str
    LEFT_SIDE = 'leftside' # type: str
    RIGHT_SIDE = 'rightside' # type: str
    SHAKEN = 'shaken' # type: str
    TAPPED = 'tapped' # type: str
    UP = 'up' # type: str
    def align_to_model(self, *args, **kwargs) -> Any:
        """"""

    def get_gesture(self, *args, **kwargs) -> Any:
        """"""

    def get_orientation(self, *args, **kwargs) -> Any:
        """"""

    def get_pitch_angle(self, *args, **kwargs) -> Any:
        """"""

    def get_roll_angle(self, *args, **kwargs) -> Any:
        """"""

    def get_yaw_angle(self, *args, **kwargs) -> Any:
        """"""

    def reset_yaw_angle(self, *args, **kwargs) -> Any:
        """"""

    def wait_for_new_gesture(self, *args, **kwargs) -> Any:
        """"""

    def wait_for_new_orientation(self, *args, **kwargs) -> Any:
        """"""

    def was_gesture(self, *args, **kwargs) -> Any:
        """"""

def sleep_ms(*args, **kwargs) -> Any:
    """"""

