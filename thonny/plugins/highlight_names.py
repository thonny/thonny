import logging
import tkinter as tk

from thonny import get_workbench, jedi_utils

logger = logging.getLogger(__name__)

tree = None


class BaseNameHighlighter:
    def __init__(self, text):
        self.text = text
        self._update_scheduled = False

    def get_positions_for(self, source, line, column):
        raise NotImplementedError()

    def get_positions(self):
        index = self.text.index("insert")

        # ignore if cursor in open string
        if self.text.tag_prevrange("open_string", index) or self.text.tag_prevrange(
            "open_string3", index
        ):

            return set()

        source = self.text.get("1.0", "end")
        index_parts = index.split(".")
        line, column = int(index_parts[0]), int(index_parts[1])

        return self.get_positions_for(source, line, column)

    def schedule_update(self):
        def perform_update():
            try:
                self.update()
            finally:
                self._update_scheduled = False

        if not self._update_scheduled:
            self._update_scheduled = True
            self.text.after_idle(perform_update)

    def update(self):
        self.text.tag_remove("matched_name", "1.0", "end")

        if get_workbench().get_option("view.name_highlighting") and self.text.is_python_text():
            try:
                positions = self.get_positions()
                if len(positions) > 1:
                    for pos in positions:
                        start_index, end_index = pos[0], pos[1]
                        self.text.tag_add("matched_name", start_index, end_index)
            except Exception as e:
                logger.exception("Problem when updating name highlighting", exc_info=e)


class VariablesHighlighter(BaseNameHighlighter):
    """This is heavy, but more correct solution for variables, than Script.usages provides
    (at least for Jedi 0.10)"""

    def _is_name_function_call_name(self, name):
        stmt = name.get_definition()
        return stmt.type == "power" and stmt.children[0] == name

    def _is_name_function_definition(self, name):
        scope = name.get_definition()
        return (
            isinstance(scope, tree.Function)
            and hasattr(scope.children[1], "value")
            and scope.children[1].value == name.value
        )

    def _get_def_from_function_params(self, func_node, name):
        params = func_node.get_params()
        for param in params:
            if param.children[0].value == name.value:
                return param.children[0]
        return None

    # copied from jedi's tree.py with a few modifications
    def _get_statement_for_position(self, node, pos):
        for c in node.children:
            # sorted here, because the end_pos property depends on the last child having the last position,
            # there seems to be a problem with jedi, where the children of a node are not always in the right order
            if isinstance(c, tree.Class):
                c.children.sort(key=lambda x: x.end_pos)
            if c.start_pos <= pos <= c.end_pos:
                if c.type not in ("decorated", "simple_stmt", "suite") and not isinstance(
                    c, (tree.Flow, tree.ClassOrFunc)
                ):
                    return c
                else:
                    try:
                        return jedi_utils.get_statement_of_position(c, pos)
                    except AttributeError as e:
                        logger.exception("Could not get statement of position", exc_info=e)
        return None

    def _is_global_stmt_with_name(self, node, name_str):
        return (
            isinstance(node, tree.BaseNode)
            and node.type == "simple_stmt"
            and isinstance(node.children[0], tree.GlobalStmt)
            and node.children[0].children[1].value == name_str
        )

    def _find_definition(self, scope, name):
        from jedi import parser_utils

        # if the name is the name of a function definition
        if isinstance(scope, tree.Function):
            if scope.children[1] == name:
                return scope.children[1]  # 0th child is keyword "def", 1st is name
            else:
                definition = self._get_def_from_function_params(scope, name)
                if definition:
                    return definition

        for c in scope.children:
            if (
                isinstance(c, tree.BaseNode)
                and c.type == "simple_stmt"
                and isinstance(c.children[0], tree.ImportName)
            ):
                for n in c.children[0].get_defined_names():
                    if n.value == name.value:
                        return n
                # print(c.path_for_name(name.value))
            if (
                isinstance(c, tree.Function)
                and c.children[1].value == name.value
                and not isinstance(parser_utils.get_parent_scope(c), tree.Class)
            ):
                return c.children[1]
            if isinstance(c, tree.BaseNode) and c.type == "suite":
                for x in c.children:
                    if self._is_global_stmt_with_name(x, name.value):
                        return self._find_definition(parser_utils.get_parent_scope(scope), name)
                    if isinstance(x, tree.Name) and x.is_definition() and x.value == name.value:
                        return x
                    def_candidate = self._find_def_in_simple_node(x, name)
                    if def_candidate:
                        return def_candidate

        if not isinstance(scope, tree.Module):
            return self._find_definition(parser_utils.get_parent_scope(scope), name)

        # if name itself is the left side of an assignment statement, then the name is the definition
        if name.is_definition():
            return name

        return None

    def _find_def_in_simple_node(self, node, name):
        if isinstance(node, tree.Name) and node.is_definition() and node.value == name.value:
            return name
        if not isinstance(node, tree.BaseNode):
            return None
        for c in node.children:
            return self._find_def_in_simple_node(c, name)

    def _get_dot_names(self, stmt):
        try:
            if (
                hasattr(stmt, "children")
                and len(stmt.children) >= 2
                and hasattr(stmt.children[1], "children")
                and len(stmt.children[1].children) >= 1
                and hasattr(stmt.children[1].children[0], "value")
                and stmt.children[1].children[0].value == "."
            ):
                return stmt.children[0], stmt.children[1].children[1]
        except Exception as e:
            logger.exception("_get_dot_names", exc_info=e)
            return ()
        return ()

    def _find_usages(self, name, stmt):
        from jedi import parser_utils

        # check if stmt is dot qualified, disregard these
        dot_names = self._get_dot_names(stmt)
        if len(dot_names) > 1 and dot_names[1].value == name.value:
            return set()

        # search for definition
        definition = self._find_definition(parser_utils.get_parent_scope(name), name)

        searched_scopes = set()

        is_function_definition = (
            self._is_name_function_definition(definition) if definition else False
        )

        def find_usages_in_node(node, global_encountered=False):
            names = []
            if isinstance(node, tree.BaseNode):
                if parser_utils.is_scope(node):
                    global_encountered = False
                    if node in searched_scopes:
                        return names
                    searched_scopes.add(node)
                    if isinstance(node, tree.Function):
                        d = self._get_def_from_function_params(node, name)
                        if d and d != definition:
                            return []

                for c in node.children:
                    dot_names = self._get_dot_names(c)
                    if len(dot_names) > 1 and dot_names[1].value == name.value:
                        continue
                    sub_result = find_usages_in_node(c, global_encountered=global_encountered)

                    if sub_result is None:
                        if not parser_utils.is_scope(node):
                            return (
                                None
                                if definition and node != parser_utils.get_parent_scope(definition)
                                else [definition]
                            )
                        else:
                            sub_result = []
                    names.extend(sub_result)
                    if self._is_global_stmt_with_name(c, name.value):
                        global_encountered = True
            elif isinstance(node, tree.Name) and node.value == name.value:
                if definition and definition != node:
                    if self._is_name_function_definition(node):
                        if isinstance(
                            parser_utils.get_parent_scope(parser_utils.get_parent_scope(node)),
                            tree.Class,
                        ):
                            return []
                        else:
                            return None
                    if (
                        node.is_definition()
                        and not global_encountered
                        and (
                            is_function_definition
                            or parser_utils.get_parent_scope(node)
                            != parser_utils.get_parent_scope(definition)
                        )
                    ):
                        return None
                    if self._is_name_function_definition(definition) and isinstance(
                        parser_utils.get_parent_scope(parser_utils.get_parent_scope(definition)),
                        tree.Class,
                    ):
                        return None
                names.append(node)
            return names

        if definition:
            if self._is_name_function_definition(definition):
                scope = parser_utils.get_parent_scope(parser_utils.get_parent_scope(definition))
            else:
                scope = parser_utils.get_parent_scope(definition)
        else:
            scope = parser_utils.get_parent_scope(name)

        usages = find_usages_in_node(scope)
        return usages

    def get_positions_for(self, source, line, column):
        module_node = jedi_utils.parse_source(source)
        pos = (line, column)
        stmt = self._get_statement_for_position(module_node, pos)

        name = None
        if isinstance(stmt, tree.Name):
            name = stmt
        elif isinstance(stmt, tree.BaseNode):
            name = stmt.get_name_of_position(pos)

        if not name:
            return set()

        # format usage positions as tkinter text widget indices
        return set(
            (
                "%d.%d" % (usage.start_pos[0], usage.start_pos[1]),
                "%d.%d" % (usage.start_pos[0], usage.start_pos[1] + len(name.value)),
            )
            for usage in self._find_usages(name, stmt)
        )


