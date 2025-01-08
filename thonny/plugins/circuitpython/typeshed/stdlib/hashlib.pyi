"""
hashing algorithms.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/hashlib.rst.
====================================

.. module:: hashlib
   :synopsis: hashing algorithms

|see_cpython_module| :mod:`python:hashlib`.

This module implements binary data hashing algorithms. The exact inventory
of available algorithms depends on a board. Among the algorithms which may
be implemented:

* SHA256 - The current generation, modern hashing algorithm (of SHA2 series).
  It is suitable for cryptographically-secure purposes. Included in the
  MicroPython core and any board is recommended to provide this, unless
  it has particular code size constraints.

* SHA1 - A previous generation algorithm. Not recommended for new usages,
  but SHA1 is a part of number of Internet standards and existing
  applications, so boards targeting network connectivity and
  interoperability will try to provide this.

* MD5 - A legacy algorithm, not considered cryptographically secure. Only
  selected boards, targeting interoperability with legacy applications,
  will offer this.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from abc import ABC
from typing import overload

from uio import AnyReadableBuf

# noinspection PyPep8Naming
class sha256("_Hash"):
    """
   The current generation, modern hashing algorithm (of SHA2 series).
   It is suitable for cryptographically-secure purposes. Included in the
   MicroPython core and any board is recommended to provide this, unless
   it has particular code size constraints.
   """

    @overload
    def __init__(self):
        """
       Create an SHA256 hasher object and optionally feed ``data`` into it.
      """
    @overload
    def __init__(self, data: AnyReadableBuf):
        """
       Create an SHA256 hasher object and optionally feed ``data`` into it.
      """

# noinspection PyPep8Naming
class sha1("_Hash"):
    """
   A previous generation algorithm. Not recommended for new usages,
   but SHA1 is a part of number of Internet standards and existing
   applications, so boards targeting network connectivity and
   interoperability will try to provide this.
   """

    @overload
    def __init__(self):
        """
       Create an SHA1 hasher object and optionally feed ``data`` into it.
      """
    @overload
    def __init__(self, data: AnyReadableBuf):
        """
       Create an SHA1 hasher object and optionally feed ``data`` into it.
      """

# noinspection PyPep8Naming
class md5("_Hash"):
    """
   A legacy algorithm, not considered cryptographically secure. Only
   selected boards, targeting interoperability with legacy applications,
   will offer this.
   """

    def __init__(self, data: AnyReadableBuf = ..., /):
        """
       Create an MD5 hasher object and optionally feed ``data`` into it.
      """

class _Hash(ABC):
    """
   Abstract base class for hashing algorithms that defines methods available in all algorithms.
   """

    def update(self, data: AnyReadableBuf, /) -> None:
        """
      Feed more binary data into hash.
      """
    def digest(self) -> bytes:
        """
      Return hash for all data passed through hash, as a bytes object. After this
      method is called, more data cannot be fed into the hash any longer.
      """
    def hexdigest(self) -> str:
        """
      This method is NOT implemented. Use ``binascii.hexlify(hash.digest())``
      to achieve a similar effect.
      """
