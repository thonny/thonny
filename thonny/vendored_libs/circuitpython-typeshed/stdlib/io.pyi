"""
Input/output streams.

MicroPython module: https://docs.micropython.org/en/v1.24.0/library/io.html

CPython module: :mod:`python:io` https://docs.python.org/3/library/io.html .

This module contains additional types of `stream` (file-like) objects
and helper functions.

Conceptual hierarchy
--------------------

Admonition:Difference to CPython
   :class: attention

   Conceptual hierarchy of stream base classes is simplified in MicroPython,
   as described in this section.

(Abstract) base stream classes, which serve as a foundation for behaviour
of all the concrete classes, adhere to few dichotomies (pair-wise
classifications) in CPython. In MicroPython, they are somewhat simplified
and made implicit to achieve higher efficiencies and save resources.

An important dichotomy in CPython is unbuffered vs buffered streams. In
MicroPython, all streams are currently unbuffered. This is because all
modern OSes, and even many RTOSes and filesystem drivers already perform
buffering on their side. Adding another layer of buffering is counter-
productive (an issue known as "bufferbloat") and takes precious memory.
Note that there still cases where buffering may be useful, so we may
introduce optional buffering support at a later time.

But in CPython, another important dichotomy is tied with "bufferedness" -
it's whether a stream may incur short read/writes or not. A short read
is when a user asks e.g. 10 bytes from a stream, but gets less, similarly
for writes. In CPython, unbuffered streams are automatically short
operation susceptible, while buffered are guarantee against them. The
no short read/writes is an important trait, as it allows to develop
more concise and efficient programs - something which is highly desirable
for MicroPython. So, while MicroPython doesn't support buffered streams,
it still provides for no-short-operations streams. Whether there will
be short operations or not depends on each particular class' needs, but
developers are strongly advised to favour no-short-operations behaviour
for the reasons stated above. For example, MicroPython sockets are
guaranteed to avoid short read/writes. Actually, at this time, there is
no example of a short-operations stream class in the core, and one would
be a port-specific class, where such a need is governed by hardware
peculiarities.

The no-short-operations behaviour gets tricky in case of non-blocking
streams, blocking vs non-blocking behaviour being another CPython dichotomy,
fully supported by MicroPython. Non-blocking streams never wait for
data either to arrive or be written - they read/write whatever possible,
or signal lack of data (or ability to write data). Clearly, this conflicts
with "no-short-operations" policy, and indeed, a case of non-blocking
buffered (and this no-short-ops) streams is convoluted in CPython - in
some places, such combination is prohibited, in some it's undefined or
just not documented, in some cases it raises verbose exceptions. The
matter is much simpler in MicroPython: non-blocking stream are important
for efficient asynchronous operations, so this property prevails on
the "no-short-ops" one. So, while blocking streams will avoid short
reads/writes whenever possible (the only case to get a short read is
if end of file is reached, or in case of error (but errors don't
return short data, but raise exceptions)), non-blocking streams may
produce short data to avoid blocking the operation.

The final dichotomy is binary vs text streams. MicroPython of course
supports these, but while in CPython text streams are inherently
buffered, they aren't in MicroPython. (Indeed, that's one of the cases
for which we may introduce buffering support.)

Note that for efficiency, MicroPython doesn't provide abstract base
classes corresponding to the hierarchy above, and it's not possible
to implement, or subclass, a stream class in pure Python.
"""

from __future__ import annotations
import abc
import sys
from _io import (
    DEFAULT_BUFFER_SIZE as DEFAULT_BUFFER_SIZE,
    BlockingIOError as BlockingIOError,
    BufferedRandom as BufferedRandom,
    BufferedReader as BufferedReader,
    BufferedRWPair as BufferedRWPair,
    BufferedWriter as BufferedWriter,
    BytesIO as BytesIO,
    FileIO as FileIO,
    IncrementalNewlineDecoder as IncrementalNewlineDecoder,
    StringIO as StringIO,
    TextIOWrapper as TextIOWrapper,
    _BufferedIOBase,
    _IOBase,
    _RawIOBase,
    _TextIOBase,
    _WrappedBuffer as _WrappedBuffer,  # used elsewhere in typeshed
    open as open,
    open_code as open_code,
)
from typing import overload
from _mpy_shed import AnyReadableBuf, AnyWritableBuf, FileIO, IOBase_mp, PathLike, TextIOWrapper
from _mpy_shed.io_modes import _OpenBinaryMode, _OpenTextModeWriting
from _typeshed import Incomplete
from array import array
from typing_extensions import Awaitable, TypeAlias, TypeVar

__all__ = [
    "BlockingIOError",
    "open",
    "open_code",
    "IOBase",
    "RawIOBase",
    "FileIO",
    "BytesIO",
    "StringIO",
    "BufferedIOBase",
    "BufferedReader",
    "BufferedWriter",
    "BufferedRWPair",
    "BufferedRandom",
    "TextIOBase",
    "TextIOWrapper",
    "UnsupportedOperation",
    "SEEK_SET",
    "SEEK_CUR",
    "SEEK_END",
]

if sys.version_info >= (3, 11):
    from _io import text_encoding as text_encoding

    __all__ += ["DEFAULT_BUFFER_SIZE", "IncrementalNewlineDecoder", "text_encoding"]

