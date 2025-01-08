"""
pack and unpack primitive data types.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/struct.rst.
=====================================================

.. module:: struct
   :synopsis: pack and unpack primitive data types

|see_cpython_module| :mod:`python:struct`.

Supported size/byte order prefixes: ``@``, ``<``, ``>``, ``!``.

Supported format codes: ``b``, ``B``, ``h``, ``H``, ``i``, ``I``, ``l``,
``L``, ``q``, ``Q``, ``s``, ``P``, ``f``, ``d`` (the latter 2 depending
on the floating-point support).

.. admonition:: Difference to CPython
   :class: attention

   Whitespace is not supported in format strings.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Any

from uio import AnyReadableBuf, AnyWritableBuf

def calcsize(fmt: str | bytes, /,) -> int:
    """
   Return the number of bytes needed to store the given *fmt*.
   """

def pack(fmt: str | bytes, /, *v: Any) -> bytes:
    """
   Pack the values *v1*, *v2*, ... according to the format string *fmt*.
   The return value is a bytes object encoding the values.
   """

def pack_into(
    fmt: str | bytes, buffer: AnyWritableBuf, offset: int, /, *v: Any
) -> None:
    """
   Pack the values *v1*, *v2*, ... according to the format string *fmt*
   into a *buffer* starting at *offset*. *offset* may be negative to count
   from the end of *buffer*.
   """

def unpack(fmt: str | bytes, data: AnyReadableBuf, /) -> tuple[Any, ...]:
    """
   Unpack from the *data* according to the format string *fmt*.
   The return value is a tuple of the unpacked values.
   """

def unpack_from(
    fmt: str | bytes, data: AnyReadableBuf, offset: int = 0, /
) -> tuple[Any, ...]:
    """
   Unpack from the *data* starting at *offset* according to the format string
   *fmt*. *offset* may be negative to count from the end of *buffer*. The return
   value is a tuple of the unpacked values.
   """
