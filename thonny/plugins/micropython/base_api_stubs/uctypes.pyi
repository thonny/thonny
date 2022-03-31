"""
access binary data in a structured way.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/uctypes.rst.
========================================================

.. module:: uctypes
   :synopsis: access binary data in a structured way

This module implements "foreign data interface" for MicroPython. The idea
behind it is similar to CPython's ``ctypes`` modules, but the actual API is
different, streamlined and optimized for small size. The basic idea of the
module is to define data structure layout with about the same power as the
C language allows, and then access it using familiar dot-syntax to reference
sub-fields.

.. warning::

    ``uctypes`` module allows access to arbitrary memory addresses of the
    machine (including I/O and control registers). Uncareful usage of it
    may lead to crashes, data loss, and even hardware malfunction.

.. seealso::

    Module :mod:`struct`
        Standard Python way to access binary data structures (doesn't scale
        well to large and complex structures).

Usage examples::

    import uctypes

    # Example 1: Subset of ELF file header
    # https://wikipedia.org/wiki/Executable_and_Linkable_Format#File_header
    ELF_HEADER = {
        "EI_MAG": (0x0 | uctypes.ARRAY, 4 | uctypes.UINT8),
        "EI_DATA": 0x5 | uctypes.UINT8,
        "e_machine": 0x12 | uctypes.UINT16,
    }

    # "f" is an ELF file opened in binary mode
    buf = f.read(uctypes.sizeof(ELF_HEADER, uctypes.LITTLE_ENDIAN))
    header = uctypes.struct(uctypes.addressof(buf), ELF_HEADER, uctypes.LITTLE_ENDIAN)
    assert header.EI_MAG == b"\x7fELF"
    assert header.EI_DATA == 1, "Oops, wrong endianness. Could retry with uctypes.BIG_ENDIAN."
    print("machine:", hex(header.e_machine))


    # Example 2: In-memory data structure, with pointers
    COORD = {
        "x": 0 | uctypes.FLOAT32,
        "y": 4 | uctypes.FLOAT32,
    }

    STRUCT1 = {
        "data1": 0 | uctypes.UINT8,
        "data2": 4 | uctypes.UINT32,
        "ptr": (8 | uctypes.PTR, COORD),
    }

    # Suppose you have address of a structure of type STRUCT1 in "addr"
    # uctypes.NATIVE is optional (used by default)
    struct1 = uctypes.struct(addr, STRUCT1, uctypes.NATIVE)
    print("x:", struct1.ptr[0].x)


    # Example 3: Access to CPU registers. Subset of STM32F4xx WWDG block
    WWDG_LAYOUT = {
        "WWDG_CR": (0, {
            # BFUINT32 here means size of the WWDG_CR register
            "WDGA": 7 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT32,
            "T": 0 << uctypes.BF_POS | 7 << uctypes.BF_LEN | uctypes.BFUINT32,
        }),
        "WWDG_CFR": (4, {
            "EWI": 9 << uctypes.BF_POS | 1 << uctypes.BF_LEN | uctypes.BFUINT32,
            "WDGTB": 7 << uctypes.BF_POS | 2 << uctypes.BF_LEN | uctypes.BFUINT32,
            "W": 0 << uctypes.BF_POS | 7 << uctypes.BF_LEN | uctypes.BFUINT32,
        }),
    }

    WWDG = uctypes.struct(0x40002c00, WWDG_LAYOUT)

    WWDG.WWDG_CFR.WDGTB = 0b10
    WWDG.WWDG_CR.WDGA = 1
    print("Current counter:", WWDG.WWDG_CR.T)

Defining structure layout
-------------------------

Structure layout is defined by a "descriptor" - a Python dictionary which
encodes field names as keys and other properties required to access them as
associated values::

    {
        "field1": <properties>,
        "field2": <properties>,
        ...
    }

Currently, ``uctypes`` requires explicit specification of offsets for each
field. Offset are given in bytes from the structure start.

Following are encoding examples for various field types:

* Scalar types::

    "field_name": offset | uctypes.UINT32

  in other words, the value is a scalar type identifier ORed with a field offset
  (in bytes) from the start of the structure.

* Recursive structures::

    "sub": (offset, {
        "b0": 0 | uctypes.UINT8,
        "b1": 1 | uctypes.UINT8,
    })

  i.e. value is a 2-tuple, first element of which is an offset, and second is
  a structure descriptor dictionary (note: offsets in recursive descriptors
  are relative to the structure it defines). Of course, recursive structures
  can be specified not just by a literal dictionary, but by referring to a
  structure descriptor dictionary (defined earlier) by name.

* Arrays of primitive types::

      "arr": (offset | uctypes.ARRAY, size | uctypes.UINT8),

  i.e. value is a 2-tuple, first element of which is ARRAY flag ORed
  with offset, and second is scalar element type ORed number of elements
  in the array.

* Arrays of aggregate types::

    "arr2": (offset | uctypes.ARRAY, size, {"b": 0 | uctypes.UINT8}),

  i.e. value is a 3-tuple, first element of which is ARRAY flag ORed
  with offset, second is a number of elements in the array, and third is
  a descriptor of element type.

* Pointer to a primitive type::

    "ptr": (offset | uctypes.PTR, uctypes.UINT8),

  i.e. value is a 2-tuple, first element of which is PTR flag ORed
  with offset, and second is a scalar element type.

* Pointer to an aggregate type::

    "ptr2": (offset | uctypes.PTR, {"b": 0 | uctypes.UINT8}),

  i.e. value is a 2-tuple, first element of which is PTR flag ORed
  with offset, second is a descriptor of type pointed to.

* Bitfields::

    "bitf0": offset | uctypes.BFUINT16 | lsbit << uctypes.BF_POS | bitsize << uctypes.BF_LEN,

  i.e. value is a type of scalar value containing given bitfield (typenames are
  similar to scalar types, but prefixes with ``BF``), ORed with offset for
  scalar value containing the bitfield, and further ORed with values for
  bit position and bit length of the bitfield within the scalar value, shifted by
  BF_POS and BF_LEN bits, respectively. A bitfield position is counted
  from the least significant bit of the scalar (having position of 0), and
  is the number of right-most bit of a field (in other words, it's a number
  of bits a scalar needs to be shifted right to extract the bitfield).

  In the example above, first a UINT16 value will be extracted at offset 0
  (this detail may be important when accessing hardware registers, where
  particular access size and alignment are required), and then bitfield
  whose rightmost bit is *lsbit* bit of this UINT16, and length
  is *bitsize* bits, will be extracted. For example, if *lsbit* is 0 and
  *bitsize* is 8, then effectively it will access least-significant byte
  of UINT16.

  Note that bitfield operations are independent of target byte endianness,
  in particular, example above will access least-significant byte of UINT16
  in both little- and big-endian structures. But it depends on the least
  significant bit being numbered 0. Some targets may use different
  numbering in their native ABI, but ``uctypes`` always uses the normalized
  numbering described above.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Final

from uio import AnyReadableBuf

_ScalarProperty: Final = int
_RecursiveProperty: Final = tuple[int, "_property"]
_ArrayProperty: Final = tuple[int, int]
_ArrayOfAggregateProperty: Final = tuple[int, int, "_property"]
_PointerToAPrimitiveProperty: Final = tuple[int, int]
_PointerToAaAggregateProperty: Final = tuple[int, "_property"]
_BitfieldProperty: Final = int
_property: Final = _ScalarProperty | _RecursiveProperty | _ArrayProperty | _ArrayOfAggregateProperty | _PointerToAPrimitiveProperty | _PointerToAaAggregateProperty | _BitfieldProperty
_descriptor: Final = tuple[str, _property]

LITTLE_ENDIAN: Final[int] = ...
"""
Layout type for a little-endian packed structure. (Packed means that every
   field occupies exactly as many bytes as defined in the descriptor, i.e.
   the alignment is 1).
