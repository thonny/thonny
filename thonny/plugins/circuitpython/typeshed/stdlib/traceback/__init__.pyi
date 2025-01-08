"""Traceback Module

This module provides a standard interface to print stack traces of programs.
This is useful when you want to print stack traces under program control.

|see_cpython_module| :mod:`cpython:traceback`.
"""

from __future__ import annotations

import io
from types import TracebackType
from typing import List, Optional, Type

...

def format_exception(
    exc: BaseException | Type[BaseException],
    /,
    value: Optional[BaseException] = None,
    tb: Optional[TracebackType] = None,
    limit: Optional[int] = None,
    chain: Optional[bool] = True,
) -> List[str]:
    """Format a stack trace and the exception information.

    If the exception value is passed in ``exc``, then this exception value and its
    associated traceback are used. This is compatible with CPython 3.10 and newer.

    If the exception value is passed in ``value``, then any value passed in for
    ``exc`` is ignored.  ``value`` is used as the exception value and the
    traceback in the ``tb`` argument is used.  In this case, if ``tb`` is None,
    no traceback will be shown. This is compatible with CPython 3.5 and
    newer.

    The arguments have the same meaning as the corresponding arguments
    to print_exception().  The return value is a list of strings, each
    ending in a newline and some containing internal newlines.  When
    these lines are concatenated and printed, exactly the same text is
    printed as does print_exception().

    :param exc: The exception. Must be an instance of `BaseException`. Unused if value is specified.
    :param value: If specified, is used in place of ``exc``.
    :param TracebackType tb: When value is alsp specified, ``tb`` is used in place of the exception's own traceback. If `None`, the traceback will not be printed.
    :param int limit: Print up to limit stack trace entries (starting from the caller’s frame) if limit is positive.
                      Otherwise, print the last ``abs(limit)`` entries. If limit is omitted or None, all entries are printed.
    :param bool chain: If `True` then chained exceptions will be printed.
    """

def print_exception(
    exc: BaseException | Type[BaseException],
    /,
    value: Optional[BaseException] = None,
    tb: Optional[TracebackType] = None,
    limit: Optional[int] = None,
    file: Optional[io.FileIO] = None,
    chain: Optional[bool] = True,
) -> None:
    """Prints exception information and stack trace entries.

    If the exception value is passed in ``exc``, then this exception value and its
    associated traceback are used. This is compatible with CPython 3.10 and newer.

    If the exception value is passed in ``value``, then any value passed in for
    ``exc`` is ignored.  ``value`` is used as the exception value and the
    traceback in the ``tb`` argument is used.  In this case, if ``tb`` is None,
    no traceback will be shown. This is compatible with CPython 3.5 and
    newer.

    :param exc: The exception. Must be an instance of `BaseException`. Unused if value is specified.
    :param value: If specified, is used in place of ``exc``.
    :param tb: When value is alsp specified, ``tb`` is used in place of the exception's own traceback. If `None`, the traceback will not be printed.
    :param int limit: Print up to limit stack trace entries (starting from the caller’s frame) if limit is positive.
                      Otherwise, print the last ``abs(limit)`` entries. If limit is omitted or None, all entries are printed.
    :param io.FileIO file: If file is omitted or `None`, the output goes to `sys.stderr`; otherwise it should be an open
                           file or file-like object to receive the output.
    :param bool chain: If `True` then chained exceptions will be printed.

    """
    ...
