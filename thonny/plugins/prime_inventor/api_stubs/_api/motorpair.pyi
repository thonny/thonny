"""
Module: '_api.motorpair' on micropython-v1.14-893-lego learning system hub
"""
# MCU: {'machine': 'LEGO Technic Large Hub with STM32F413xx', 'sysname': 'LEGO Technic Large Hub', 'platform': 'LEGO Learning System Hub', 'nodename': 'LEGO Learning System Hub', 'ver': 'v1.14-893', 'release': '1.14.0', 'name': 'micropython', 'family': 'micropython', 'port': 'LEGO Learning System Hub', 'version': '1.14.0', 'mpy': 517, 'build': '893'}
# Stubber: 1.7.2
from typing import Any


class MotorPair():
    def __init__(self, *argv, **kwargs) -> None:
        """"""

    BRAKE = 'brake' # type: str
    CM = 'cm' # type: str
    COAST = 'coast' # type: str
    DEGREES = 'degrees' # type: str
    HOLD = 'hold' # type: str
    IN = 'in' # type: str
    ROTATIONS = 'rotations' # type: str
    SECONDS = 'seconds' # type: str
    def get_default_speed(self, *args, **kwargs) -> Any:
        """"""

    def move(self, *args, **kwargs) -> Any:
        """"""

    def move_tank(self, *args, **kwargs) -> Any:
        """"""

    def set_default_speed(self, *args, **kwargs) -> Any:
        """"""

    def set_motor_rotation(self, *args, **kwargs) -> Any:
        """"""

    def set_stop_action(self, *args, **kwargs) -> Any:
        """"""

    def start(self, *args, **kwargs) -> Any:
        """"""

    def start_at_power(self, *args, **kwargs) -> Any:
        """"""

    def start_tank(self, *args, **kwargs) -> Any:
        """"""

    def start_tank_at_power(self, *args, **kwargs) -> Any:
        """"""

    def stop(self, *args, **kwargs) -> Any:
        """"""

    def was_interrupted(self, *args, **kwargs) -> Any:
        """"""

PORTS = {} # type: dict
def clamp_power(*args, **kwargs) -> Any:
    """"""

def clamp_speed(*args, **kwargs) -> Any:
    """"""

def clamp_steering(*args, **kwargs) -> Any:
    """"""

def from_steering(*args, **kwargs) -> Any:
    """"""

system : Any ## <class 'System'> = <System object at 20028790>
def wait_for_async(*args, **kwargs) -> Any:
    """"""

