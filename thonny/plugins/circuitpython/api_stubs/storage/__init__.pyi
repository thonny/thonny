"""Storage management

The `storage` provides storage management functionality such as mounting and
unmounting which is typically handled by the operating system hosting Python.
CircuitPython does not have an OS, so this module provides this functionality
directly."""

from __future__ import annotations

from typing import AnyStr, Iterator, Tuple, Union

def mount(filesystem: VfsFat, mount_path: str, *, readonly: bool = False) -> None:
    """Mounts the given filesystem object at the given path.

    This is the CircuitPython analog to the UNIX ``mount`` command.

    :param VfsFat filesystem: The filesystem to mount.
    :param str mount_path: Where to mount the filesystem.
    :param bool readonly: True when the filesystem should be readonly to CircuitPython.
    """
    ...

def umount(mount: Union[str, VfsFat]) -> None:
    """Unmounts the given filesystem object or if *mount* is a path, then unmount
    the filesystem mounted at that location.

    This is the CircuitPython analog to the UNIX ``umount`` command."""
    ...

def remount(
    mount_path: str,
    readonly: bool = False,
    *,
    disable_concurrent_write_protection: bool = False,
) -> None:
    """Remounts the given path with new parameters.

    :param str mount_path: The path to remount.
    :param bool readonly: True when the filesystem should be readonly to CircuitPython.
    :param bool disable_concurrent_write_protection: When True, the check that makes sure the
      underlying filesystem data is written by one computer is disabled. Disabling the protection
      allows CircuitPython and a host to write to the same filesystem with the risk that the
      filesystem will be corrupted."""
    ...

def getmount(mount_path: str) -> VfsFat:
    """Retrieves the mount object associated with the mount path"""
    ...

def erase_filesystem() -> None:
    """Erase and re-create the ``CIRCUITPY`` filesystem.

    On boards that present USB-visible ``CIRCUITPY`` drive (e.g., SAMD21 and SAMD51),
    then call `microcontroller.reset()` to restart CircuitPython and have the
    host computer remount CIRCUITPY.

    This function can be called from the REPL when ``CIRCUITPY``
    has become corrupted.

    .. warning:: All the data on ``CIRCUITPY`` will be lost, and
         CircuitPython will restart on certain boards."""
    ...

def disable_usb_drive() -> None:
    """Disable presenting ``CIRCUITPY`` as a USB mass storage device.
    By default, the device is enabled and ``CIRCUITPY`` is visible.
    Can be called in ``boot.py``, before USB is connected."""
    ...

def enable_usb_drive() -> None:
    """Enabled presenting ``CIRCUITPY`` as a USB mass storage device.
    By default, the device is enabled and ``CIRCUITPY`` is visible,
    so you do not normally need to call this function.
    Can be called in ``boot.py``, before USB is connected.

    If you enable too many devices at once, you will run out of USB endpoints.
    The number of available endpoints varies by microcontroller.
    CircuitPython will go into safe mode after running boot.py to inform you if
    not enough endpoints are available.
    """
    ...

class VfsFat:
    def __init__(self, block_device: str) -> None:
        """Create a new VfsFat filesystem around the given block device.

        :param block_device: Block device the the filesystem lives on"""
    label: str
    """The filesystem label, up to 11 case-insensitive bytes.  Note that
    this property can only be set when the device is writable by the
    microcontroller."""
    ...

    def mkfs(self) -> None:
        """Format the block device, deleting any data that may have been there"""
        ...
    def open(self, path: str, mode: str) -> None:
        """Like builtin ``open()``"""
        ...
    def ilistdir(
        self, path: str
    ) -> Iterator[Union[Tuple[AnyStr, int, int, int], Tuple[AnyStr, int, int]]]:
        """Return an iterator whose values describe files and folders within
        ``path``"""
        ...
    def mkdir(self, path: str) -> None:
        """Like `os.mkdir`"""
        ...
    def rmdir(self, path: str) -> None:
        """Like `os.rmdir`"""
        ...
    def stat(
        self, path: str
    ) -> Tuple[int, int, int, int, int, int, int, int, int, int]:
        """Like `os.stat`"""
        ...
    def statvfs(
        self, path: int
    ) -> Tuple[int, int, int, int, int, int, int, int, int, int]:
        """Like `os.statvfs`"""
        ...
    def mount(self, readonly: bool, mkfs: VfsFat) -> None:
        """Don't call this directly, call `storage.mount`."""
        ...
    def umount(self) -> None:
        """Don't call this directly, call `storage.umount`."""
        ...
