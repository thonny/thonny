# -*- coding: utf-8 -*-
import ast
import sys
import tkinter as tk
from logging import getLogger
from typing import Optional

from thonny import ast_utils, get_workbench, ui_utils
from thonny.common import TextRange, range_contains_smaller
from thonny.languages import tr

logger = getLogger(__name__)


class AstView(ui_utils.TreeFrame):
    def __init__(self, master):
        ui_utils.TreeFrame.__init__(
            self,
            master,
            columns=("range", "lineno", "col_offset", "end_lineno", "end_col_offset"),
            displaycolumns=(0,),
        )

        self._current_code_view = None
        self.tree.bind("<<TreeviewSelect>>", self._locate_code)
        self.tree.bind("<<Copy>>", self._copy_to_clipboard)
        self.tree.bind("<Map>", self._update, True)
        get_workbench().get_editor_notebook().bind("<<NotebookTabChanged>>", self._update, True)
        get_workbench().bind("Save", self._update, True)
        get_workbench().bind("SaveAs", self._update, True)
        get_workbench().bind_class("Text", "<Double-Button-1>", self._update, True)

        self.tree.column("#0", width=550, anchor=tk.W)
        self.tree.column("range", width=100, anchor=tk.W)
        self.tree.column("lineno", width=30, anchor=tk.W)
        self.tree.column("col_offset", width=30, anchor=tk.W)
        self.tree.column("end_lineno", width=30, anchor=tk.W)
        self.tree.column("end_col_offset", width=30, anchor=tk.W)

        self.tree.heading("#0", text="Node", anchor=tk.W)
        self.tree.heading("range", text="Code range", anchor=tk.W)

        self.tree["show"] = ("headings", "tree")
        self._current_source: Optional[str] = None

        self._update(None)

    def _update(self, event):
        if not self.winfo_ismapped():
            return

        editor = get_workbench().get_editor_notebook().get_current_editor()

        if not editor:
            self._current_code_view = None
            return

        new_cw = editor.get_code_view()
        new_source = new_cw.get_content()
        if self._current_code_view == new_cw and self._current_source == new_source:
            return

        self._current_code_view = new_cw
        self._current_source = new_source
        selection = self._current_code_view.get_selected_range()

        self._clear_tree()

        if not self._current_source.strip():
            return

        try:
            root = ast_utils.parse_source(self._current_source, fallback_to_one_char=True)
            selected_ast_node = _find_closest_containing_node(root, selection)

        except Exception as e:
            self.tree.insert("", "end", text=str(e), open=True)
            logger.exception("Could not select AST node", exc_info=e)
            return

        def _format(key, node, parent_id):
            if isinstance(node, ast.AST):
                fields = list(ast.iter_fields(node))

                value_label = node.__class__.__name__

            elif isinstance(node, list):
                fields = list(enumerate(node))
                if len(node) == 0:
                    value_label = "[]"
                else:
                    value_label = "[...]"
            else:
                fields = []
                value_label = repr(node)

            item_text = str(key) + "=" + value_label
            node_id = self.tree.insert(parent_id, "end", text=item_text, open=True)
            if node == selected_ast_node:
                self.tree.see(node_id)
                self.tree.selection_add(node_id)

            if hasattr(node, "lineno") and hasattr(node, "col_offset"):
                self.tree.set(node_id, "lineno", node.lineno)
                self.tree.set(node_id, "col_offset", node.col_offset)

                range_str = str(node.lineno) + "." + str(node.col_offset)
                if hasattr(node, "end_lineno") and hasattr(node, "end_col_offset"):
                    self.tree.set(node_id, "end_lineno", node.end_lineno)
                    self.tree.set(node_id, "end_col_offset", node.end_col_offset)
                    range_str += "  -  " + str(node.end_lineno) + "." + str(node.end_col_offset)
                else:
                    # fallback
                    self.tree.set(node_id, "end_lineno", node.lineno)
                    self.tree.set(node_id, "end_col_offset", node.col_offset + 1)

                self.tree.set(node_id, "range", range_str)

            for field_key, field_value in fields:
                _format(field_key, field_value, node_id)

        _format("root", root, "")

    def _locate_code(self, event):
        if self._current_code_view is None:
            return

        iid = self.tree.focus()

        if iid != "":
            values = self.tree.item(iid)["values"]
            if isinstance(values, list) and len(values) >= 5:
                start_line, start_col, end_line, end_col = values[1:5]
                self._current_code_view.select_range(
                    TextRange(start_line, start_col, end_line, end_col)
                )

    def _clear_tree(self):
        for child_id in self.tree.get_children():
            self.tree.delete(child_id)

    def _copy_to_clipboard(self, event):
        self.clipboard_clear()
        if self._current_source is not None:
            pretty_ast = pretty(ast_utils.parse_source(self._current_source))
            self.clipboard_append(pretty_ast)


def _find_closest_containing_node(tree, text_range):
    # first look among children
    for child in ast.iter_child_nodes(tree):
        result = _find_closest_containing_node(child, text_range)
        if result is not None:
            return result

    # no suitable child was found
    if hasattr(tree, "lineno") and range_contains_smaller(
        TextRange(tree.lineno, tree.col_offset, tree.end_lineno, tree.end_col_offset), text_range
    ):
        return tree
    # nope
    else:
        return None


def pretty(node, key="/", level=0):
    """Used for exporting ASTView content"""
    if isinstance(node, ast.AST):
        fields = list(ast.iter_fields(node))
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


def load_plugin() -> None:
    get_workbench().add_view(AstView, tr("Program tree"), "s")
