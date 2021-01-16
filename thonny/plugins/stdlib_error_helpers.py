import builtins
import os.path
import re
import token

from thonny import assistance
from thonny.assistance import (
    ErrorHelper,
    Suggestion,
    add_error_helper,
    name_similarity,
    HelperNotSupportedError,
)
from thonny.misc_utils import running_on_windows


class SyntaxErrorHelper(ErrorHelper):
    def __init__(self, error_info):
        import tokenize

        super().__init__(error_info)

        self.tokens = []
        self.token_error = None

        if self.error_info["message"] == "EOL while scanning string literal":
            self.intro_text = (
                "You haven't properly closed the string on line %s." % self.error_info["lineno"]
                + "\n(If you want a multi-line string, then surround it with"
                + " `'''` or `\"\"\"` at both ends.)"
            )

        elif self.error_info["message"] == "EOF while scanning triple-quoted string literal":
            # lineno is not useful, as it is at the end of the file and user probably
            # didn't want the string to end there
            self.intro_text = "You haven't properly closed a triple-quoted string"

        else:
            if self.error_info["filename"] and os.path.isfile(self.error_info["filename"]):
                with open(self.error_info["filename"], mode="rb") as fp:
                    try:
                        for t in tokenize.tokenize(fp.readline):
                            self.tokens.append(t)
                    except tokenize.TokenError as e:
                        self.token_error = e
                    except IndentationError as e:
                        self.indentation_error = e

                if not self.tokens or self.tokens[-1].type not in [
                    token.ERRORTOKEN,
                    token.ENDMARKER,
                ]:
                    self.tokens.append(tokenize.TokenInfo(token.ERRORTOKEN, "", None, None, ""))
            else:
                self.tokens = []

            unbalanced = self._sug_unbalanced_parens()
            if unbalanced:
                self.intro_text = (
                    "Unbalanced parentheses, brackets or braces:\n\n" + unbalanced.body
                )
                self.intro_confidence = 5
            else:
                self.intro_text = "Python doesn't know how to read your program."

                if "^" in str(self.error_info):
                    self.intro_text += (
                        "\n\nSmall `^` in the original error message shows where it gave up,"
                        + " but the actual mistake can be before this."
                    )

                self.suggestions = [self._sug_missing_or_misplaced_colon()]

    def _sug_missing_or_misplaced_colon(self):
        import tokenize

        i = 0
        title = "Did you forget the colon?"
        relevance = 0
        body = ""
        while i < len(self.tokens) and self.tokens[i].type != token.ENDMARKER:
            t = self.tokens[i]
            if t.string in [
                "if",
                "elif",
                "else",
                "while",
                "for",
                "with",
                "try",
                "except",
                "finally",
                "class",
                "def",
            ]:
                keyword_pos = i
                while (
                    self.tokens[i].type
                    not in [
                        token.NEWLINE,
                        token.ENDMARKER,
                        token.COLON,  # colon may be OP
                        token.RBRACE,
                    ]
                    and self.tokens[i].string != ":"
                ):

                    old_i = i
                    if self.tokens[i].string in "([{":
                        i = self._skip_braced_part(i)
                        assert i > old_i
                        if i == len(self.tokens):
                            return None
                    else:
                        i += 1

                if self.tokens[i].string != ":":
                    relevance = 9
                    body = "`%s` header must end with a colon." % t.string
                    break

                # Colon was present, but maybe it should have been right
                # after the keyword.
                if (
                    t.string in ["else", "try", "finally"]
                    and self.tokens[keyword_pos + 1].string != ":"
                ):
                    title = "Incorrect use of `%s`" % t.string
                    body = "Nothing is allowed between `%s` and colon." % t.string
                    relevance = 9
                    if (
                        self.tokens[keyword_pos + 1].type not in (token.NEWLINE, tokenize.COMMENT)
                        and t.string == "else"
                    ):
                        body = "If you want to specify a condition, then use `elif` or nested `if`."
                    break

            i += 1

        return Suggestion("missing-or-misplaced-colon", title, body, relevance)

    def _sug_unbalanced_parens(self):
        problem = self._find_first_braces_problem()
        if not problem:
            return None

        return Suggestion("missing-or-misplaced-colon", "Unbalanced brackets", problem[1], 8)

    def _sug_wrong_increment_op(self):
        pass

    def _sug_wrong_decrement_op(self):
        pass

    def _sug_wrong_comparison_op(self):
        pass

    def _sug_switched_assignment_sides(self):
        pass

    def _skip_braced_part(self, token_index):
        assert self.tokens[token_index].string in ["(", "[", "{"]
        level = 1
        token_index += 1
        while token_index < len(self.tokens):

            if self.tokens[token_index].string in ["(", "[", "{"]:
                level += 1
            elif self.tokens[token_index].string in [")", "]", "}"]:
                level -= 1

            token_index += 1

            if level <= 0:
                return token_index

        assert token_index == len(self.tokens)
        return token_index

    def _find_first_braces_problem(self):
        # closers = {'(':')', '{':'}', '[':']'}
        openers = {")": "(", "}": "{", "]": "["}

        brace_stack = []
        for t in self.tokens:
            if t.string in ["(", "[", "{"]:
                brace_stack.append(t)
            elif t.string in [")", "]", "}"]:
                if not brace_stack:
                    return (
                        t,
                        "Found '`%s`' at `line %d <%s>`_ without preceding matching '`%s`'"
                        % (
                            t.string,
                            t.start[0],
                            assistance.format_file_url(
                                self.error_info["filename"], t.start[0], t.start[1]
                            ),
                            openers[t.string],
                        ),
                    )
                elif brace_stack[-1].string != openers[t.string]:
                    return (
                        t,
                        "Found '`%s`' at `line %d <%s>`__ when last unmatched opener was '`%s`' at `line %d <%s>`__"
                        % (
                            t.string,
                            t.start[0],
                            assistance.format_file_url(
                                self.error_info["filename"], t.start[0], t.start[1]
                            ),
                            brace_stack[-1].string,
                            brace_stack[-1].start[0],
                            assistance.format_file_url(
                                self.error_info["filename"],
                                brace_stack[-1].start[0],
                                brace_stack[-1].start[1],
                            ),
                        ),
                    )
                else:
                    brace_stack.pop()

        if brace_stack:
            return (
                brace_stack[-1],
                "'`%s`' at `line %d <%s>`_ is not closed by the end of the program"
                % (
                    brace_stack[-1].string,
                    brace_stack[-1].start[0],
                    assistance.format_file_url(
                        self.error_info["filename"],
                        brace_stack[-1].start[0],
                        brace_stack[-1].start[1],
                    ),
                ),
            )

        return None


