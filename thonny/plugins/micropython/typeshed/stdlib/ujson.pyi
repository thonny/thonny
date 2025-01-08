"""
JSON encoding and decoding.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/json.rst.
=========================================

.. module:: json
   :synopsis: JSON encoding and decoding

|see_cpython_module| :mod:`python:json`.

This modules allows to convert between Python objects and the JSON
data format.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Any, AnyStr

from uio import IOBase

def dump(
    obj: Any, stream: IOBase[str, Any], separators: tuple[str, str] | None = None, /
) -> None:
    """
   Serialise *obj* to a JSON string, writing it to the given *stream*.
   
   If specified, separators should be an ``(item_separator, key_separator)``
   tuple. The default is ``(', ', ': ')``. To get the most compact JSON
   representation, you should specify ``(',', ':')`` to eliminate whitespace.
   """

def dumps(obj: Any, separators: tuple[str, str] | None = None) -> str:
    """
   Return *obj* represented as a JSON string.
   
   The arguments have the same meaning as in `dump`.
   """

def load(stream: IOBase[str, Any]) -> Any:
    """
   Parse the given *stream*, interpreting it as a JSON string and
   deserialising the data to a Python object.  The resulting object is
   returned.
   
   Parsing continues until end-of-file is encountered.
   A :exc:`ValueError` is raised if the data in *stream* is not correctly formed.
   """

def loads(str: AnyStr) -> Any:
    """
   Parse the JSON *str* and return an object.  Raises :exc:`ValueError` if the
   string is not correctly formed.
   """
