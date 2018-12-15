# -*- coding: utf-8 -*-

import ast
import sys
import _ast

from asttokens import ASTTokens


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
    for node in ast.walk(node):
        if (
            isinstance(node, ast.expr)
            and node.lineno == text_range.lineno
            and node.col_offset == text_range.col_offset
            and node.end_lineno == text_range.end_lineno
            and node.end_col_offset == text_range.end_col_offset
        ):
            return node


def parse_source(source: bytes, filename="<unknown>", mode="exec"):
    root = ast.parse(source, filename, mode)
    mark_text_ranges(root, source)
    return root


def get_last_child(node):
    def last_ok(nodes):
        if not nodes:
            return None
        node = nodes[-1]
        if isinstance(node, ast.Starred):
            return node.value
        else:
            return node

    if isinstance(node, ast.Call):
        # TODO: take care of Python 3.5 updates (Starred etc.)
        if hasattr(node, "kwargs"):
            return node.kwargs
        elif hasattr(node, "starargs"):
            return node.starargs
        elif node.keywords:
            return node.keywords[-1].value
        elif node.args:
            return node.args[-1]
        else:
            return node.func

    elif isinstance(node, ast.BoolOp):
        return last_ok(node.values)

    elif isinstance(node, ast.BinOp):
        return node.right

    elif isinstance(node, ast.Compare):
        return last_ok(node.comparators)

    elif isinstance(node, ast.UnaryOp):
        return node.operand

    elif isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return last_ok(node.elts)

    elif isinstance(node, ast.Dict):
        # TODO: actually should pairwise check last value, then last key, etc.
        return last_ok(node.values)

    elif isinstance(
        node, (ast.Return, ast.Assign, ast.AugAssign, ast.Yield, ast.YieldFrom, ast.Expr)
    ):
        return node.value

    elif isinstance(node, ast.Delete):
        return last_ok(node.targets)

    elif isinstance(node, ast.Assert):
        return node.msg or node.test

    elif isinstance(node, ast.Subscript):
        if hasattr(node.slice, "value"):
            return node.slice.value
        else:
            assert (
                hasattr(node.slice, "lower")
                and hasattr(node.slice, "upper")
                and hasattr(node.slice, "step")
            )

            return node.slice.step or node.slice.upper or node.slice.lower

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

    ASTTokens(source.decode('utf8'), tree=node)
    for child in ast.walk(node):
        if hasattr(child, 'last_token'):
            child.end_lineno, child.end_col_offset = child.last_token.end

            if hasattr(child, 'lineno'):
                # Fixes problems with some nodes like binop
                child.lineno, child.col_offset = child.first_token.start


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
