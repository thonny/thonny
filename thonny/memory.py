# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.font as tk_font

from thonny import get_workbench, ui_utils
from thonny.common import ValueInfo
from thonny.ui_utils import TreeFrame

MAX_REPR_LENGTH_IN_GRID = 100


def format_object_id(object_id):
    # this format aligns with how Python shows memory addresses
    if object_id is None:
        return None
    else:
        return "0x" + hex(object_id)[2:].upper()  # .rjust(8,'0')


def parse_object_id(object_id_repr):
    return int(object_id_repr, base=16)


class MemoryFrame(TreeFrame):
    def __init__(self, master, columns):
        TreeFrame.__init__(self, master, columns)

        font = tk_font.nametofont("TkDefaultFont").copy()
        font.configure(underline=True)
        self.tree.tag_configure("hovered", font=font)

    def stop_debugging(self):
        self._clear_tree()

    def show_selected_object_info(self):
        iid = self.tree.focus()
        if iid != "":
            # NB! Assuming id is second column!
            id_str = self.tree.item(iid)["values"][1]
            if id_str in ["", None, "None"]:
                return

            object_id = parse_object_id(id_str)
            get_workbench().event_generate("ObjectSelect", object_id=object_id)


class VariablesFrame(MemoryFrame):
    def __init__(self, master):
        MemoryFrame.__init__(self, master, ("name", "id", "value"))

        self.tree.column("name", width=120, anchor=tk.W, stretch=False)
        self.tree.column("id", width=450, anchor=tk.W, stretch=True)
        self.tree.column("value", width=450, anchor=tk.W, stretch=True)

        self.tree.heading("name", text="Name", anchor=tk.W)
        self.tree.heading("id", text="Value ID", anchor=tk.W)
        self.tree.heading("value", text="Value", anchor=tk.W)

        get_workbench().bind("ShowView", self._update_memory_model, True)
        get_workbench().bind("HideView", self._update_memory_model, True)
        self._update_memory_model()
        self.tree.tag_configure(
            "group_title",
            font="BoldTkDefaultFont",
            background=ui_utils.lookup_style_option(".", "background"),
        )

    def destroy(self):
        MemoryFrame.destroy(self)
        get_workbench().unbind("ShowView", self._update_memory_model)
        get_workbench().unbind("HideView", self._update_memory_model)

    def _update_memory_model(self, event=None):
        if get_workbench().in_heap_mode():
            self.tree.configure(displaycolumns=("name", "id"))
            # self.tree.columnconfigure(1, weight=1, width=400)
            # self.tree.columnconfigure(2, weight=0)
        else:
            self.tree.configure(displaycolumns=("name", "value"))
            # self.tree.columnconfigure(1, weight=0)
            # self.tree.columnconfigure(2, weight=1, width=400)

    def update_variables(self, all_variables):
        self._clear_tree()

        if not all_variables:
            return

        if isinstance(all_variables, list):
            groups = all_variables
        else:
            groups = [("", all_variables)]

        for group_title, variables in groups:
            if group_title:
                node_id = self.tree.insert("", "end", tags=("group_title",))
                self.tree.set(node_id, "name", group_title)

            for name in sorted(variables.keys()):

                if not name.startswith("__"):
                    node_id = self.tree.insert("", "end", tags="item")
                    self.tree.set(node_id, "name", name)
                    if isinstance(variables[name], ValueInfo):
                        description = variables[name].repr
                        id_str = variables[name].id
                    else:
                        description = variables[name]
                        id_str = None

                    self.tree.set(node_id, "id", format_object_id(id_str))
                    self.tree.set(node_id, "value", description)

    def on_select(self, event):
        self.show_selected_object_info()
