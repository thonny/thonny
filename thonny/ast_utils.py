# -*- coding: utf-8 -*-

import ast
import io
import logging
import sys
import token
import tokenize

import _ast


def extract_text_range(source, text_range):
    if isinstance(source, bytes):
        # TODO: may be wrong encoding
        source = source.decode("utf-8")

    lines = source.splitlines(True)
    # get relevant lines
    lines = lines[text_range.lineno - 1 : text_range.end_lineno]

    # trim last and first lines
    lines[-1] = lines[-1][: text_range.end_col_offset]
    lines[0] = lines[0][text_range.col_offset :]
    return "".join(lines)


def find_expression(node, text_range):
    if (
        hasattr(node, "lineno")
        and node.lineno == text_range.lineno
        and node.col_offset == text_range.col_offset
        and node.end_lineno == text_range.end_lineno
        and node.end_col_offset == text_range.end_col_offset
        # expression and Expr statement can have same range
        and isinstance(node, _ast.expr)
    ):
        return node
    else:
        for child in ast.iter_child_nodes(node):
            result = find_expression(child, text_range)
            if result is not None:
                return result
        return None


def contains_node(parent_node, child_node):
    for child in ast.iter_child_nodes(parent_node):
        if child == child_node or contains_node(child, child_node):
            return True

    return False


def has_parent_with_class(target_node, parent_class, tree):
    for node in ast.walk(tree):
        if isinstance(node, parent_class) and contains_node(node, target_node):
            return True

    return False


def parse_source(source: bytes, filename="<unknown>", mode="exec"):
    root = ast.parse(source, filename, mode)
    mark_text_ranges(root, source)
    return root


def get_last_child(node, skip_incorrect=True):
    def ok_node(node):
        if node is None:
            return None

        if skip_incorrect and getattr(node, "incorrect_range", False):
            return None

        return node

    def last_ok(nodes):
        for i in range(len(nodes) - 1, -1, -1):
            if ok_node(nodes[i]):
                node = nodes[i]
                if isinstance(node, ast.Starred):
                    if ok_node(node.value):
                        return node.value
                    else:
                        return None
                else:
                    return nodes[i]

        return None

    if isinstance(node, ast.Call):
        # TODO: take care of Python 3.5 updates (Starred etc.)
        if hasattr(node, "kwargs") and ok_node(node.kwargs):
            return node.kwargs
        elif hasattr(node, "starargs") and ok_node(node.starargs):
            return node.starargs
        else:
            kw_values = list(map(lambda x: x.value, node.keywords))
            last_ok_kw = last_ok(kw_values)
            if last_ok_kw:
                return last_ok_kw
            elif last_ok(node.args):
                return last_ok(node.args)
            else:
                return ok_node(node.func)

    elif isinstance(node, ast.BoolOp):
        return last_ok(node.values)

    elif isinstance(node, ast.BinOp):
        if ok_node(node.right):
            return node.right
        else:
            return ok_node(node.left)

    elif isinstance(node, ast.Compare):
        return last_ok(node.comparators)

    elif isinstance(node, ast.UnaryOp):
        return ok_node(node.operand)

    elif isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return last_ok(node.elts)

    elif isinstance(node, ast.Dict):
        # TODO: actually should pairwise check last value, then last key, etc.
        return last_ok(node.values)

    elif isinstance(
        node, (ast.Return, ast.Assign, ast.AugAssign, ast.Yield, ast.YieldFrom)
    ):
        return ok_node(node.value)

    elif isinstance(node, ast.Delete):
        return last_ok(node.targets)

    elif isinstance(node, ast.Expr):
        return ok_node(node.value)

    elif isinstance(node, ast.Assert):
        if ok_node(node.msg):
            return node.msg
        else:
            return ok_node(node.test)

    elif isinstance(node, ast.Subscript):
        if hasattr(node.slice, "value") and ok_node(node.slice.value):
            return node.slice.value
        else:
            assert (
                hasattr(node.slice, "lower")
                and hasattr(node.slice, "upper")
                and hasattr(node.slice, "step")
            )

            if ok_node(node.slice.step):
                return node.slice.step
            elif ok_node(node.slice.upper):
                return node.slice.upper
            else:
                return ok_node(node.slice.lower)

    elif isinstance(node, (ast.For, ast.While, ast.If, ast.With)):
        return True  # There is last child, but I don't know which it will be

    # TODO: pick more cases from here:
    """
    (isinstance(node, (ast.IfExp, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp))
            or isinstance(node, ast.Raise) and (node.exc is not None or node.cause is not None)
            # or isinstance(node, ast.FunctionDef, ast.Lambda) and len(node.args.defaults) > 0
                and (node.dest is not None or len(node.values) > 0))

            #"TODO: Import ja ImportFrom"
            # TODO: what about ClassDef ???
    """

    return None


