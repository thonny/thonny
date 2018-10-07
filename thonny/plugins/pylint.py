import ast
import subprocess

from thonny import ui_utils, get_workbench
from thonny.assistance import SubprocessProgramAnalyzer, add_program_analyzer
from thonny.running import get_frontend_python
import logging


class PylintAnalyzer(SubprocessProgramAnalyzer):
    def start_analysis(self, main_file_path, imported_file_paths):
        relevant_symbols = {
            key
            for key in all_checks_by_symbol
            if all_checks_by_symbol[key]["usage"] == "warning"
        }

        if "bad-python3-import" in relevant_symbols:
            # https://github.com/PyCQA/pylint/issues/2453
            # TODO: allow if this is fixed in current version
            relevant_symbols.remove("bad-python3-import")

        # remove user-disabled checks
        relevant_symbols = relevant_symbols - set(
            get_workbench().get_option("assistance.disabled_checks")
        )

        ignored_modules = {"turtle"}  # has dynamically generated attributes

        options = [
            # "--rcfile=None", # TODO: make it ignore any rcfiles that can be somewhere
            "--persistent=n",
            # "--confidence=HIGH", # Leave empty to show all. Valid levels: HIGH, INFERENCE, INFERENCE_FAILURE, UNDEFINED
            # "--disable=missing-docstring,invalid-name,trailing-whitespace,trailing-newlines,missing-final-newline,locally-disabled,suppressed-message",
            "--disable=all",
            "--enable=" + ",".join(relevant_symbols),
            "--ignored-modules=" + ",".join(ignored_modules),
            "--max-line-length=120",
            "--output-format=text",
            "--reports=n",
            "--msg-template={{'filename':{abspath!r}, 'lineno':{line}, 'col_offset':{column}, 'symbol':{symbol!r}, 'msg':{msg!r}, 'msg_id':{msg_id!r}, 'category' : {C!r} }}",
        ]

        # disallow unused globals only in main script
        """
        Not good idea, because unused * imports also count as unused global vars
        from pylint.__pkginfo__ import numversion

        if not imported_file_paths and numversion >= (1, 7):
            # (unfortunately can't separate main script when user modules are present)
            options.append("--allow-global-unused-variables=no")
        """
        
        self._proc = ui_utils.popen_with_ui_thread_callback(
            [get_frontend_python(), "-m", "pylint"]
            + options
            + [main_file_path]
            + list(imported_file_paths),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            on_completion=self._parse_and_output_warnings,
        )

    def _parse_and_output_warnings(self, pylint_proc, out_lines, err_lines):
        # print("COMPL", out, err)
        # get rid of non-error
        err = "".join(err_lines).replace(
            "No config file found, using default configuration", ""
        ).strip()
        
        if err:
            logging.getLogger("thonny").error("Pylint: " + err)

        warnings = []
        for line in out_lines:
            if line.startswith("{"):
                try:
                    atts = ast.literal_eval(line.strip())
                except SyntaxError:
                    logging.error("Can't parse Pylint line: " + line)
                    continue
                else:
                    check = all_checks_by_symbol[atts["symbol"]]
                    if check.get("tho_xpln"):
                        explanation = check["tho_xpln"]
                    else:
                        explanation = check["msg_xpln"]

                    if explanation.startswith("Used when an "):
                        explanation = (
                            "It looks like the " + explanation[(len("Used when an ")) :]
                        )
                    elif explanation.startswith("Emitted when an "):
                        explanation = (
                            "It looks like the "
                            + explanation[(len("Emitted when an ")) :]
                        )
                    elif explanation.startswith("Used when a "):
                        explanation = (
                            "It looks like the " + explanation[(len("Used when a ")) :]
                        )
                    elif explanation.startswith("Emitted when a "):
                        explanation = (
                            "It looks like the "
                            + explanation[(len("Emitted when a ")) :]
                        )
                    elif explanation.startswith("Used when "):
                        explanation = (
                            "It looks like " + explanation[(len("Used when ")) :]
                        )
                    elif explanation.startswith("Emitted when "):
                        explanation = (
                            "It looks like " + explanation[(len("Emitted when ")) :]
                        )

                    atts["explanation"] = explanation

                    if check.get("tho_xpln_rst"):
                        atts["explanation_rst"] = check["tho_xpln_rst"]

                    if atts["category"] in ("I", "F"):
                        atts["msg"] = (
                            "INTERNAL ERROR when analyzing the code: " + atts["msg"]
                        )

                    # atts["more_info_url"] = "http://pylint-messages.wikidot.com/messages:%s" % atts["msg_id"].lower()
                    warnings.append(atts)

        self.completion_handler(self, warnings)