class NameErrorHelper(ErrorHelper):
    def __init__(self, error_info):
        super().__init__(error_info)

        names = re.findall(r"\'.*\'", error_info["message"])
        assert len(names) == 1
        self.name = names[0].strip("'")

        self.intro_text = "Python doesn't know what `%s` stands for." % self.name
        self.suggestions = [
            self._sug_bad_spelling(),
            self._sug_missing_quotes(),
            self._sug_missing_import(),
            self._sug_local_from_global(),
            self._sug_not_defined_yet(),
        ]

    def _sug_missing_quotes(self):
        if self._is_attribute_value() or self._is_call_function() or self._is_subscript_value():
            relevance = 0
        else:
            relevance = 5

        return Suggestion(
            "missing-quotes",
            "Did you actually mean string (text)?",
            'If you didn\'t mean a variable but literal text "%s", then surround it with quotes.'
            % self.name,
            relevance,
        )

    def _sug_bad_spelling(self):

        # Yes, it would be more proper to consult builtins from the backend,
        # but it's easier this way...
        all_names = {name for name in dir(builtins) if not name.startswith("_")}
        all_names |= {"pass", "break", "continue", "return", "yield"}

        if self.last_frame.globals is not None:
            all_names |= set(self.last_frame.globals.keys())
        if self.last_frame.locals is not None:
            all_names |= set(self.last_frame.locals.keys())

        similar_names = {self.name}
        if all_names:
            relevance = 0
            for name in all_names:
                sim = name_similarity(name, self.name)
                if sim > 4:
                    similar_names.add(name)
                relevance = max(sim, relevance)
        else:
            relevance = 3

        if len(similar_names) > 1:
            body = "I found similar names. Are all of them spelled correctly?\n\n"
            for name in sorted(similar_names, key=lambda x: x.lower()):
                # TODO: add location info
                body += "* `%s`\n\n" % name
        else:
            body = (
                "Compare the name with corresponding definition / assignment / documentation."
                + " Don't forget that case of the letters matters!"
            )

        return Suggestion("bad-spelling-name", "Did you misspell it (somewhere)?", body, relevance)

    def _sug_missing_import(self):
        likely_importable_functions = {
            "math": {"ceil", "floor", "sqrt", "sin", "cos", "degrees"},
            "random": {"randint"},
            "turtle": {
                "left",
                "right",
                "forward",
                "fd",
                "goto",
                "setpos",
                "Turtle",
                "penup",
                "up",
                "pendown",
                "down",
                "color",
                "pencolor",
                "fillcolor",
                "begin_fill",
                "end_fill",
                "pensize",
                "width",
            },
            "re": {"search", "match", "findall"},
            "datetime": {"date", "time", "datetime", "today"},
            "statistics": {
                "mean",
                "median",
                "median_low",
                "median_high",
                "mode",
                "pstdev",
                "pvariance",
                "stdev",
                "variance",
            },
            "os": {"listdir"},
            "time": {"time", "sleep"},
        }

        body = None

        if self._is_call_function():
            relevance = 5
            for mod in likely_importable_functions:
                if self.name in likely_importable_functions[mod]:
                    relevance += 3
                    body = (
                        "If you meant `%s` from module `%s`, then add\n\n`from %s import %s`\n\nto the beginning of your script."
                        % (self.name, mod, mod, self.name)
                    )
                    break

        elif self._is_attribute_value():
            relevance = 5
            body = (
                "If you meant module `%s`, then add `import %s` to the beginning of your script"
                % (self.name, self.name)
            )

            if self.name in likely_importable_functions:
                relevance += 3

        elif self._is_subscript_value() and self.name != "argv":
            relevance = 0
        elif self.name == "pi":
            body = "If you meant the constant π, then add `from math import pi` to the beginning of your script."
            relevance = 8
        elif self.name == "argv":
            body = "If you meant the list with program arguments, then add `from sys import argv` to the beginning of your script."
            relevance = 8
        else:
            relevance = 3

        if body is None:
            body = "Some functions/variables need to be imported before they can be used."

        return Suggestion("missing-import", "Did you forget to import it?", body, relevance)

    def _sug_local_from_global(self):
        import ast

        relevance = 0
        body = None

        if self.last_frame.code_name == "<module>" and self.last_frame_module_ast is not None:
            function_names = set()
            for node in ast.walk(self.last_frame_module_ast):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if self.name in map(lambda x: x.arg, node.args.args):
                        function_names.add(node.name)
                    # TODO: varargs, kw, ...
                    declared_global = False
                    for localnode in ast.walk(node):
                        # print(node.name, localnode)
                        if (
                            isinstance(localnode, ast.Name)
                            and localnode.id == self.name
                            and isinstance(localnode.ctx, ast.Store)
                        ):
                            function_names.add(node.name)
                        elif isinstance(localnode, ast.Global) and self.name in localnode.names:
                            declared_global = True

                    if node.name in function_names and declared_global:
                        function_names.remove(node.name)

            if function_names:
                relevance = 9
                body = (
                    (
                        "Name `%s` defined in `%s` is not accessible in the global/module level."
                        % (self.name, " and ".join(function_names))
                    )
                    + "\n\nIf you need that data at the global level, then consider changing the function so that it `return`-s the value."
                )

        return Suggestion(
            "local-from-global",
            "Are you trying to access a local variable outside of the function?",
            body,
            relevance,
        )

    def _sug_not_defined_yet(self):
        return Suggestion(
            "not-defined-yet",
            "Has Python executed the definition?",
            (
                "Don't forget that name becomes defined when corresponding definition ('=', 'def' or 'import') gets executed."
                + " If the definition comes later in code or is inside an if-statement, Python may not have executed it (yet)."
                + "\n\n"
                + "Make sure Python arrives to the definition before it arrives to this line. When in doubt, "
                + "`use the debugger <debuggers.rst>`_."
            ),
            2,
        )

    def _sug_maybe_attribute(self):
        "TODO:"

    def _sug_synonym(self):
        "TODO:"

    def _is_call_function(self):
        return self.name + "(" in (
            self.error_info["line"].replace(" ", "").replace("\n", "").replace("\r", "")
        )

    def _is_subscript_value(self):
        return self.name + "[" in (
            self.error_info["line"].replace(" ", "").replace("\n", "").replace("\r", "")
        )

    def _is_attribute_value(self):
        return self.name + "." in (
            self.error_info["line"].replace(" ", "").replace("\n", "").replace("\r", "")
        )