def mark_text_ranges(node, source: bytes):
    """
    Node is an AST, source is corresponding source as string.
    Function adds recursively attributes end_lineno and end_col_offset to each node
    which has attributes lineno and col_offset.
    """

    def _extract_tokens(tokens, lineno, col_offset, end_lineno, end_col_offset):
        return list(
            filter(
                (
                    lambda tok: tok.start[0] >= lineno
                    and (tok.start[1] >= col_offset or tok.start[0] > lineno)
                    and tok.end[0] <= end_lineno
                    and (tok.end[1] <= end_col_offset or tok.end[0] < end_lineno)
                    and tok.string != ""
                ),
                tokens,
            )
        )

    def _mark_text_ranges_rec(node, tokens, prelim_end_lineno, prelim_end_col_offset):
        """
        Returns the earliest starting position found in given tree,
        this is convenient for internal handling of the siblings
        """

        # set end markers to this node
        if "lineno" in node._attributes and "col_offset" in node._attributes:
            tokens = _extract_tokens(
                tokens,
                node.lineno,
                node.col_offset,
                prelim_end_lineno,
                prelim_end_col_offset,
            )
            try:
                tokens = _mark_end_and_return_child_tokens(
                    node, tokens, prelim_end_lineno, prelim_end_col_offset
                )
            except Exception:
                logging.getLogger("thonny").warning("Problem with marking %s", node)
                # fallback to incorrect marking instead of exception
                node.incorrect_range = True
                node.end_lineno = node.lineno
                node.end_col_offset = node.col_offset + 1

        # mark its children, starting from last one
        # NB! need to sort children because eg. in dict literal all keys come first and then all values
        children = list(_get_ordered_child_nodes(node))
        for child in reversed(children):
            (prelim_end_lineno, prelim_end_col_offset) = _mark_text_ranges_rec(
                child, tokens, prelim_end_lineno, prelim_end_col_offset
            )

        if "lineno" in node._attributes and "col_offset" in node._attributes:
            # new "front" is beginning of this node
            prelim_end_lineno = node.lineno
            prelim_end_col_offset = node.col_offset

        return (prelim_end_lineno, prelim_end_col_offset)

    def _strip_trailing_junk_from_expressions(tokens):
        while (
            tokens[-1].type
            not in (
                token.RBRACE,
                token.RPAR,
                token.RSQB,
                token.NAME,
                token.NUMBER,
                token.STRING,
                token.ELLIPSIS,
            )
            and tokens[-1].string != "..."  # See https://bugs.python.org/issue31394
            and tokens[-1].string not in ")}]"
            or tokens[-1].string
            in [
                "and",
                "as",
                "assert",
                "class",
                "def",
                "del",
                "elif",
                "else",
                "except",
                "finally",
                "for",
                "from",
                "global",
                "if",
                "import",
                "in",
                "is",
                "lambda",
                "not",
                "or",
                "try",
                "while",
                "with",
                "yield",
            ]
        ):
            del tokens[-1]

    def _strip_trailing_extra_closers(tokens, remove_naked_comma):
        level = 0
        for i in range(len(tokens)):
            if tokens[i].string in "({[":
                level += 1
            elif tokens[i].string in ")}]":
                level -= 1

            if level == 0 and tokens[i].string == "," and remove_naked_comma:
                tokens[:] = tokens[0:i]
                return

            if level < 0:
                tokens[:] = tokens[0:i]
                return

    def _strip_unclosed_brackets(tokens):
        level = 0
        for i in range(len(tokens) - 1, -1, -1):
            if tokens[i].string in "({[":
                level -= 1
            elif tokens[i].string in ")}]":
                level += 1

            if level < 0:
                tokens[:] = tokens[0:i]
                level = 0  # keep going, there may be more unclosed brackets

    def _mark_end_and_return_child_tokens(
        node, tokens, prelim_end_lineno, prelim_end_col_offset
    ):
        """
        # shortcut
        node.end_lineno = prelim_end_lineno
        node.end_col_offset = prelim_end_col_offset
        return tokens
        """
        # prelim_end_lineno and prelim_end_col_offset are the start of
        # next positioned node or end of source, ie. the suffix of given
        # range may contain keywords, commas and other stuff not belonging to current node

        # Function returns the list of tokens which cover all its children

        if isinstance(node, _ast.stmt):
            # remove empty trailing lines
            while tokens[-1].type in (
                tokenize.NL,
                tokenize.COMMENT,
                token.NEWLINE,
                token.INDENT,
            ) or tokens[-1].string in (":", "else", "elif", "finally", "except"):
                del tokens[-1]

        else:
            _strip_trailing_extra_closers(
                tokens, not isinstance(node, (ast.Tuple, ast.Lambda))
            )
            _strip_trailing_junk_from_expressions(tokens)
            _strip_unclosed_brackets(tokens)

        # set the end markers of this node
        node.end_lineno = tokens[-1].end[0]
        node.end_col_offset = tokens[-1].end[1]

        # Peel off some trailing tokens which can't be part any
        # positioned child node.
        # TODO: maybe cleaning from parent side is better than
        # _strip_trailing_junk_from_expressions

        # Remove trailing empty parens from no-arg call
        if isinstance(node, ast.Call) and _tokens_text(tokens[-2:]) == "()":
            del tokens[-2:]

        # Remove trailing full slice
        elif isinstance(node, ast.Subscript):
            if _tokens_text(tokens[-3:]) == "[:]":
                del tokens[-3:]

            elif _tokens_text(tokens[-4:]) == "[::]":
                del tokens[-4:]

        # Attribute name would confuse the "value" of Attribute
        elif isinstance(node, ast.Attribute):
            assert tokens[-1].type == token.NAME
            del tokens[-1]
            _strip_trailing_junk_from_expressions(tokens)

        return tokens

    all_tokens = list(tokenize.tokenize(io.BytesIO(source).readline))
    source_lines = source.splitlines(True)
    fix_ast_problems(node, source_lines, all_tokens)
    prelim_end_lineno = len(source_lines)
    prelim_end_col_offset = len(source_lines[len(source_lines) - 1])
    _mark_text_ranges_rec(node, all_tokens, prelim_end_lineno, prelim_end_col_offset)


