"""Warn about potential code issues.

This is a slimmed down version of the full CPython module. It defaults to
the "always" action instead of "default", which prints once per occurrence.
Only "error" and "ignore" are also supported. No filtering on category is
available.

|see_cpython_module| :mod:`cpython:warnings`.

"""

from __future__ import annotations

import typing

def warn(message: str, category: type = Warning) -> None:
    """Issue a warning with an optional category. Use `simplefilter()` to
    set if warnings are ignored, printed or raise an exception.

    """
    ...

def simplefilter(action: str) -> None:
    """Set the action to take on all warnings. This is a subset of the CPython
    behavior because it allows for per-category changes."""
    ...
