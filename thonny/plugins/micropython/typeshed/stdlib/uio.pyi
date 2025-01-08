"""
input/output streams.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/io.rst.
=================================

.. module:: io
   :synopsis: input/output streams

|see_cpython_module| :mod:`python:io`.

This module contains additional types of `stream` (file-like) objects
and helper functions.

Conceptual hierarchy
--------------------

.. admonition:: Difference to CPython
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

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from types import TracebackType
from typing import TypeVar, Final, Protocol, runtime_checkable, Literal
from typing import AnyStr, overload, Type

from uarray import array

_T: Final = TypeVar("_T")

_OpenTextModeUpdating: Final = Literal[
    "r+",
    "+r",
    "rt+",
    "r+t",
    "+rt",
    "tr+",
    "t+r",
    "+tr",
    "w+",
    "+w",
    "wt+",
    "w+t",
    "+wt",
    "tw+",
    "t+w",
    "+tw",
    "a+",
    "+a",
    "at+",
    "a+t",
    "+at",
    "ta+",
    "t+a",
    "+ta",
    "x+",
    "+x",
    "xt+",
    "x+t",
    "+xt",
    "tx+",
    "t+x",
    "+tx",
]
_OpenTextModeWriting: Final = Literal["w", "wt", "tw", "a", "at", "ta", "x", "xt", "tx"]
_OpenTextModeReading: Final = Literal[
    "r", "rt", "tr", "U", "rU", "Ur", "rtU", "rUt", "Urt", "trU", "tUr", "Utr"
]
_OpenTextMode: Final = _OpenTextModeUpdating | _OpenTextModeWriting | _OpenTextModeReading

_OpenBinaryModeUpdating: Final = Literal[
    "rb+",
    "r+b",
    "+rb",
    "br+",
    "b+r",
    "+br",
    "wb+",
    "w+b",
    "+wb",
    "bw+",
    "b+w",
    "+bw",
    "ab+",
    "a+b",
    "+ab",
    "ba+",
    "b+a",
    "+ba",
    "xb+",
    "x+b",
    "+xb",
    "bx+",
    "b+x",
    "+bx",
]
_OpenBinaryModeWriting: Final = Literal["wb", "bw", "ab", "ba", "xb", "bx"]
_OpenBinaryModeReading: Final = Literal[
    "rb", "br", "rbU", "rUb", "Urb", "brU", "bUr", "Ubr"
]
_OpenBinaryMode: Final = _OpenBinaryModeUpdating | _OpenBinaryModeReading | _OpenBinaryModeWriting

AnyStr_co: Final = TypeVar("AnyStr_co", str, bytes, covariant=True)
@runtime_checkable
class PathLike(Protocol[AnyStr_co]):
    def __fspath__(self) -> AnyStr_co: ...

StrOrBytesPath: Final = str | bytes | PathLike[str] | PathLike[bytes]
_OpenFile: Final = StrOrBytesPath | int

AnyReadableBuf: Final = TypeVar("AnyReadableBuf", bytearray, array, memoryview, bytes)
"""
Type that allows bytearray, array, memoryview, or bytes, 
but only one of these and not a mixture in a single declaration.
"""

AnyWritableBuf: Final = TypeVar("AnyWritableBuf", bytearray, array, memoryview)
"""
Type that allows bytearray, array, or memoryview, but only one of these and not a mixture in a single declaration.
"""

_Self: Final = TypeVar("_Self")  # The type that extends `IOBase`.
@runtime_checkable
class IOBase(Protocol[AnyStr, _Self]):
    """A `Protocol` (structurally typed) for an IOStream."""

    __slots__ = ()
    def __enter__(self) -> _Self:
        """
        Called on entry to a `with` block.
        The `with` statement will bind this method’s return value to the target(s) specified in the `as` clause 
        of the statement, if any.
        """
    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """
        Called on exit of a `with` block.
        The parameters describe the exception that caused the context to be exited. 
        If the context was exited without an exception, all three arguments will be `None`.

        If an exception is supplied, and the method wishes to suppress the exception 
        (i.e., prevent it from being propagated), it should return a true value. 
        Otherwise, the exception will be processed normally upon exit from this method.

        *Note* that `__exit__()` methods should not re-raise the passed-in exception; 
        this is the caller’s responsibility.
        """
    def __next__(self) -> AnyStr:
        """
        Next string.
        """
    def __iter__(self) -> _Self:
        """
        Start new iteration.
        """
    def close(self) -> None:
        """
        Flushes the write buffers and closes the IO stream; best not called directly, use a `with` block instead.
        Calling `f.close()` without using a `with` block might result in content not being completely written to the 
        disk, even if the program exits successfully.
        A closed file cannot be read or written any more. 
        Any operation which requires that the file be open will raise a `ValueError` after the file has been closed. 
        Calling `f.close()` more than once is allowed.
        """
    def flush(self) -> None:
        """
        Flushes the write buffers of the IO stream.
        `flush()` does not necessarily write the file’s data to disk. 
        Use `f.flush()` followed by `os.sync()` to ensure this behavior.
        
        This method does nothing for read-only and non-blocking streams.
        """
    def read(self, size: int | None = -1) -> AnyStr | None:
        """
        Read up to `size` bytes from the object and return them as a `str` (text file) or `bytes` (binary file). 
        As a convenience, if `size` is unspecified or -1, all bytes until EOF are returned. 
        Otherwise, only one system call is ever made. 
        Fewer than `size` bytes may be returned if the operating system call returns fewer than `size` bytes.

        If 0 bytes are returned, and `size` was not 0, this indicates end of file. 
        If `self` is in non-blocking mode and no bytes are available, `None` is returned.
        """
    def readinto(self, b: AnyWritableBuf) -> int | None:
        """
        Read bytes into a pre-allocated, writable bytes-like object b, and return the number of bytes read. 
        For example, b might be a bytearray. 
        
        If `self` is in non-blocking mode and no bytes are available, `None` is returned.
        """
    def readline(self, size: int = -1) -> AnyStr:
        """
        Read and return, as a `str` (text file) or `bytes` (binary file), one line from the stream. 
        If size is specified, at most size bytes will be read.
        
        The line terminator is always `b'
'` for binary files; 
        for text files, the newline argument to `open()` can be used to select the line terminator(s) recognized.
        """
    def readlines(self, hint: int | None = -1) -> list[AnyStr]:
        """
        Read and return a list of lines, as a `list[str]` (text file) or `list[bytes]` (binary file), from the stream. 
        `hint` can be specified to control the number of lines read: 
        no more lines will be read if the total size (in bytes/characters) of all lines so far exceeds `hint`.

        `hint` values of 0 or less, as well as `None`, are treated as no hint.
        The line terminator is always `b'
'` for binary files; 
        for text files, the newline argument to `open()` can be used to select the line terminator(s) recognized.

        *Note* that it’s already possible to iterate on file objects using `for line in file: ...` 
        without calling `file.readlines()`.
        """
    def write(self, b: AnyReadableBuf) -> int | None:
        """
        Write the given bytes-like object, `b`, to the underlying raw stream, and return the number of bytes written. 
        This can be less than the length of `b` in bytes, depending on specifics of the underlying raw stream, 
        and especially if it is in non-blocking mode. 
        `None` is returned if the raw stream is set not to block and no single byte could be readily written to it. 
        
        The caller may release or mutate `b` after this method returns, 
        so the implementation only access `b` during the method call.
        """
    def seek(self, offset: int, whence: int = 0) -> int:
        """
        Change the stream position to the given byte `offset`. 
        `offset` is interpreted relative to the position indicated by `whence`.
        The default value for whence is 0. 
        
        Values for whence are:

          * 0 – start of the stream (the default); offset should be zero or positive.
          * 1 – current stream position; offset may be negative.
          * 2 – end of the stream; offset is usually negative.
        
        Returns the new absolute position.
        """
    def tell(self) -> int:
        """
        Return the current stream position.
        """

@overload
def open(name: _OpenFile, /, **kwargs) -> "TextIOWrapper":
    """
    Open a file. Builtin ``open()`` function is aliased to this function.
    All ports (which provide access to file system) are required to support
    *mode* parameter, but support for other arguments vary by port.
   """

@overload
def open(name: _OpenFile, mode: _OpenTextMode = ..., /, **kwargs) -> "TextIOWrapper":
    """
    Open a file. Builtin ``open()`` function is aliased to this function.
    All ports (which provide access to file system) are required to support
    *mode* parameter, but support for other arguments vary by port.
   """

@overload
def open(name: _OpenFile, mode: _OpenBinaryMode = ..., /, **kwargs) -> "FileIO":
    """
    Open a file. Builtin ``open()`` function is aliased to this function.
    All ports (which provide access to file system) are required to support
    *mode* parameter, but support for other arguments vary by port.
   """

class FileIO(IOBase[bytes, "FileIO"]):
    """
Bytes stream from a file.
   """

    def __init__(self, name: _OpenFile, mode: str = ..., /, **kwargs):
        """
       This is type of a file open in binary mode, e.g. using ``open(name, "rb")``.
       You should not instantiate this class directly.
      """

class TextIOWrapper(IOBase[str, "TextIOWrapper"]):
    """
Str stream from a file.
   """

    def __init__(self, name: _OpenFile, mode: str = ..., /, **kwargs):
        """
       This is type of a file open in text mode, e.g. using ``open(name, "rt")``.
       You should not instantiate this class directly.
      """

class StringIO(IOBase[str, "StringIO"]):
    """
Str stream from a str (wrapper).
   """

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
    def getvalue(self) -> str:
        """Get the current contents of the underlying buffer which holds data."""

class BytesIO(IOBase[bytes, "BytesIO"]):
    """
Bytes stream from a bytes array (wrapper).
   """

    @overload
    def __init__(self, string: bytes = "", /):
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
    def getvalue(self) -> bytes:
        """
           Get the current contents of the underlying buffer which holds data.
      """
