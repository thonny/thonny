"""
Efficient arrays of numeric data.

MicroPython module: https://docs.micropython.org/en/v1.24.0/library/array.html

CPython module: :mod:`python:array` https://docs.python.org/3/library/array.html .

Supported format codes: ``b``, ``B``, ``h``, ``H``, ``i``, ``I``, ``l``,
``L``, ``q``, ``Q``, ``f``, ``d`` (the latter 2 depending on the
floating-point support).
"""

from __future__ import annotations
import sys
from _typeshed import Incomplete, ReadableBuffer, SupportsRead, SupportsWrite
from collections.abc import MutableSequence, Sequence, Iterable

# pytype crashes if array inherits from collections.abc.MutableSequence instead of typing.MutableSequence
from typing import Generic, Any, Literal, MutableSequence, SupportsIndex, TypeVar, overload  # noqa: Y022
from typing_extensions import Awaitable, TypeVar, Self, TypeAlias

if sys.version_info >= (3, 12):
    from types import GenericAlias

_IntTypeCode: TypeAlias = Literal["b", "B", "h", "H", "i", "I", "l", "L", "q", "Q"]
_FloatTypeCode: TypeAlias = Literal["f", "d"]
_UnicodeTypeCode: TypeAlias = Literal["u"]
_TypeCode: TypeAlias = _IntTypeCode | _FloatTypeCode | _UnicodeTypeCode

_T = TypeVar("_T", int, float, str)

# typecodes: str