def fix_ast_problems(tree, source_lines, tokens):
    # Problem 1:
    # Python parser gives col_offset as offset to its internal UTF-8 byte array
    # I need offsets to chars

    # TODO: what if source_lines are in a different encoding???
    utf8_byte_lines = source_lines

    # Problem 2:
    # triple-quoted strings have just plain wrong positions: http://bugs.python.org/issue18370
    # Fortunately lexer gives them correct positions
    string_tokens = list(filter(lambda tok: tok.type == token.STRING, tokens))

    # Problem 3:
    # Binary operations have wrong positions: http://bugs.python.org/issue18374

    # Problem 4:
    # Function calls have wrong positions in Python 3.4: http://bugs.python.org/issue21295
    # TODO: Python 3.4 is not supported anymore
    # similar problem is with Attributes and Subscripts

    # Problem 5: FormattedValue nodes have location of corresponding
    # JoinedStr, but I'd prefer being more precise

    JoinedStr = getattr(ast, "JoinedStr", type(None))
    FormattedValue = getattr(ast, "FormattedValue", type(None))

    def fix_node(node, inside_joined_str=False):
        assert node is not None

        # first fix the children
        for child in _get_ordered_child_nodes(node):
            fix_node(child, isinstance(node, JoinedStr) or inside_joined_str)

        # now the node itself
        if isinstance(node, (ast.Str, JoinedStr)) and not inside_joined_str:
            # fix triple-quote problem
            # get position from tokens.

            # (Child Str positions are wrong in 3.7, but I don't know how to fix them)
            # Don't recurse inside JoinedStr as it may have several child Str nodes
            # but only one string token.
            # TODO: implicit concatenation messes up token-node correspondence?
            tok = string_tokens.pop(0)
            node.lineno, node.col_offset = tok.start

        elif isinstance(node, FormattedValue):
            # Node has wrong position in 3.7, probably taken from string token.
            # Use the position of value instead
            node.lineno = node.value.lineno
            node.col_offset = node.value.col_offset

        elif isinstance(node, (ast.Expr, ast.Attribute)) and isinstance(
            node.value, ast.Str
        ):
            # they share the wrong offset of their triple-quoted child
            # get position from already fixed child
            # TODO: try whether this works when child is in parentheses
            node.lineno = node.value.lineno
            node.col_offset = node.value.col_offset

        elif (
            isinstance(node, ast.BinOp) and compare_node_positions(node, node.left) > 0
        ):
            # fix binop problem
            # get position from an already fixed child
            node.lineno = node.left.lineno
            node.col_offset = node.left.col_offset

            # Note that this doesn't fix
            # (3)+3

        elif isinstance(node, ast.Call) and compare_node_positions(node, node.func) > 0:
            # Python 3.4 call problem
            # get position from an already fixed child
            node.lineno = node.func.lineno
            node.col_offset = node.func.col_offset

            # Note that there remains problem with
            # (f)()
            # but this can't be fixed without knowing child end position

        elif (
            isinstance(node, ast.Attribute)
            and compare_node_positions(node, node.value) > 0
        ):
            # Python 3.4 attribute problem ...
            node.lineno = node.value.lineno
            node.col_offset = node.value.col_offset

        elif (
            isinstance(node, ast.Subscript)
            and compare_node_positions(node, node.value) > 0
        ):
            # Python 3.4 Subscript problem ...
            node.lineno = node.value.lineno
            node.col_offset = node.value.col_offset

        else:
            # Let's hope this node has correct lineno, and byte-based col_offset
            # Now compute char-based col_offset
            if hasattr(node, "lineno"):
                byte_line = utf8_byte_lines[node.lineno - 1]
                char_col_offset = len(byte_line[: node.col_offset].decode("UTF-8"))
                node.col_offset = char_col_offset

    fix_node(tree)