class AttributeErrorHelper(ErrorHelper):
    def __init__(self, error_info):
        super().__init__(error_info)

        names = re.findall(r"\'.*?\'", error_info["message"])
        if len(names) != 2:
            # Can happen eg. in PGZero
            # https://github.com/thonny/thonny/issues/1535
            raise HelperNotSupportedError()

        self.type_name = names[0].strip("'")
        self.att_name = names[1].strip("'")

        self.intro_text = (
            "Your program tries to "
            + ("call method " if self._is_call_function() else "access attribute ")
            + "`%s` of " % self.att_name
            + _get_phrase_for_object(self.type_name)
            + ", but this type doesn't have such "
            + ("method." if self._is_call_function() else "attribute.")
        )

        self.suggestions = [
            self._sug_wrong_attribute_instead_of_len(),
            self._sug_bad_spelling(),
            self._sug_bad_type(),
        ]

    def _sug_wrong_attribute_instead_of_len(self):

        if self.type_name == "str":
            goal = "length"
        elif self.type_name == "bytes":
            goal = "number of bytes"
        elif self.type_name == "list":
            goal = "number of elements"
        elif self.type_name == "tuple":
            goal = "number of elements"
        elif self.type_name == "set":
            goal = "number of elements"
        elif self.type_name == "dict":
            goal = "number of entries"
        else:
            return None

        return Suggestion(
            "wrong-attribute-instead-of-len",
            "Did you mean to ask the %s?" % goal,
            "This can be done with function `len`, eg:\n\n`len(%s)`"
            % _get_sample_for_type(self.type_name),
            (9 if self.att_name.lower() in ("len", "length", "size") else 0),
        )

    def _sug_bad_spelling(self):
        # TODO: compare with attributes of known types
        return Suggestion(
            "bad-spelling-attribute",
            "Did you misspell the name?",
            "Don't forget that case of the letters matters too!",
            3,
        )

    def _sug_bad_type(self):
        if self._is_call_function():
            action = "call this function on"
        else:
            action = "ask this attribute from"

        return Suggestion(
            "wrong-type-attribute",
            "Did you expect another type?",
            "If you didn't mean %s %s, " % (action, _get_phrase_for_object(self.type_name))
            + "then step through your program to see "
            + "why this type appears here.",
            3,
        )

    def _is_call_function(self):
        return "." + self.att_name + "(" in (
            self.error_info["line"].replace(" ", "").replace("\n", "").replace("\r", "")
        )


