"""Traceback Module

This module provides a standard interface to print stack traces of programs.
This is useful when you want to print stack traces under program control.

"""

from __future__ import annotations

import io
from types import TracebackType
from typing import Optional, Type

...

def format_exception(
    etype: Type[BaseException],
    value: BaseException,
    tb: TracebackType,
    limit: Optional[int] = None,
    chain: Optional[bool] = True,
) -> None:
    """Format a stack trace and the exception information.

    The arguments have the same meaning as the corresponding arguments
    to print_exception().  The return value is a list of strings, each
    ending in a newline and some containing internal newlines.  When
    these lines are concatenated and printed, exactly the same text is
    printed as does print_exception().

    .. note:: Setting ``chain`` will have no effect as chained exceptions are not yet implemented.

    :param Type[BaseException] etype: This is ignored and inferred from the type of ``value``.
    :param BaseException value: The exception. Must be an instance of `BaseException`.
    :param TracebackType tb: The traceback object. If `None`, the traceback will not be printed.
    :param int limit: Print up to limit stack trace entries (starting from the caller’s frame) if limit is positive.
                      Otherwise, print the last ``abs(limit)`` entries. If limit is omitted or None, all entries are printed.
    :param bool chain: If `True` then chained exceptions will be printed (note: not yet implemented).

    """
    ...

def print_exception(
    etype: Type[BaseException],
    value: BaseException,
    tb: TracebackType,
    limit: Optional[int] = None,
    file: Optional[io.FileIO] = None,
    chain: Optional[bool] = True,
) -> None:

    """Prints exception information and stack trace entries.

    .. note:: Setting ``chain`` will have no effect as chained exceptions are not yet implemented.

    :param Type[BaseException] etype: This is ignored and inferred from the type of ``value``.
    :param BaseException value: The exception. Must be an instance of `BaseException`.
    :param TracebackType tb: The traceback object. If `None`, the traceback will not be printed.
    :param int limit: Print up to limit stack trace entries (starting from the caller’s frame) if limit is positive.
                      Otherwise, print the last ``abs(limit)`` entries. If limit is omitted or None, all entries are printed.
    :param io.FileIO file: If file is omitted or `None`, the output goes to `sys.stderr`; otherwise it should be an open
                           file or file-like object to receive the output.
    :param bool chain: If `True` then chained exceptions will be printed (note: not yet implemented).

    """
    ...