def compare_node_positions(n1, n2):
    if n1.lineno > n2.lineno:
        return 1
    elif n1.lineno < n2.lineno:
        return -1
    elif n1.col_offset > n2.col_offset:
        return 1
    elif n1.col_offset < n2.col_offset:
        return -1
    else:
        return 0


def pretty(node, key="/", level=0):
    """Used for testing and new test generation via AstView.
    Don't change the format without updating tests"""
    if isinstance(node, ast.AST):
        fields = [(key, val) for key, val in ast.iter_fields(node)]
        value_label = node.__class__.__name__
        if isinstance(node, ast.Call):
            # Try to make 3.4 AST-s more similar to 3.5
            if sys.version_info[:2] == (3, 4):
                if ("kwargs", None) in fields:
                    fields.remove(("kwargs", None))
                if ("starargs", None) in fields:
                    fields.remove(("starargs", None))

            # TODO: translate also non-None kwargs and starargs

    elif isinstance(node, list):
        fields = list(enumerate(node))
        if len(node) == 0:
            value_label = "[]"
        else:
            value_label = "[...]"
    else:
        fields = []
        value_label = repr(node)

    item_text = level * "    " + str(key) + "=" + value_label

    if hasattr(node, "lineno"):
        item_text += " @ " + str(getattr(node, "lineno"))
        if hasattr(node, "col_offset"):
            item_text += "." + str(getattr(node, "col_offset"))

        if hasattr(node, "end_lineno"):
            item_text += "  -  " + str(getattr(node, "end_lineno"))
            if hasattr(node, "end_col_offset"):
                item_text += "." + str(getattr(node, "end_col_offset"))

    lines = [item_text] + [
        pretty(field_value, field_key, level + 1) for field_key, field_value in fields
    ]

    return "\n".join(lines)


def _get_ordered_child_nodes(node):
    if isinstance(node, ast.Dict):
        children = []
        for i in range(len(node.keys)):
            if node.keys[i] is not None:
                children.append(node.keys[i])
            children.append(node.values[i])
        return children
    elif isinstance(node, ast.Call):
        children = [node.func] + node.args

        for kw in node.keywords:
            children.append(kw.value)

        # TODO: take care of Python 3.5 updates (eg. args=[Starred] and keywords)
        if hasattr(node, "starargs") and node.starargs is not None:
            children.append(node.starargs)
        if hasattr(node, "kwargs") and node.kwargs is not None:
            children.append(node.kwargs)

        children.sort(key=lambda x: (x.lineno, x.col_offset))
        return children

    # arguments and their defaults are detached in the AST
    elif isinstance(node, ast.arguments):
        children = node.args + node.kwonlyargs + node.kw_defaults + node.defaults

        if node.vararg is not None:
            children.append(node.vararg)
        if node.kwarg is not None:
            children.append(node.kwarg)

        children.sort(key=lambda x: (x.lineno, x.col_offset))
        return children

    else:
        return ast.iter_child_nodes(node)


def _tokens_text(tokens):
    return "".join([t.string for t in tokens])
