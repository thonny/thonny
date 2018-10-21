"""Facilities for learning the structure of incomplete Python code
Mostly copied/adapted from idlelib.HyperParser and idlelib.PyParse
"""


import re
import string
from collections import Mapping
from keyword import iskeyword
from typing import Dict  # @UnusedImport

NUM_CONTEXT_LINES = (50, 500, 5000000)

# Reason last stmt is continued (or C_NONE if it's not).
(C_NONE, C_BACKSLASH, C_STRING_FIRST_LINE, C_STRING_NEXT_LINES, C_BRACKET) = range(5)

# Find what looks like the start of a popular stmt.

_synchre = re.compile(
    r"""
    ^
    [ \t]*
    (?: while
    |   else
    |   def
    |   return
    |   assert
    |   break
    |   class
    |   continue
    |   elif
    |   try
    |   except
    |   raise
    |   import
    |   yield
    )
    \b
""",
    re.VERBOSE | re.MULTILINE,
).search

# Match blank line or non-indenting comment line.

_junkre = re.compile(
    r"""
    [ \t]*
    (?: \# \S .* )?
    \n
""",
    re.VERBOSE,
).match

# Match any flavor of string; the terminating quote is optional
# so that we're robust in the face of incomplete program text.

_match_stringre = re.compile(
    r"""
    \""" [^"\\]* (?:
                     (?: \\. | "(?!"") )
                     [^"\\]*
                 )*
    (?: \""" )?

|   " [^"\\\n]* (?: \\. [^"\\\n]* )* "?

|   ''' [^'\\]* (?:
                   (?: \\. | '(?!'') )
                   [^'\\]*
                )*
    (?: ''' )?

|   ' [^'\\\n]* (?: \\. [^'\\\n]* )* '?
""",
    re.VERBOSE | re.DOTALL,
).match

# Match a line that starts with something interesting;
# used to find the first item of a bracket structure.

_itemre = re.compile(
    r"""
    [ \t]*
    [^\s#\\]    # if we match, m.end()-1 is the interesting char
""",
    re.VERBOSE,
).match

# Match start of stmts that should be followed by a dedent.

_closere = re.compile(
    r"""
    \s*
    (?: return
    |   break
    |   continue
    |   raise
    |   pass
    )
    \b
""",
    re.VERBOSE,
).match

# Chew up non-special chars as quickly as possible.  If match is
# successful, m.end() less 1 is the index of the last boring char
# matched.  If match is unsuccessful, the string starts with an
# interesting char.

_chew_ordinaryre = re.compile(
    r"""
    [^[\](){}#'"\\]+
""",
    re.VERBOSE,
).match


class StringTranslatePseudoMapping(Mapping):
    r"""Utility class to be used with str.translate()

    This Mapping class wraps a given dict. When a value for a key is
    requested via __getitem__() or get(), the key is looked up in the
    given dict. If found there, the value from the dict is returned.
    Otherwise, the default value given upon initialization is returned.

    This allows using str.translate() to make some replacements, and to
    replace all characters for which no replacement was specified with
    a given character instead of leaving them as-is.

    For example, to replace everything except whitespace with 'x':

    >>> whitespace_chars = ' \t\n\r'
    >>> preserve_dict = {ord(c): ord(c) for c in whitespace_chars}
    >>> mapping = StringTranslatePseudoMapping(preserve_dict, ord('x'))
    >>> text = "a + b\tc\nd"
    >>> text.translate(mapping)
    'x x x\tx\nx'
    """

    def __init__(self, non_defaults, default_value):
        self._non_defaults = non_defaults
        self._default_value = default_value

        def _get(key, _get=non_defaults.get, _default=default_value):
            return _get(key, _default)

        self._get = _get

    def __getitem__(self, item):
        return self._get(item)

    def __len__(self):
        return len(self._non_defaults)

    def __iter__(self):
        return iter(self._non_defaults)

    def get(self, key, default=None):
        return self._get(key)