# according to version 2.1.1
all_checks = [
    {
        "msg_id": "C0102",
        "msg_sym": "blacklisted-name",
        "msg_text": 'Black listed name "%s"',
        "msg_xpln": "Used when the name is listed in the black list (unauthorized "
        "names).",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0103",  # TODO: usable with custom regex which allows shorter names
        "msg_sym": "invalid-name",
        "msg_text": '%s name "%s" doesn\'t conform to %s',
        "msg_xpln": "Used when the name doesn't conform to naming rules associated "
        "to its type (constant, variable, class...).",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "C0111",
        "msg_sym": "missing-docstring",
        "msg_text": "Missing %s docstring",
        "msg_xpln": "Used when a module, function, class or method has no "
        "docstring.Some special methods like __init__ doesn't necessary "
        "require a docstring.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0112",
        "msg_sym": "empty-docstring",
        "msg_text": "Empty %s docstring",
        "msg_xpln": "Used when a module, function, class or method has an empty "
        "docstring (it would be too easy ;).",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0113",
        "msg_sym": "unneeded-not",
        "msg_text": 'Consider changing "%s" to "%s"',
        "msg_xpln": "Used when a boolean expression contains an unneeded negation.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "C0121",  # TODO: find out what it means. NB! Other message in wikidot
        "msg_sym": "singleton-comparison",
        "msg_text": "Comparison to %s should be %s",
        "msg_xpln": "Used when an expression is compared to singleton values like "
        "True, False or None.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0122",
        "msg_sym": "misplaced-comparison-constant",
        "msg_text": "Comparison should be %s",
        "msg_xpln": "Used when the constant is placed on the left side of a "
        "comparison. It is usually clearer in intent to place it in the "
        "right hand side of the comparison.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "C0123",
        "msg_sym": "unidiomatic-typecheck",
        "msg_text": "Using type() instead of isinstance() for a typecheck.",
        "msg_xpln": "The idiomatic way to perform an explicit typecheck in Python is "
        "to use isinstance(x, Y) rather than type(x) == Y, type(x) is Y. "
        "Though there are unusual situations where these give different "
        "results.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "C0200",
        "msg_sym": "consider-using-enumerate",
        "msg_text": "Consider using enumerate instead of iterating with range and "
        "len",
        "msg_xpln": "Emitted when code that iterates with range and len is "
        "encountered. Such code can be simplified by using the enumerate "
        "builtin.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "C0201",
        "msg_sym": "consider-iterating-dictionary",
        "msg_text": "Consider iterating the dictionary directly instead of calling "
        ".keys()",
        "msg_xpln": "Emitted when the keys of a dictionary are iterated through the "
        ".keys() method. It is enough to just iterate through the "
        'dictionary itself, as in "for key in dictionary".',
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "C0202",
        "msg_sym": "bad-classmethod-argument",
        "msg_text": "Class method %s should have %s as first argument",
        "msg_xpln": "Used when a class method has a first argument named differently "
        "than the value specified in valid-classmethod-first-arg option "
        '(default to "cls"), recommended to easily differentiate them '
        "from regular instance methods.",
        "tho_xpln": "",
        "usage": "enhancement",
    },  # TODO: simplify message
    {
        "msg_id": "C0203",
        "msg_sym": "bad-mcs-method-argument",
        "msg_text": "Metaclass method %s should have %s as first argument",
        "msg_xpln": "Used when a metaclass method has a first argument named "
        "differently than the value specified in "
        'valid-classmethod-first-arg option (default to "cls"), '
        "recommended to easily differentiate them from regular instance "
        "methods.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0204",
        "msg_sym": "bad-mcs-classmethod-argument",
        "msg_text": "Metaclass class method %s should have %s as first argument",
        "msg_xpln": "Used when a metaclass class method has a first argument named "
        "differently than the value specified in "
        "valid-metaclass-classmethod-first-arg option (default to "
        '"mcs"), recommended to easily differentiate them from regular '
        "instance methods.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0205",
        "msg_sym": "single-string-used-for-slots",
        "msg_text": "Class __slots__ should be a non-string iterable",
        "msg_xpln": "Used when a class __slots__ is a simple string, rather than an "
        "iterable.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0301",  # option: max-line-length, 100 by default
        "msg_sym": "line-too-long",
        "msg_text": "Line too long (%s/%s)",
        "msg_xpln": "Used when a line is longer than a given number of characters.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "C0302",
        "msg_sym": "too-many-lines",
        "msg_text": "Too many lines in module (%s/%s)",
        "msg_xpln": "Used when a module has too many lines, reducing its "
        "readability.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0303",
        "msg_sym": "trailing-whitespace",
        "msg_text": "Trailing whitespace",
        "msg_xpln": "Used when there is whitespace between the end of a line and the "
        "newline.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0304",
        "msg_sym": "missing-final-newline",
        "msg_text": "Final newline missing",
        "msg_xpln": "Used when the last line in a file is missing a newline.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0305",
        "msg_sym": "trailing-newlines",
        "msg_text": "Trailing newlines",
        "msg_xpln": "Used when there are trailing blank lines in a file.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0321",
        "msg_sym": "multiple-statements",
        "msg_text": "More than one statement on a single line",
        "msg_xpln": "Used when more than on statement are found on the same line.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0325",
        "msg_sym": "superfluous-parens",
        "msg_text": "Unnecessary parens after %r keyword",
        "msg_xpln": "Used when a single item in parentheses follows an if, for, or "
        "other keyword.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "C0326",
        "msg_sym": "bad-whitespace",
        "msg_text": "%s space %s %s %s",
        "msg_xpln": "Used when a wrong number of spaces is used around an operator, "
        "bracket or block opener.",
        "tho_xpln": "",
        "usage": "style",
    },
    {
        "msg_id": "C0327",
        "msg_sym": "mixed-line-endings",
        "msg_text": "Mixed line endings LF and CRLF",
        "msg_xpln": "Used when there are mixed (LF and CRLF) newline signs in a "
        "file.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0328",
        "msg_sym": "unexpected-line-ending-format",
        "msg_text": "Unexpected line ending format. There is '%s' while it should be "
        "'%s'.",
        "msg_xpln": "Used when there is different newline than expected.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0330",
        "msg_sym": "bad-continuation",
        "msg_text": "Wrong %s indentation%s%s.",
        "msg_xpln": "TODO",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0401",
        "msg_sym": "wrong-spelling-in-comment",
        "msg_text": "Wrong spelling of a word '%s' in a comment:",
        "msg_xpln": "Used when a word in comment is not spelled correctly.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0402",
        "msg_sym": "wrong-spelling-in-docstring",
        "msg_text": "Wrong spelling of a word '%s' in a docstring:",
        "msg_xpln": "Used when a word in docstring is not spelled correctly.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0403",
        "msg_sym": "invalid-characters-in-docstring",
        "msg_text": "Invalid characters %r in a docstring",
        "msg_xpln": "Used when a word in docstring cannot be checked by enchant.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0410",
        "msg_sym": "multiple-imports",
        "msg_text": "Multiple imports on one line (%s)",
        "msg_xpln": "Used when import statement importing multiple modules is "
        "detected.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0411",
        "msg_sym": "wrong-import-order",
        "msg_text": "%s should be placed before %s",
        "msg_xpln": "Used when PEP8 import order is not respected (standard imports "
        "first, then third-party libraries, then local imports)",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0412",
        "msg_sym": "ungrouped-imports",
        "msg_text": "Imports from package %s are not grouped",
        "msg_xpln": "Used when imports are not grouped by packages",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0413",
        "msg_sym": "wrong-import-position",
        "msg_text": 'Import "%s" should be placed at the top of the module',
        "msg_xpln": "Used when code and imports are mixed",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "C0414",
        "msg_sym": "useless-import-alias",
        "msg_text": "Import alias does not rename original package",
        "msg_xpln": "Used when an import alias is same as original package.e.g using "
        "import numpy as numpy instead of import numpy as np",
        "tho_xpln": "Used when an import alias is same as original package. e.g using "
        "import numpy as numpy instead of import numpy as np "
        "or e.g using import os.path as path instead of from os import path.",
        "usage": "enhancement",
    },
    {
        "msg_id": "C1801",
        "msg_sym": "len-as-condition",
        "msg_text": "Do not use `len(SEQUENCE)` to determine if a sequence is empty",
        "msg_xpln": "Used when Pylint detects that len(sequence) is being used "
        "inside a condition to determine if a sequence is empty. Instead "
        "of comparing the length to 0, rely on the fact that empty "
        "sequences are false.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0001",
        "msg_sym": "syntax-error",
        "msg_text": "",
        "msg_xpln": "Used when a syntax error is raised for a module.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0011",
        "msg_sym": "unrecognized-inline-option",
        "msg_text": "Unrecognized file option %r",
        "msg_xpln": "Used when an unknown inline option is encountered.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0012",
        "msg_sym": "bad-option-value",
        "msg_text": "Bad option value %r",
        "msg_xpln": "Used when a bad value for an inline option is encountered.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0100",
        "msg_sym": "init-is-generator",
        "msg_text": "__init__ method is a generator",
        "msg_xpln": "Used when the special class method __init__ is turned into a "
        "generator by a yield in its body.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0101",
        "msg_sym": "return-in-init",
        "msg_text": "Explicit return in __init__",
        "msg_xpln": "Used when the special class method __init__ has an explicit "
        "return value.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0102",
        "msg_sym": "function-redefined",
        "msg_text": "%s already defined line %s",
        "msg_xpln": "Used when a function / class / method is redefined.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0103",  # Will be reported by Python
        "msg_sym": "not-in-loop",
        "msg_text": "%r not properly in loop",
        "msg_xpln": "Used when break or continue keywords are used outside a loop.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0104",  # Will be reported by Python
        "msg_sym": "return-outside-function",
        "msg_text": "Return outside function",
        "msg_xpln": 'Used when a "return" statement is found outside a function or '
        "method.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0105",  # Will be reported by Python
        "msg_sym": "yield-outside-function",
        "msg_text": "Yield outside function",
        "msg_xpln": 'Used when a "yield" statement is found outside a function or '
        "method.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0107",
        "msg_sym": "nonexistent-operator",
        "msg_text": "Use of the non-existent %s operator",
        "msg_xpln": "Used when you attempt to use the C-style pre-increment or "
        "pre-decrement operator -- and ++, which doesn't exist in "
        "Python.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0108",  # Will be reported by Python
        "msg_sym": "duplicate-argument-name",
        "msg_text": "Duplicate argument name %s in function definition",
        "msg_xpln": "Duplicate argument names in function definitions are syntax "
        "errors.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0110",
        "msg_sym": "abstract-class-instantiated",
        "msg_text": "Abstract class %r with abstract methods instantiated",
        "msg_xpln": "Used when an abstract class with `abc.ABCMeta` as metaclass has "
        "abstract methods and is instantiated.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0111",
        "msg_sym": "bad-reversed-sequence",
        "msg_text": "The first reversed() argument is not a sequence",
        "msg_xpln": "Used when the first argument to reversed() builtin isn't a "
        "sequence (does not implement __reversed__, nor __getitem__ and "
        "__len__",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E0112",  # Will be reported by Python
        "msg_sym": "too-many-star-expressions",
        "msg_text": "More than one starred expression in assignment",
        "msg_xpln": "Emitted when there are more than one starred expressions (`*x`) "
        "in an assignment. This is a SyntaxError.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0113",  # Better message than in Python
        "msg_sym": "invalid-star-assignment-target",
        "msg_text": "Starred assignment target must be in a list or tuple",
        "msg_xpln": "Emitted when a star expression is used as a starred assignment "
        "target.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0114",  # ????
        "msg_sym": "star-needs-assignment-target",
        "msg_text": "Can use starred expression only in assignment target",
        "msg_xpln": "Emitted when a star expression is not used in an assignment "
        "target.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0115",  # better message than in Python
        "msg_sym": "nonlocal-and-global",
        "msg_text": "Name %r is nonlocal and global",
        "msg_xpln": "Emitted when a name is both nonlocal and global.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0116",  # Is reported in Python
        "msg_sym": "continue-in-finally",
        "msg_text": "'continue' not supported inside 'finally' clause",
        "msg_xpln": "Emitted when the `continue` keyword is found inside a finally "
        "clause, which is a SyntaxError.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0117",  # reported by Python
        "msg_sym": "nonlocal-without-binding",
        "msg_text": "nonlocal name %s found without binding",
        "msg_xpln": "Emitted when a nonlocal variable does not have an attached name "
        "somewhere in the parent scopes",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0118",  # Reported by Python
        "msg_sym": "used-prior-global-declaration",
        "msg_text": "Name %r is used prior to global declaration",
        "msg_xpln": "Emitted when a name is used prior a global declaration, which "
        "results in an error since Python 3.6. This message can't be "
        "emitted when using Python < 3.6.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0119",
        "msg_sym": "misplaced-format-function",
        "msg_text": "format function is not called on str",
        "msg_xpln": "Emitted when format function is not called on str object. e.g "
        'doing print("value: {}").format(123) instead of print("value: '
        '{}".format(123)). This might not be what the user intended to '
        "do.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E0202",
        "msg_sym": "method-hidden",
        "msg_text": "An attribute defined in %s line %s hides this method",
        "msg_xpln": "Used when a class defines a method which is hidden by an "
        "instance attribute from an ancestor class or set by some client "
        "code.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0203",
        "msg_sym": "access-member-before-definition",
        "msg_text": "Access to member %r before its definition line %s",
        "msg_xpln": "Used when an instance member is accessed before it's actually "
        "assigned.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0211",
        "msg_sym": "no-method-argument",
        "msg_text": "Method has no argument",
        "msg_xpln": "Used when a method which should have the bound instance as "
        "first argument has no argument defined.",
        "tho_xpln": 'Methods should have "self" as first argument.',
        "usage": "warning",
    },
    {
        "msg_id": "E0213",
        "msg_sym": "no-self-argument",
        "msg_text": 'Method should have "self" as first argument',
        "msg_xpln": 'Used when a method has an attribute different the "self" as '
        "first argument. This is considered as an error since this is a "
        "so common convention that you shouldn't break it!",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0236",
        "msg_sym": "invalid-slots-object",
        "msg_text": "Invalid object %r in __slots__, must contain only non empty "
        "strings",
        "msg_xpln": "Used when an invalid (non-string) object occurs in __slots__.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0237",
        "msg_sym": "assigning-non-slot",
        "msg_text": "Assigning to attribute %r not defined in class slots",
        "msg_xpln": "Used when assigning to an attribute not defined in the class "
        "slots.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0238",
        "msg_sym": "invalid-slots",
        "msg_text": "Invalid __slots__ object",
        "msg_xpln": "Used when an invalid __slots__ is found in class. Only a "
        "string, an iterable or a sequence is permitted.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0239",
        "msg_sym": "inherit-non-class",
        "msg_text": "Inheriting %r, which is not a class.",
        "msg_xpln": "Used when a class inherits from something which is not a class.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0240",
        "msg_sym": "inconsistent-mro",
        "msg_text": "Inconsistent method resolution order for class %r",
        "msg_xpln": "Used when a class has an inconsistent method resolution order.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0241",
        "msg_sym": "duplicate-bases",
        "msg_text": "Duplicate bases for class %r",
        "msg_xpln": "Used when a class has duplicate bases.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0301",
        "msg_sym": "non-iterator-returned",
        "msg_text": "__iter__ returns non-iterator",
        "msg_xpln": "Used when an __iter__ method returns something which is not an "
        "iterable (i.e. has no `__next__` method)",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0302",
        "msg_sym": "unexpected-special-method-signature",
        "msg_text": "The special method %r expects %s param(s), %d %s given",
        "msg_xpln": "Emitted when a special method was defined with an invalid "
        "number of parameters. If it has too few or too many, it might "
        "not work at all.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0303",
        "msg_sym": "invalid-length-returned",
        "msg_text": "__len__ does not return non-negative integer",
        "msg_xpln": "Used when a __len__ method returns something which is not a "
        "non-negative integer",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0401",
        "msg_sym": "import-error",
        "msg_text": "Unable to import %s",
        "msg_xpln": "Used when pylint has been unable to import a module.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0402",
        "msg_sym": "relative-beyond-top-level",
        "msg_text": "Attempted relative import beyond top-level package",
        "msg_xpln": "Used when a relative import tries to access too many levels in "
        "the current package.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0601",
        "msg_sym": "used-before-assignment",
        "msg_text": "Using variable %r before assignment",
        "msg_xpln": "Used when a local variable is accessed before its assignment.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0602",
        "msg_sym": "undefined-variable",
        "msg_text": "Undefined variable %r",
        "msg_xpln": "Used when an undefined variable is accessed.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E0603",
        "msg_sym": "undefined-all-variable",
        "msg_text": "Undefined variable name %r in __all__",
        "msg_xpln": "Used when an undefined variable name is referenced in __all__.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0604",
        "msg_sym": "invalid-all-object",
        "msg_text": "Invalid object %r in __all__, must contain only strings",
        "msg_xpln": "Used when an invalid (non-string) object occurs in __all__.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E0611",
        "msg_sym": "no-name-in-module",
        "msg_text": "No name %r in module %r",
        "msg_xpln": "Used when a name cannot be found in a module.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E0632",
        "msg_sym": "unbalanced-tuple-unpacking",
        "msg_text": "Possible unbalanced tuple unpacking with sequence%s: left side "
        "has %d label(s), right side has %d value(s)",
        "msg_xpln": "Used when there is an unbalanced tuple unpacking in assignment",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E0633",  # Reported by Python and MyPy
        "msg_sym": "unpacking-non-sequence",
        "msg_text": "Attempting to unpack a non-sequence%s",
        "msg_xpln": "Used when something which is not a sequence is used in an "
        "unpack assignment",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E0701",
        "msg_sym": "bad-except-order",
        "msg_text": "Bad except clauses order (%s)",
        "msg_xpln": "Used when except clauses are not in the correct order (from the "
        "more specific to the more generic). If you don't fix the order, "
        "some exceptions may not be caught by the most specific handler.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0702",  # reported by Python and MyPy
        "msg_sym": "raising-bad-type",
        "msg_text": "Raising %s while only classes or instances are allowed",
        "msg_xpln": "Used when something which is neither a class, an instance or a "
        "string is raised (i.e. a `TypeError` will be raised).",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E0703",  # reported by Python and MyPy
        "msg_sym": "bad-exception-context",
        "msg_text": "Exception context set to something which is not an exception, "
        "nor None",
        "msg_xpln": 'Used when using the syntax "raise ... from ...", where the '
        "exception context is not an exception, nor None.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E0704",
        "msg_sym": "misplaced-bare-raise",
        "msg_text": "The raise statement is not inside an except clause",
        "msg_xpln": "Used when a bare raise is not used inside an except clause. "
        "This generates an error, since there are no active exceptions "
        "to be reraised. An exception to this rule is represented by a "
        "bare raise inside a finally clause, which might work, as long "
        "as an exception is raised inside the try block, but it is "
        "nevertheless a code smell that must not be relied upon.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0710",
        "msg_sym": "raising-non-exception",
        "msg_text": "Raising a new style class which doesn't inherit from "
        "BaseException",
        "msg_xpln": "Used when a new style class which doesn't inherit from "
        "BaseException is raised.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E0711",
        "msg_sym": "notimplemented-raised",
        "msg_text": "NotImplemented raised - should raise NotImplementedError",
        "msg_xpln": "Used when NotImplemented is raised instead of "
        "NotImplementedError",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E0712",
        "msg_sym": "catching-non-exception",
        "msg_text": "Catching an exception which doesn't inherit from Exception: %s",
        "msg_xpln": "Used when a class which doesn't inherit from Exception is used "
        "as an exception in an except clause.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1003",
        "msg_sym": "bad-super-call",
        "msg_text": "Bad first argument %r given to super()",
        "msg_xpln": "Used when another argument than the current class is given as "
        "first argument of the super builtin.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1101",
        "msg_sym": "no-member",
        "msg_text": "%s %r has no %r member%s",
        "msg_xpln": "Used when a variable is accessed for an unexistent member.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1102",
        "msg_sym": "not-callable",
        "msg_text": "%s is not callable",
        "msg_xpln": "Used when an object being called has been inferred to a non "
        "callable object.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1111",
        "msg_sym": "assignment-from-no-return",
        "msg_text": "Assigning to function call which doesn't return",  # TODO: to => from
        "msg_xpln": "Used when an assignment is done on a function call but the "
        "inferred function doesn't return anything.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1120",
        "msg_sym": "no-value-for-parameter",
        "msg_text": "No value for argument %s in %s call",
        "msg_xpln": "Used when a function call passes too few arguments.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1121",
        "msg_sym": "too-many-function-args",
        "msg_text": "Too many positional arguments for %s call",
        "msg_xpln": "Used when a function call passes too many positional arguments.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1123",
        "msg_sym": "unexpected-keyword-arg",
        "msg_text": "Unexpected keyword argument %r in %s call",
        "msg_xpln": "Used when a function call passes a keyword argument that "
        "doesn't correspond to one of the function's parameter names.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1124",
        "msg_sym": "redundant-keyword-arg",
        "msg_text": "Argument %r passed by position and keyword in %s call",
        "msg_xpln": "Used when a function call would result in assigning multiple "
        "values to a function parameter, one value from a positional "
        "argument and one from a keyword argument.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1125",
        "msg_sym": "missing-kwoa",
        "msg_text": "Missing mandatory keyword argument %r in %s call",
        "msg_xpln": "Used when a function call does not pass a mandatory "
        "keyword-only argument.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1126",
        "msg_sym": "invalid-sequence-index",
        "msg_text": "Sequence index is not an int, slice, or instance with __index__",
        "msg_xpln": "Used when a sequence type is indexed with an invalid type. "
        "Valid types are ints, slices, and objects with an __index__ "
        "method.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1127",
        "msg_sym": "invalid-slice-index",
        "msg_text": "Slice index is not an int, None, or instance with __index__",
        "msg_xpln": "Used when a slice index is not an integer, None, or an object "
        "with an __index__ method.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1128",
        "msg_sym": "assignment-from-none",
        "msg_text": "Assigning to function call which only returns None",
        "msg_xpln": "Used when an assignment is done on a function call but the "
        "inferred function returns nothing but None.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1129",
        "msg_sym": "not-context-manager",
        "msg_text": "Context manager '%s' doesn't implement __enter__ and __exit__.",
        "msg_xpln": "Used when an instance in a with statement doesn't implement the "
        "context manager protocol(__enter__/__exit__).",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1130",
        "msg_sym": "invalid-unary-operand-type",
        "msg_text": "",
        "msg_xpln": "Emitted when a unary operand is used on an object which does "
        "not support this type of operation.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1131",
        "msg_sym": "unsupported-binary-operation",
        "msg_text": "",
        "msg_xpln": "Emitted when a binary arithmetic operation between two operands "
        "is not supported.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1132",
        "msg_sym": "repeated-keyword",
        "msg_text": "Got multiple values for keyword argument %r in function call",
        "msg_xpln": "Emitted when a function call got multiple values for a keyword.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1133",
        "msg_sym": "not-an-iterable",
        "msg_text": "Non-iterable value %s is used in an iterating context",
        "msg_xpln": "Used when a non-iterable value is used in place where iterable "
        "is expected",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1134",
        "msg_sym": "not-a-mapping",
        "msg_text": "Non-mapping value %s is used in a mapping context",
        "msg_xpln": "Used when a non-mapping value is used in place where mapping is "
        "expected",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1135",
        "msg_sym": "unsupported-membership-test",
        "msg_text": "Value '%s' doesn't support membership test",
        "msg_xpln": "Emitted when an instance in membership test expression doesn't "
        "implement membership protocol "
        "(__contains__/__iter__/__getitem__).",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1136",
        "msg_sym": "unsubscriptable-object",
        "msg_text": "Value '%s' is unsubscriptable",
        "msg_xpln": "Emitted when a subscripted value doesn't support subscription "
        "(i.e. doesn't define __getitem__ method).",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1137",
        "msg_sym": "unsupported-assignment-operation",
        "msg_text": "%r does not support item assignment",
        "msg_xpln": "Emitted when an object does not support item assignment (i.e. "
        "doesn't define __setitem__ method).",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1138",
        "msg_sym": "unsupported-delete-operation",
        "msg_text": "%r does not support item deletion",
        "msg_xpln": "Emitted when an object does not support item deletion (i.e. "
        "doesn't define __delitem__ method).",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1139",
        "msg_sym": "invalid-metaclass",
        "msg_text": "Invalid metaclass %r used",
        "msg_xpln": "Emitted whenever we can detect that a class is using, as a "
        "metaclass, something which might be invalid for using as a "
        "metaclass.",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1140",
        "msg_sym": "unhashable-dict-key",
        "msg_text": "Dict key is unhashable",
        "msg_xpln": "Emitted when a dict key is not hashable (i.e. doesn't define "
        "__hash__ method).",
        "tho_xpln": "",
        "usage": "typing",
    },
    {
        "msg_id": "E1200",
        "msg_sym": "logging-unsupported-format",
        "msg_text": "Unsupported logging format character %r (%#02x) at index %d",
        "msg_xpln": "Used when an unsupported format character is used in a logging "
        "statement format string.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1201",
        "msg_sym": "logging-format-truncated",
        "msg_text": "Logging format string ends in middle of conversion specifier",
        "msg_xpln": "Used when a logging statement format string terminates before "
        "the end of a conversion specifier.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1205",
        "msg_sym": "logging-too-many-args",
        "msg_text": "Too many arguments for logging format string",
        "msg_xpln": "Used when a logging format string is given too many arguments.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1206",
        "msg_sym": "logging-too-few-args",
        "msg_text": "Not enough arguments for logging format string",
        "msg_xpln": "Used when a logging format string is given too few arguments.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1300",
        "msg_sym": "bad-format-character",
        "msg_text": "Unsupported format character %r (%#02x) at index %d",
        "msg_xpln": "Used when an unsupported format character is used in a format "
        "string.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1301",
        "msg_sym": "truncated-format-string",
        "msg_text": "Format string ends in middle of conversion specifier",
        "msg_xpln": "Used when a format string terminates before the end of a "
        "conversion specifier.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1302",
        "msg_sym": "mixed-format-string",
        "msg_text": "Mixing named and unnamed conversion specifiers in format string",
        "msg_xpln": "Used when a format string contains both named (e.g. '%(foo)d') "
        "and unnamed (e.g. '%d') conversion specifiers. This is also "
        "used when a named conversion specifier contains * for the "
        "minimum field width and/or precision.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1303",
        "msg_sym": "format-needs-mapping",
        "msg_text": "Expected mapping for format string, not %s",
        "msg_xpln": "Used when a format string that uses named conversion specifiers "
        "is used with an argument that is not a mapping.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1304",
        "msg_sym": "missing-format-string-key",
        "msg_text": "Missing key %r in format string dictionary",
        "msg_xpln": "Used when a format string that uses named conversion specifiers "
        "is used with a dictionary that doesn't contain all the keys "
        "required by the format string.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1305",
        "msg_sym": "too-many-format-args",
        "msg_text": "Too many arguments for format string",
        "msg_xpln": "Used when a format string that uses unnamed conversion "
        "specifiers is given too many arguments.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1306",
        "msg_sym": "too-few-format-args",
        "msg_text": "Not enough arguments for format string",
        "msg_xpln": "Used when a format string that uses unnamed conversion "
        "specifiers is given too few arguments",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1310",
        "msg_sym": "bad-str-strip-call",
        "msg_text": "Suspicious argument in %s.%s call",
        "msg_xpln": "The argument to a str.{l,r,}strip call contains a duplicate "
        "character,",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1507",
        "msg_sym": "invalid-envvar-value",
        "msg_text": "%s does not support %s type argument",
        "msg_xpln": "Env manipulation functions support only string type arguments. "
        "See https://docs.python.org/3/library/os.html#os.getenv.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "E1601",
        "msg_sym": "print-statement",
        "msg_text": "print statement used",
        "msg_xpln": "Used when a print statement is used (`print` is a function in "
        "Python 3)",
        "tho_xpln": "",
        "usage": "skip",
    },  # Nice SyntaxError from Python
    {
        "msg_id": "E1602",
        "msg_sym": "parameter-unpacking",
        "msg_text": "Parameter unpacking specified",
        "msg_xpln": "Used when parameter unpacking is specified for a "
        "function(Python 3 doesn't allow it)",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E1603",
        "msg_sym": "unpacking-in-except",
        "msg_text": "Implicit unpacking of exceptions is not supported in Python 3",
        "msg_xpln": "Python3 will not allow implicit unpacking of exceptions in "
        "except clauses. See http://www.python.org/dev/peps/pep-3110/",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E1604",
        "msg_sym": "old-raise-syntax",
        "msg_text": "Use raise ErrorClass(args) instead of raise ErrorClass, args.",
        "msg_xpln": "Used when the alternate raise syntax 'raise foo, bar' is used "
        "instead of 'raise foo(bar)'.",
        "tho_xpln": "",
        "usage": "skip",
    },  # Looks like this doesn't work
    {
        "msg_id": "E1605",
        "msg_sym": "backtick",
        "msg_text": "Use of the `` operator",
        "msg_xpln": 'Used when the deprecated "``" (backtick) operator is used '
        "instead of the str() function.",
        "tho_xpln": "",
        "usage": "skip",
    },  # Looks like this doesn't work
    {
        "msg_id": "E1700",
        "msg_sym": "yield-inside-async-function",
        "msg_text": "Yield inside async function",
        "msg_xpln": "Used when an `yield` or `yield from` statement is found inside "
        "an async function. This message can't be emitted when using "
        "Python < 3.5.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "E1701",
        "msg_sym": "not-async-context-manager",
        "msg_text": "Async context manager '%s' doesn't implement __aenter__ and "
        "__aexit__.",
        "msg_xpln": "Used when an async context manager is used with an object that "
        "does not implement the async context management protocol. This "
        "message can't be emitted when using Python < 3.5.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "F0001",
        "msg_sym": "fatal",
        "msg_text": "",
        "msg_xpln": "Used when an error occurred preventing the analysis of a module "
        "(unable to find it for instance).",
        "tho_xpln": "Program analyzer internal error. Used when an error occurred preventing the analysis of a module "
        "(unable to find it for instance).",
        "usage": "warning",
    },
    {
        "msg_id": "F0002",
        "msg_sym": "astroid-error",
        "msg_text": "%s: %s",
        "msg_xpln": "Used when an unexpected error occurred while building the "
        "Astroid representation. This is usually accompanied by a "
        "traceback. Please report such errors !",
        "tho_xpln": "Program analyzer internal error. Used when an unexpected error occurred while building the "
        "Astroid representation. This is usually accompanied by a "
        "traceback. Please report such errors !",
        "usage": "warning",
    },
    {
        "msg_id": "F0010",
        "msg_sym": "parse-error",
        "msg_text": "error while code parsing: %s",
        "msg_xpln": "Used when an exception occurred while building the Astroid "
        "representation which could be handled by astroid.",
        "tho_xpln": "Program analyzer internal error. Used when an exception occurred while building the Astroid "
        "representation which could be handled by astroid.",
        "usage": "warning",
    },
    {
        "msg_id": "F0202",
        "msg_sym": "method-check-failed",
        "msg_text": "Unable to check methods signature (%s / %s)",
        "msg_xpln": "Used when Pylint has been unable to check methods signature "
        "compatibility for an unexpected reason. Please report this kind "
        "if you don't make sense of it.",
        "tho_xpln": "Program analyzer internal error. Used when Pylint has been unable to check methods signature "
        "compatibility for an unexpected reason. Please report this kind "
        "if you don't make sense of it.",
        "usage": "warning",
    },
    {
        "msg_id": "I0001",
        "msg_sym": "raw-checker-failed",
        "msg_text": "Unable to run raw checkers on built-in module %s",
        "msg_xpln": "Used to inform that a built-in module has not been checked "
        "using the raw checkers.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "I0010",
        "msg_sym": "bad-inline-option",
        "msg_text": "Unable to consider inline option %r",
        "msg_xpln": "Used when an inline option is either badly formatted or can't "
        "be used inside modules.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "I0011",
        "msg_sym": "locally-disabled",
        "msg_text": "Locally disabling %s (%s)",
        "msg_xpln": "Used when an inline option disables a message or a messages "
        "category.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "I0012",
        "msg_sym": "locally-enabled",
        "msg_text": "Locally enabling %s (%s)",
        "msg_xpln": "Used when an inline option enables a message or a messages "
        "category.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "I0013",
        "msg_sym": "file-ignored",
        "msg_text": "Ignoring entire file",
        "msg_xpln": "Used to inform that the file will not be checked",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "I0020",
        "msg_sym": "suppressed-message",
        "msg_text": "Suppressed %s (from line %d)",
        "msg_xpln": "A message was triggered on a line, but suppressed explicitly by "
        "a disable= comment in the file. This message is not generated "
        "for messages that are ignored due to configuration settings.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "I0021",
        "msg_sym": "useless-suppression",
        "msg_text": "Useless suppression of %s",
        "msg_xpln": "Reported when a message is explicitly disabled for a line or a "
        "block of code, but never triggered.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "I0022",
        "msg_sym": "deprecated-pragma",
        "msg_text": 'Pragma "%s" is deprecated, use "%s" instead',
        "msg_xpln": "Some inline pylint options have been renamed or reworked, only "
        "the most recent form should be used. NOTE:skip-all is only "
        "available with pylint >= 0.26",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "I0023",
        "msg_sym": "use-symbolic-message-instead",
        "msg_text": "",
        "msg_xpln": "Used when a message is enabled or disabled by id.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "I1101",
        "msg_sym": "c-extension-no-member",
        "msg_text": "%s %r has no %r member%s, but source is unavailable. Consider "
        "adding this module to extension-pkg-whitelist if you want to "
        "perform analysis based on run-time introspection of living "
        "objects.",
        "msg_xpln": "Used when a variable is accessed for non-existent member of C "
        "extension. Due to unavailability of source static analysis is "
        "impossible, but it may be performed by introspecting living "
        "objects in run-time.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0123",
        "msg_sym": "literal-comparison",
        "msg_text": "Comparison to literal",
        "msg_xpln": "Used when comparing an object to a literal, which is usually "
        "what you do not want to do, since you can compare to a "
        "different literal than what was expected altogether.",
        "tho_xpln": 'Are you sure you want to compare with "is"/"is not" instead of "=="/"!=" ?',
        "usage": "warning",
    },
    {
        "msg_id": "R0124",
        "msg_sym": "comparison-with-itself",
        "msg_text": "Redundant comparison - %s",
        "msg_xpln": "Used when something is compared against itself.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "R0201",
        "msg_sym": "no-self-use",
        "msg_text": "Method could be a function",
        "msg_xpln": "Used when a method doesn't use its bound instance, and so could "
        "be written as a function.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0202",
        "msg_sym": "no-classmethod-decorator",
        "msg_text": "Consider using a decorator instead of calling classmethod",
        "msg_xpln": "Used when a class method is defined without using the decorator "
        "syntax.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R0203",
        "msg_sym": "no-staticmethod-decorator",
        "msg_text": "Consider using a decorator instead of calling staticmethod",
        "msg_xpln": "Used when a static method is defined without using the "
        "decorator syntax.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R0205",
        "msg_sym": "useless-object-inheritance",
        "msg_text": "Class %r inherits from object, can be safely removed from bases "
        "in python3",
        "msg_xpln": "Used when a class inherit from object, which under python3 is "
        "implicit, hence can be safely removed from bases.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R0401",
        "msg_sym": "cyclic-import",
        "msg_text": "Cyclic import (%s)",
        "msg_xpln": "Used when a cyclic import between two or more modules is "
        "detected.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0801",
        "msg_sym": "duplicate-code",
        "msg_text": "Similar lines in %s files",
        "msg_xpln": "Indicates that a set of similar lines has been detected among "
        "multiple file. This usually means that the code should be "
        "refactored to avoid this duplication.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R0901",
        "msg_sym": "too-many-ancestors",
        "msg_text": "Too many ancestors (%s/%s)",
        "msg_xpln": "Used when class has too many parent classes, try to reduce this "
        "to get a simpler (and so easier to use) class.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0902",
        "msg_sym": "too-many-instance-attributes",
        "msg_text": "Too many instance attributes (%s/%s)",
        "msg_xpln": "Used when class has too many instance attributes, try to reduce "
        "this to get a simpler (and so easier to use) class.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0903",
        "msg_sym": "too-few-public-methods",
        "msg_text": "Too few public methods (%s/%s)",
        "msg_xpln": "Used when class has too few public methods, so be sure it's "
        "really worth it.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0904",
        "msg_sym": "too-many-public-methods",
        "msg_text": "Too many public methods (%s/%s)",
        "msg_xpln": "Used when class has too many public methods, try to reduce this "
        "to get a simpler (and so easier to use) class.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0911",
        "msg_sym": "too-many-return-statements",
        "msg_text": "Too many return statements (%s/%s)",
        "msg_xpln": "Used when a function or method has too many return statement, "
        "making it hard to follow.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0912",
        "msg_sym": "too-many-branches",
        "msg_text": "Too many branches (%s/%s)",
        "msg_xpln": "Used when a function or method has too many branches, making it "
        "hard to follow.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0913",
        "msg_sym": "too-many-arguments",
        "msg_text": "Too many arguments (%s/%s)",
        "msg_xpln": "Used when a function or method takes too many arguments.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0914",
        "msg_sym": "too-many-locals",
        "msg_text": "Too many local variables (%s/%s)",
        "msg_xpln": "Used when a function or method has too many local variables.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R0915",
        "msg_sym": "too-many-statements",
        "msg_text": "Too many statements (%s/%s)",
        "msg_xpln": "Used when a function or method has too many statements. You "
        "should then split it in smaller functions / methods.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R0916",
        "msg_sym": "too-many-boolean-expressions",
        "msg_text": "Too many boolean expressions in if statement (%s/%s)",
        "msg_xpln": "Used when an if statement contains too many boolean "
        "expressions.",
        "tho_xpln": "Consider simplifying the expression with helper variables or functions.",
        "usage": "enhancement",
    },
    {
        "msg_id": "R1701",
        "msg_sym": "consider-merging-isinstance",
        "msg_text": "Consider merging these isinstance calls to isinstance(%s, (%s))",
        "msg_xpln": "Used when multiple consecutive isinstance calls can be merged "
        "into one.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R1702",
        "msg_sym": "too-many-nested-blocks",
        "msg_text": "Too many nested blocks (%s/%s)",
        "msg_xpln": "Used when a function or a method has too many nested blocks. "
        "This makes the code less understandable and maintainable.",
        "tho_xpln": "Consider moving some of the code to helper functions.",
        "usage": "enhancement",
    },
    {
        "msg_id": "R1703",
        "msg_sym": "simplifiable-if-statement",
        "msg_text": "The if statement can be replaced with %s",
        "msg_xpln": "Used when an if statement can be replaced with 'bool(test)'.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R1704",
        "msg_sym": "redefined-argument-from-local",
        "msg_text": "Redefining argument with the local name %r",
        "msg_xpln": "Used when a local name is redefining an argument, which might "
        "suggest a potential error. This is taken in account only for a "
        "handful of name binding operations, such as for iteration, with "
        "statement assignment and exception handler assignment.",
        "tho_xpln": "Did you notice that an argument gets overwritten here?",
        "usage": "warning",
    },
    {
        "msg_id": "R1705",
        "msg_sym": "no-else-return",
        "msg_text": 'Unnecessary "%s" after "return"',
        "msg_xpln": "Used in order to highlight an unnecessary block of code "
        "following an if containing a return statement. As such, it will "
        "warn when it encounters an else following a chain of ifs, all "
        "of them containing a return statement.",
        "tho_xpln": "",
        "usage": "skip",
    },  # not sure if the recommended style is better (https://github.com/SoCo/SoCo/issues/500)
    {
        "msg_id": "R1706",
        "msg_sym": "consider-using-ternary",
        "msg_text": "Consider using ternary (%s)",
        "msg_xpln": "Used when one of known pre-python 2.5 ternary syntax is used.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R1707",
        "msg_sym": "trailing-comma-tuple",
        "msg_text": "Disallow trailing comma tuple",
        "msg_xpln": "In Python, a tuple is actually created by the comma symbol, not "
        "by the parentheses. Unfortunately, one can actually create a "
        "tuple by misplacing a trailing comma, which can lead to "
        "potential weird bugs in your code. You should always use "
        "parentheses explicitly for creating a tuple.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "R1708",
        "msg_sym": "stop-iteration-return",
        "msg_text": "Do not raise StopIteration in generator, use return statement "
        "instead",
        "msg_xpln": "According to PEP479, the raise of StopIteration to end the loop "
        "of a generator may lead to hard to find bugs. This PEP specify "
        "that raise StopIteration has to be replaced by a simple return "
        "statement",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "R1709",  # not sure what this means
        "msg_sym": "simplify-boolean-expression",
        "msg_text": "Boolean expression may be simplified to %s",
        "msg_xpln": "Emitted when redundant pre-python 2.5 ternary syntax is used.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R1710",
        "msg_sym": "inconsistent-return-statements",
        "msg_text": "Either all return statements in a function should return an "
        "expression, or none of them should.",
        "msg_xpln": "According to PEP8, if any return statement returns an "
        "expression, any return statements where no value is returned "
        "should explicitly state this as return None, and an explicit "
        "return statement should be present at the end of the function "
        "(if reachable)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "R1711",
        "msg_sym": "useless-return",
        "msg_text": "Useless return at end of function or method",
        "msg_xpln": 'Emitted when a single "return" or "return None" statement is '
        "found at the end of function or method definition. This "
        "statement can safely be removed because Python will implicitly "
        "return None",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "R1712",
        "msg_sym": "consider-swap-variables",
        "msg_text": "Consider using tuple unpacking for swapping variables",
        "msg_xpln": "You do not have to use a temporary variable in order to swap "
        'variables. Using "tuple unpacking" to directly swap variables '
        "makes the intention more clear.",
        "tho_xpln": "You do not have to use a temporary variable in order to swap "
        'variables. Using "tuple unpacking" to directly swap variables '
        "makes the intention more clear. "
        'Example: "a, b = b, a".',
        "usage": "enhancement",
    },
    {
        "msg_id": "R1713",
        "msg_sym": "consider-using-join",
        "msg_text": "Consider using str.join(sequence) for concatenating strings "
        "from an iterable",
        "msg_xpln": "Using str.join(sequence) is faster, uses less memory and "
        "increases readability compared to for-loop iteration.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R1714",
        "msg_sym": "consider-using-in",
        "msg_text": 'Consider merging these comparisons with "in" to %r',
        "msg_xpln": "To check if a variable is equal to one of many values,combine "
        "the values into a tuple and check if the variable is contained "
        '"in" it instead of checking for equality against each of the '
        "values.This is faster and less verbose.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R1715",
        "msg_sym": "consider-using-get",
        "msg_text": "Consider using dict.get for getting values from a dict if a key "
        "is present or a default if not",
        "msg_xpln": "Using the builtin dict.get for getting a value from a "
        "dictionary if a key is present or a default if not, is simpler "
        "and considered more idiomatic, although sometimes a bit slower",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R1716",
        "msg_sym": "chained-comparison",
        "msg_text": "Simplify chained comparison between the operands",
        "msg_xpln": "This message is emitted when pylint encounters boolean "
        'operation like"a < b and b < c", suggesting instead to refactor '
        'it to "a < b < c"',
        "tho_xpln": "",
        "usage": "skip",
    },  # IMO this is confusing syntax if one expects < to be binary op
    {
        "msg_id": "R1717",
        "msg_sym": "consider-using-dict-comprehension",
        "msg_text": "Consider using a dictionary comprehension",
        "msg_xpln": "Although there is nothing syntactically wrong with this code, "
        "it is hard to read and can be simplified to a dict "
        "comprehension. Also it is faster since you don't need to create "
        "another transient list",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "R1718",
        "msg_sym": "consider-using-set-comprehension",
        "msg_text": "Consider using a set comprehension",
        "msg_xpln": "Although there is nothing syntactically wrong with this code, "
        "it is hard to read and can be simplified to a set "
        "comprehension. Also it is faster since you don't need to create "
        "another transient list",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "W0101",
        "msg_sym": "unreachable",
        "msg_text": "Unreachable code",
        "msg_xpln": 'Used when there is some code behind a "return" or "raise" '
        "statement, which will never be accessed.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0102",
        "msg_sym": "dangerous-default-value",
        "msg_text": "Dangerous default value %s as argument",
        "msg_xpln": "Used when a mutable value as list or dictionary is detected in "
        "a default value for an argument.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0104",
        "msg_sym": "pointless-statement",
        "msg_text": "Statement seems to have no effect",
        "msg_xpln": "Used when a statement doesn't have any effect.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0105",
        "msg_sym": "pointless-string-statement",
        "msg_text": "String statement has no effect",
        "msg_xpln": "Used when a string is used as a statement (which of course has "
        "no effect). This is a particular case of W0104 with its own "
        "message so you can easily disable it if you're using those "
        "strings as documentation, instead of comments.",
        "tho_xpln": "",
        "usage": "skip",
    },  # string is useful for commenting out. Hard to misread such cases.
    {
        "msg_id": "W0106",
        "msg_sym": "expression-not-assigned",
        "msg_text": 'Expression "%s" is assigned to nothing',
        "msg_xpln": "Used when an expression that is not a function call is assigned "
        "to nothing. Probably something else was intended.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0107",
        "msg_sym": "unnecessary-pass",
        "msg_text": "Unnecessary pass statement",
        "msg_xpln": 'Used when a "pass" statement that can be avoided is '
        "encountered.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "W0108",
        "msg_sym": "unnecessary-lambda",
        "msg_text": "Lambda may not be necessary",
        "msg_xpln": "Used when the body of a lambda expression is a function call on "
        "the same argument list as the lambda itself; such lambda "
        "expressions are in all but a few cases replaceable with the "
        "function being called in the body of the lambda.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0109",
        "msg_sym": "duplicate-key",
        "msg_text": "Duplicate key %r in dictionary",
        "msg_xpln": "Used when a dictionary expression binds the same key multiple "
        "times.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0111",
        "msg_sym": "assign-to-new-keyword",
        "msg_text": "Name %s will become a keyword in Python %s",
        "msg_xpln": "Used when assignment will become invalid in future Python "
        "release due to introducing new keyword.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0120",
        "msg_sym": "useless-else-on-loop",
        "msg_text": "Else clause on loop without a break statement",
        "msg_xpln": "Loops should only have an else clause if they can exit early "
        "with a break statement, otherwise the statements under else "
        "should be on the same scope as the loop itself.",
        "tho_xpln": "",
        "usage": "enhancement",
    },  # See https://github.com/PyCQA/pylint/issues/1272
    {
        "msg_id": "W0122",
        "msg_sym": "exec-used",
        "msg_text": "Use of exec",
        "msg_xpln": 'Used when you use the "exec" statement (function for Python 3), '
        "to discourage its usage. That doesn't mean you cannot use it !",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "W0123",
        "msg_sym": "eval-used",
        "msg_text": "Use of eval",
        "msg_xpln": 'Used when you use the "eval" function, to discourage its usage. '
        "Consider using `ast.literal_eval` for safely evaluating strings "
        "containing Python expressions from untrusted sources.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "W0124",
        "msg_sym": "confusing-with-statement",
        "msg_text": 'Following "as" with another context manager looks like a tuple.',
        "msg_xpln": "Emitted when a `with` statement component returns multiple "
        "values and uses name binding with `as` only for a part of those "
        "values, as in with ctx() as a, b. This can be misleading, since "
        "it's not clear if the context manager returns a tuple or if the "
        "node without a name binding is another context manager.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0125",
        "msg_sym": "using-constant-test",
        "msg_text": "Using a conditional statement with a constant value",
        "msg_xpln": "Emitted when a conditional statement (if or ternary if) uses a "
        "constant value for its test. This might not be what the user "
        "intended to do.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0143",
        "msg_sym": "comparison-with-callable",
        "msg_text": "Comparing against a callable, did you omit the parenthesis?",
        "msg_xpln": "This message is emitted when pylint detects that a comparison "
        "with a callable was made, which might suggest that some "
        "parenthesis were omitted, resulting in potential unwanted "
        "behaviour.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0150",
        "msg_sym": "lost-exception",
        "msg_text": "%s statement in finally block may swallow exception",
        "msg_xpln": "Used when a break or a return statement is found inside the "
        "finally clause of a try...finally block: the exceptions raised "
        "in the try clause will be silently swallowed instead of being "
        "re-raised.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0199",
        "msg_sym": "assert-on-tuple",
        "msg_text": "Assert called on a 2-uple. Did you mean 'assert x,y'?",
        "msg_xpln": "A call of assert on a tuple will always evaluate to true if the "
        "tuple is not empty, and will always evaluate to false if it is.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0201",
        "msg_sym": "attribute-defined-outside-init",
        "msg_text": "Attribute %r defined outside __init__",
        "msg_xpln": "Used when an instance attribute is defined outside the __init__ "
        "method.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "W0211",
        "msg_sym": "bad-staticmethod-argument",
        "msg_text": "Static method with %r as first argument",
        "msg_xpln": 'Used when a static method has "self" or a value specified in '
        "valid- classmethod-first-arg option or "
        "valid-metaclass-classmethod-first-arg option as first argument.",
        "tho_xpln": 'Static methods should not have "self" as first argument.',
        "usage": "warning",
    },
    {
        "msg_id": "W0212",
        "msg_sym": "protected-access",
        "msg_text": "Access to a protected member %s of a client class",
        "msg_xpln": "Used when a protected member (i.e. class member with a name "
        "beginning with an underscore) is access outside the class or a "
        "descendant of the class where it's defined.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0221",
        "msg_sym": "arguments-differ",
        "msg_text": "Parameters differ from %s %r method",
        "msg_xpln": "Used when a method has a different number of arguments than in "
        "the implemented interface or in an overridden method.",
        "tho_xpln": "",
        "usage": "warning",
    },  # looks like MyPy 0.620 doesn't catch this
    {
        "msg_id": "W0222",
        "msg_sym": "signature-differs",
        "msg_text": "Signature differs from %s %r method",
        "msg_xpln": "Used when a method signature is different than in the "
        "implemented interface or in an overridden method.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0223",
        "msg_sym": "abstract-method",
        "msg_text": "Method %r is abstract in class %r but is not overridden",
        "msg_xpln": "Used when an abstract method (i.e. raise NotImplementedError) "
        "is not overridden in concrete class.",
        "tho_xpln": "",
        "usage": "skip",
    },  # Can't decide if it's OK to leave abstract. https://stackoverflow.com/questions/30884804/pylint-for-half-implemented-abstract-classes
    {
        "msg_id": "W0231",
        "msg_sym": "super-init-not-called",
        "msg_text": "__init__ method from base class %r is not called",
        "msg_xpln": "Used when an ancestor class method has an __init__ method which "
        "is not called by a derived class.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0232",
        "msg_sym": "no-init",
        "msg_text": "Class has no __init__ method",
        "msg_xpln": "Used when a class has no __init__ method, neither its parent "
        "classes.",
        "tho_xpln": "",
        "usage": "skip",
    },  # so what?
    {
        "msg_id": "W0233",
        "msg_sym": "non-parent-init-called",
        "msg_text": "__init__ method from a non direct base class %r is called",
        "msg_xpln": "Used when an __init__ method is called on a class which is not "
        "in the direct ancestors for the analysed class.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0235",
        "msg_sym": "useless-super-delegation",
        "msg_text": "Useless super delegation in method %r",
        "msg_xpln": "Used whenever we can detect that an overridden method is "
        "useless, relying on super() delegation to do the same thing as "
        "another method from the MRO.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "W0301",
        "msg_sym": "unnecessary-semicolon",
        "msg_text": "Unnecessary semicolon",
        "msg_xpln": 'Used when a statement is ended by a semi-colon (";"), which '
        "isn't necessary (that's python, not C ;).",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "W0311",
        "msg_sym": "bad-indentation",
        "msg_text": "Bad indentation. Found %s %s, expected %s",
        "msg_xpln": "Used when an unexpected number of indentation's tabulations or "
        "spaces has been found.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0312",
        "msg_sym": "mixed-indentation",
        "msg_text": "Found indentation with %ss instead of %ss",
        "msg_xpln": "Used when there are some mixed tabs and spaces in a module.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0401",
        "msg_sym": "wildcard-import",
        "msg_text": "Wildcard import %s",
        "msg_xpln": "Used when `from module import *` is detected.",
        "tho_xpln": '"from ____ import *" is not recommended. It\'s better to import only required names from the module',
        "usage": "enhancement",
    },
    {
        "msg_id": "W0402",
        "msg_sym": "deprecated-module",
        "msg_text": "Uses of a deprecated module %r",
        "msg_xpln": "Used a module marked as deprecated is imported.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0404",
        "msg_sym": "reimported",
        "msg_text": "Reimport %r (imported line %s)",
        "msg_xpln": "Used when a module is reimported multiple times.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0406",
        "msg_sym": "import-self",
        "msg_text": "Module import itself",
        "msg_xpln": "This usually happens when you give your script the same "
        "as name a library module you are trying to import. "
        "This won't work, because your module will shadow the library module.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0410",
        "msg_sym": "misplaced-future",
        "msg_text": "__future__ import is not the first non docstring statement",
        "msg_xpln": "Python 2.5 and greater require __future__ import to be the "
        "first non docstring statement in the module.",
        "tho_xpln": "",
        "usage": "skip",
    },  # Python explains it in SyntaxError
    {
        "msg_id": "W0511",
        "msg_sym": "fixme",
        "msg_text": "",
        "msg_xpln": "Used when a warning note as FIXME or XXX is detected.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "W0601",
        "msg_sym": "global-variable-undefined",
        "msg_text": "Global variable %r undefined at the module level",
        "msg_xpln": 'Used when a variable is defined through the "global" statement '
        "but the variable is not defined in the module scope.",
        "tho_xpln": "",
        "usage": "warning",
    },  # Better message than MyPy
    {
        "msg_id": "W0602",
        "msg_sym": "global-variable-not-assigned",
        "msg_text": "Using global for %r but no assignment is done",
        "msg_xpln": 'Used when a variable is defined through the "global" statement '
        "but no assignment to this variable is done.",
        "tho_xpln": "You don't need \"global\" statement if you don't want to update the variable.",
        "usage": "warning",
    },
    {
        "msg_id": "W0603",
        "msg_sym": "global-statement",
        "msg_text": "Using the global statement",
        "msg_xpln": 'Used when you use the "global" statement to update a global '
        "variable. Pylint just tries to discourage this usage. That "
        "doesn't mean you cannot use it !",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "W0604",
        "msg_sym": "global-at-module-level",
        "msg_text": "Using the global statement at the module level",
        "msg_xpln": 'Used when you use the "global" statement at the module level '
        "since it has no effect",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0611",
        "msg_sym": "unused-import",
        "msg_text": "Unused %s",
        "msg_xpln": "Used when an imported module or variable is not used.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0612",
        "msg_sym": "unused-variable",
        "msg_text": "Unused variable %r",
        "msg_xpln": "Used when a variable is defined but not used.",
        "tho_xpln": "Looks like the variable is defined (or imported) but not used.",
        "usage": "warning",
    },  # NB! Only applies to local variables
    {
        "msg_id": "W0613",
        "msg_sym": "unused-argument",
        "msg_text": "Unused argument %r",
        "msg_xpln": "Used when a function or method argument is not used.",
        "tho_xpln": "If you want to keep the argument and silence this warning, "
        'then add comment "#pylint: disable=unused-argument" as first line in your function body.',
        "usage": "warning",
    },
    {
        "msg_id": "W0614",
        "msg_sym": "unused-wildcard-import",
        "msg_text": "Unused import %s from wildcard import",
        "msg_xpln": "Used when an imported module or variable is not used from a "
        "`'from X import *'` style import.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "W0621",
        "msg_sym": "redefined-outer-name",
        "msg_text": "Redefining name %r from outer scope (line %s)",
        "msg_xpln": "Used when a variable's name hides a name defined in the outer "
        "scope.",
        "tho_xpln": "It looks like the local variable is "
        "hiding a global variable with the same name.\n\n"
        "Most likely there is nothing wrong with this. "
        "I just wanted to remind you that you can't access the global variable like this. "
        "If you knew it then please ignore the warning.\n\n"
        "If you don't want to see this reminder in the future, then add "
        '"redefined-outer-name" (without quotes) into "Tools → Options → Assistant → Disabled checks".',
        "usage": "warning",
    },
    {
        "msg_id": "W0622",
        "msg_sym": "redefined-builtin",
        "msg_text": "Redefining built-in %r",
        "msg_xpln": "Used when a variable or function override a built-in.",
        "tho_xpln": "",
        "usage": "enhancement",
    },  # warning about "list", "min" and "max" would cause too much confusion
    {
        "msg_id": "W0623",
        "msg_sym": "redefine-in-handler",
        "msg_text": "Redefining name %r from %s in exception handler",
        "msg_xpln": "Used when an exception handler assigns the exception to an "
        "existing name",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0631",
        "msg_sym": "undefined-loop-variable",
        "msg_text": "Using possibly undefined loop variable %r",
        "msg_xpln": "Used when a loop variable (i.e. defined by a for loop or a list "
        "comprehension or a generator expression) is used outside the "
        "loop.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0640",
        "msg_sym": "cell-var-from-loop",
        "msg_text": "Cell variable %s defined in loop",
        "msg_xpln": "A variable used in a closure is defined in a loop. This will "
        "result in all closures using the same value for the closed-over "
        "variable.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0641",
        "msg_sym": "possibly-unused-variable",
        "msg_text": "Possibly unused variable %r",
        "msg_xpln": "Used when a variable is defined but might not be used. The "
        "possibility comes from the fact that locals() might be used, "
        "which could consume or not the said variable",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0642",
        "msg_sym": "self-cls-assignment",
        "msg_text": "Invalid assignment to %s in method",
        "msg_xpln": "Invalid assignment to self or cls in instance or class method "
        "respectively.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0702",
        "msg_sym": "bare-except",
        "msg_text": "No exception type(s) specified",
        "msg_xpln": "Used when an except clause doesn't specify exceptions type to "
        "catch.",
        "tho_xpln": "Used when an except clause doesn't specify exceptions type to catch. "
        "Did you mean to catch also SystemExit and KeyboardInterrupt? "
        'If not then prefer "except Exception:".',
        "usage": "enhancement",
    },
    {
        "msg_id": "W0703",
        "msg_sym": "broad-except",
        "msg_text": "Catching too general exception %s",
        "msg_xpln": "Used when an except catches a too general exception, possibly "
        "burying unrelated errors.",
        "tho_xpln": "This may silence unrelated errors. Consider using more narrow "
        ' type or several types, eg. "except (ZeroDivisionError, IndexError):".',
        "usage": "enhancement",
    },
    {
        "msg_id": "W0705",
        "msg_sym": "duplicate-except",
        "msg_text": "Catching previously caught exception type %s",
        "msg_xpln": "Used when an except catches a type that was already caught by a "
        "previous handler.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0706",
        "msg_sym": "try-except-raise",
        "msg_text": "The except handler raises immediately",
        "msg_xpln": "Used when an except handler uses raise as its first or only "
        "operator. This is useless because it raises back the exception "
        "immediately. Remove the raise operator or the entire "
        "try-except-raise block!",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0711",
        "msg_sym": "binary-op-exception",
        "msg_text": 'Exception to catch is the result of a binary "%s" operation',
        "msg_xpln": 'Used when the exception to catch is of the form "except A or '
        'B:". If intending to catch multiple, rewrite as "except (A, '
        'B):"',
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W0715",
        "msg_sym": "raising-format-tuple",
        "msg_text": "Exception arguments suggest string formatting might be intended",
        "msg_xpln": "Used when passing multiple arguments to an exception "
        "constructor, the first of them a string literal containing what "
        "appears to be placeholders intended for formatting",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1113",
        "msg_sym": "keyword-arg-before-vararg",
        "msg_text": "Keyword argument before variable positional arguments list in "
        "the definition of %s function",
        "msg_xpln": "When defining a keyword argument before variable positional "
        "arguments, one can end up in having multiple values passed for "
        "the aforementioned parameter in case the method is called with "
        "keyword arguments.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1201",
        "msg_sym": "logging-not-lazy",
        "msg_text": "Specify string format arguments as logging function parameters",
        "msg_xpln": "Used when a logging statement has a call form of "
        '"logging.<logging method>(format_string % (format_args...))". '
        "Such calls should leave string interpolation to the logging "
        'method itself and be written "logging.<logging '
        'method>(format_string, format_args...)" so that the program may '
        "avoid incurring the cost of the interpolation in those cases in "
        "which no message will be logged. For more, see "
        "http://www.python.org/dev/peps/pep-0282/.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "W1202",
        "msg_sym": "logging-format-interpolation",
        "msg_text": "Use % formatting in logging functions and pass the % parameters "
        "as arguments",
        "msg_xpln": "Used when a logging statement has a call form of "
        '"logging.<logging '
        'method>(format_string.format(format_args...))". Such calls '
        "should use % formatting instead, but leave interpolation to the "
        "logging function by passing the parameters as arguments.",
        "tho_xpln": "",
        "usage": "skip",
    },  # Don't want to force this
    {
        "msg_id": "W1203",
        "msg_sym": "logging-fstring-interpolation",
        "msg_text": "Use % formatting in logging functions and pass the % parameters "
        "as arguments",
        "msg_xpln": "Used when a logging statement has a call form of "
        '"logging.method(f"..."))". Such calls should use % formatting '
        "instead, but leave interpolation to the logging function by "
        "passing the parameters as arguments.",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "W1300",
        "msg_sym": "bad-format-string-key",
        "msg_text": "Format string dictionary key should be a string, not %s",
        "msg_xpln": "Used when a format string that uses named conversion specifiers "
        "is used with a dictionary whose keys are not all strings.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1301",
        "msg_sym": "unused-format-string-key",
        "msg_text": "Unused key %r in format string dictionary",
        "msg_xpln": "Used when a format string that uses named conversion specifiers "
        "is used with a dictionary that contains keys not required by "
        "the format string.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1302",
        "msg_sym": "bad-format-string",
        "msg_text": "Invalid format string",
        "msg_xpln": "Used when a PEP 3101 format string is invalid. This message "
        "can't be emitted when using Python < 2.7.",
        "tho_xpln": "Used when a PEP 3101 format string is invalid.",
        "usage": "warning",
    },
    {
        "msg_id": "W1303",
        "msg_sym": "missing-format-argument-key",
        "msg_text": "Missing keyword argument %r for format string",
        "msg_xpln": "Used when a PEP 3101 format string that uses named fields "
        "doesn't receive one or more required keywords. This message "
        "can't be emitted when using Python < 2.7.",
        "tho_xpln": "Used when a PEP 3101 format string that uses named fields "
        "doesn't receive one or more required keywords.",
        "usage": "warning",
    },
    {
        "msg_id": "W1304",
        "msg_sym": "unused-format-string-argument",
        "msg_text": "Unused format argument %r",
        "msg_xpln": "Used when a PEP 3101 format string that uses named fields is "
        "used with an argument that is not required by the format "
        "string. This message can't be emitted when using Python < 2.7.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1305",
        "msg_sym": "format-combined-specification",
        "msg_text": "Format string contains both automatic field numbering and "
        "manual field specification",
        "msg_xpln": "Used when a PEP 3101 format string contains both automatic "
        "field numbering (e.g. '{}') and manual field specification "
        "(e.g. '{0}'). This message can't be emitted when using Python < "
        "2.7.",
        "tho_xpln": "Used when a PEP 3101 format string contains both automatic "
        "field numbering (e.g. '{}') and manual field specification "
        "(e.g. '{0}').",
        "usage": "warning",
    },
    {
        "msg_id": "W1306",
        "msg_sym": "missing-format-attribute",
        "msg_text": "Missing format attribute %r in format specifier %r",
        "msg_xpln": "Used when a PEP 3101 format string uses an attribute specifier "
        "({0.length}), but the argument passed for formatting doesn't "
        "have that attribute. This message can't be emitted when using "
        "Python < 2.7.",
        "tho_xpln": "Used when a PEP 3101 format string uses an attribute specifier "
        "({0.length}), but the argument passed for formatting doesn't "
        "have that attribute.",
        "usage": "warning",
    },
    {
        "msg_id": "W1307",
        "msg_sym": "invalid-format-index",
        "msg_text": "Using invalid lookup key %r in format specifier %r",
        "msg_xpln": "Used when a PEP 3101 format string uses a lookup specifier "
        "({a[1]}), but the argument passed for formatting doesn't "
        "contain or doesn't have that key as an attribute. This message "
        "can't be emitted when using Python < 2.7.",
        "tho_xpln": "Used when a PEP 3101 format string uses a lookup specifier "
        "({a[1]}), but the argument passed for formatting doesn't "
        "contain or doesn't have that key as an attribute.",
        "usage": "warning",
    },
    {
        "msg_id": "W1401",
        "msg_sym": "anomalous-backslash-in-string",
        "msg_text": "Anomalous backslash in string: '%s'. String constant might be "
        "missing an r prefix.",
        "msg_xpln": "Used when a backslash is in a literal string but not as an "
        "escape.",
        "tho_xpln_rst": "In regular string literals backslash is treated as a special character. "
        "If you meant to represent backslash itself, "
        """then you should double it, eg:\n\n``'C:\\\\Users\\\\Tim'``\n\n"""
        """or use raw-string literal, eg:\n\n``r'C:\\Users\\Tim'``""",
        "usage": "warning",
    },
    {
        "msg_id": "W1402",
        "msg_sym": "anomalous-unicode-escape-in-string",
        "msg_text": "Anomalous Unicode escape in byte string: '%s'. String constant "
        "might be missing an r or u prefix.",
        "msg_xpln": "Used when an escape like \\u is encountered in a byte string "
        "where it has no effect.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1501",
        "msg_sym": "bad-open-mode",
        "msg_text": '"%s" is not a valid mode for open.',
        "msg_xpln": "Python supports: r, w, a[, x] modes with b, +, and U (only with "
        "r) options. See "
        "http://docs.python.org/3/library/functions.html#open",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1503",
        "msg_sym": "redundant-unittest-assert",
        "msg_text": "Redundant use of %s with constant value %r",
        "msg_xpln": "The first argument of assertTrue and assertFalse is a "
        "condition. If a constant is passed as parameter, that condition "
        "will be always true. In this case a warning should be emitted.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1505",
        "msg_sym": "deprecated-method",
        "msg_text": "Using deprecated method %s()",
        "msg_xpln": "The method is marked as deprecated and will be removed in a "
        "future version of Python. Consider looking for an alternative "
        "in the documentation.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1506",
        "msg_sym": "bad-thread-instantiation",
        "msg_text": "threading.Thread needs the target function",
        "msg_xpln": "The warning is emitted when a threading.Thread class is "
        "instantiated without the target function being passed. By "
        "default, the first parameter is the group param, not the target "
        "param.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1507",
        "msg_sym": "shallow-copy-environ",
        "msg_text": "Using copy.copy(os.environ). Use os.environ.copy() instead.",
        "msg_xpln": "os.environ is not a dict object but proxy object, so shallow "
        "copy has still effects on original object. See "
        "https://bugs.python.org/issue15373 for reference.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1508",
        "msg_sym": "invalid-envvar-default",
        "msg_text": "%s default type is %s. Expected str or None.",
        "msg_xpln": "Env manipulation functions return None or str values. Supplying "
        "anything different as a default may cause bugs. See "
        "https://docs.python.org/3/library/os.html#os.getenv.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1509",
        "msg_sym": "subprocess-popen-preexec-fn",
        "msg_text": "Using preexec_fn keyword which may be unsafe in the presence of "
        "threads",
        "msg_xpln": "The preexec_fn parameter is not safe to use in the presence of "
        "threads in your application. The child process could deadlock "
        "before exec is called. If you must use it, keep it trivial! "
        "Minimize the number of libraries you call "
        "into.https://docs.python.org/3/library/subprocess.html#popen-constructor",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1601",
        "msg_sym": "apply-builtin",
        "msg_text": "apply built-in referenced",
        "msg_xpln": "Used when the apply built-in function is referenced (missing "
        "from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1602",
        "msg_sym": "basestring-builtin",
        "msg_text": "basestring built-in referenced",
        "msg_xpln": "Used when the basestring built-in function is referenced "
        "(missing from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1603",
        "msg_sym": "buffer-builtin",
        "msg_text": "buffer built-in referenced",
        "msg_xpln": "Used when the buffer built-in function is referenced (missing "
        "from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1604",
        "msg_sym": "cmp-builtin",
        "msg_text": "cmp built-in referenced",
        "msg_xpln": "Used when the cmp built-in function is referenced (missing from "
        "Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1605",
        "msg_sym": "coerce-builtin",
        "msg_text": "coerce built-in referenced",
        "msg_xpln": "Used when the coerce built-in function is referenced (missing "
        "from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1606",
        "msg_sym": "execfile-builtin",
        "msg_text": "execfile built-in referenced",
        "msg_xpln": "Used when the execfile built-in function is referenced (missing "
        "from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1607",
        "msg_sym": "file-builtin",
        "msg_text": "file built-in referenced",
        "msg_xpln": "Used when the file built-in function is referenced (missing "
        "from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1608",
        "msg_sym": "long-builtin",
        "msg_text": "long built-in referenced",
        "msg_xpln": "Used when the long built-in function is referenced (missing "
        "from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1609",
        "msg_sym": "raw_input-builtin",
        "msg_text": "raw_input built-in referenced",
        "msg_xpln": "Used when the raw_input built-in function is referenced "
        "(missing from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1610",
        "msg_sym": "reduce-builtin",
        "msg_text": "reduce built-in referenced",
        "msg_xpln": "Used when the reduce built-in function is referenced (missing "
        "from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1611",
        "msg_sym": "standarderror-builtin",
        "msg_text": "StandardError built-in referenced",
        "msg_xpln": "Used when the StandardError built-in function is referenced "
        "(missing from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1612",
        "msg_sym": "unicode-builtin",
        "msg_text": "unicode built-in referenced",
        "msg_xpln": "Used when the unicode built-in function is referenced (missing "
        "from Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1613",
        "msg_sym": "xrange-builtin",
        "msg_text": "xrange built-in referenced",
        "msg_xpln": "Used when the xrange built-in function is referenced (missing "
        "from Python 3)",
        "tho_xpln": "Used when the xrange built-in function is referenced (missing "
        "from Python 3). Use range instead.",
        "usage": "warning",
    },
    {
        "msg_id": "W1614",
        "msg_sym": "coerce-method",
        "msg_text": "__coerce__ method defined",
        "msg_xpln": "Used when a __coerce__ method is defined (method is not used by "
        "Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1615",
        "msg_sym": "delslice-method",
        "msg_text": "__delslice__ method defined",
        "msg_xpln": "Used when a __delslice__ method is defined (method is not used "
        "by Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1616",
        "msg_sym": "getslice-method",
        "msg_text": "__getslice__ method defined",
        "msg_xpln": "Used when a __getslice__ method is defined (method is not used "
        "by Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1617",
        "msg_sym": "setslice-method",
        "msg_text": "__setslice__ method defined",
        "msg_xpln": "Used when a __setslice__ method is defined (method is not used "
        "by Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1618",
        "msg_sym": "no-absolute-import",
        "msg_text": "import missing `from __future__ import absolute_import`",
        "msg_xpln": "Used when an import is not accompanied by ``from __future__ "
        "import absolute_import`` (default behaviour in Python 3)",
        "tho_xpln": "",
        "usage": "skip",
    },  # Not relevant anymore
    {
        "msg_id": "W1619",
        "msg_sym": "old-division",
        "msg_text": "division w/o __future__ statement",
        "msg_xpln": "Used for non-floor division w/o a float literal or ``from "
        "__future__ import division`` (Python 3 returns a float for int "
        "division unconditionally)",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "W1620",
        "msg_sym": "dict-iter-method",
        "msg_text": "Calling a dict.iter*() method",
        "msg_xpln": "Used for calls to dict.iterkeys(), itervalues() or iteritems() "
        "(Python 3 lacks these methods)",
        "tho_xpln": "Used for calls to dict.iterkeys(), itervalues() or iteritems(). "
        "Python 3 lacks these methods, use dict.keys(), values() or items().",
        "usage": "warning",
    },
    {
        "msg_id": "W1621",
        "msg_sym": "dict-view-method",
        "msg_text": "Calling a dict.view*() method",
        "msg_xpln": "Used for calls to dict.viewkeys(), viewvalues() or viewitems() "
        "(Python 3 lacks these methods)",
        "tho_xpln": "Used for calls to dict.viewkeys(), viewvalues() or viewitems(). "
        "Python 3 lacks these methods,  use dict.keys(), values() or items().",
        "usage": "warning",
    },
    {
        "msg_id": "W1622",
        "msg_sym": "next-method-called",
        "msg_text": "Called a next() method on an object",
        "msg_xpln": "Used when an object's next() method is called (Python 3 uses "
        "the next() built- in function)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1623",
        "msg_sym": "metaclass-assignment",
        "msg_text": "Assigning to a class's __metaclass__ attribute",
        "msg_xpln": "Used when a metaclass is specified by assigning to "
        "__metaclass__ (Python 3 specifies the metaclass as a class "
        "statement argument)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1624",
        "msg_sym": "indexing-exception",
        "msg_text": "Indexing exceptions will not work on Python 3",
        "msg_xpln": "Indexing exceptions will not work on Python 3. Use "
        "`exception.args[index]` instead.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1625",
        "msg_sym": "raising-string",
        "msg_text": "Raising a string exception",
        "msg_xpln": "Used when a string exception is raised. This will not work on "
        "Python 3.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1626",
        "msg_sym": "reload-builtin",
        "msg_text": "reload built-in referenced",
        "msg_xpln": "Used when the reload built-in function is referenced (missing "
        "from Python 3). You can use instead imp.reload or "
        "importlib.reload.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1627",
        "msg_sym": "oct-method",
        "msg_text": "__oct__ method defined",
        "msg_xpln": "Used when an __oct__ method is defined (method is not used by "
        "Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1628",
        "msg_sym": "hex-method",
        "msg_text": "__hex__ method defined",
        "msg_xpln": "Used when a __hex__ method is defined (method is not used by "
        "Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1629",
        "msg_sym": "nonzero-method",
        "msg_text": "__nonzero__ method defined",
        "msg_xpln": "Used when a __nonzero__ method is defined (method is not used "
        "by Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1630",
        "msg_sym": "cmp-method",
        "msg_text": "__cmp__ method defined",
        "msg_xpln": "Used when a __cmp__ method is defined (method is not used by "
        "Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1632",
        "msg_sym": "input-builtin",
        "msg_text": "input built-in referenced",
        "msg_xpln": "Used when the input built-in is referenced "
        "(backwards-incompatible semantics in Python 3)",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "W1633",
        "msg_sym": "round-builtin",
        "msg_text": "round built-in referenced",
        "msg_xpln": "Used when the round built-in is referenced "
        "(backwards-incompatible semantics in Python 3)",
        "tho_xpln": "",
        "usage": "skip",
    },
    {
        "msg_id": "W1634",
        "msg_sym": "intern-builtin",
        "msg_text": "intern built-in referenced",
        "msg_xpln": "Used when the intern built-in is referenced (Moved to "
        "sys.intern in Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1635",
        "msg_sym": "unichr-builtin",
        "msg_text": "unichr built-in referenced",
        "msg_xpln": "Used when the unichr built-in is referenced (Use chr in Python "
        "3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1636",
        "msg_sym": "map-builtin-not-iterating",
        "msg_text": "map built-in referenced when not iterating",
        "msg_xpln": "Used when the map built-in is referenced in a non-iterating "
        "context (returns an iterator in Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1637",
        "msg_sym": "zip-builtin-not-iterating",
        "msg_text": "zip built-in referenced when not iterating",
        "msg_xpln": "Used when the zip built-in is referenced in a non-iterating "
        "context (returns an iterator in Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1638",
        "msg_sym": "range-builtin-not-iterating",
        "msg_text": "range built-in referenced when not iterating",
        "msg_xpln": "Used when the range built-in is referenced in a non-iterating "
        "context (returns an iterator in Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1639",
        "msg_sym": "filter-builtin-not-iterating",
        "msg_text": "filter built-in referenced when not iterating",
        "msg_xpln": "Used when the filter built-in is referenced in a non-iterating "
        "context (returns an iterator in Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1640",
        "msg_sym": "using-cmp-argument",
        "msg_text": "Using the cmp argument for list.sort / sorted",
        "msg_xpln": "Using the cmp argument for list.sort or the sorted builtin "
        "should be avoided, since it was removed in Python 3. Using "
        "either `key` or `functools.cmp_to_key` should be preferred.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1641",
        "msg_sym": "eq-without-hash",
        "msg_text": "Implementing __eq__ without also implementing __hash__",
        "msg_xpln": "Used when a class implements __eq__ but not __hash__. In Python "
        "2, objects get object.__hash__ as the default implementation, "
        "in Python 3 objects get None as their default __hash__ "
        "implementation if they also implement __eq__.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1642",
        "msg_sym": "div-method",
        "msg_text": "__div__ method defined",
        "msg_xpln": "Used when a __div__ method is defined. Using `__truediv__` and "
        "setting__div__ = __truediv__ should be preferred.(method is not "
        "used by Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1643",
        "msg_sym": "idiv-method",
        "msg_text": "__idiv__ method defined",
        "msg_xpln": "Used when an __idiv__ method is defined. Using `__itruediv__` "
        "and setting__idiv__ = __itruediv__ should be preferred.(method "
        "is not used by Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1644",
        "msg_sym": "rdiv-method",
        "msg_text": "__rdiv__ method defined",
        "msg_xpln": "Used when a __rdiv__ method is defined. Using `__rtruediv__` "
        "and setting__rdiv__ = __rtruediv__ should be preferred.(method "
        "is not used by Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1645",
        "msg_sym": "exception-message-attribute",
        "msg_text": "Exception.message removed in Python 3",
        "msg_xpln": "Used when the message attribute is accessed on an Exception. "
        "Use str(exception) instead.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1646",
        "msg_sym": "invalid-str-codec",
        "msg_text": "non-text encoding used in str.decode",
        "msg_xpln": "Used when using str.encode or str.decode with a non-text "
        "encoding. Use codecs module to handle arbitrary codecs.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1647",
        "msg_sym": "sys-max-int",
        "msg_text": "sys.maxint removed in Python 3",
        "msg_xpln": "Used when accessing sys.maxint. Use sys.maxsize instead.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1648",
        "msg_sym": "bad-python3-import",
        "msg_text": "Module moved in Python 3",
        "msg_xpln": "Used when importing a module that no longer exists in Python 3.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1649",
        "msg_sym": "deprecated-string-function",
        "msg_text": "Accessing a deprecated function on the string module",
        "msg_xpln": "Used when accessing a string function that has been deprecated "
        "in Python 3.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1650",
        "msg_sym": "deprecated-str-translate-call",
        "msg_text": "Using str.translate with deprecated deletechars parameters",
        "msg_xpln": "Used when using the deprecated deletechars parameters from "
        "str.translate. Use re.sub to remove the desired characters",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1651",
        "msg_sym": "deprecated-itertools-function",
        "msg_text": "Accessing a deprecated function on the itertools module",
        "msg_xpln": "Used when accessing a function on itertools that has been "
        "removed in Python 3.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1652",
        "msg_sym": "deprecated-types-field",
        "msg_text": "Accessing a deprecated fields on the types module",
        "msg_xpln": "Used when accessing a field on types that has been removed in "
        "Python 3.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1653",
        "msg_sym": "next-method-defined",
        "msg_text": "next method defined",
        "msg_xpln": "Used when a next method is defined that would be an iterator in "
        "Python 2 but is treated as a normal function in Python 3.",
        "tho_xpln": "",
        "usage": "enhancement",
    },
    {
        "msg_id": "W1654",
        "msg_sym": "dict-items-not-iterating",
        "msg_text": "dict.items referenced when not iterating",
        "msg_xpln": "Used when dict.items is referenced in a non-iterating context "
        "(returns an iterator in Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1655",
        "msg_sym": "dict-keys-not-iterating",
        "msg_text": "dict.keys referenced when not iterating",
        "msg_xpln": "Used when dict.keys is referenced in a non-iterating context "
        "(returns an iterator in Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1656",
        "msg_sym": "dict-values-not-iterating",
        "msg_text": "dict.values referenced when not iterating",
        "msg_xpln": "Used when dict.values is referenced in a non-iterating context "
        "(returns an iterator in Python 3)",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1657",
        "msg_sym": "deprecated-operator-function",
        "msg_text": "Accessing a removed attribute on the operator module",
        "msg_xpln": "Used when accessing a field on operator module that has been "
        "removed in Python 3.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1658",
        "msg_sym": "deprecated-urllib-function",
        "msg_text": "Accessing a removed attribute on the urllib module",
        "msg_xpln": "Used when accessing a field on urllib module that has been "
        "removed or moved in Python 3.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1659",
        "msg_sym": "xreadlines-attribute",
        "msg_text": "Accessing a removed xreadlines attribute",
        "msg_xpln": "Used when accessing the xreadlines() function on a file stream, "
        "removed in Python 3.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1660",
        "msg_sym": "deprecated-sys-function",
        "msg_text": "Accessing a removed attribute on the sys module",
        "msg_xpln": "Used when accessing a field on sys module that has been removed "
        "in Python 3.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1661",
        "msg_sym": "exception-escape",
        "msg_text": "Using an exception object that was bound by an except handler",
        "msg_xpln": "Emitted when using an exception, that was bound in an except "
        "handler, outside of the except handler. On Python 3 these "
        "exceptions will be deleted once they get out of the except "
        "handler.",
        "tho_xpln": "",
        "usage": "warning",
    },
    {
        "msg_id": "W1662",
        "msg_sym": "comprehension-escape",
        "msg_text": "Using a variable that was bound inside a comprehension",
        "msg_xpln": "Emitted when using a variable, that was bound in a "
        "comprehension handler, outside of the comprehension itself. On "
        "Python 3 these variables will be deleted outside of the "
        "comprehension.",
        "tho_xpln": "",
        "usage": "warning",
    },
]

all_checks_by_symbol = {c["msg_sym"]: c for c in all_checks}


def load_plugin():
    add_program_analyzer(PylintAnalyzer)
