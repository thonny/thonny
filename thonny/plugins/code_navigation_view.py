import os
import re
from logging import getLogger

import tkinter as tk

from thonny import get_workbench
from thonny import ui_utils
from thonny.ui_utils import ems_to_pixels

from thonny.languages import tr

logger = getLogger(__name__)


INFO_TEXT = tr("---")

CMD_HISTORY_BACK = "history_back"
CMD_HISTORY_FORWARD = "history_forward"
CMD_HISTORY_CLR = "history_clear"

user_root = os.path.expanduser("~")

code_nav_view_history = []
code_nav_view_pos = -1

code_nav_view = None

code_nav_bind_late = False


class CodeNavigationItem(object):
    def __init__(self, file, line_no, comment):
        self.file = file
        if self.file.startswith(user_root + os.sep):
            self.file = self.file.replace(user_root, "~")
        self.line = line_no
        self.comment = comment

    def get_path(self):
        return os.path.expanduser(self.file)

    def __eq__(self, a):
        return self.file == a.file and self.line == a.line


#


def clr_code_history():

    # todo, clear on backend restart event ?

    global code_nav_view_history
    code_nav_view_history.clear()

    global code_nav_view_pos
    code_nav_view_pos = -1

    if code_nav_view:
        code_nav_view._update(None)


def add_code_history(file, line, comment=None):
    global code_nav_view_history
    global code_nav_view_pos

    _late_bind_buttons()

    if comment is None:
        comment = ""
        try:
            with open(file) as f:
                lines = f.read().splitlines()
                comment = lines[line - 1].rstrip()
        except:
            pass

    hist = CodeNavigationItem(file, line, comment)

    if code_nav_view_pos >= 0:
        code_nav_view_history = code_nav_view_history[code_nav_view_pos:]

    if len(code_nav_view_history) > 0:
        if code_nav_view_history[0] == hist:
            # do not add same reference again
            return

    code_nav_view_history.insert(0, hist)
    code_nav_view_pos = 0

    if code_nav_view:
        code_nav_view._update(None)


#


class CodeNavigationView(ui_utils.TreeFrame):
    def __init__(self, master):

        global code_nav_view
        code_nav_view = self

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

        self.tree.bind("<<TreeviewSelect>>", self._on_click)
        self.tree.bind("<Map>", self._update, True)

        self.tree.column("file", width=ems_to_pixels(30), anchor=tk.W)
        self.tree.column("line_no", width=ems_to_pixels(4), anchor=tk.W)
        self.tree.column("code_info", width=ems_to_pixels(30), anchor=tk.W)

        self.tree.heading("file", text=tr("File"), anchor=tk.W)
        self.tree.heading("line_no", text=tr("Line"), anchor=tk.W)
        self.tree.heading("code_info", text=tr("Info"), anchor=tk.W)

        self.tree["show"] = ["headings"]

        self._current_code_view = None
        self._current_source = None

        self._update(None)

    def _update(self, event):

        self._clear()

        for hist in code_nav_view_history:
            self.add(hist.file, hist.line, hist.comment)

        if len(self.tree.get_children()) == 0:
            self.tree.insert(
                "",
                "end",
                values=(
                    "",
                    INFO_TEXT,
                    tr("use goto code with <Control>+MouseClick to get the code reference here."),
                ),
            )
        else:
            self.set_nav_selection()

    def set_nav_selection(self):
        if code_nav_view_pos >= 0:
            self.tree.selection_clear()
            sel = self.tree.get_children()[code_nav_view_pos]
            self.tree.selection_add(sel)

    def _clear(self):
        self.tree.delete(*self.tree.get_children())

    def add(self, file, line_no, code_info):
        self.tree.insert("", "end", values=(file, line_no, code_info))

    def _on_click(self, event):
        iid = self.tree.focus()
        if iid != "":
            values = self.tree.item(iid)["values"]
            if values[1] == INFO_TEXT:
                return
            pos = self.tree.get_children().index(iid)
            history_goto(pos)


#


def _history_backward_enabled():
    l = len(code_nav_view_history)
    if l == 0:
        return False
    return code_nav_view_pos < l - 1


def _history_forward_enabled():
    if len(code_nav_view_history) == 0:
        return False
    return code_nav_view_pos > 0


def _history_clear_enabled():
    return len(code_nav_view_history) > 0


def history_goto(pos):
    global code_nav_view_pos
    code_nav_view_pos = pos

    nav = code_nav_view_history[pos]

    editor = get_workbench().get_editor_notebook().show_file(nav.get_path())
    editor.select_line(nav.line)

    if code_nav_view:
        code_nav_view._update(None)


def history_backward():
    global code_nav_view_pos
    if code_nav_view_pos < len(code_nav_view_history) - 1:
        code_nav_view_pos += 1
    history_goto(code_nav_view_pos)


def history_forward():
    global code_nav_view_pos
    if code_nav_view_pos > 0:
        code_nav_view_pos -= 1
    history_goto(code_nav_view_pos)


#


def _show_history_menu(event, element_range):
    popup_menu = tk.Menu()
    for pos in element_range:
        nav = code_nav_view_history[pos]
        fnam = os.path.basename(nav.file)
        lbl = fnam + " : " + str(nav.line)

        def _goto(x):
            return lambda: history_goto(x)

        popup_menu.add_command(label=lbl, compound="left", command=_goto(pos))
    popup_menu.tk_popup(event.x_root, event.y_root)


def _show_back_menu(event):
    element_range = range(code_nav_view_pos + 1, len(code_nav_view_history))
    _show_history_menu(event, element_range)


def _show_forward_menu(event):
    element_range = reversed(range(0, code_nav_view_pos))
    _show_history_menu(event, element_range)


#


def _late_bind_buttons():

    global code_nav_bind_late
    if code_nav_bind_late:
        return

    code_nav_bind_late = True
    get_workbench().get_toolbar_button(CMD_HISTORY_BACK).bind(
        "<Button-3>", lambda x: _show_back_menu(x)
    )
    get_workbench().get_toolbar_button(CMD_HISTORY_FORWARD).bind(
        "<Button-3>", lambda x: _show_forward_menu(x)
    )


#


def in_expert_mode():
    # todo refactor to workbench
    return get_workbench().get_ui_mode() == "expert"


def load_plugin() -> None:
    get_workbench().add_view(CodeNavigationView, tr("Code Navigation"), "s")

    BACK = tr("Back in code navigation history. Click right for more...")
    get_workbench().add_command(
        CMD_HISTORY_BACK,
        "edit",
        BACK,
        lambda: history_backward(),
        caption=BACK,
        tester=lambda: _history_backward_enabled(),
        group=30,
        image="nav-backward",
        include_in_toolbar=in_expert_mode(),
    )

    FORWARD = tr("Forward in code navigation history. Click right for more...")
    get_workbench().add_command(
        CMD_HISTORY_FORWARD,
        "edit",
        FORWARD,
        lambda: history_forward(),
        caption=FORWARD,
        tester=lambda: _history_forward_enabled(),
        group=30,
        image="nav-forward",
        include_in_toolbar=in_expert_mode(),
    )

    CLRHIST = tr("Clear code navigation history")
    get_workbench().add_command(
        CMD_HISTORY_CLR,
        "edit",
        CLRHIST,
        lambda: clr_code_history(),
        caption=CLRHIST,
        tester=lambda: _history_clear_enabled(),
        group=30,
        image="clear_co",
        include_in_toolbar=in_expert_mode(),
    )
