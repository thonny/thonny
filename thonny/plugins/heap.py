# -*- coding: utf-8 -*-

import tkinter as tk
from _tkinter import TclError
from tkinter import ttk

from thonny import get_runner, get_workbench
from thonny.common import InlineCommand
from thonny.languages import tr
from thonny.memory import MAX_REPR_LENGTH_IN_GRID, MemoryFrame, format_object_id, parse_object_id
from thonny.misc_utils import shorten_repr


class HeapView(MemoryFrame):
    def __init__(self, master):
        MemoryFrame.__init__(self, master, ("id", "value"))

        self.tree.column("id", width=100, anchor=tk.W, stretch=False)
        self.tree.column("value", width=150, anchor=tk.W, stretch=True)

        self.tree.heading("id", text=tr("ID"), anchor=tk.W)
        self.tree.heading("value", text=tr("Value"), anchor=tk.W)

        self.search_var = tk.StringVar()
        self.search_frame = ttk.Frame(self)
        self.search_frame.grid(row=2, column=0, sticky="ew", columnspan=2)
        self.search_label = ttk.Label(self.search_frame, text=tr("Search ID:"))
        self.search_label.pack(side="left", padx=(5, 2))
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.search_entry.bind("<Return>", lambda event: self._search_heap()) 
        self.search_button = ttk.Button(self.search_frame, text=tr("Find"), command=self._search_heap)
        self.search_button.pack(side="left")

        get_workbench().bind("get_heap_response", self._handle_heap_event, True)
        get_workbench().bind("DebuggerResponse", self._request_heap_data, True)
        get_workbench().bind("ToplevelResponse", self._request_heap_data, True)
        get_workbench().bind("get_globals_response", self._request_heap_data, True)

        self.bind("<Map>", self._on_map, True)
        self.bind("<Unmap>", self._on_unmap, True)
        info_icon = get_workbench().get_image("information")
        self.info_label = ttk.Label(
            get_workbench().get_toolbar(),
            text=tr("Heap mode is on.\nClose Heap view to turn it off."),
            image=info_icon,
            compound="left",
            background="#F4FFBA",
            foreground="green",
            padding=(3, 0),
        )

    def _search_heap(self):
        search_id = self.search_var.get()
        found = False
        for child in self.tree.get_children():
            if self.tree.set(child, "id").startswith(search_id):
                self.tree.selection_set(child)
                self.tree.see(child)
                found = True
                break
        if not found:
            tk.messagebox.showinfo(tr("Search"), tr(f"No ID starting with '{search_id}' found in the heap."))

    def _update_data(self, data):
        self._clear_tree()
        for value_id in sorted(data.keys()):
            node_id = self.tree.insert("", "end")
            self.tree.set(node_id, "id", format_object_id(value_id))
            self.tree.set(
                node_id, "value", shorten_repr(data[value_id].repr, MAX_REPR_LENGTH_IN_GRID)
            )

    def before_show(self):
        self._request_heap_data(even_when_hidden=True)

    def get_object_id(self):
        iid = self.tree.focus()
        if iid != "":
            return parse_object_id(self.tree.item(iid)["values"][0])

        return None

    def _request_heap_data(self, msg=None, even_when_hidden=False):
        if self.winfo_ismapped() or even_when_hidden:
            # TODO: update itself also when it becomes visible
            if get_runner() is not None:
                get_runner().send_command(InlineCommand("get_heap"))

    def _handle_heap_event(self, msg):
        if self.winfo_ismapped():
            if hasattr(msg, "heap"):
                self._update_data(msg.heap)

    def _on_map(self, event):
        self.info_label.grid(row=0, column=1005)

    def _on_unmap(self, event):
        try:
            self.info_label.grid_remove()
        except TclError:
            pass


def load_plugin() -> None:
    get_workbench().add_view(HeapView, tr("Heap"), "e")
