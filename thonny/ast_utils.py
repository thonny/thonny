# -*- coding: utf-8 -*-

import ast
from typing import Union


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


def find_expression(start_node, text_range):
    for node in ast.walk(start_node):
        if (
            isinstance(node, ast.expr)
            and node.lineno == text_range.lineno
            and node.col_offset == text_range.col_offset
            and node.end_lineno == text_range.end_lineno
            and node.end_col_offset == text_range.end_col_offset
        ):
            return node

    return None


def parse_source(source: bytes, filename="<unknown>", mode="exec", fallback_to_one_char=False):
    root = ast.parse(source, filename, mode)
    mark_text_ranges(root, source, fallback_to_one_char)
    return root


def get_last_child(node, skip_incorrect=True):
    """Returns last focusable child expression or child statement"""

    def ok_node(node):
        if node is None:
            return None

        assert isinstance(node, (ast.expr, ast.stmt))

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
        node, (ast.Index, ast.Return, ast.Assign, ast.AugAssign, ast.Yield, ast.YieldFrom)
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

    elif isinstance(node, ast.Slice):
        # [:]
        if ok_node(node.step):
            return node.step
        elif ok_node(node.upper):
            return node.upper
        else:
            return ok_node(node.lower)

    elif isinstance(node, ast.ExtSlice):
        # [:,:]
        for dim in reversed(node.dims):
            result = get_last_child(dim, skip_incorrect)
            assert result is None or isinstance(result, ast.expr)
            if result is not None:
                return result
        return None

    elif isinstance(node, ast.Subscript):
        result = get_last_child(node.slice, skip_incorrect)
        if result is not None:
            return result
        else:
            return node.value

    elif isinstance(node, ast.Raise):
        if ok_node(node.cause):
            return node.cause
        elif ok_node(node.exc):
            return node.exc

    elif isinstance(node, (ast.For, ast.While, ast.If, ast.With)):
        return True  # There is last child, but I don't know which it will be

    # TODO: pick more cases from here:
    """
    (isinstance(node, (ast.IfExp, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp))
            # or isinstance(node, ast.FunctionDef, ast.Lambda) and len(node.args.defaults) > 0
                and (node.dest is not None or len(node.values) > 0))

            #"TODO: Import ja ImportFrom"
            # TODO: what about ClassDef ???
    """

    return None


def mark_text_ranges(node, source: Union[bytes, str], fallback_to_one_char=False):
    """
    Node is an AST, source is corresponding source as string.
    Function adds recursively attributes end_lineno and end_col_offset to each node
    which has attributes lineno and col_offset.
    """
    from asttokens.asttokens import ASTTokens

    if isinstance(source, bytes):
        source = source.decode("utf8")

    ASTTokens(source, tree=node)
    for child in ast.walk(node):
        if hasattr(child, "last_token"):
            child.end_lineno, child.end_col_offset = child.last_token.end

            if hasattr(child, "lineno"):
                # Fixes problems with some nodes like binop
                child.lineno, child.col_offset = child.first_token.start

        # some nodes stay without end info
        if (
            hasattr(child, "lineno")
            and (not hasattr(child, "end_lineno") or not hasattr(child, "end_col_offset"))
            and fallback_to_one_char
        ):
            child.end_lineno = child.lineno
            child.end_col_offset = child.col_offset + 2
