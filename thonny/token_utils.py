import builtins
import keyword


def matches_any(name, alternates):
    "Return a named group pattern matching list of alternates."
    return "(?P<%s>" % name + "|".join(alternates) + ")"


# not perfect, but hopefully good enough
_SOFT_KEYWORD = [r"^[ \t]*(match|case)[ \t]+(?!=)"]
KEYWORD = matches_any("keyword", [r"\b" + k + r"\b" for k in keyword.kwlist] + _SOFT_KEYWORD)
_builtinlist = [
    str(name) for name in dir(builtins) if not name.startswith("_") and name not in keyword.kwlist
]

# Not really built-ins, but special names nevertheless
_builtinlist.append("self")
_builtinlist.append("cls")


# TODO: move builtin handling to global-local
BUILTIN = r"([^.'\"\\#]\b|^)" + matches_any("builtin", _builtinlist) + r"\b"
NUMBER = matches_any(
    "number",
    [
        r"\b0[bB][_0-1]+",
        r"\b0[oO][_0-7]+",
        r"\b0[xX][_0-9a-fA-F]+",
        r"\b(\d[_\d]*(\.[_\d]*)?|\.\d[_\d]*)([eE][+-]?[_\d]+)?j?",
    ],
)
# TODO: would it make regex too slow? VARIABLE = matches_any("VARIABLE", [...])

METHOD_CALL = matches_any("method_call", [r"(?<=\.)([\w_]+)(?=\()"])
FUNCTION_CALL = matches_any("function_call", [r"(?:(?<=^)|(?<=[^._\w]))([\w_]+)(?=\()"])

COMMENT = matches_any("comment", [r"#[^\n]*"])
MAGIC_COMMAND = matches_any("magic", [r"^%[^\n]*"])  # used only in shell
STRINGPREFIX = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR|rb|rB|Rb|RB|f|F|fr|Fr|fR|FR|rf|rF|Rf|RF)?"

SQSTRING_OPEN = STRINGPREFIX + r"'[^'\\\n]*(\\.[^'\\\n]*)*\n?"
SQSTRING_CLOSED = STRINGPREFIX + r"'[^'\\\n]*(\\.[^'\\\n]*)*'"

DQSTRING_OPEN = STRINGPREFIX + r'"[^"\\\n]*(\\.[^"\\\n]*)*\n?'
DQSTRING_CLOSED = STRINGPREFIX + r'"[^"\\\n]*(\\.[^"\\\n]*)*"'

SQ3STRING = STRINGPREFIX + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
DQ3STRING = STRINGPREFIX + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'

SQ3DELIMITER = STRINGPREFIX + "'''"
DQ3DELIMITER = STRINGPREFIX + '"""'
COMMENT_WITH_Q3DELIMITER = matches_any("q3comment", [r"#[^\n]*('''|\"\"\")[^\n]*"])

STRING_OPEN = matches_any("open_string", [SQSTRING_OPEN, DQSTRING_OPEN])
STRING_CLOSED = matches_any("string", [SQSTRING_CLOSED, DQSTRING_CLOSED])
STRING3_DELIMITER = matches_any("DELIMITER3", [SQ3DELIMITER, DQ3DELIMITER])
STRING3 = matches_any("string3", [DQ3STRING, SQ3STRING])

TAB = matches_any("tab", "\t")
