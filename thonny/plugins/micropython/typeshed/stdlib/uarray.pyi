"""
efficient arrays of numeric data.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/array.rst.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import (
    overload,
    Sequence,
    Any,
    MutableSequence,
    Generic,
    Text,
    TypeVar,
    Final,
)

_T: Final = TypeVar("_T", int, float, Text)

# noinspection PyPep8Naming
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

    def __init__(self, typecode: str, iterable: Sequence[Any] = ..., /):
        """
       Create array with elements of given type. Initial contents of the
       array are given by *iterable*. If it is not provided, an empty
       array is created.
      """
    def append(self, val: Any, /) -> None:
        """
           Append new element *val* to the end of array, growing it.
      """
    def extend(self, iterable: Sequence[Any], /) -> None:
        """
           Append new elements as contained in *iterable* to the end of
           array, growing it.
      """
    def decode(self, encoding: str = "utf-8", errors: str = "strict") -> str:
        """
        Deprecated *do not use*, likely to be removed in future!
        
        Note: ``decode`` is only meant to be present for ``bytearray``, 
        but for efficiency of code-size reasons ``bytearray`` is implemented with the same code as the 
        other array type-codes and hence ``decode`` is on all ``array``s at present.
        """
    @overload
    def __delitem__(self, i: int) -> None:
        """``array`` object does **not** support item deletion."""
    @overload
    def __delitem__(self, sl: slice) -> None:
        """``array`` object does **not** support item deletion."""
    def insert(self, index: int, value: _T) -> None:
        """``array`` object does **not** support item insertion."""
    @overload
    def __getitem__(self, index: int) -> _T:
        """
        Indexed read of ``self``; called as ``a[index]``, where ``a`` is an ``array``.
        Returns the value at the given ``index``. 
        Negative indices count from end and ``IndexError``is thrown if the index out of range.
        
        **Note:** ``__getitem__`` cannot be called directly (``a.__getitem__(index)`` fails) and
        is not present in ``__dict__``, however ``a[index]`` does work.
        """
    @overload
    def __getitem__(self, sl: slice) -> array[_T]:
        """
        Slice read of ``self``; called as ``a[sl]``, where ``a`` is an ``array``.
        Returns an ``array`` of values for the given slice. 
        Negative slice indices count from end and ``IndexError``is thrown if any of the slice indices are out of range.
        **Note:** ``__getitem__`` cannot be called directly (``a.__getitem__(sl)`` fails) and
        is not present in ``__dict__``, however ``a[sl]`` does work.
        """
    @overload
    def __setitem__(self, index: int, value: _T) -> None:
        """
        Indexed write into ``self``; called as ``a[index] = value`` where ``a`` is an ``array``,
        ``index`` is an ``int``, and ``value`` is the same type as ``a``'s content.
        Negative indices count from end and ``IndexError``is thrown if the index out of range.
        
        **Note:** ``__setitem__`` cannot be called directly (``a.__setitem__(index, value)`` fails) and
        is not present in ``__dict__``, however ``a[index] = value`` does work.
        """
    @overload
    def __setitem__(self, sl: slice, values: array[_T]) -> None:
        """
        Indexed write into ``self``; called as ``a[sl] = values``, where ``a`` is an ``array``,
        ``sl`` is an ``slice``, and ``values`` is the same type as ``a``.
        Negative indices count from end and ``IndexError``is thrown if any of the slice indices are out of range.
        **Note:** ``__setitem__`` cannot be called directly (``a.__setitem__(index, value)`` fails) and
        is not present in ``__dict__``, however ``a[index] = value`` does work.
        """
    def __len__(self) -> int:
        """
        Returns the number of items in ``self``; called as ``len(a)``, where ``a`` is an ``array``.
        **Note:** ``__len__`` cannot be called directly (``a.__len__()`` fails) and the 
        method is not present in ``__dict__``, however ``len(a)`` does work.
        """
    def __add__(self, other: array[_T]) -> array[_T]:
        """
        Return a new ``array`` that is the concatenation of ``self`` with ``other``;
        called as ``a + other`` (where ``a`` and ``other`` are both ``array``s).
        **Note:** ``__add__`` cannot be called directly (``a.__add__(other)`` fails) and
        is not present in ``__dict__``, however ``a + other`` does work.
        """
    def __iadd__(self, other: array[_T]) -> None:
        """
        Concatenates ``self`` with ``other`` in-place;
        called as ``a += other``, where ``a`` and ``other`` are both ``array``s.
        Equivalent to ``extend(other)``.
        **Note:** ``__iadd__`` cannot be called directly (``a.__iadd__(other)`` fails) and
        is not present in ``__dict__``, however ``a += other`` does work.
        """
    def __repr__(self) -> str:
        """
        Returns the string representation of ``self``; called as ``str(a)`` or ``repr(a)```, 
        where ``a`` is an ``array``.
        Returns the string 'array(<type>, [<elements>])', 
        where ``<type>`` is the type code letter for ``self`` and ``<elements>`` is a 
        comma separated list of the elements of ``self``.
        **Note:** ``__repr__`` cannot be called directly (``a.__repr__()`` fails) and
        is not present in ``__dict__``, however ``str(a)`` and ``repr(a)`` both work.
        """
