import re
from logging import getLogger

import tkinter as tk

from thonny import get_workbench, ui_utils
from thonny.languages import tr

logger = getLogger(__name__)


class TodoView(ui_utils.TreeFrame):
    def __init__(self, master):

        ui_utils.TreeFrame.__init__(
            self,
            master,
            columns=("line_no", "todo_text"),
            displaycolumns=(0, 1),
        )

        self.tree.bind("<<TreeviewSelect>>", self._on_click)
        self.tree.bind("<Map>", self._update, True)

        # todo bind to reload event for update

        get_workbench().get_editor_notebook().bind("<<NotebookTabChanged>>", self._update)
        get_workbench().bind("Save", self._update, True)
        get_workbench().bind("SaveAs", self._update, True)
        get_workbench().bind_class("Text", "<Double-Button-1>", self._update, True)

        self.tree.column("line_no", width=70, anchor=tk.W)
        self.tree.column("todo_text", width=750, anchor=tk.W)

        self.tree.heading("line_no", text=tr("Line"), anchor=tk.W)
        self.tree.heading("todo_text", text=tr("Info"), anchor=tk.W)

        self.tree["show"] = ["headings"]

        self._current_code_view = None
        self._current_source = None

        self._update(None)

    def _update(self, event):

        # todo: not updated on first run

        self.clear()

        if not self.winfo_ismapped():
            return

        editor = get_workbench().get_editor_notebook().get_current_editor()

        if editor is None:
            self._current_code_view = None
            self._current_source = None
            return

        new_cw = editor.get_code_view()
        new_source = new_cw.get_content_as_bytes()

        if self._current_code_view == new_cw and self._current_source == new_source:
            return

        self._current_code_view = new_cw
        self._current_source = new_source

        # todo support of other file types and introducing comment tags

        r_ex = r"((#\s*(TODO|BUG|FIXME|ERROR|NOTE|REMARK)[:\s]*).*)"
        r_match = re.compile(r_ex, re.IGNORECASE)

        line_no = 0
        for line in new_source.splitlines():
            line_no += 1
            matches = r_match.finditer(line.decode())
            if matches:
                for m in matches:
                    todo_text = m.groups()[0]
                    self.tree.insert("", "end", values=(line_no, todo_text))

    def clear(self):
        self.tree.delete(*self.tree.get_children())

    def _on_click(self, event):
        if self._current_code_view is None:
            return

        iid = self.tree.focus()

        if iid != "":
            values = self.tree.item(iid)["values"]
            line_no = values[0]
            if line_no:
                editor = get_workbench().get_editor_notebook().get_current_editor()
                editor.select_line(line_no)


def load_plugin() -> None:
    get_workbench().add_view(TodoView, tr("Todo's"), "s")
