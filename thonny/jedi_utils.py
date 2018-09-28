"""Utils to handle different jedi versions

Because of Debian Stretch, Thonny needs to support jedi 0.10,
which doesn't use separate parso
"""


def import_python_tree():
    # pylint: disable=import-error,no-name-in-module

    if get_version_tuple() < (0, 11, 0):
        # make sure not to import parso in this case, even if it exits
        from jedi.parser.python import tree  # @UnresolvedImport @UnusedImport
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
        from jedi.parser_utils import get_statement_of_position

        return get_statement_of_position(node, pos)
    except ImportError:
        # Older versions
        return node.get_statement_for_position(pos)


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
