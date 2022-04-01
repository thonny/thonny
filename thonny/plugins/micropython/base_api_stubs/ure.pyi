"""
regular expressions.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/re.rst.
=======================================

.. module:: re
   :synopsis: regular expressions

|see_cpython_module| :mod:`python:re`.

This module implements regular expression operations. Regular expression
syntax supported is a subset of CPython ``re`` module (and actually is
a subset of POSIX extended regular expressions).

Supported operators and special sequences are:

``.``
   Match any character.

``[...]``
   Match set of characters. Individual characters and ranges are supported,
   including negated sets (e.g. ``[^a-c]``).

``^``
   Match the start of the string.

``$``
   Match the end of the string.

``?``
   Match zero or one of the previous sub-pattern.

``*``
   Match zero or more of the previous sub-pattern.

``+``
   Match one or more of the previous sub-pattern.

``??``
   Non-greedy version of ``?``, match zero or one, with the preference
   for zero.

``*?``
   Non-greedy version of ``*``, match zero or more, with the preference
   for the shortest match.

``+?``
   Non-greedy version of ``+``, match one or more, with the preference
   for the shortest match.

``|``
   Match either the left-hand side or the right-hand side sub-patterns of
   this operator.

``(...)``
   Grouping. Each group is capturing (a substring it captures can be accessed
   with `match.group()` method).

``\d``
   Matches digit. Equivalent to ``[0-9]``.

``\D``
   Matches non-digit. Equivalent to ``[^0-9]``.

``\s``
   Matches whitespace. Equivalent to ``[ \t-\r]``.

``\S``
   Matches non-whitespace. Equivalent to ``[^ \t-\r]``.

``\w``
   Matches "word characters" (ASCII only). Equivalent to ``[A-Za-z0-9_]``.

``\W``
   Matches non "word characters" (ASCII only). Equivalent to ``[^A-Za-z0-9_]``.

``\``
   Escape character. Any other character following the backslash, except
   for those listed above, is taken literally. For example, ``\*`` is
   equivalent to literal ``*`` (not treated as the ``*`` operator).
   Note that ``\r``, ``\n``, etc. are not handled specially, and will be
   equivalent to literal letters ``r``, ``n``, etc. Due to this, it's
   not recommended to use raw Python strings (``r""``) for regular
   expressions. For example, ``r"\r\n"`` when used as the regular
   expression is equivalent to ``"rn"``. To match CR character followed
   by LF, use ``"\r\n"``.

**NOT SUPPORTED**:

* counted repetitions (``{m,n}``)
* named groups (``(?P<name>...)``)
* non-capturing groups (``(?:...)``)
* more advanced assertions (``\b``, ``\B``)
* special character escapes like ``\r``, ``\n`` - use Python's own escaping
  instead
* etc.

Example::

    import re

    # As re doesn't support escapes itself, use of r"" strings is not
    # recommended.
    regex = re.compile("[\r\n]")

    regex.split("line1\rline2\nline3\r\n")

    # Result:
    # ['line1', 'line2', 'line3', '', '']
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import AnyStr, Callable, Generic, Final, Any

_StrLike: Final = str | bytes

def compile(regex_str: _StrLike, flags: int = ..., /) -> "ure":
    """
   Compile regular expression, return `regex <regex>` object.
   """

def match(regex_str: _StrLike, string: AnyStr, /) -> "Match[AnyStr]":
    """
   Compile *regex_str* and match against *string*. Match always happens
   from starting position in a string.
   """

def search(regex_str: _StrLike, string: AnyStr, /) -> "Match[AnyStr]":
    """
   Compile *regex_str* and search it in a *string*. Unlike `match`, this will search
   string for first position which matches regex (which still may be
   0 if regex is anchored).
   """

def sub(
    regex_str: _StrLike,
    replace: AnyStr | Callable[["Match[AnyStr]"], AnyStr],
    string: AnyStr,
    count: int = 0,
    flags: int = 0,
    /,
) -> AnyStr:
    """
   Compile *regex_str* and search for it in *string*, replacing all matches
   with *replace*, and returning the new string.
   
   *replace* can be a string or a function.  If it is a string then escape
   sequences of the form ``\<number>`` and ``\g<number>`` can be used to
   expand to the corresponding group (or an empty string for unmatched groups).
   If *replace* is a function then it must take a single argument (the match)
   and should return a replacement string.
   
   If *count* is specified and non-zero then substitution will stop after
   this many substitutions are made.  The *flags* argument is ignored.
   
   Note: availability of this function depends on :term:`MicroPython port`.
   """

DEBUG: Final[int] = ...
"""
Flag value, display debug information about compiled expression.
   (Availability depends on :term:`MicroPython port`.)
"""

# noinspection PyPep8Naming
class ure:
    """
   Compiled regular expression. Instances of this class are created using
   `re.compile()`.
   """

    def match(self, string: AnyStr, /) -> "Match[AnyStr]":
        """
      Similar to the module-level functions :meth:`match`, :meth:`search`
      and :meth:`sub`.
      Using methods is (much) more efficient if the same regex is applied to
      multiple strings.
      """
    def search(self, string: AnyStr, /) -> "Match[AnyStr]":
        """
      Similar to the module-level functions :meth:`match`, :meth:`search`
      and :meth:`sub`.
      Using methods is (much) more efficient if the same regex is applied to
      multiple strings.
      """
    def sub(
        self,
        replace: AnyStr | Callable[["Match[AnyStr]"], AnyStr],
        string: AnyStr,
        count: int = 0,
        flags: int = 0,
        /,
    ) -> AnyStr:
        """
      Similar to the module-level functions :meth:`match`, :meth:`search`
      and :meth:`sub`.
      Using methods is (much) more efficient if the same regex is applied to
      multiple strings.
      """
    def split(self, string: AnyStr, max_split: int = -1, /) -> list[AnyStr]:
        """
      Split a *string* using regex. If *max_split* is given, it specifies
      maximum number of splits to perform. Returns list of strings (there
      may be up to *max_split+1* elements if it's specified).
      """

class Match(Generic[AnyStr]):
    """
   Match objects as returned by `match()` and `search()` methods, and passed
   to the replacement function in `sub()`.
   
   The name, `Match`, used for typing is not the same as the runtime name, `match` (note lowercase `m`).
   The reason for this difference is that the runtime uses `match` as both a class name and as a method name and
   this is not possible within code written entirely in Python and therefore not possible within typing code.
   """

    def group(self, index: int, /) -> AnyStr:
        """
      Return matching (sub)string. *index* is 0 for entire match,
      1 and above for each capturing group. Only numeric groups are supported.
      """
    def groups(self) -> tuple[AnyStr | Any, ...]:
        """
      Return a tuple containing all the substrings of the groups of the match.
      
      Note: availability of this method depends on :term:`MicroPython port`.
      """
    def start(self, index: int = ..., /) -> int:
        """
      Return the index in the original string of the start or end of the
      substring group that was matched.  *index* defaults to the entire
      group, otherwise it will select a group.
      
      Note: availability of these methods depends on :term:`MicroPython port`.
      """
    def end(self, index: int = ..., /) -> int:
        """
      Return the index in the original string of the start or end of the
      substring group that was matched.  *index* defaults to the entire
      group, otherwise it will select a group.
      
      Note: availability of these methods depends on :term:`MicroPython port`.
      """
    def span(self, index: int = ..., /) -> tuple[int, int]:
        """
      Returns the 2-tuple ``(match.start(index), match.end(index))``.
      
      Note: availability of this method depends on :term:`MicroPython port`.
      """
