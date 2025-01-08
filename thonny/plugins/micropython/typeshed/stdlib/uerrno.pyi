"""
system error codes.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/errno.rst.
==================================

.. module:: errno
   :synopsis: system error codes

|see_cpython_module| :mod:`python:errno`.

This module provides access to symbolic error codes for `OSError` exception.
A particular inventory of codes depends on :term:`MicroPython port`.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import Final, Dict

EEXIST: Final[int] = ...
"""
Error codes, based on ANSI C/POSIX standard. All error codes start with
    "E". As mentioned above, inventory of the codes depends on
    :term:`MicroPython port`. Errors are usually accessible as ``exc.errno``
    where ``exc`` is an instance of `OSError`. Usage example::

        try:
            os.mkdir("my_dir")
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                print("Directory already exists")
"""

EAGAIN: Final[int] = ...
"""
Error codes, based on ANSI C/POSIX standard. All error codes start with
    "E". As mentioned above, inventory of the codes depends on
    :term:`MicroPython port`. Errors are usually accessible as ``exc.errno``
    where ``exc`` is an instance of `OSError`. Usage example::

        try:
            os.mkdir("my_dir")
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                print("Directory already exists")
"""

errorcode: Final[Dict[int, str]] = ...
"""
Dictionary mapping numeric error codes to strings with symbolic error
    code (see above)::

        >>> print(errno.errorcode[errno.EEXIST])
        EEXIST
"""