class UsagesHighlighter(BaseNameHighlighter):
    """Script.usages looks tempting method to use for finding variable occurrences,
    but it only returns last
    assignments to a variable, not really all usages (with Jedi 0.10).
    But it finds attribute usages quite nicely.

    TODO: check if this gets fixed in later versions of Jedi

    NB!!!!!!!!!!!!! newer jedi versions use subprocess and are too slow to run
    for each keypress"""

    def get_positions_for(self, source, line, column):
        # https://github.com/davidhalter/jedi/issues/897
        from jedi import Script

        script = Script(source + ")")
        usages = script.get_references(line, column, include_builtins=False)

        result = {
            (
                "%d.%d" % (usage.line, usage.column),
                "%d.%d" % (usage.line, usage.column + len(usage.name)),
            )
            for usage in usages
            if usage.module_name == ""
        }

        return result


class CombinedHighlighter(VariablesHighlighter, UsagesHighlighter):
    def get_positions_for(self, source, line, column):
        usages = UsagesHighlighter.get_positions_for(self, source, line, column)
        variables = VariablesHighlighter.get_positions_for(self, source, line, column)
        return usages | variables


def update_highlighting(event):
    if not get_workbench().ready:
        # don't slow down loading process
        return

    global tree
    if not tree:
        # using lazy importing to speed up Thonny loading
        from parso.python import tree  # pylint: disable=redefined-outer-name

    assert isinstance(event.widget, tk.Text)
    text = event.widget

    if not hasattr(text, "name_highlighter"):
        text.name_highlighter = VariablesHighlighter(text)
        # Alternatives:
        # NB! usages() is too slow when used on library names
        # text.name_highlighter = CombinedHighlighter(text)
        # text.name_highlighter = UsagesHighlighter(text)

    text.name_highlighter.schedule_update()


def load_plugin() -> None:
    wb = get_workbench()
    wb.set_default("view.name_highlighting", False)
    wb.bind_class("CodeViewText", "<<CursorMove>>", update_highlighting, True)
    wb.bind_class("CodeViewText", "<<TextChange>>", update_highlighting, True)
    wb.bind("<<UpdateAppearance>>", update_highlighting, True)
