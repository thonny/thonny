from tkinter import Text

from jedi import Script
from jedi.parser import tree
from thonny.globals import get_workbench

NAME_CONF = {'background': 'Black', 'foreground': 'White'}


class NameHighlighter:

    def __init__(self):
        self.text = None # type: Text
        self.bound_ids = {}

    @staticmethod
    def is_name_function_call_name(name):
        stmt = name.get_definition()
        return stmt.type == "power" and stmt.children[0] == name

    @staticmethod
    def is_name_function_definition(name):
        scope = name.get_definition()
        return isinstance(scope, tree.Function) and scope.children[1].value == name.value

    @staticmethod
    def find_definition(scope, name):
        if NameHighlighter.is_assignment_name(name):
            return name
        if isinstance(scope, tree.Function) and scope.children[1].value == name.value:
            return scope.children[1]
        for c in scope.children:
            if isinstance(c, tree.Function) and c.children[1].value == name.value:
                return c.children[1]

            if isinstance(c, tree.BaseNode) and c.type == "suite":
                for x in c.children:
                    if NameHighlighter.is_assignment_node(x) and x.children[0].children[0].value == name.value:
                        return x.children[0].children[0]
        if not isinstance(scope, tree.Module):
            return NameHighlighter.find_definition(scope.get_parent_scope(), name)
        return None

    @staticmethod
    def is_assignment_name(name):
        stmt = name.get_definition()
        return isinstance(stmt, tree.ExprStmt) and stmt.children[0].value == name.value

    @staticmethod
    def is_assignment_node(node):
        return isinstance(node, tree.BaseNode) and node.type == "simple_stmt" and \
               isinstance(node.children[0], tree.ExprStmt)

    @staticmethod
    def find_usages(name):
        # search for definition
        definition = NameHighlighter.find_definition(name.get_parent_scope(), name)
        searched_scopes = set()
        def find_names_in_node(node):
            names = []
            if isinstance(node, tree.BaseNode):
                if node.is_scope():
                    if node in searched_scopes:
                        return names
                    searched_scopes.add(node)
                for c in node.children:
                    sub_result = find_names_in_node(c)
                    if sub_result is None:
                        if node != scope:
                            return None if node != definition.get_parent_scope() else [definition]
                        else:
                            sub_result = []
                    names.extend(sub_result)
            elif isinstance(node, tree.Name) and node.value == name.value:
                if (NameHighlighter.is_assignment_name(node) or NameHighlighter.is_name_function_definition(node))\
                        and definition != node:
                    return None
                names.append(node)
            return names

        if NameHighlighter.is_name_function_definition(definition):
            scope = definition.get_parent_scope().get_parent_scope()
        else:
            scope = definition.get_parent_scope()

        usages = find_names_in_node(scope)

        return usages

    def get_positions(self):

        index = self.text.index("insert").split(".")
        l, c = int(index[0]), int(index[1])
        script = Script(self.text.get('1.0', 'end'), l, c)

        user_stmt = script._parser.user_stmt()
        name = None

        if isinstance(user_stmt, tree.Name):
            name = user_stmt
        elif isinstance(user_stmt, tree.BaseNode):
            name = user_stmt.name_for_position(script._pos)

        if not name:
            return set()

        usages = NameHighlighter.find_usages(name)

        return set(("%d.%d" % (usage.start_pos[0], usage.start_pos[1]),
                "%d.%d" % (usage.start_pos[0], usage.start_pos[1] + len(name.value)))
                for usage in usages)

    def _highlight(self, pos_info):
        if not self.text:
            return

        self.text.tag_delete("NAME")
        self.text.tag_config("NAME", NAME_CONF)

        for pos in pos_info:
            start_index, end_index = pos[0], pos[1]
            self.text.tag_add("NAME", start_index, end_index)

    def _on_change(self, event):
        highlight_positions = self.get_positions()
        self._highlight(highlight_positions)

    def _on_editor_change(self, event):
        if self.text:
            # unbind events from previous editor's text
            for k, v in self.bound_ids.items():
                self.text.unbind(k, v)

        # get the active text widget from the active editor of the active tab of the editor notebook
        self.text = event.widget.get_current_editor().get_text_widget()

        self.bound_ids["<<CursorMove>>"] = self.text.bind("<<CursorMove>>", self._on_change, True)
        self.bound_ids["<<TextChange>>"] = self.text.bind("<<TextChange>>", self._on_change, True)


def load_plugin():
    wb = get_workbench()  # type:Workbench
    nb = wb.get_editor_notebook()  # type:EditorNotebook

    name_hl = NameHighlighter()

    nb.bind("<<NotebookTabChanged>>", name_hl._on_editor_change, True)