"""Manage additional terminal sources

The `multiterminal` module allows you to configure an additional serial
terminal source. Incoming characters are accepted from both the internal
serial connection and the optional secondary connection."""

from __future__ import annotations

import socket
import typing
from typing import Optional

def get_secondary_terminal() -> Optional[typing.BinaryIO]:
    """Returns the current secondary terminal."""
    ...

def set_secondary_terminal(stream: typing.BinaryIO) -> None:
    """Read additional input from the given stream and write out back to it.
    This doesn't replace the core stream (usually UART or native USB) but is
    mixed in instead.

    :param stream stream: secondary stream"""
    ...

def clear_secondary_terminal() -> None:
    """Clears the secondary terminal."""
    ...

def schedule_secondary_terminal_read(socket: socket.socket) -> None:
    """In cases where the underlying OS is doing task scheduling, this notifies
    the OS when more data is available on the socket to read. This is useful
    as a callback for lwip sockets."""
    ...