class OSErrorHelper(ErrorHelper):
    def __init__(self, error_info):
        super().__init__(error_info)

        if "Address already in use" in self.error_info["message"]:
            self.intro_text = "Your programs tries to listen on a port which is already taken."
            self.suggestions = [
                Suggestion(
                    "kill-by-port-type-error",
                    "Want to close the other process?",
                    self.get_kill_process_instructions(),
                    5,
                ),
                Suggestion(
                    "use-another-type-error",
                    "Can you use another port?",
                    "If you don't want to mess with the other process, then check whether"
                    + " you can configure your program to use another port.",
                    3,
                ),
            ]

        else:
            self.intro_text = "No specific information is available for this error."

    def get_kill_process_instructions(self):
        s = (
            "Let's say you need port 5000. If you don't know which process is using it,"
            + " then enter following system command into Thonny's Shell:\n\n"
        )

        if running_on_windows():
            s += (
                "``!netstat -ano | findstr :5000``\n\n"
                + "You should see the process ID in the last column.\n\n"
            )
        else:
            s += (
                "``!lsof -i:5000``\n\n" + "You should see the process ID under the heading PID.\n\n"
            )

        s += (
            "Let's pretend the ID is 12345."
            " You can try hard-killing the process with following command:\n\n"
        )

        if running_on_windows():
            s += "``!tskill 12345``\n"
        else:
            s += (
                "``!kill -9 12345``\n\n"
                + "Both steps can be combined into single command:\n\n"
                + "``!kill -9 $(lsof -t -i:5000)``\n\n"
            )

        return s