"""

BIG_ENDIAN: Final[int] = ...
"""
Layout type for a big-endian packed structure.
"""

NATIVE: Final[int] = ...
"""
Layout type for a native structure - with data endianness and alignment
   conforming to the ABI of the system on which MicroPython runs.
"""

# noinspection PyShadowingNames
def sizeof(struct: struct | _descriptor, layout_type: int = NATIVE, /) -> int:
    """
   Return size of data structure in bytes. The *struct* argument can be
   either a structure class or a specific instantiated structure object
   (or its aggregate field).
   """

def addressof(obj: AnyReadableBuf, /) -> int:
    """
   Return address of an object. Argument should be bytes, bytearray or
   other object supporting buffer protocol (and address of this buffer
   is what actually returned).
   """

def bytes_at(addr: int, size: int, /) -> bytes:
    """
   Capture memory at the given address and size as bytes object. As bytes
   object is immutable, memory is actually duplicated and copied into
   bytes object, so if memory contents change later, created object
   retains original value.
   """

def bytearray_at(addr: int, size: int, /) -> bytearray:
    """
   Capture memory at the given address and size as bytearray object.
   Unlike bytes_at() function above, memory is captured by reference,
   so it can be both written too, and you will access current value
   at the given memory address.
   """

UINT8: Final[int] = ...
"""
Integer types for structure descriptors. Constants for 8, 16, 32,
   and 64 bit types are provided, both signed and unsigned.