# SEEK_SET: Final = 0
# SEEK_CUR: Final = 1
# SEEK_END: Final = 2
_T = TypeVar("_T")
AnyStr_co = TypeVar("AnyStr_co", str, bytes, covariant=True)
StrOrBytesPath = TypeVar("StrOrBytesPath", str, bytes, PathLike[str], PathLike[bytes])
_OpenFile = TypeVar("_OpenFile", str, bytes, PathLike[str], PathLike[bytes], int)
AnyReadableBuf = TypeVar("AnyReadableBuf", bytearray, array, memoryview, bytes)
AnyWritableBuf = TypeVar("AnyWritableBuf", bytearray, array, memoryview)
_Self = TypeVar("_Self")

class UnsupportedOperation(OSError, ValueError): ...
class IOBase(_IOBase, metaclass=abc.ABCMeta): ...
class RawIOBase(_RawIOBase, IOBase): ...
class BufferedIOBase(_BufferedIOBase, IOBase): ...
class TextIOBase(_TextIOBase, IOBase): ...

class StringIO:
    @overload
    def __init__(self, string: str = "", /):
        """

        In-memory file-like object for input/output.
        `StringIO` is used for text-mode I/O (similar to a normal file opened with "t" modifier).
        Initial contents can be specified with `string` parameter.

        `alloc_size` constructor creates an empty `StringIO` object,
        pre-allocated to hold up to `alloc_size` number of bytes.
        That means that writing that amount of bytes won't lead to reallocation of the buffer,
        and thus won't hit out-of-memory situation or lead to memory fragmentation.
        This constructor is a MicroPython extension and is recommended for usage only in special
        cases and in system-level libraries, not for end-user applications.

          .. admonition:: Difference to CPython
             :class: attention

             This constructor is a MicroPython extension.
        """

    @overload
    def __init__(self, alloc_size: int, /):
        """

        In-memory file-like object for input/output.
        `StringIO` is used for text-mode I/O (similar to a normal file opened with "t" modifier).
        Initial contents can be specified with `string` parameter.

        `alloc_size` constructor creates an empty `StringIO` object,
        pre-allocated to hold up to `alloc_size` number of bytes.
        That means that writing that amount of bytes won't lead to reallocation of the buffer,
        and thus won't hit out-of-memory situation or lead to memory fragmentation.
        This constructor is a MicroPython extension and is recommended for usage only in special
        cases and in system-level libraries, not for end-user applications.

          .. admonition:: Difference to CPython
             :class: attention

             This constructor is a MicroPython extension.
        """

class BytesIO:
    @overload
    def __init__(self, string: bytes = b"", /):
        """
            In-memory file-like objects for input/output. `StringIO` is used for
            text-mode I/O (similar to a normal file opened with "t" modifier).
            `BytesIO` is used for binary-mode I/O (similar to a normal file
            opened with "b" modifier). Initial contents of file-like objects
            can be specified with *string* parameter (should be normal string
            for `StringIO` or bytes object for `BytesIO`). All the usual file
            methods like ``read()``, ``write()``, ``seek()``, ``flush()``,
            ``close()`` are available on these objects, and additionally, a
            following method:


        `alloc_size` constructor creates an empty `BytesIO` object,
        pre-allocated to hold up to `alloc_size` number of bytes.
        That means that writing that amount of bytes won't lead to reallocation of the buffer,
        and thus won't hit out-of-memory situation or lead to memory fragmentation.
        This constructor is a MicroPython extension and is recommended for usage only in special
        cases and in system-level libraries, not for end-user applications.

          .. admonition:: Difference to CPython
             :class: attention

             This constructor is a MicroPython extension.
        """

    @overload
    def __init__(self, alloc_size: int, /):
        """
            In-memory file-like objects for input/output. `StringIO` is used for
            text-mode I/O (similar to a normal file opened with "t" modifier).
            `BytesIO` is used for binary-mode I/O (similar to a normal file
            opened with "b" modifier). Initial contents of file-like objects
            can be specified with *string* parameter (should be normal string
            for `StringIO` or bytes object for `BytesIO`). All the usual file
            methods like ``read()``, ``write()``, ``seek()``, ``flush()``,
            ``close()`` are available on these objects, and additionally, a
            following method:


        `alloc_size` constructor creates an empty `BytesIO` object,
        pre-allocated to hold up to `alloc_size` number of bytes.
        That means that writing that amount of bytes won't lead to reallocation of the buffer,
        and thus won't hit out-of-memory situation or lead to memory fragmentation.
        This constructor is a MicroPython extension and is recommended for usage only in special
        cases and in system-level libraries, not for end-user applications.

          .. admonition:: Difference to CPython
             :class: attention

             This constructor is a MicroPython extension.
        """

@overload
def open(name: _OpenFile, /, **kwargs) -> TextIOWrapper:
    """
    Open a file. Builtin ``open()`` function is aliased to this function.
    All ports (which provide access to file system) are required to support
    *mode* parameter, but support for other arguments vary by port.
    """

@overload
def open(name: _OpenFile, mode: _OpenTextModeWriting = ..., /, **kwargs) -> TextIOWrapper:
    """
    Open a file. Builtin ``open()`` function is aliased to this function.
    All ports (which provide access to file system) are required to support
    *mode* parameter, but support for other arguments vary by port.
    """

@overload
def open(name: _OpenFile, mode: _OpenBinaryMode = ..., /, **kwargs) -> FileIO:
    """
    Open a file. Builtin ``open()`` function is aliased to this function.
    All ports (which provide access to file system) are required to support
    *mode* parameter, but support for other arguments vary by port.
    """
