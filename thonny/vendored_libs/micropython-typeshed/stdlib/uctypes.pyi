"""
Access binary data in a structured way.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/uctypes.html

This module implements "foreign data interface" for MicroPython. The idea
behind it is similar to CPython's ``ctypes`` modules, but the actual API is
different, streamlined and optimized for small size. The basic idea of the
module is to define data structure layout with about the same power as the
C language allows, and then access it using familiar dot-syntax to reference
sub-fields.

---
Module: 'uctypes' on micropython-v1.25.0-esp32-ESP32_GENERIC-SPIRAM
"""

# MCU: {'variant': 'SPIRAM', 'build': '', 'arch': 'xtensawin', 'port': 'esp32', 'board': 'ESP32_GENERIC', 'board_id': 'ESP32_GENERIC-SPIRAM', 'mpy': 'v6.3', 'ver': '1.25.0', 'family': 'micropython', 'cpu': 'ESP32', 'version': '1.25.0'}
# Stubber: v1.25.0
from __future__ import annotations
from typing import overload, Any, Final, Generator
from _typeshed import Incomplete
from _mpy_shed import AnyReadableBuf, AnyWritableBuf
from typing_extensions import Awaitable, TypeAlias, TypeVar

VOID: Final[int] = 0
NATIVE: Final[int] = 2
PTR: Final[int] = 536870912
SHORT: Final[int] = 402653184
LONGLONG: Final[int] = 939524096
INT8: Final[int] = 134217728
LITTLE_ENDIAN: Final[int] = 0
LONG: Final[int] = 671088640
UINT: Final[int] = 536870912
ULONG: Final[int] = 536870912
ULONGLONG: Final[int] = 805306368
USHORT: Final[int] = 268435456
UINT8: Final[int] = 0
UINT16: Final[int] = 268435456
UINT32: Final[int] = 536870912
UINT64: Final[int] = 805306368
INT64: Final[int] = 939524096
BFUINT16: Final[int] = -805306368
BFUINT32: Final[int] = -536870912
BFUINT8: Final[int] = -1073741824
BFINT8: Final[int] = -939524096
ARRAY: Final[int] = -1073741824
BFINT16: Final[int] = -671088640
BFINT32: Final[int] = -402653184
BF_LEN: Final[int] = 22
INT: Final[int] = 671088640
INT16: Final[int] = 402653184
INT32: Final[int] = 671088640
FLOAT64: Final[int] = -134217728
BF_POS: Final[int] = 17
BIG_ENDIAN: Final[int] = 1
FLOAT32: Final[int] = -268435456
_ScalarProperty: TypeAlias = int
_RecursiveProperty: TypeAlias = tuple[int, _property]
_ArrayProperty: TypeAlias = tuple[int, int]
_ArrayOfAggregateProperty: TypeAlias = tuple[int, int, _property]
_PointerToAPrimitiveProperty: TypeAlias = tuple[int, int]
_PointerToAaAggregateProperty: TypeAlias = tuple[int, "_property"]
_BitfieldProperty: TypeAlias = int
_property: TypeAlias = (
    _ScalarProperty
    | _RecursiveProperty
    | _ArrayProperty
    | _ArrayOfAggregateProperty
    | _PointerToAPrimitiveProperty
    | _PointerToAaAggregateProperty
    | _BitfieldProperty
)
_descriptor: TypeAlias = tuple[str, _property]

def sizeof(struct: struct | _descriptor | dict, layout_type: int = NATIVE, /) -> int:
    """
    Return size of data structure in bytes. The *struct* argument can be
    either a structure class or a specific instantiated structure object
    (or its aggregate field).
    """
    ...

def bytes_at(addr: int, size: int, /) -> bytes:
    """
    Capture memory at the given address and size as bytes object. As bytes
    object is immutable, memory is actually duplicated and copied into
    bytes object, so if memory contents change later, created object
    retains original value.
    """
    ...

def bytearray_at(addr: int, size: int, /) -> bytearray:
    """
    Capture memory at the given address and size as bytearray object.
    Unlike bytes_at() function above, memory is captured by reference,
    so it can be both written too, and you will access current value
    at the given memory address.
    """
    ...

def addressof(obj: AnyReadableBuf, /) -> int:
    """
    Return address of an object. Argument should be bytes, bytearray or
    other object supporting buffer protocol (and address of this buffer
    is what actually returned).
    """
    ...

class struct:
    """
    Module contents
    ---------------
    """

    def __init__(self, addr: int, descriptor: _descriptor, layout_type: int = NATIVE, /) -> None:
        """
        Instantiate a "foreign data structure" object based on structure address in
        memory, descriptor (encoded as a dictionary), and layout type (see below).
        """

    @overload  # force push
    def __getattr__(self, a): ...