class RoughParser:
    def __init__(self, indent_width, tabwidth):
        self.indent_width = indent_width
        self.tabwidth = tabwidth

    def set_str(self, s):
        assert len(s) == 0 or s[-1] == "\n"
        self.str = s
        self.study_level = 0

    # Return index of a good place to begin parsing, as close to the
    # end of the string as possible.  This will be the start of some
    # popular stmt like "if" or "def".  Return None if none found:
    # the caller should pass more prior context then, if possible, or
    # if not (the entire program text up until the point of interest
    # has already been tried) pass 0 to set_lo.
    #
    # This will be reliable iff given a reliable is_char_in_string
    # function, meaning that when it says "no", it's absolutely
    # guaranteed that the char is not in a string.

    def find_good_parse_start(self, is_char_in_string=None, _synchre=_synchre):
        # pylint: disable=redefined-builtin

        str, pos = self.str, None  # @ReservedAssignment

        if not is_char_in_string:
            # no clue -- make the caller pass everything
            return None

        # Peek back from the end for a good place to start,
        # but don't try too often; pos will be left None, or
        # bumped to a legitimate synch point.
        limit = len(str)
        for _ in range(5):
            i = str.rfind(":\n", 0, limit)
            if i < 0:
                break
            i = str.rfind("\n", 0, i) + 1  # start of colon line
            m = _synchre(str, i, limit)
            if m and not is_char_in_string(m.start()):
                pos = m.start()
                break
            limit = i
        if pos is None:
            # Nothing looks like a block-opener, or stuff does
            # but is_char_in_string keeps returning true; most likely
            # we're in or near a giant string, the colorizer hasn't
            # caught up enough to be helpful, or there simply *aren't*
            # any interesting stmts.  In any of these cases we're
            # going to have to parse the whole thing to be sure, so
            # give it one last try from the start, but stop wasting
            # time here regardless of the outcome.
            m = _synchre(str)
            if m and not is_char_in_string(m.start()):
                pos = m.start()
            return pos

        # Peeking back worked; look forward until _synchre no longer
        # matches.
        i = pos + 1
        while 1:
            m = _synchre(str, i)
            if m:
                s, i = m.span()
                if not is_char_in_string(s):
                    pos = s
            else:
                break
        return pos

    # Throw away the start of the string.  Intended to be called with
    # find_good_parse_start's result.

    def set_lo(self, lo):
        assert lo == 0 or self.str[lo - 1] == "\n"
        if lo > 0:
            self.str = self.str[lo:]

    # Build a translation table to map uninteresting chars to 'x', open
    # brackets to '(', close brackets to ')' while preserving quotes,
    # backslashes, newlines and hashes. This is to be passed to
    # str.translate() in _study1().
    _tran1 = {}  # type: Dict[int, int]
    _tran1.update((ord(c), ord("(")) for c in "({[")
    _tran1.update((ord(c), ord(")")) for c in ")}]")
    _tran1.update((ord(c), ord(c)) for c in "\"'\\\n#")
    _tran = StringTranslatePseudoMapping(_tran1, default_value=ord("x"))

    # As quickly as humanly possible <wink>, find the line numbers (0-
    # based) of the non-continuation lines.
    # Creates self.{goodlines, continuation}.

    def _study1(self):
        # pylint: disable=redefined-builtin

        if self.study_level >= 1:
            return
        self.study_level = 1

        # Map all uninteresting characters to "x", all open brackets
        # to "(", all close brackets to ")", then collapse runs of
        # uninteresting characters.  This can cut the number of chars
        # by a factor of 10-40, and so greatly speed the following loop.
        str = (
            self.str.translate(self._tran)  # @ReservedAssignment
            .replace("xxxxxxxx", "x")
            .replace("xxxx", "x")
            .replace("xx", "x")
            .replace("xx", "x")
            .replace("\nx", "\n")
        )
        # note that replacing x\n with \n would be incorrect, because
        # x may be preceded by a backslash

        # March over the squashed version of the program, accumulating
        # the line numbers of non-continued stmts, and determining
        # whether & why the last stmt is a continuation.
        continuation = C_NONE
        level = lno = 0  # level is nesting level; lno is line number
        self.goodlines = goodlines = [0]
        push_good = goodlines.append
        i, n = 0, len(str)
        while i < n:
            ch = str[i]
            i = i + 1

            # cases are checked in decreasing order of frequency
            if ch == "x":
                continue

            if ch == "\n":
                lno = lno + 1
                if level == 0:
                    push_good(lno)
                    # else we're in an unclosed bracket structure
                continue

            if ch == "(":
                level = level + 1
                continue

            if ch == ")":
                if level:
                    level = level - 1
                    # else the program is invalid, but we can't complain
                continue

            if ch == '"' or ch == "'":
                # consume the string
                quote = ch
                if str[i - 1 : i + 2] == quote * 3:
                    quote = quote * 3
                firstlno = lno
                w = len(quote) - 1
                i = i + w
                while i < n:
                    ch = str[i]
                    i = i + 1

                    if ch == "x":
                        continue

                    if str[i - 1 : i + w] == quote:
                        i = i + w
                        break

                    if ch == "\n":
                        lno = lno + 1
                        if w == 0:
                            # unterminated single-quoted string
                            if level == 0:
                                push_good(lno)
                            break
                        continue

                    if ch == "\\":
                        assert i < n
                        if str[i] == "\n":
                            lno = lno + 1
                        i = i + 1
                        continue

                    # else comment char or paren inside string

                else:
                    # didn't break out of the loop, so we're still
                    # inside a string
                    if (lno - 1) == firstlno:
                        # before the previous \n in str, we were in the first
                        # line of the string
                        continuation = C_STRING_FIRST_LINE
                    else:
                        continuation = C_STRING_NEXT_LINES
                continue  # with outer loop

            if ch == "#":
                # consume the comment
                i = str.find("\n", i)
                assert i >= 0
                continue

            assert ch == "\\"
            assert i < n
            if str[i] == "\n":
                lno = lno + 1
                if i + 1 == n:
                    continuation = C_BACKSLASH
            i = i + 1

        # The last stmt may be continued for all 3 reasons.
        # String continuation takes precedence over bracket
        # continuation, which beats backslash continuation.
        if (
            continuation != C_STRING_FIRST_LINE
            and continuation != C_STRING_NEXT_LINES
            and level > 0
        ):
            continuation = C_BRACKET
        self.continuation = continuation

        # Push the final line number as a sentinel value, regardless of
        # whether it's continued.
        assert (continuation == C_NONE) == (goodlines[-1] == lno)
        if goodlines[-1] != lno:
            push_good(lno)

    def get_continuation_type(self):
        self._study1()
        return self.continuation

    # study1 was sufficient to determine the continuation status,
    # but doing more requires looking at every character.  study2
    # does this for the last interesting statement in the block.
    # Creates:
    #     self.stmt_start, stmt_end
    #         slice indices of last interesting stmt
    #     self.stmt_bracketing
    #         the bracketing structure of the last interesting stmt;
    #         for example, for the statement "say(boo) or die", stmt_bracketing
    #         will be [(0, 0), (3, 1), (8, 0)]. Strings and comments are
    #         treated as brackets, for the matter.
    #     self.lastch
    #         last non-whitespace character before optional trailing
    #         comment
    #     self.lastopenbracketpos
    #         if continuation is C_BRACKET, index of last open bracket

    def _study2(self):
        # pylint: disable=redefined-builtin

        if self.study_level >= 2:
            return
        self._study1()
        self.study_level = 2

        # Set p and q to slice indices of last interesting stmt.
        str, goodlines = self.str, self.goodlines  # @ReservedAssignment
        i = len(goodlines) - 1
        p = len(str)  # index of newest line
        while i:
            assert p
            # p is the index of the stmt at line number goodlines[i].
            # Move p back to the stmt at line number goodlines[i-1].
            q = p
            for _ in range(goodlines[i - 1], goodlines[i]):  # @UnusedVariable
                # tricky: sets p to 0 if no preceding newline
                p = str.rfind("\n", 0, p - 1) + 1
            # The stmt str[p:q] isn't a continuation, but may be blank
            # or a non-indenting comment line.
            if _junkre(str, p):
                i = i - 1
            else:
                break
        if i == 0:
            # nothing but junk!
            assert p == 0
            q = p
        self.stmt_start, self.stmt_end = p, q

        # Analyze this stmt, to find the last open bracket (if any)
        # and last interesting character (if any).
        lastch = ""
        stack = []  # stack of open bracket indices
        push_stack = stack.append
        bracketing = [(p, 0)]
        while p < q:
            # suck up all except ()[]{}'"#\\
            m = _chew_ordinaryre(str, p, q)
            if m:
                # we skipped at least one boring char
                newp = m.end()
                # back up over totally boring whitespace
                i = newp - 1  # index of last boring char
                while i >= p and str[i] in " \t\n":
                    i = i - 1
                if i >= p:
                    lastch = str[i]
                p = newp
                if p >= q:
                    break

            ch = str[p]

            if ch in "([{":
                push_stack(p)
                bracketing.append((p, len(stack)))
                lastch = ch
                p = p + 1
                continue

            if ch in ")]}":
                if stack:
                    del stack[-1]
                lastch = ch
                p = p + 1
                bracketing.append((p, len(stack)))
                continue

            if ch == '"' or ch == "'":
                # consume string
                # Note that study1 did this with a Python loop, but
                # we use a regexp here; the reason is speed in both
                # cases; the string may be huge, but study1 pre-squashed
                # strings to a couple of characters per line.  study1
                # also needed to keep track of newlines, and we don't
                # have to.
                bracketing.append((p, len(stack) + 1))
                lastch = ch
                p = _match_stringre(str, p, q).end()
                bracketing.append((p, len(stack)))
                continue

            if ch == "#":
                # consume comment and trailing newline
                bracketing.append((p, len(stack) + 1))
                p = str.find("\n", p, q) + 1
                assert p > 0
                bracketing.append((p, len(stack)))
                continue

            assert ch == "\\"
            p = p + 1  # beyond backslash
            assert p < q
            if str[p] != "\n":
                # the program is invalid, but can't complain
                lastch = ch + str[p]
            p = p + 1  # beyond escaped char

        # end while p < q:

        self.lastch = lastch
        if stack:
            self.lastopenbracketpos = stack[-1]
        self.stmt_bracketing = tuple(bracketing)

    # Assuming continuation is C_BRACKET, return the number
    # of spaces the next line should be indented.

    def compute_bracket_indent(self):
        # pylint: disable=redefined-builtin
        self._study2()
        assert self.continuation == C_BRACKET
        j = self.lastopenbracketpos
        str = self.str  # @ReservedAssignment
        n = len(str)
        origi = i = str.rfind("\n", 0, j) + 1
        j = j + 1  # one beyond open bracket
        # find first list item; set i to start of its line
        while j < n:
            m = _itemre(str, j)
            if m:
                j = m.end() - 1  # index of first interesting char
                extra = 0
                break
            else:
                # this line is junk; advance to next line
                i = j = str.find("\n", j) + 1
        else:
            # nothing interesting follows the bracket;
            # reproduce the bracket line's indentation + a level
            j = i = origi
            while str[j] in " \t":
                j = j + 1
            extra = self.indent_width
        return len(str[i:j].expandtabs(self.tabwidth)) + extra

    # Return number of physical lines in last stmt (whether or not
    # it's an interesting stmt!  this is intended to be called when
    # continuation is C_BACKSLASH).

    def get_num_lines_in_stmt(self):
        self._study1()
        goodlines = self.goodlines
        return goodlines[-1] - goodlines[-2]

    # Assuming continuation is C_BACKSLASH, return the number of spaces
    # the next line should be indented.  Also assuming the new line is
    # the first one following the initial line of the stmt.

    def compute_backslash_indent(self):
        # pylint: disable=redefined-builtin
        self._study2()
        assert self.continuation == C_BACKSLASH
        str = self.str  # @ReservedAssignment
        i = self.stmt_start
        while str[i] in " \t":
            i = i + 1
        startpos = i

        # See whether the initial line starts an assignment stmt; i.e.,
        # look for an = operator
        endpos = str.find("\n", startpos) + 1
        found = level = 0
        while i < endpos:
            ch = str[i]
            if ch in "([{":
                level = level + 1
                i = i + 1
            elif ch in ")]}":
                if level:
                    level = level - 1
                i = i + 1
            elif ch == '"' or ch == "'":
                i = _match_stringre(str, i, endpos).end()
            elif ch == "#":
                break
            elif (
                level == 0
                and ch == "="
                and (i == 0 or str[i - 1] not in "=<>!")
                and str[i + 1] != "="
            ):
                found = 1
                break
            else:
                i = i + 1

        if found:
            # found a legit =, but it may be the last interesting
            # thing on the line
            i = i + 1  # move beyond the =
            found = re.match(r"\s*\\", str[i:endpos]) is None

        if not found:
            # oh well ... settle for moving beyond the first chunk
            # of non-whitespace chars
            i = startpos
            while str[i] not in " \t\n":
                i = i + 1

        return len(str[self.stmt_start : i].expandtabs(self.tabwidth)) + 1

    # Return the leading whitespace on the initial line of the last
    # interesting stmt.

    def get_base_indent_string(self):
        self._study2()
        i, n = self.stmt_start, self.stmt_end
        j = i
        str_ = self.str
        while j < n and str_[j] in " \t":
            j = j + 1
        return str_[i:j]

    # Did the last interesting stmt open a block?

    def is_block_opener(self):
        self._study2()
        return self.lastch == ":"

    # Did the last interesting stmt close a block?

    def is_block_closer(self):
        self._study2()
        return _closere(self.str, self.stmt_start) is not None

    # index of last open bracket ({[, or None if none
    lastopenbracketpos = None

    def get_last_open_bracket_pos(self):
        self._study2()
        return self.lastopenbracketpos

    # the structure of the bracketing of the last interesting statement,
    # in the format defined in _study2, or None if the text didn't contain
    # anything
    stmt_bracketing = None

    def get_last_stmt_bracketing(self):
        self._study2()
        return self.stmt_bracketing


