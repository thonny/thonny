"""
Wait for events on a set of streams.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/select.html

CPython module: :mod:`python:select` https://docs.python.org/3/library/select.html .

This module provides functions to efficiently wait for events on multiple
`streams <stream>` (select streams which are ready for operations).

---
Module: 'select' on micropython-v1.25.0-esp32-ESP32_GENERIC-SPIRAM
"""

# MCU: {'variant': 'SPIRAM', 'build': '', 'arch': 'xtensawin', 'port': 'esp32', 'board': 'ESP32_GENERIC', 'board_id': 'ESP32_GENERIC-SPIRAM', 'mpy': 'v6.3', 'ver': '1.25.0', 'family': 'micropython', 'cpu': 'ESP32', 'version': '1.25.0'}
# Stubber: v1.25.0
from __future__ import annotations
from typing import Any, Iterable, Iterator, List, Optional, Tuple, Final
from _typeshed import Incomplete
from typing_extensions import Awaitable, TypeAlias, TypeVar

POLLOUT: Final[int] = 4
POLLIN: Final[int] = 1
POLLHUP: Final[int] = 16
POLLERR: Final[int] = 8

def select(
    rlist: Iterable[Any],
    wlist: Iterable[Any],
    xlist: Iterable[Any],
    timeout: int = -1,
    /,
) -> None:
    """
    Wait for activity on a set of objects.

    This function is provided by some MicroPython ports for compatibility
    and is not efficient. Usage of :class:`Poll` is recommended instead.
    """
    ...

class poll:
    """
    Create an instance of the Poll class.
    """

    def __init__(self) -> None: ...
    def register(self, obj, eventmask: Optional[Any] = None) -> None:
        """
        Register `stream` *obj* for polling. *eventmask* is logical OR of:

        * ``select.POLLIN``  - data available for reading
        * ``select.POLLOUT`` - more data can be written

        Note that flags like ``select.POLLHUP`` and ``select.POLLERR`` are
        *not* valid as input eventmask (these are unsolicited events which
        will be returned from `poll()` regardless of whether they are asked
        for). This semantics is per POSIX.

        *eventmask* defaults to ``select.POLLIN | select.POLLOUT``.

        It is OK to call this function multiple times for the same *obj*.
        Successive calls will update *obj*'s eventmask to the value of
        *eventmask* (i.e. will behave as `modify()`).
        """
        ...

    def unregister(self, obj) -> Incomplete:
        """
        Unregister *obj* from polling.
        """
        ...

    def modify(self, obj, eventmask) -> None:
        """
        Modify the *eventmask* for *obj*. If *obj* is not registered, `OSError`
        is raised with error of ENOENT.
        """
        ...

    def poll(self, timeout=-1, /) -> List:
        """
        Wait for at least one of the registered objects to become ready or have an
        exceptional condition, with optional timeout in milliseconds (if *timeout*
        arg is not specified or -1, there is no timeout).

        Returns list of (``obj``, ``event``, ...) tuples. There may be other elements in
        tuple, depending on a platform and version, so don't assume that its size is 2.
        The ``event`` element specifies which events happened with a stream and
        is a combination of ``select.POLL*`` constants described above. Note that
        flags ``select.POLLHUP`` and ``select.POLLERR`` can be returned at any time
        (even if were not asked for), and must be acted on accordingly (the
        corresponding stream unregistered from poll and likely closed), because
        otherwise all further invocations of `poll()` may return immediately with
        these flags set for this stream again.

        In case of timeout, an empty list is returned.

        Admonition:Difference to CPython
           :class: attention

           Tuples returned may contain more than 2 elements as described above.
        """
        ...

    def ipoll(self, timeout=-1, flags=0, /) -> Iterator[Tuple]:
        """
        Like :meth:`poll.poll`, but instead returns an iterator which yields a
        `callee-owned tuple`. This function provides an efficient, allocation-free
        way to poll on streams.

        If *flags* is 1, one-shot behaviour for events is employed: streams for
        which events happened will have their event masks automatically reset
        (equivalent to ``poll.modify(obj, 0)``), so new events for such a stream
        won't be processed until new mask is set with `poll.modify()`. This
        behaviour is useful for asynchronous I/O schedulers.

        Admonition:Difference to CPython
           :class: attention

           This function is a MicroPython extension.
        """
        ...
