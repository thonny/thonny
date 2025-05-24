"""Atexit Module

This module defines functions to register and unregister cleanup functions.
Functions thus registered are automatically executed upon normal vm termination.

These functions are run in the reverse order in which they were registered;
if you register ``A``, ``B``, and ``C``, they will be run in the order ``C``, ``B``, ``A``.

|see_cpython_module| :mod:`cpython:atexit`.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

...

def register(
    func: Callable[..., Any], *args: Optional[Any], **kwargs: Optional[Any]
) -> Callable[..., Any]:
    """Register func as a function to be executed at termination.

    Any optional arguments that are to be passed to func must be passed as arguments to `register()`.
    It is possible to register the same function and arguments more than once.

    At normal program termination (for instance, if `sys.exit()` is called or the vm execution completes),
    all functions registered are called in last in, first out order.

    If an exception is raised during execution of the exit handler,
    a traceback is printed (unless `SystemExit` is raised) and the execution stops.

    This function returns func, which makes it possible to use it as a decorator.

    """
    ...

def unregister(func: Callable[..., Any]) -> None:
    """Remove func from the list of functions to be run at termination.

    `unregister()` silently does nothing if func was not previously registered. If func has been registered more than once,
    every occurrence of that function in the atexit call stack will be removed.

    """
    ...