# all ASCII chars that may be in an identifier
_ASCII_ID_CHARS = frozenset(string.ascii_letters + string.digits + "_")
# all ASCII chars that may be the first char of an identifier
_ASCII_ID_FIRST_CHARS = frozenset(string.ascii_letters + "_")

# lookup table for whether 7-bit ASCII chars are valid in a Python identifier
_IS_ASCII_ID_CHAR = [(chr(x) in _ASCII_ID_CHARS) for x in range(128)]
# lookup table for whether 7-bit ASCII chars are valid as the first
# char in a Python identifier
_IS_ASCII_ID_FIRST_CHAR = [(chr(x) in _ASCII_ID_FIRST_CHARS) for x in range(128)]


class HyperParser:
    """Provide advanced parsing abilities for ParenMatch and other extensions.
    
    HyperParser uses PyParser.  PyParser mostly gives information on the
    proper indentation of code.  HyperParser gives additional information on
    the structure of code.
    """

    def __init__(self, text, index):
        "To initialize, analyze the surroundings of the given index."

        self.text = text

        parser = RoughParser(text.indent_width, text.tabwidth)

        def index2line(index):
            return int(float(index))

        lno = index2line(text.index(index))

        for context in NUM_CONTEXT_LINES:
            startat = max(lno - context, 1)
            startatindex = repr(startat) + ".0"
            stopatindex = "%d.end" % lno
            # We add the newline because PyParse requires a newline
            # at end. We add a space so that index won't be at end
            # of line, so that its status will be the same as the
            # char before it, if should.
            parser.set_str(text.get(startatindex, stopatindex) + " \n")
            bod = parser.find_good_parse_start(_build_char_in_string_func(startatindex))
            if bod is not None or startat == 1:
                break
        parser.set_lo(bod or 0)

        # We want what the parser has, minus the last newline and space.
        self.rawtext = parser.str[:-2]
        # Parser.str apparently preserves the statement we are in, so
        # that stopatindex can be used to synchronize the string with
        # the text box indices.
        self.stopatindex = stopatindex
        self.bracketing = parser.get_last_stmt_bracketing()
        # find which pairs of bracketing are openers. These always
        # correspond to a character of rawtext.
        self.isopener = [
            i > 0 and self.bracketing[i][1] > self.bracketing[i - 1][1]
            for i in range(len(self.bracketing))
        ]

        self.set_index(index)

    def set_index(self, index):
        """Set the index to which the functions relate.

        The index must be in the same statement.
        """
        indexinrawtext = len(self.rawtext) - len(self.text.get(index, self.stopatindex))
        if indexinrawtext < 0:
            raise ValueError("Index %s precedes the analyzed statement" % index)
        self.indexinrawtext = indexinrawtext
        # find the rightmost bracket to which index belongs
        self.indexbracket = 0
        while (
            self.indexbracket < len(self.bracketing) - 1
            and self.bracketing[self.indexbracket + 1][0] < self.indexinrawtext
        ):
            self.indexbracket += 1
        if (
            self.indexbracket < len(self.bracketing) - 1
            and self.bracketing[self.indexbracket + 1][0] == self.indexinrawtext
            and not self.isopener[self.indexbracket + 1]
        ):
            self.indexbracket += 1

    def is_in_string(self):
        """Is the index given to the HyperParser in a string?"""
        # The bracket to which we belong should be an opener.
        # If it's an opener, it has to have a character.
        return self.isopener[self.indexbracket] and self.rawtext[
            self.bracketing[self.indexbracket][0]
        ] in ('"', "'")

    def is_in_code(self):
        """Is the index given to the HyperParser in normal code?"""
        return not self.isopener[self.indexbracket] or self.rawtext[
            self.bracketing[self.indexbracket][0]
        ] not in ("#", '"', "'")

    def get_surrounding_brackets(self, openers="([{", mustclose=False):
        """Return bracket indexes or None.

        If the index given to the HyperParser is surrounded by a
        bracket defined in openers (or at least has one before it),
        return the indices of the opening bracket and the closing
        bracket (or the end of line, whichever comes first).

        If it is not surrounded by brackets, or the end of line comes
        before the closing bracket and mustclose is True, returns None.
        """

        bracketinglevel = self.bracketing[self.indexbracket][1]
        before = self.indexbracket
        while (
            not self.isopener[before]
            or self.rawtext[self.bracketing[before][0]] not in openers
            or self.bracketing[before][1] > bracketinglevel
        ):
            before -= 1
            if before < 0:
                return None
            bracketinglevel = min(bracketinglevel, self.bracketing[before][1])
        after = self.indexbracket + 1
        while (
            after < len(self.bracketing)
            and self.bracketing[after][1] >= bracketinglevel
        ):
            after += 1

        beforeindex = self.text.index(
            "%s-%dc"
            % (self.stopatindex, len(self.rawtext) - self.bracketing[before][0])
        )
        if after >= len(self.bracketing) or self.bracketing[after][0] > len(
            self.rawtext
        ):
            if mustclose:
                return None
            afterindex = self.stopatindex
        else:
            # We are after a real char, so it is a ')' and we give the
            # index before it.
            afterindex = self.text.index(
                "%s-%dc"
                % (
                    self.stopatindex,
                    len(self.rawtext) - (self.bracketing[after][0] - 1),
                )
            )

        return beforeindex, afterindex

    # the set of built-in identifiers which are also keywords,
    # i.e. keyword.iskeyword() returns True for them
    _ID_KEYWORDS = frozenset({"True", "False", "None"})

    @classmethod
    def _eat_identifier(cls, s, limit, pos):
        """Given a string and pos, return the number of chars in the
        identifier which ends at pos, or 0 if there is no such one.

        This ignores non-identifier eywords are not identifiers.
        """
        is_ascii_id_char = _IS_ASCII_ID_CHAR

        # Start at the end (pos) and work backwards.
        i = pos

        # Go backwards as long as the characters are valid ASCII
        # identifier characters. This is an optimization, since it
        # is faster in the common case where most of the characters
        # are ASCII.
        while i > limit and (ord(s[i - 1]) < 128 and is_ascii_id_char[ord(s[i - 1])]):
            i -= 1

        # If the above loop ended due to reaching a non-ASCII
        # character, continue going backwards using the most generic
        # test for whether a string contains only valid identifier
        # characters.
        if i > limit and ord(s[i - 1]) >= 128:
            while i - 4 >= limit and ("a" + s[i - 4 : pos]).isidentifier():
                i -= 4
            if i - 2 >= limit and ("a" + s[i - 2 : pos]).isidentifier():
                i -= 2
            if i - 1 >= limit and ("a" + s[i - 1 : pos]).isidentifier():
                i -= 1

            # The identifier candidate starts here. If it isn't a valid
            # identifier, don't eat anything. At this point that is only
            # possible if the first character isn't a valid first
            # character for an identifier.
            if not s[i:pos].isidentifier():
                return 0
        elif i < pos:
            # All characters in str[i:pos] are valid ASCII identifier
            # characters, so it is enough to check that the first is
            # valid as the first character of an identifier.
            if not _IS_ASCII_ID_FIRST_CHAR[ord(s[i])]:
                return 0

        # All keywords are valid identifiers, but should not be
        # considered identifiers here, except for True, False and None.
        if i < pos and (iskeyword(s[i:pos]) and s[i:pos] not in cls._ID_KEYWORDS):
            return 0

        return pos - i

    # This string includes all chars that may be in a white space
    _whitespace_chars = " \t\n\\"

    def get_expression(self):
        """Return a string with the Python expression which ends at the
        given index, which is empty if there is no real one.
        """
        if not self.is_in_code():
            raise ValueError(
                "get_expression should only be called" "if index is inside a code."
            )

        rawtext = self.rawtext
        bracketing = self.bracketing

        brck_index = self.indexbracket
        brck_limit = bracketing[brck_index][0]
        pos = self.indexinrawtext

        last_identifier_pos = pos
        postdot_phase = True

        while 1:
            # Eat whitespaces, comments, and if postdot_phase is False - a dot
            while 1:
                if pos > brck_limit and rawtext[pos - 1] in self._whitespace_chars:
                    # Eat a whitespace
                    pos -= 1
                elif not postdot_phase and pos > brck_limit and rawtext[pos - 1] == ".":
                    # Eat a dot
                    pos -= 1
                    postdot_phase = True
                # The next line will fail if we are *inside* a comment,
                # but we shouldn't be.
                elif (
                    pos == brck_limit
                    and brck_index > 0
                    and rawtext[bracketing[brck_index - 1][0]] == "#"
                ):
                    # Eat a comment
                    brck_index -= 2
                    brck_limit = bracketing[brck_index][0]
                    pos = bracketing[brck_index + 1][0]
                else:
                    # If we didn't eat anything, quit.
                    break

            if not postdot_phase:
                # We didn't find a dot, so the expression end at the
                # last identifier pos.
                break

            ret = self._eat_identifier(rawtext, brck_limit, pos)
            if ret:
                # There is an identifier to eat
                pos = pos - ret
                last_identifier_pos = pos
                # Now, to continue the search, we must find a dot.
                postdot_phase = False
                # (the loop continues now)

            elif pos == brck_limit:
                # We are at a bracketing limit. If it is a closing
                # bracket, eat the bracket, otherwise, stop the search.
                level = bracketing[brck_index][1]
                while brck_index > 0 and bracketing[brck_index - 1][1] > level:
                    brck_index -= 1
                if bracketing[brck_index][0] == brck_limit:
                    # We were not at the end of a closing bracket
                    break
                pos = bracketing[brck_index][0]
                brck_index -= 1
                brck_limit = bracketing[brck_index][0]
                last_identifier_pos = pos
                if rawtext[pos] in "([":
                    # [] and () may be used after an identifier, so we
                    # continue. postdot_phase is True, so we don't allow a dot.
                    pass
                else:
                    # We can't continue after other types of brackets
                    if rawtext[pos] in "'\"":
                        # Scan a string prefix
                        while pos > 0 and rawtext[pos - 1] in "rRbBuU":
                            pos -= 1
                        last_identifier_pos = pos
                    break

            else:
                # We've found an operator or something.
                break

        return rawtext[last_identifier_pos : self.indexinrawtext]


def _is_char_in_string(text_index):
    # in idlelib.EditorWindow this used info from colorer
    # to speed up things, but I dont want to rely on this
    return 1


def _build_char_in_string_func(startindex):
    # copied from idlelib.EditorWindow (Python 3.4.2)

    # Our editwin provides a _is_char_in_string function that works
    # with a Tk text index, but PyParse only knows about offsets into
    # a string. This builds a function for PyParse that accepts an
    # offset.

    def inner(offset, _startindex=startindex, _icis=_is_char_in_string):
        return _icis(_startindex + "+%dc" % offset)

    return inner
