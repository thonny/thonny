"""System specific functions"""

from typing import Any, Dict, List, NoReturn, TextIO, Tuple

def exit(retval: object = ...) -> NoReturn:
    """Terminate current program with a given exit code.

    Example: ``sys.exit(1)``

    This function raises a ``SystemExit`` exception. If an argument is given, its
    value given as an argument to ``SystemExit``.

    :param retval: The exit code or message.
    """
    ...

def print_exception(exc: Exception) -> None:
    """
    Print an exception with a traceback.

    Example: ``sys.print_exception(e)``

    :param exc: The exception to print

    This is simplified version of a function which appears in the
    ``traceback`` module in CPython.
    """

argv: List[str]
"""A mutable list of arguments the current program was started with."""

byteorder: str
"""The byte order of the system (``"little"`` or ``"big"``)."""

class _implementation:
    name: str
    version: Tuple[int, int, int]

implementation: _implementation
"""Object with information about the current Python implementation.

For MicroPython, it has following attributes:

- ``name`` - string "micropython"
- ``version`` - tuple (major, minor, micro), e.g. (1, 7, 0)

This object is the recommended way to distinguish MicroPython from other
Python implementations (note that it still may not exist in the very
minimal ports).

CPython mandates more attributes for this object, but the actual useful
bare minimum is implemented in MicroPython.
"""

maxsize: int
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

modules: Dict[str, Any]
"""Dictionary of loaded modules. 

On some ports, it may not include builtin modules."""

path: List[str]
"""A mutable list of directories to search for imported modules."""

platform: str
"""The platform that MicroPython is running on. 

For OS/RTOS ports, this is usually an identifier of the OS, e.g. ``"linux"``.
For baremetal ports it is an identifier of a board, e.g. ``"pyboard"`` for 
the original MicroPython reference board. It thus can be used to
distinguish one board from another.

If you need to check whether your program runs on MicroPython (vs other
Python implementation), use ``sys.implementation`` instead.
"""

version: str
"""Python language version that this implementation conforms to, as a string."""

version_info: Tuple[int, int, int]
"""Python language version that this implementation conforms to, as a tuple of ints.

Only the first three version numbers (major, minor, micro) are supported and
they can be referenced only by index, not by name.
"""
