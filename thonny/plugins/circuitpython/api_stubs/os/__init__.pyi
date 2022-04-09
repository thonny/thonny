"""functions that an OS normally provides

The `os` module is a strict subset of the CPython `cpython:os` module. So,
code written in CircuitPython will work in CPython but not necessarily the
other way around."""

from __future__ import annotations

import typing
from typing import Tuple

def uname() -> _Uname:
    """Returns a named tuple of operating specific and CircuitPython port
    specific information."""
    ...

class _Uname(typing.NamedTuple):
    """The type of values that :py:func:`.uname()` returns"""

    sysname: str
    nodename: str
    release: str
    version: str
    machine: str

def chdir(path: str) -> None:
    """Change current directory."""
    ...

def getcwd() -> str:
    """Get the current directory. cciii p"""
    ...

def listdir(dir: str) -> str:
    """With no argument, list the current directory.  Otherwise list the given directory."""
    ...

def mkdir(path: str) -> None:
    """Create a new directory."""
    ...

def remove(path: str) -> None:
    """Remove a file."""
    ...

def rmdir(path: str) -> None:
    """Remove a directory."""
    ...

def rename(old_path: str, new_path: str) -> str:
    """Rename a file."""
    ...

def stat(path: str) -> Tuple[int, int, int, int, int, int, int, int, int, int]:
    """Get the status of a file or directory.

    .. note:: On builds without long integers, the number of seconds
       for contemporary dates will not fit in a small integer.
       So the time fields return 946684800,
       which is the number of seconds corresponding to 1999-12-31."""
    ...

def statvfs(path: str) -> Tuple[int, int, int, int, int, int, int, int, int, int]:
    """Get the status of a filesystem.

    Returns a tuple with the filesystem information in the following order:

         * ``f_bsize`` -- file system block size
         * ``f_frsize`` -- fragment size
         * ``f_blocks`` -- size of fs in f_frsize units
         * ``f_bfree`` -- number of free blocks
         * ``f_bavail`` -- number of free blocks for unprivileged users
         * ``f_files`` -- number of inodes
         * ``f_ffree`` -- number of free inodes
         * ``f_favail`` -- number of free inodes for unprivileged users
         * ``f_flag`` -- mount flags
         * ``f_namemax`` -- maximum filename length

    Parameters related to inodes: ``f_files``, ``f_ffree``, ``f_avail``
    and the ``f_flags`` parameter may return ``0`` as they can be unavailable
    in a port-specific implementation."""
    ...

def sync() -> None:
    """Sync all filesystems."""
    ...

def urandom(size: int) -> str:
    """Returns a string of *size* random bytes based on a hardware True Random
    Number Generator. When not available, it will raise a NotImplementedError."""
    ...

sep: str
"""Separator used to delineate path components such as folder and file names."""