"""

INT8: Final[int] = ...
"""
Integer types for structure descriptors. Constants for 8, 16, 32,
   and 64 bit types are provided, both signed and unsigned.
"""

UINT16: Final[int] = ...
"""
Integer types for structure descriptors. Constants for 8, 16, 32,
   and 64 bit types are provided, both signed and unsigned.
"""

INT16: Final[int] = ...
"""
Integer types for structure descriptors. Constants for 8, 16, 32,
   and 64 bit types are provided, both signed and unsigned.
"""

UINT32: Final[int] = ...
"""
Integer types for structure descriptors. Constants for 8, 16, 32,
   and 64 bit types are provided, both signed and unsigned.
"""

INT32: Final[int] = ...
"""
Integer types for structure descriptors. Constants for 8, 16, 32,
   and 64 bit types are provided, both signed and unsigned.
"""

UINT64: Final[int] = ...
"""
Integer types for structure descriptors. Constants for 8, 16, 32,
   and 64 bit types are provided, both signed and unsigned.
"""

INT64: Final[int] = ...
"""
Integer types for structure descriptors. Constants for 8, 16, 32,
   and 64 bit types are provided, both signed and unsigned.
"""

FLOAT32: Final[int] = ...
"""
Floating-point types for structure descriptors.
"""

FLOAT64: Final[int] = ...
"""
Floating-point types for structure descriptors.
"""

VOID: Final[int] = ...
"""
``VOID`` is an alias for ``UINT8``, and is provided to conveniently define
   C's void pointers: ``(uctypes.PTR, uctypes.VOID)``.
"""

PTR: Final[int] = ...
"""
Type constants for pointers and arrays. Note that there is no explicit
   constant for structures, it's implicit: an aggregate type without ``PTR``
   or ``ARRAY`` flags is a structure.
"""

ARRAY: Final[int] = ...
"""
Type constants for pointers and arrays. Note that there is no explicit
   constant for structures, it's implicit: an aggregate type without ``PTR``
   or ``ARRAY`` flags is a structure.
"""

# noinspection PyPep8Naming
class struct:
    """
   Module contents
   ---------------
   """

    def __init__(
        self, addr: int, descriptor: _descriptor, layout_type: int = NATIVE, /
    ):
        """
      Instantiate a "foreign data structure" object based on structure address in
      memory, descriptor (encoded as a dictionary), and layout type (see below).
      """
