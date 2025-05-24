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

    Example I/O register usage on RP2040::

       import binascii
       import board
       import digitalio
       import memorymap

       def rp2040_set_pad_drive(p, d):
           pads_bank0 = memorymap.AddressRange(start=0x4001C000, length=0x4000)
           pad_ctrl = int.from_bytes(pads_bank0[p*4+4:p*4+8], "little")
           # Pad control register is updated using an MP-safe atomic XOR
           pad_ctrl ^= (d << 4)
           pad_ctrl &= 0x00000030
           pads_bank0[p*4+0x1004:p*4+0x1008] = pad_ctrl.to_bytes(4, "little")

       def rp2040_get_pad_drive(p):
           pads_bank0 = memorymap.AddressRange(start=0x4001C000, length=0x4000)
           pad_ctrl = int.from_bytes(pads_bank0[p*4+4:p*4+8], "little")
           return (pad_ctrl >> 4) & 0x3

       # set GPIO16 pad drive strength to 12 mA
       rp2040_set_pad_drive(16, 3)

       # print GPIO16 pad drive strength
       print(rp2040_get_pad_drive(16))

    Note that the above example does **not** work on RP2350 because base
    address and  organization of the "pads0" registers changed compared
    to the RP2040.
    """

    def __init__(self, *, start: int, length: int) -> None:
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

        1, 2, 4 and 8 byte aligned reads will be done in one transaction
        when possible.
        All others may use multiple transactions."""
        ...

    @overload
    def __setitem__(self, index: slice, value: ReadableBuffer) -> None: ...
    @overload
    def __setitem__(self, index: int, value: int) -> None:
        """Set the value(s) at the given index.

        1, 2, 4 and 8 byte aligned writes will be done in one transaction
        when possible.
        All others may use multiple transactions."""
        ...
