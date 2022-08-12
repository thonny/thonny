import os
import re
from logging import getLogger

import tkinter as tk

from thonny import get_workbench, ui_utils
from thonny.languages import tr

logger = getLogger(__name__)


class CodeNavigationView(ui_utils.TreeFrame):
    def __init__(self, master):

        # todo workbench view / event ?
        global code_nav
        code_nav = self

        ui_utils.TreeFrame.__init__(
            self,
            master,
            columns=("file", "line_no", "code_info"),
            displaycolumns=(
                0,
                1,
                2,
            ),
        )

        # todo bind to reload event for update

        get_workbench().get_editor_notebook().bind("<<NotebookTabChanged>>", self._update, True)

        self.tree.bind("<<TreeviewSelect>>", self._on_click)
        self.tree.bind("<Map>", self._update, True)

        self.tree.column("file", width=250, anchor=tk.W)
        self.tree.column("line_no", width=150, anchor=tk.W)
        self.tree.column("code_info", width=500, anchor=tk.W)

        self.tree.heading("file", text=tr("File"), anchor=tk.W)
        self.tree.heading("line_no", text=tr("Line"), anchor=tk.W)
        self.tree.heading("code_info", text=tr("Info"), anchor=tk.W)

        self.tree["show"] = ["headings"]

        self._current_code_view = None
        self._current_source = None

        self._update(None)

    def _update(self, event):

        self.clear()

        # if not self.winfo_ismapped():
        #    return

        for hist in code_nav_history:
            self.add(hist.file, hist.line, hist.comment)

        if len(self.tree.get_children()) == 0:
            self.tree.insert(
                "",
                "end",
                values=(
                    "",
                    "INFO",
                    tr("use goto code with <Control>+MouseClick to get the code reference here."),
                ),
            )

    def clear(self):
        self.tree.delete(*self.tree.get_children())

    def add(self, file, line_no, code_info):
        self.tree.insert("", "end", values=(file, line_no, code_info))

    def _on_click(self, event):

        iid = self.tree.focus()

        if iid != "":
            values = self.tree.item(iid)["values"]
            print(values)
            file = values[0]
            line_no = values[1]
            if line_no and line_no != "INFO":
                file = os.path.expanduser(file)
                editor = get_workbench().get_editor_notebook().show_file(file)
                editor.select_line(line_no)


#

code_nav_history = []
user_root = os.path.expanduser("~")


class CodeNavigationItem(object):
    def __init__(self, file, line_no, comment):
        self.file = file
        if self.file.startswith(user_root + os.sep):
            self.file = self.file.replace(user_root, "~")
        self.line = line_no
        self.comment = comment

    def __eq__(self, a):
        return self.file == a.file and self.line == a.line


# todo singleton, replace by ... ???
code_nav = None


def clr_code_history():

    # todo
    # clear on backend restart event, and separate toolbar button

    global code_nav_history
    code_nav_history.clear()


def add_code_history(file, line, comment=None):
    print("add_code_history", file, line)
    global code_nav_history
    if comment is None:
        comment = ""
        try:
            with open(file) as f:
                lines = f.read().splitlines()
                comment = lines[line - 1].rstrip()
        except:
            pass

    hist = CodeNavigationItem(file, line, comment)

    if len(code_nav_history) > 0:
        if code_nav_history[0] == hist:
            # do not add same reference again
            return

    code_nav_history.insert(0, hist)

    if code_nav:
        code_nav._update(None)


#
# todo
# separate toolbar button for going backward amd forward ?


def load_plugin() -> None:
    get_workbench().add_view(CodeNavigationView, tr("Code Navigation"), "s")
