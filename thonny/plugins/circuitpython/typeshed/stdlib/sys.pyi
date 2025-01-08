"""
system specific functions.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/sys.rst.
=======================================

.. module:: sys
   :synopsis: system specific functions

|see_cpython_module| :mod:`python:sys`.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Callable, Final, Literal, NoReturn

from uio import IOBase

class Implementation(tuple[str, tuple[int, int, int], int]):
    name: str
    version: tuple[int, int, int]
    mpy: int

class ModuleType:
    __class__: str
    __name__: str

def exit(retval: object = 0, /) -> NoReturn:
    """
   Terminate current program with a given exit code. Underlyingly, this
   function raise as `SystemExit` exception. If an argument is given, its
   value given as an argument to `SystemExit`.
   """

def atexit(func: Callable[[], None] | None, /) -> Callable[[], None] | None:
    """
   Register *func* to be called upon termination.  *func* must be a callable
   that takes no arguments, or ``None`` to disable the call.  The ``atexit``
   function will return the previous value set by this function, which is
   initially ``None``.
   
   .. admonition:: Difference to CPython
      :class: attention
   
      This function is a MicroPython extension intended to provide similar
      functionality to the :mod:`atexit` module in CPython.
   """

def print_exception(exc: BaseException, file: IOBase[str] = "stdout", /) -> None:
    """
   Print exception with a traceback to a file-like object *file* (or
   `sys.stdout` by default).
   
   .. admonition:: Difference to CPython
      :class: attention
   
      This is simplified version of a function which appears in the
      ``traceback`` module in CPython. Unlike ``traceback.print_exception()``,
      this function takes just exception value instead of exception type,
      exception value, and traceback object; *file* argument should be
      positional; further arguments are not supported. CPython-compatible
      ``traceback`` module can be found in `micropython-lib`.
   
   .. function:: settrace(tracefunc)
   
   Enable tracing of bytecode execution.  For details see the `CPython
   documentaion <https://docs.python.org/3/library/sys.html#sys.settrace>`_.
   
   This function requires a custom MicroPython build as it is typically not
   present in pre-built firmware (due to it affecting performance).  The relevant
   configuration option is *MICROPY_PY_SYS_SETTRACE*.
   """

argv: Final[list[str]] = ...
"""
A mutable list of arguments the current program was started with.
"""

byteorder: Final[Literal["little", "big"]] = ...
"""
The byte order of the system (``"little"`` or ``"big"``).
"""

implementation: Final[Implementation] = ...
"""
Object with information about the current Python implementation. For
   MicroPython, it has following attributes:

   * *name* - string "micropython"
   * *version* - tuple (major, minor, micro), e.g. (1, 7, 0)

   This object is the recommended way to distinguish MicroPython from other
   Python implementations (note that it still may not exist in the very
   minimal ports).

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

modules: Final[dict[str, ModuleType]] = ...
"""
Dictionary of loaded modules. On some ports, it may not include builtin
   modules.
"""

path: Final[list[str]] = ...
"""
A mutable list of directories to search for imported modules.
"""

platform: Final[str] = ...
"""
The platform that MicroPython is running on. For OS/RTOS ports, this is
   usually an identifier of the OS, e.g. ``"linux"``. For baremetal ports it
   is an identifier of a board, e.g. ``"pyboard"`` for the original MicroPython
   reference board. It thus can be used to distinguish one board from another.
   If you need to check whether your program runs on MicroPython (vs other
   Python implementation), use `sys.implementation` instead.
"""

stderr: Final[IOBase[str]] = ...
"""
Standard error `stream`.
"""

stdin: Final[IOBase[str]] = ...
"""
Standard input `stream`.
"""

stdout: Final[IOBase[str]] = ...
"""
Standard output `stream`.
"""

version: Final[str] = ...
"""
Python language version that this implementation conforms to, as a string.
"""

version_info: Final[tuple[int, int, int]] = ...
"""
Python language version that this implementation conforms to, as a tuple of ints.

    .. admonition:: Difference to CPython
      :class: attention

      Only the first three version numbers (major, minor, micro) are supported and
      they can be referenced only by index, not by name.
"""
