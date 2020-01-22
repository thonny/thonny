"""Utils to handle different jedi versions

Because of Debian Stretch, Thonny needs to support jedi 0.10,
which doesn't use separate parso
"""


def import_python_tree():
    # pylint: disable=import-error,no-name-in-module

    if get_version_tuple() < (0, 11, 0):
        # make sure not to import parso in this case, even if it exits
        from jedi.parser import tree  # @UnresolvedImport @UnusedImport
    else:
        # assume older versions, which use parso
        from parso.python import tree  # @UnresolvedImport @UnusedImport @Reimport

    return tree


def get_params(func_node):
    if hasattr(func_node, "get_params"):
        # parso
        return func_node.get_params()
    else:
        # older jedi
        return func_node.params


def get_parent_scope(node):
    try:
        # jedi 0.11
        from jedi import parser_utils

        return parser_utils.get_parent_scope(node)
    except ImportError:
        # Older versions
        return node.get_parent_scope()


def get_statement_of_position(node, pos):
    try:
        # jedi 0.11
        # pylint: disable=redefined-outer-name
        import jedi.parser_utils

        func = getattr(
            jedi.parser_utils, "get_statement_of_position", _copy_of_get_statement_of_position
        )
        return func(node, pos)
    except ImportError:
        # Older versions
        return node.get_statement_for_position(pos)


def _copy_of_get_statement_of_position(node, pos):
    # https://github.com/davidhalter/jedi/commit/9f3a2f93c48eda24e2dcc25e54eb7cc10aa73848
    from parso.python import tree

    for c in node.children:
        if c.start_pos <= pos <= c.end_pos:
            if c.type not in (
                "decorated",
                "simple_stmt",
                "suite",
                "async_stmt",
                "async_funcdef",
            ) and not isinstance(c, (tree.Flow, tree.ClassOrFunc)):
                return c
            else:
                try:
                    return _copy_of_get_statement_of_position(c, pos)
                except AttributeError:
                    pass  # Must be a non-scope
    return None


def get_module_node(script):
    if hasattr(script, "_module_node"):  # Jedi 0.12
        return script._module_node
    elif hasattr(script, "_get_module_node"):  # Jedi 0.10 - 0.11
        return script._get_module_node()
    elif hasattr(script, "_get_module"):
        return script._get_module()
    else:
        return script._parser.module()


def is_scope(node):
    try:
        # jedi 0.11 and older
        from jedi import parser_utils

        return parser_utils.is_scope(node)
    except ImportError:
        # Older versions
        return node.is_scope()


def get_name_of_position(obj, position):
    if hasattr(obj, "get_name_of_position"):
        # parso
        return obj.get_name_of_position(position)
    else:
        # older jedi
        return obj.name_for_position(position)


def parse_source(source):
    try:
        import parso

        return parso.parse(source)
    except ImportError:
        import jedi

        script = jedi.Script(source)
        return get_module_node(script)


def get_version_tuple():
    import jedi

    nums = []
    for item in jedi.__version__.split("."):
        try:
            nums.append(int(item))
        except Exception:
            nums.append(0)

    return tuple(nums)
