import tkinter as tk
from logging import getLogger

from thonny import get_workbench


class LocalsHighlighter:
    def __init__(self, text):
        self.text = text

        self._update_scheduled = False

    def get_positions(self):
        import parso
        from jedi import parser_utils
        from parso.python import tree

        locs = []

        def process_scope(scope):
            if isinstance(scope, tree.Function):
                # process all children after name node,
                # (otherwise name of global function will be marked as local def)
                local_names = set()
                global_names = set()
                for child in scope.children[2:]:
                    process_node(child, local_names, global_names)
            else:
                if hasattr(scope, "subscopes"):
                    for child in scope.subscopes:
                        process_scope(child)
                elif hasattr(scope, "children"):
                    for child in scope.children:
                        process_scope(child)

        def process_node(node, local_names, global_names):
            if isinstance(node, tree.GlobalStmt):
                global_names.update([n.value for n in node.get_global_names()])

            elif isinstance(node, tree.Name):
                if node.value in global_names:
                    return

                if node.is_definition():  # local def
                    locs.append(node)
                    local_names.add(node.value)
                elif node.value in local_names:  # use of local
                    locs.append(node)

            elif isinstance(node, tree.BaseNode):
                # ref: jedi/parser/grammar*.txt
                if node.type == "trailer" and node.children[0].value == ".":
                    # this is attribute
                    return

                if isinstance(node, tree.Function):
                    global_names = set()  # outer global statement doesn't have effect anymore

                for child in node.children:
                    process_node(child, local_names, global_names)

        source = self.text.get("1.0", "end")
        module = parso.parse(source)
        for child in module.children:
            if isinstance(child, tree.BaseNode) and parser_utils.is_scope(child):
                process_scope(child)

        loc_pos = set(
            (
                "%d.%d" % (usage.start_pos[0], usage.start_pos[1]),
                "%d.%d" % (usage.start_pos[0], usage.start_pos[1] + len(usage.value)),
            )
            for usage in locs
        )

        return loc_pos

    def _highlight(self, pos_info):
        for pos in pos_info:
            start_index, end_index = pos[0], pos[1]
            self.text.tag_add("local_name", start_index, end_index)

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
        self.text.tag_remove("local_name", "1.0", "end")

        if get_workbench().get_option("view.locals_highlighting") and self.text.is_python_text():
            try:
                highlight_positions = self.get_positions()
                self._highlight(highlight_positions)
            except Exception:
                logger.exception("Problem when updating local variable tags")


def update_highlighting(event):
    if not get_workbench().ready:
        # don't slow down initial loading process by importing parso and jedi
        return

    assert isinstance(event.widget, tk.Text)
    text = event.widget

    if not hasattr(text, "local_highlighter"):
        text.local_highlighter = LocalsHighlighter(text)

    text.local_highlighter.schedule_update()


def load_plugin() -> None:
    wb = get_workbench()
    wb.set_default("view.locals_highlighting", False)
    wb.bind_class("CodeViewText", "<<TextChange>>", update_highlighting, True)
    wb.bind("<<UpdateAppearance>>", update_highlighting, True)
