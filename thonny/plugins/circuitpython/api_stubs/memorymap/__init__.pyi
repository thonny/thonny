"""Raw memory map access

The `memorymap` module allows you to read and write memory addresses in the
address space seen from the processor running CircuitPython. It is usually
the physical address space.
"""

from __future__ import annotations

from typing import overload

from circuitpython_typing import ReadableBuffer

class AddressRange:
    r"""Presents a range of addresses as a bytearray.

    The addresses may access memory or memory mapped peripherals.

    Some address ranges may be protected by CircuitPython to prevent errors.
    An exception will be raised when constructing an AddressRange for an
    invalid or protected address.

    Multiple AddressRanges may overlap. There is no "claiming" of addresses.

    Example usage on ESP32-S2::

       import memorymap
       rtc_slow_mem = memorymap.AddressRange(start=0x50000000, length=0x2000)
       rtc_slow_mem[0:3] = b"\xcc\x10\x00"
    """
    def __init__(self, *, start, length) -> None:
        """Constructs an address range starting at ``start`` and ending at
        ``start + length``. An exception will be raised if any of the
        addresses are invalid or protected."""
        ...
    def __bool__(self) -> bool: ...
    def __len__(self) -> int:
        """Return the length. This is used by (`len`)"""
        ...
    @overload
    def __getitem__(self, index: slice) -> bytearray: ...
    @overload
    def __getitem__(self, index: int) -> int:
        """Returns the value(s) at the given index.

        1, 2, 4 and 8 byte aligned reads will be done in one transaction.
        All others may use multiple transactions."""
        ...
    @overload
    def __setitem__(self, index: slice, value: ReadableBuffer) -> None: ...
    @overload
    def __setitem__(self, index: int, value: int) -> None:
        """Set the value(s) at the given index.

        1, 2, 4 and 8 byte aligned writes will be done in one transaction.
        All others may use multiple transactions."""
        ...
