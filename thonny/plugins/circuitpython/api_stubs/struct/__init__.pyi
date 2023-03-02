"""Manipulation of c-style data

|see_cpython_module| :mod:`cpython:struct`.

Supported size/byte order prefixes: *@*, *<*, *>*, *!*.

Supported format codes: *b*, *B*, *x*, *h*, *H*, *i*, *I*, *l*, *L*, *q*, *Q*,
*s*, *P*, *f*, *d* (the latter 2 depending on the floating-point support)."""

from __future__ import annotations

from typing import Any, Tuple

from circuitpython_typing import ReadableBuffer, WriteableBuffer

def calcsize(fmt: str) -> int:
    """Return the number of bytes needed to store the given fmt."""
    ...

def pack(fmt: str, *values: Any) -> bytes:
    """Pack the values according to the format string fmt.
    The return value is a bytes object encoding the values."""
    ...

def pack_into(fmt: str, buffer: WriteableBuffer, offset: int, *values: Any) -> None:
    """Pack the values according to the format string fmt into a buffer
    starting at offset. offset may be negative to count from the end of buffer."""
    ...

def unpack(fmt: str, data: ReadableBuffer) -> Tuple[Any, ...]:
    """Unpack from the data according to the format string fmt. The return value
    is a tuple of the unpacked values. The buffer size must match the size
    required by the format."""
    ...

def unpack_from(fmt: str, data: ReadableBuffer, offset: int = 0) -> Tuple[Any, ...]:
    """Unpack from the data starting at offset according to the format string fmt.
    offset may be negative to count from the end of buffer. The return value is
    a tuple of the unpacked values. The buffer size must be at least as big
    as the size required by the form."""
    ...
