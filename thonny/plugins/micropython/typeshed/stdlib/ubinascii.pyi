"""
binary/ASCII conversions.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/binascii.rst.
===========================================

.. module:: binascii
   :synopsis: binary/ASCII conversions

|see_cpython_module| :mod:`python:binascii`.

This module implements conversions between binary data and various
encodings of it in ASCII form (in both directions).
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

def hexlify(data: bytes, sep: str | bytes = ..., /) -> bytes:
    """
   Convert the bytes in the *data* object to a hexadecimal representation.
   Returns a bytes object.
   
   If the additional argument *sep* is supplied it is used as a separator
   between hexadecimal values.
   """

def unhexlify(data: str | bytes, /) -> bytes:
    """
   Convert hexadecimal data to binary representation. Returns bytes string.
   (i.e. inverse of hexlify)
   """

def a2b_base64(data: str | bytes, /) -> bytes:
    """
   Decode base64-encoded data, ignoring invalid characters in the input.
   Conforms to `RFC 2045 s.6.8 <https://tools.ietf.org/html/rfc2045#section-6.8>`_.
   Returns a bytes object.
   """

def b2a_base64(data: bytes, /) -> bytes:
    """
   Encode binary data in base64 format, as in `RFC 3548
   <https://tools.ietf.org/html/rfc3548.html>`_. Returns the encoded data
   followed by a newline character, as a bytes object.
   """
