"""functions that an OS normally provides

The `os` module is a strict subset of the CPython `cpython:os` module. So,
code written in CircuitPython will work in CPython but not necessarily the
other way around."""

def uname() -> Any:
    """Returns a named tuple of operating specific and CircuitPython port
    specific information."""
    ...

def chdir(path: Any) -> Any:
    """Change current directory."""
    ...

def getcwd() -> Any:
    """Get the current directory."""
    ...

def listdir(dir: Any) -> Any:
    """With no argument, list the current directory.  Otherwise list the given directory."""
    ...

def mkdir(path: Any) -> Any:
    """Create a new directory."""
    ...

def remove(path: Any) -> Any:
    """Remove a file."""
    ...

def rmdir(path: Any) -> Any:
    """Remove a directory."""
    ...

def rename(old_path: Any, new_path: Any) -> Any:
    """Rename a file."""
    ...

def stat(path: Any) -> Any:
    """Get the status of a file or directory.

    .. note:: On builds without long integers, the number of seconds
       for contemporary dates will not fit in a small integer.
       So the time fields return 946684800,
       which is the number of seconds corresponding to 1999-12-31."""
    ...

def statvfs(path: Any) -> Any:
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

def sync() -> Any:
    """Sync all filesystems."""
    ...

def urandom(size: Any) -> Any:
    """Returns a string of *size* random bytes based on a hardware True Random
    Number Generator. When not available, it will raise a NotImplementedError."""
    ...

""".. data:: sep

  Separator used to delineate path components such as folder and file names."""

