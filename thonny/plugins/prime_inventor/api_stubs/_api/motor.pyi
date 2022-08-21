"""
Module: '_api.motor' on micropython-v1.14-893-lego learning system hub
"""
# MCU: {'machine': 'LEGO Technic Large Hub with STM32F413xx', 'sysname': 'LEGO Technic Large Hub', 'platform': 'LEGO Learning System Hub', 'nodename': 'LEGO Learning System Hub', 'ver': 'v1.14-893', 'release': '1.14.0', 'name': 'micropython', 'family': 'micropython', 'port': 'LEGO Learning System Hub', 'version': '1.14.0', 'mpy': 517, 'build': '893'}
# Stubber: 1.7.2
from typing import Any

MOTOR_TYPES = () # type: tuple

class Motor():
    def __init__(self, *argv, **kwargs) -> None:
        """"""

    BRAKE = 'brake' # type: str
    COAST = 'coast' # type: str
    HOLD = 'hold' # type: str
    def get_default_speed(self, *args, **kwargs) -> Any:
        """"""

    def get_degrees_counted(self, *args, **kwargs) -> Any:
        """"""

    def get_position(self, *args, **kwargs) -> Any:
        """"""

    def get_speed(self, *args, **kwargs) -> Any:
        """"""

    def run_for_degrees(self, *args, **kwargs) -> Any:
        """"""

    def run_for_rotations(self, *args, **kwargs) -> Any:
        """"""

    def run_for_seconds(self, *args, **kwargs) -> Any:
        """"""

    def run_to_degrees_counted(self, *args, **kwargs) -> Any:
        """"""

    def run_to_position(self, *args, **kwargs) -> Any:
        """"""

    def set_default_speed(self, *args, **kwargs) -> Any:
        """"""

    def set_degrees_counted(self, *args, **kwargs) -> Any:
        """"""

    def set_stall_detection(self, *args, **kwargs) -> Any:
        """"""

    def set_stop_action(self, *args, **kwargs) -> Any:
        """"""

    def start(self, *args, **kwargs) -> Any:
        """"""

    def start_at_power(self, *args, **kwargs) -> Any:
        """"""

    def stop(self, *args, **kwargs) -> Any:
        """"""

    def was_interrupted(self, *args, **kwargs) -> Any:
        """"""

    def was_stalled(self, *args, **kwargs) -> Any:
        """"""

PORTS = {} # type: dict
def clamp_power(*args, **kwargs) -> Any:
    """"""

def clamp_speed(*args, **kwargs) -> Any:
    """"""

def is_type(*args, **kwargs) -> Any:
    """"""

def newSensorDisconnectedError(*args, **kwargs) -> Any:
    """"""

def sleep_ms(*args, **kwargs) -> Any:
    """"""

system : Any ## <class 'System'> = <System object at 20028790>
def wait_for_async(*args, **kwargs) -> Any:
    """"""

