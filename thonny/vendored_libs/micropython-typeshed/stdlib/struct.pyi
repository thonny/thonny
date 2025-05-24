"""
Pack and unpack primitive data types.

MicroPython module: https://docs.micropython.org/en/v1.24.0/library/struct.html

CPython module: :mod:`python:struct` https://docs.python.org/3/library/struct.html .

The following byte orders are supported:

+-----------+------------------------+----------+-----------+
| Character | Byte order             | Size     | Alignment |
+===========+========================+==========+===========+
| @         | native                 | native   | native    |
+-----------+------------------------+----------+-----------+
| <         | little-endian          | standard | none      |
+-----------+------------------------+----------+-----------+
| >         | big-endian             | standard | none      |
+-----------+------------------------+----------+-----------+
| !         | network (= big-endian) | standard | none      |
+-----------+------------------------+----------+-----------+

The following data types are supported:

+--------+--------------------+-------------------+---------------+
| Format | C Type             | Python type       | Standard size |
+========+====================+===================+===============+
| b      | signed char        | integer           | 1             |
+--------+--------------------+-------------------+---------------+
| B      | unsigned char      | integer           | 1             |
+--------+--------------------+-------------------+---------------+
| h      | short              | integer           | 2             |
+--------+--------------------+-------------------+---------------+
| H      | unsigned short     | integer           | 2             |
+--------+--------------------+-------------------+---------------+
| i      | int                | integer (`1<fn>`) | 4             |
+--------+--------------------+-------------------+---------------+
| I      | unsigned int       | integer (`1<fn>`) | 4             |
+--------+--------------------+-------------------+---------------+
| l      | long               | integer (`1<fn>`) | 4             |
+--------+--------------------+-------------------+---------------+
| L      | unsigned long      | integer (`1<fn>`) | 4             |
+--------+--------------------+-------------------+---------------+
| q      | long long          | integer (`1<fn>`) | 8             |
+--------+--------------------+-------------------+---------------+
| Q      | unsigned long long | integer (`1<fn>`) | 8             |
+--------+--------------------+-------------------+---------------+
| e      | n/a (half-float)   | float (`2<fn>`)   | 2             |
+--------+--------------------+-------------------+---------------+
| f      | float              | float (`2<fn>`)   | 4             |
+--------+--------------------+-------------------+---------------+
| d      | double             | float (`2<fn>`)   | 8             |
+--------+--------------------+-------------------+---------------+
| s      | char[]             | bytes             |               |
+--------+--------------------+-------------------+---------------+
| P      | void *             | integer           |               |
+--------+--------------------+-------------------+---------------+
"""

from __future__ import annotations
from _typeshed import Incomplete, ReadableBuffer, WriteableBuffer
from collections.abc import Iterator
from typing import Any
from _mpy_shed import AnyReadableBuf, AnyWritableBuf
from typing_extensions import Awaitable, TypeAlias, TypeVar

__all__ = ["calcsize", "pack", "pack_into", "unpack", "unpack_from", "iter_unpack", "Struct", "error"]

class error(Exception): ...

def pack(fmt: str | bytes, /, *v: Any) -> bytes:
    """
    Pack the values *v1*, *v2*, ... according to the format string *fmt*.
    The return value is a bytes object encoding the values.
    """
    ...

def pack_into(fmt: str | bytes, buffer: AnyWritableBuf, offset: int, /, *v: Any) -> None:
    """
    Pack the values *v1*, *v2*, ... according to the format string *fmt*
    into a *buffer* starting at *offset*. *offset* may be negative to count
    from the end of *buffer*.
    """
    ...

def unpack(fmt: str | bytes, data: AnyReadableBuf, /) -> tuple[Any, ...]:
    """
    Unpack from the *data* according to the format string *fmt*.
    The return value is a tuple of the unpacked values.
    """
    ...

def unpack_from(fmt: str | bytes, data: AnyReadableBuf, offset: int = 0, /) -> tuple[Any, ...]:
    """
    Unpack from the *data* starting at *offset* according to the format string
    *fmt*. *offset* may be negative to count from the end of *data*. The return
    value is a tuple of the unpacked values.
    """
    ...

def iter_unpack(format: str | bytes, buffer: ReadableBuffer, /) -> Iterator[tuple[Any, ...]]: ...
def calcsize(
    fmt: str | bytes,
    /,
) -> int:
    """
    Return the number of bytes needed to store the given *fmt*.
    """
    ...

class Struct:
    @property
    def format(self) -> str: ...
    @property
    def size(self) -> int: ...
    def __init__(self, format: str | bytes) -> None: ...
    def pack(self, *v: Any) -> bytes: ...
    def pack_into(self, buffer: WriteableBuffer, offset: int, *v: Any) -> None: ...
    def unpack(self, buffer: ReadableBuffer, /) -> tuple[Any, ...]: ...
    def unpack_from(self, buffer: ReadableBuffer, offset: int = 0) -> tuple[Any, ...]: ...
    def iter_unpack(self, buffer: ReadableBuffer, /) -> Iterator[tuple[Any, ...]]: ...
