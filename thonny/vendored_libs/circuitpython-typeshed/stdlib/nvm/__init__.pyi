"""Non-volatile memory

The `nvm` module allows you to store whatever raw bytes you wish in a
reserved section non-volatile memory.

Note that this module can't be imported and used directly. The sole
instance of :class:`ByteArray` is available at
:attr:`microcontroller.nvm`."""

from __future__ import annotations

from typing import overload

from circuitpython_typing import ReadableBuffer

class ByteArray:
    r"""Presents a stretch of non-volatile memory as a bytearray.

    Non-volatile memory is available as a byte array that persists over reloads
    and power cycles. Each assignment causes an erase and write cycle so its recommended to assign
    all values to change at once.

    Usage::

       import microcontroller
       microcontroller.nvm[0:3] = b"\xcc\x10\x00"
    """

    def __init__(self) -> None:
        """Not currently dynamically supported. Access the sole instance through `microcontroller.nvm`."""
        ...

    def __bool__(self) -> bool: ...
    def __len__(self) -> int:
        """Return the length. This is used by (`len`)"""
        ...

    @overload
    def __getitem__(self, index: slice) -> bytearray: ...
    @overload
    def __getitem__(self, index: int) -> int:
        """Returns the value at the given index."""
        ...

    @overload
    def __setitem__(self, index: slice, value: ReadableBuffer) -> None: ...
    @overload
    def __setitem__(self, index: int, value: int) -> None:
        """Set the value at the given index."""
        ...
