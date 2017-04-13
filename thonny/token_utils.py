import keyword
import builtins


def matches_any(name, alternates):
    "Return a named group pattern matching list of alternates."
    return "(?P<%s>" % name + "|".join(alternates) + ")"

KW = r"\b" + matches_any("KEYWORD", keyword.kwlist) + r"\b"
_builtinlist = [str(name) for name in dir(builtins)
                                    if not name.startswith('_') and \
                                    name not in keyword.kwlist]

# TODO: move builtin handling to global-local
BUILTIN = r"([^.'\"\\#]\b|^)" + matches_any("BUILTIN", _builtinlist) + r"\b"
COMMENT = matches_any("COMMENT", [r"#[^\n]*"])
MAGIC_COMMAND = matches_any("MAGIC_COMMAND", [r"^%[^\n]*"]) # used only in shell
STRINGPREFIX = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR|rb|rB|Rb|RB)?"

SQSTRING_OPEN = STRINGPREFIX + r"'[^'\\\n]*(\\.[^'\\\n]*)*\n?"
SQSTRING_CLOSED = STRINGPREFIX + r"'[^'\\\n]*(\\.[^'\\\n]*)*'"

DQSTRING_OPEN = STRINGPREFIX + r'"[^"\\\n]*(\\.[^"\\\n]*)*\n?'
DQSTRING_CLOSED = STRINGPREFIX + r'"[^"\\\n]*(\\.[^"\\\n]*)*"'

SQ3STRING = STRINGPREFIX + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
DQ3STRING = STRINGPREFIX + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'

SQ3DELIMITER = STRINGPREFIX + "'''"
DQ3DELIMITER = STRINGPREFIX + '"""'

STRING_OPEN = matches_any("STRING_OPEN", [SQSTRING_OPEN, DQSTRING_OPEN])
STRING_CLOSED = matches_any("STRING_CLOSED", [SQSTRING_CLOSED, DQSTRING_CLOSED])
STRING3_DELIMITER = matches_any("DELIMITER3", [SQ3DELIMITER, DQ3DELIMITER])
STRING3 = matches_any("STRING3", [DQ3STRING, SQ3STRING])
