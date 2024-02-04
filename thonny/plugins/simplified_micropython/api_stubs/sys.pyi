"""
system specific functions

Descriptions taken from
`https://raw.githubusercontent.com/micropython/micropython/master/docs/library/sys.rst`, etc.
=======================================

.. module:: sys
   :synopsis: system specific functions

|see_cpython_module| :mod:`python:sys`.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.1.0"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Dict, Final, List, Tuple

class _Implementation(Tuple[str, Tuple[int, int, int]]):
    name: str
    version: Tuple[int, int, int]


class _ModuleType:
    __class__: str
    __name__: str


def exit(retval: object = 0, /) -> None:
    """
    Dummy method. Does nothing on micro:bit
    """


def print_exception(exc: BaseException, file: object = "stdout", /) -> None:
    """
    Print exception with a traceback. Argument `file` is ignored.

   .. admonition:: Difference to CPython
      :class: attention

      This is simplified version of a function which appears in the
      ``traceback`` module in CPython. Unlike ``traceback.print_exception()``,
      this function takes just exception value instead of exception type,
      exception value, and traceback object; *file* argument should be
      positional; further arguments are not supported. CPython-compatible
      ``traceback`` module can be found in `micropython-lib`.
   """


argv: Final[List[str]] = []
"""
List of arguments the current program was started with. Empty on micro:bit.
"""

byteorder: Final[str] = "little"
"""
The byte order of the system. `"little"` on micro:bit.
"""

implementation: Final[_Implementation] = ...
"""
Object with information about the current Python implementation. For
   MicroPython, it has following attributes:

   * *name* - string "micropython"
   * *version* - tuple (major, minor, micro), e.g. (1, 15, 0)

   This object is the recommended way to distinguish MicroPython from other
   Python implementations.

   .. admonition:: Difference to CPython
      :class: attention

      CPython mandates more attributes for this object, but the actual useful
      bare minimum is implemented in MicroPython.
"""

maxsize: Final[int] = ...
"""
Maximum value which a native integer type can hold on the current platform,
   or maximum value representable by MicroPython integer type, if it's smaller
   than platform max value (that is the case for MicroPython ports without
   long int support).

   This attribute is useful for detecting "bitness" of a platform (32-bit vs
   64-bit, etc.). It's recommended to not compare this attribute to some
   value directly, but instead count number of bits in it::

    bits = 0
    v = sys.maxsize
    while v:
        bits += 1
        v >>= 1
    if bits > 32:
        # 64-bit (or more) platform
        ...
    else:
        # 32-bit (or less) platform
        # Note that on 32-bit platform, value of bits may be less than 32
        # (e.g. 31) due to peculiarities described above, so use "> 16",
        # "> 32", "> 64" style of comparisons.
"""

modules: Final[Dict[str, _ModuleType]] = ...
"""
Dictionary of loaded modules. On some ports, it may not include builtin
   modules.
"""

path: Final[List[str]] = ...
"""
A mutable list of directories to search for imported modules. Not useful on micro:bit.
"""

platform: Final[str] = "microbit"
"""
The platform that MicroPython is running on. For OS/RTOS ports, this is
   usually an identifier of the OS, e.g. ``"linux"``. For baremetal ports it
   is an identifier of a board, e.g. ``"pyboard"`` for the original MicroPython
   reference board. It thus can be used to distinguish one board from another.
   If you need to check whether your program runs on MicroPython (vs other
   Python implementation), use `sys.implementation` instead.
"""


version: Final[str] = ...
"""
Python language version that this implementation conforms to, as a string.
"""

version_info: Final[Tuple[int, int, int]] = ...
"""
Python language version that this implementation conforms to, as a tuple of ints.

    .. admonition:: Difference to CPython
      :class: attention

      Only the first three version numbers (major, minor, micro) are supported and
      they can be referenced only by index, not by name.
"""