class array(MutableSequence[_T], Generic[_T]):
    """
    |see_cpython_module| :mod:`python:array`.

    Supported format codes: ``b``, ``B``, ``h``, ``H``, ``i``, ``I``, ``l``,
    ``L``, ``q``, ``Q``, ``f``, ``d`` (the latter 2 depending on the
    floating-point support).

     +-----------+--------------------+-------------------+-----------------------+
     | Type code | C Type             | Python Type       | Minimum size in bytes |
     +===========+====================+===================+=======================+
     | ``'b'``   | signed char        | int               | 1                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'B'``   | unsigned char      | int               | 1                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'h'``   | signed short       | int               | 2                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'H'``   | unsigned short     | int               | 2                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'i'``   | signed int         | int               | 2                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'I'``   | unsigned int       | int               | 2                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'l'``   | signed long        | int               | 4                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'L'``   | unsigned long      | int               | 4                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'q'``   | signed long long   | int               | 8                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'Q'``   | unsigned long long | int               | 8                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'f'``   | float              | float             | 4                     |
     +-----------+--------------------+-------------------+-----------------------+
     | ``'d'``   | double             | float             | 8                     |
     +-----------+--------------------+-------------------+-----------------------+
    """

    @property
    def typecode(self) -> _TypeCode: ...
    @property
    def itemsize(self) -> int: ...
    @overload
    def __init__(self: array[int], typecode: _IntTypeCode, initializer: bytes | bytearray | Iterable[int] = ..., /) -> None: ...
    @overload
    def __init__(self: array[float], typecode: _FloatTypeCode, initializer: bytes | bytearray | Iterable[float] = ..., /) -> None: ...
    @overload
    def __init__(self: array[str], typecode: _UnicodeTypeCode, initializer: bytes | bytearray | Iterable[str] = ..., /) -> None: ...
    @overload
    def __init__(self, typecode: str, initializer: Iterable[_T], /) -> None: ...
    @overload
    def __init__(self, typecode: str, initializer: bytes | bytearray = ..., /) -> None: ...
    def append(self, val: Any, /) -> None:
        """
        Append new element *val* to the end of array, growing it.
        """
        ...

    def buffer_info(self) -> tuple[int, int]: ...
    def byteswap(self) -> None: ...
    def count(self, v: _T, /) -> int: ...
    def extend(self, iterable: Sequence[Any], /) -> None:
        """
        Append new elements as contained in *iterable* to the end of
        array, growing it.
        """
        ...

    def frombytes(self, buffer: ReadableBuffer, /) -> None: ...
    def fromfile(self, f: SupportsRead[bytes], n: int, /) -> None: ...
    def fromlist(self, list: list[_T], /) -> None: ...
    def fromunicode(self, ustr: str, /) -> None: ...
    if sys.version_info >= (3, 10):
        def index(self, v: _T, start: int = 0, stop: int = sys.maxsize, /) -> int: ...
    else:
        def index(self, v: _T, /) -> int: ...  # type: ignore[override]

    def insert(self, i: int, v: _T, /) -> None: ...
    def pop(self, i: int = -1, /) -> _T: ...
    def remove(self, v: _T, /) -> None: ...
    def tobytes(self) -> bytes: ...
    def tofile(self, f: SupportsWrite[bytes], /) -> None: ...
    def tolist(self) -> list[_T]: ...
    def tounicode(self) -> str: ...
    if sys.version_info < (3, 9):
        def fromstring(self, buffer: str | ReadableBuffer, /) -> None: ...
        def tostring(self) -> bytes: ...

    def __len__(self) -> int:
        """
        Returns the number of items in the array, called as ``len(a)`` (where ``a`` is an ``array``).

        **Note:** ``__len__`` cannot be called directly (``a.__len__()`` fails) and the
        method is not present in ``__dict__``, however ``len(a)`` does work.
        """
        ...

    @overload
    def __getitem__(self, key: SupportsIndex, /) -> _T: ...
    @overload
    def __getitem__(self, key: slice, /) -> array[_T]: ...
    @overload
    def __getitem__(self, index: int) -> _T:
        """
        Indexed read of the array, called as ``a[index]`` (where ``a`` is an ``array``).
        Returns a value if *index* is an ``int`` and an ``array`` if *index* is a slice.
        Negative indices count from the end and ``IndexError`` is thrown if the index is
        out of range.

        **Note:** ``__getitem__`` cannot be called directly (``a.__getitem__(index)`` fails) and
        is not present in ``__dict__``, however ``a[index]`` does work.
        """

    @overload
    def __getitem__(self, sl: slice) -> array[_T]:
        """
        Indexed read of the array, called as ``a[index]`` (where ``a`` is an ``array``).
        Returns a value if *index* is an ``int`` and an ``array`` if *index* is a slice.
        Negative indices count from the end and ``IndexError`` is thrown if the index is
        out of range.

        **Note:** ``__getitem__`` cannot be called directly (``a.__getitem__(index)`` fails) and
        is not present in ``__dict__``, however ``a[index]`` does work.
        """

    @overload  # type: ignore[override]
    def __setitem__(self, key: SupportsIndex, value: _T, /) -> None: ...
    @overload
    def __setitem__(self, key: slice, value: array[_T], /) -> None: ...
    @overload
    def __setitem__(self, index: int, value: _T) -> None:
        """
        Indexed write into the array, called as ``a[index] = value`` (where ``a`` is an ``array``).
        ``value`` is a single value if *index* is an ``int`` and an ``array`` if *index* is a slice.
        Negative indices count from the end and ``IndexError`` is thrown if the index is out of range.

        **Note:** ``__setitem__`` cannot be called directly (``a.__setitem__(index, value)`` fails) and
        is not present in ``__dict__``, however ``a[index] = value`` does work.
        """

    @overload
    def __setitem__(self, sl: slice, values: array[_T]) -> None:
        """
        Indexed write into the array, called as ``a[index] = value`` (where ``a`` is an ``array``).
        ``value`` is a single value if *index* is an ``int`` and an ``array`` if *index* is a slice.
        Negative indices count from the end and ``IndexError`` is thrown if the index is out of range.

        **Note:** ``__setitem__`` cannot be called directly (``a.__setitem__(index, value)`` fails) and
        is not present in ``__dict__``, however ``a[index] = value`` does work.
        """

    def __delitem__(self, key: SupportsIndex | slice, /) -> None: ...
    def __add__(self, other: array[_T]) -> array[_T]:
        """
        Return a new ``array`` that is the concatenation of the array with *other*, called as
        ``a + other`` (where ``a`` and *other* are both ``arrays``).

        **Note:** ``__add__`` cannot be called directly (``a.__add__(other)`` fails) and
        is not present in ``__dict__``, however ``a + other`` does work.
        """
        ...

    def __eq__(self, value: object, /) -> bool: ...
    def __ge__(self, value: array[_T], /) -> bool: ...
    def __gt__(self, value: array[_T], /) -> bool: ...
    def __iadd__(self, other: array[_T]) -> Self:
        """
        Concatenates the array with *other* in-place, called as ``a += other`` (where ``a`` and *other*
        are both ``arrays``).  Equivalent to ``extend(other)``.

        **Note:** ``__iadd__`` cannot be called directly (``a.__iadd__(other)`` fails) and
        is not present in ``__dict__``, however ``a += other`` does work.
        """
        ...

    def __imul__(self, value: int, /) -> Self: ...
    def __le__(self, value: array[_T], /) -> bool: ...
    def __lt__(self, value: array[_T], /) -> bool: ...
    def __mul__(self, value: int, /) -> array[_T]: ...
    def __rmul__(self, value: int, /) -> array[_T]: ...
    def __copy__(self) -> array[_T]: ...
    def __deepcopy__(self, unused: Any, /) -> array[_T]: ...
    def __buffer__(self, flags: int, /) -> memoryview: ...
    def __release_buffer__(self, buffer: memoryview, /) -> None: ...
    if sys.version_info >= (3, 12):
        def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...

# ArrayType = array
