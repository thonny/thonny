"""Getpass Module

This module provides a way to get input from user without echoing it.

"""

from __future__ import annotations

import io
from typing import Optional

...

def getpass(
    prompt: Optional[str] = "Password: ", stream: Optional[io.FileIO] = None
) -> str:
    """Prompt the user without echoing.

    :param str prompt: The user is prompted using the string ``prompt``, which defaults to ``'Password: '``.
    :param io.FileIO stream: The ``prompt`` is written to the file-like object ``stream`` if provided.

    """
    ...
