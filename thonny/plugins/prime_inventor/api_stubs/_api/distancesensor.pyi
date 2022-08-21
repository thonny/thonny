"""
Module: '_api.distancesensor' on micropython-v1.14-893-lego learning system hub
"""
# MCU: {'machine': 'LEGO Technic Large Hub with STM32F413xx', 'sysname': 'LEGO Technic Large Hub', 'platform': 'LEGO Learning System Hub', 'nodename': 'LEGO Learning System Hub', 'ver': 'v1.14-893', 'release': '1.14.0', 'name': 'micropython', 'family': 'micropython', 'port': 'LEGO Learning System Hub', 'version': '1.14.0', 'mpy': 517, 'build': '893'}
# Stubber: 1.7.2
from typing import Any


class DistanceSensor():
    def __init__(self, *argv, **kwargs) -> None:
        """"""

    CM = 'cm' # type: str
    IN = 'in' # type: str
    PERCENT = '%' # type: str
    def get_distance_cm(self, *args, **kwargs) -> Any:
        """"""

    def get_distance_inches(self, *args, **kwargs) -> Any:
        """"""

    def get_distance_percentage(self, *args, **kwargs) -> Any:
        """"""

    def light_up(self, *args, **kwargs) -> Any:
        """"""

    def light_up_all(self, *args, **kwargs) -> Any:
        """"""

    def wait_for_distance_closer_than(self, *args, **kwargs) -> Any:
        """"""

    def wait_for_distance_farther_than(self, *args, **kwargs) -> Any:
        """"""

LPF2_FLIPPER_DISTANCE = 62 # type: int
PORTS = {} # type: dict
def clamp(*args, **kwargs) -> Any:
    """"""

def is_type(*args, **kwargs) -> Any:
    """"""

def newSensorDisconnectedError(*args, **kwargs) -> Any:
    """"""

def sleep_ms(*args, **kwargs) -> Any:
    """"""

