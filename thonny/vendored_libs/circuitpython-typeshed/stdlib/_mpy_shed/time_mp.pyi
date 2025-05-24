"""
The tuple to pass or receive from the time methods is unfortunately 
defined differently on different ports, boards and versions of MicroPython.

The _Time8Tuple and _Time9Tuple are the most common ones, and are unified in the _TimeTuple.

As this still does not cover all cases, the _TimeTuple is a union of the two common cases and the generic Tuple.
"""

from typing import Tuple
from typing_extensions import TypeAlias

_Time8Tuple: TypeAlias = Tuple[int, int, int, int, int, int, int, int]
_Time9Tuple: TypeAlias = Tuple[int, int, int, int, int, int, int, int, int]
_TimeTuple: TypeAlias = _Time8Tuple | _Time9Tuple | Tuple[int, ...]
