"""
Module: 'termios' on micropython-v1.24.1-unix
"""

# MCU: {'family': 'micropython', 'version': '1.24.1', 'build': '', 'ver': '1.24.1', 'port': 'unix', 'board': '', 'cpu': 'linux [GCC 12.4.0] version', 'mpy': 'v6.3', 'arch': 'x64'}
# Stubber: v1.24.0
from __future__ import annotations
from typing import Any, Final, Generator
from _typeshed import Incomplete

B576000: Final[int] = 4102
B57600: Final[int] = 4097
B500000: Final[int] = 4101
B921600: Final[int] = 4103
B9600: Final[int] = 13
TCSANOW: Final[int] = 0
B115200: Final[int] = 4098
B1000000: Final[int] = 4104
B460800: Final[int] = 4100
B1152000: Final[int] = 4105
B230400: Final[int] = 4099

def tcgetattr(*args, **kwargs) -> Incomplete: ...
def tcsetattr(*args, **kwargs) -> Incomplete: ...
def setraw(*args, **kwargs) -> Incomplete: ...
