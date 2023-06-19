import re
import time
import tkinter as tk
from logging import getLogger

from thonny import get_workbench, ui_utils
from thonny.languages import tr
from thonny.ui_utils import ems_to_pixels

logger = getLogger(__name__)

INFO_TEXT = "---"


class TodoView(ui_utils.TreeFrame):
    def __init__(self, master):
        ui_utils.TreeFrame.__init__(
            self,
            master,
            columns=("line_no", "todo_text"),
            displaycolumns=(0, 1),
        )

        self._current_code_view = None
        self._current_source = None

        self.tree.bind("<<TreeviewSelect>>", self._on_click, True)
        self.tree.bind("<Map>", self._update, True)

        get_workbench().bind("WorkbenchReady", self._update, True)
        get_workbench().bind("Save", self._update, True)
        get_workbench().bind("SaveAs", self._update, True)

        get_workbench().bind_class("Text", "<Double-Button-1>", self._update, True)
        get_workbench().bind_class("Text", "<<NewLine>>", self._update, True)

        get_workbench().get_editor_notebook().bind("<<NotebookTabChanged>>", self._update, True)
        get_workbench().bind_class("EditorCodeViewText", "<<TextChange>>", self._text_change, True)

        self.tree.column("line_no", width=ems_to_pixels(4), anchor=tk.W)
        self.tree.column("todo_text", width=ems_to_pixels(100), anchor=tk.W)

        self.tree.heading("line_no", text=tr("Line"), anchor=tk.W)
        self.tree.heading("todo_text", text=tr("Info"), anchor=tk.W)

        self.tree["show"] = ["headings"]

        self._update(None)

    def _last_op_delta(self):
        last_op = self._current_code_view.text.get_last_operation_time()
        now = time.time()
        return now - last_op

    def _text_change(self, event):
        if self._current_code_view is None:
            return

        if not hasattr(self._current_code_view, "_update_already_scheduled"):
            self._current_code_view._update_already_scheduled = False

        if self._current_code_view._update_already_scheduled:
            return

        if self._last_op_delta() < 0.3:
            self._current_code_view._update_already_scheduled = True

            def delay_update():
                if self._last_op_delta() < 0.3:
                    # still typing
                    self._current_code_view.text.after(100, delay_update)
                    return

                self._current_code_view._update_already_scheduled = False
                self._update(None)

            self._current_code_view.text.after_idle(delay_update)

        else:
            self._update(event)

    def _update(self, event):
        if not self.winfo_ismapped():
            return

        editor = get_workbench().get_editor_notebook().get_current_editor()

        if editor is None:
            self._current_code_view = None
            self._current_source = None
            return

        new_codeview = editor.get_code_view()
        new_source = new_codeview.get_content()

        if self._current_code_view == new_codeview and self._current_source == new_source:
            return

        self.clear()

        self._current_code_view = new_codeview
        self._current_source = new_source

        # todo support of other file types and introducing comment tags

        r_ex = r"^.*((#.*[\t ]*(TODO|BUG|FIXME|ERROR|NOTE|REMARK)([:\t ]*))(.*))$"
        r_match = re.compile(r_ex, re.IGNORECASE | re.MULTILINE)

        line_no = 0
        for line in new_source.splitlines():
            line_no += 1
            matches = r_match.finditer(line)
            if matches:
                for m in matches:
                    todo_text = m.groups()[0]
                    self.tree.insert("", "end", values=(line_no, todo_text))

        if len(self.tree.get_children()) == 0:
            # todo enhance the regex so that a todo within quotes is not shown in the list
            # low prio
            self.tree.insert("", "end", values=(INFO_TEXT, tr("No line marked with #todo found")))

    def clear(self):
        self.tree.delete(*self.tree.get_children())

    def _on_click(self, event):
        if self._current_code_view is None:
            return

        iid = self.tree.focus()

        if iid != "":
            values = self.tree.item(iid)["values"]
            line_no = values[0]
            if line_no and line_no != INFO_TEXT:
                editor = get_workbench().get_editor_notebook().get_current_editor()
                editor.select_line(line_no)


def load_plugin() -> None:
    get_workbench().add_view(TodoView, tr("TODO"), "s")