class TypeErrorHelper(ErrorHelper):
    def __init__(self, error_info):
        super().__init__(error_info)

        self.intro_text = (
            "Python was asked to do an operation with an object which " + "doesn't support it."
        )

        self.suggestions = [
            Suggestion(
                "step-to-find-type-error",
                "Did you expect another type?",
                "Step through your program to see why this type appears here.",
                3,
            ),
            Suggestion(
                "look-documentation-type-error",
                "Maybe you forgot some details about this operation?",
                "Look up the documentation or perform a web search with the error message.",
                2,
            ),
        ]

        # overwrite / add for special cases
        # something + str or str + something
        for r, string_first in [
            (r"unsupported operand type\(s\) for \+: '(.+?)' and 'str'", False),
            (r"^Can't convert '(.+?)' object to str implicitly$", True),  # Python 3.5
            (r"^must be str, not (.+)$", True),  # Python 3.6
            (r'^can only concatenate str (not "(.+?)") to str$', True),  # Python 3.7
        ]:
            m = re.match(r, error_info["message"], re.I)  # @UndefinedVariable
            if m is not None:
                self._bad_string_concatenation(m.group(1), string_first)
                return

        # TODO: other operations, when one side is string

    def _bad_string_concatenation(self, other_type_name, string_first):
        self.intro_text = "Your program is trying to put together " + (
            "a string and %s." if string_first else "%s and a string."
        ) % _get_phrase_for_object(other_type_name)

        self.suggestions.append(
            Suggestion(
                "convert-other-operand-to-string",
                "Did you mean to treat both sides as text and produce a string?",
                "In this case you should apply function `str` to the %s "
                % _get_phrase_for_object(other_type_name, False)
                + "in order to convert it to string first, eg:\n\n"
                + ("`'abc' + str(%s)`" if string_first else "`str(%s) + 'abc'`")
                % _get_sample_for_type(other_type_name),
                8,
            )
        )

        if other_type_name in ("float", "int"):
            self.suggestions.append(
                Suggestion(
                    "convert-other-operand-to-number",
                    "Did you mean to treat both sides as numbers and produce a sum?",
                    "In this case you should first convert the string to a number "
                    + "using either function `float` or `int`, eg:\n\n"
                    + ("`float('3.14') + 22`" if string_first else "`22 + float('3.14')`"),
                    7,
                )
            )


def _get_phrase_for_object(type_name, with_article=True):
    friendly_names = {
        "str": "a string",
        "int": "an integer",
        "float": "a float",
        "list": "a list",
        "tuple": "a tuple",
        "dict": "a dictionary",
        "set": "a set",
        "bool": "a boolean",
    }
    result = friendly_names.get(type_name, "an object of type '%s'" % type_name)

    if with_article:
        return result
    else:
        _, rest = result.split(" ", maxsplit=1)
        return rest


def _get_sample_for_type(type_name):
    if type_name == "int":
        return "42"
    elif type_name == "float":
        return "3.14"
    elif type_name == "str":
        return "'abc'"
    elif type_name == "bytes":
        return "b'abc'"
    elif type_name == "list":
        return "[1, 2, 3]"
    elif type_name == "tuple":
        return "(1, 2, 3)"
    elif type_name == "set":
        return "{1, 2, 3}"
    elif type_name == "dict":
        return "{1 : 'one', 2 : 'two'}"
    else:
        return "..."


def load_plugin():
    for name in globals():
        if name.endswith("ErrorHelper") and not name.startswith("_"):
            type_name = name[: -len("Helper")]
            add_error_helper(type_name, globals()[name])
