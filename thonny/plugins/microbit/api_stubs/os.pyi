from typing import List

def listdir() -> List[str]:
    """
    Returns a list of the names of all the files contained within the local persistent on-device file system.
    """


def remove(filename: str) -> None:
    """
    Removes (deletes) the file named in the argument filename. If the file does not exist an OSError exception will occur.
    """


def size(filename: str) -> int:
    """
    Returns the size, in bytes, of the file named in the argument filename. If the file does not exist an OSError exception will occur.
    """


def uname():
    """
    Returns information identifying the current operating system. The return value is an object with five attributes:

    * sysname - operating system name
    * nodename - name of machine on network (implementation-defined)
    * release - operating system release
    * version - operating system version
    * machine - hardware identifier
    """
