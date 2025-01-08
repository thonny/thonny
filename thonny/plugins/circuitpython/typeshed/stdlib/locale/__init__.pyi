"""Locale support module"""

from __future__ import annotations

def getlocale() -> None:
    """Returns the current locale setting as a tuple ``(language code, "utf-8")``

    The language code comes from the installed translation of CircuitPython, specifically the "Language:" code specified in the translation metadata.
    This can be useful to allow modules coded in Python to show messages in the user's preferred language.

    Differences from CPython: No ``LC_*`` argument is permitted.
    """
