"""
Utils to handle different jedi versions
"""


def get_statement_of_position(node, pos):
    import jedi.parser_utils

    func = getattr(
        jedi.parser_utils, "get_statement_of_position", _copy_of_get_statement_of_position
    )
    return func(node, pos)


# TODO: try to get rid of this
def _copy_of_get_statement_of_position(node, pos):
    # https://github.com/davidhalter/jedi/commit/9f3a2f93c48eda24e2dcc25e54eb7cc10aa73848
    from parso.python import tree

    for c in node.children:
        if c.start_pos <= pos <= c.end_pos:
            if (
                c.type
                not in (
                    "decorated",
                    "simple_stmt",
                    "suite",
                    "async_stmt",
                    "async_funcdef",
                )
                and not isinstance(c, (tree.Flow, tree.ClassOrFunc))
            ):
                return c
            else:
                try:
                    return _copy_of_get_statement_of_position(c, pos)
                except AttributeError:
                    pass  # Must be a non-scope
    return None


def parse_source(source):
    import parso

    return parso.parse(source)
