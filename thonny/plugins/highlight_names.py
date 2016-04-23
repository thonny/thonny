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
    def is_node_function_definition(name):
        scope = name.get_parent_scope()
        return isinstance(scope, tree.Function) and scope.children[1] == name

    @staticmethod
    def is_name_function_call_name(name):
        stmt = name.get_definition()
        return stmt.type == "power" and stmt.children[0] == name

    @staticmethod
    def find_definition(scope, name):
        if isinstance(scope, tree.Function) and scope.children[1].value == name.value:
            return scope
        for c in scope.children:
            if isinstance(c, tree.Function) and c.children[1].value == name.value:
                return c
        if not isinstance(scope, tree.Module):
            return NameHighlighter.find_definition(scope.get_parent_scope(), name)
        return None


    def find_usages(self, name):
        # search for definition
        definition = NameHighlighter.find_definition(name.get_parent_scope(), name)
        searched_scopes = set()

        def find_names_in_node(node, definition=None):
            names = []
            if isinstance(node, tree.BaseNode):
                if node.is_scope():
                    if node in searched_scopes:
                        return names
                    searched_scopes.add(node)
                for c in node.children:
                    if isinstance(c, tree.Function) and c.children[1].value == name.value and definition and \
                                    c != definition:
                        return []

                    sub_result = find_names_in_node(c, definition)
                    names.extend(sub_result)
            elif isinstance(node, tree.Name) and node.value == name.value:
                names.append(node)
            return names


        scope = name.get_parent_scope()
        usages = find_names_in_node(scope, definition)
        if usages is None:
            usages = []
        while not isinstance(scope, tree.Module):
            searched_scopes.add(scope)
            scope = scope.get_parent_scope()
            names = find_names_in_node(scope, definition)
            if names is not None:
                usages.extend(names)

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

        usages = self.find_usages(name)

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

        # ...and bind the paren checking procedure to that widget's cursor move event
        self.bound_ids["<<CursorMove>>"] = self.text.bind("<<CursorMove>>", self._on_change, True)
        self.bound_ids["<<TextChange>>"] = self.text.bind("<<TextChange>>", self._on_change, True)


def _load_plugin():
    wb = get_workbench()  # type:Workbench
    nb = wb.get_editor_notebook()  # type:EditorNotebook

    name_hl = NameHighlighter()

    nb.bind("<<NotebookTabChanged>>", name_hl._on_editor_change, True)