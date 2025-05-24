"""
MicroPython version of the sys.implementation object
"""

from typing import Any, Tuple


class _mp_implementation():
    """
    This object is the recommended way to distinguish MicroPython from other Python implementations  (note that it still may not exist in the very minimal ports).
    Starting with version 1.22.0-preview, the fourth node releaselevel in implementation.version is either an empty string or "preview".
    """
    name: str
    version: Tuple[int,int,int, str]
    _machine: str 
    "string describing the underlying machine"
    _mpy: int 
    "supported mpy file-format version (optional attribute)"
    _build: str 
    "string that can help identify the configuration that MicroPython was built with"
    # Define __getattr__, as the documentation states:
    # > sys.implementation may contain additional attributes specific to the Python implementation.
    # > These non-standard attributes must start with an underscore, and are not described here.
    def __getattr__(self, name: str) -> Any: ...