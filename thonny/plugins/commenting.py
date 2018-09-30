import tkinter as tk

from thonny import get_workbench
from thonny.common import TextRange
from thonny.ui_utils import select_sequence

BLOCK_COMMENT_PREFIX = "#"


def _get_focused_writable_text():
    widget = get_workbench().focus_get()
    # In Ubuntu when moving from one menu to another, this may give None when text is actually focused
    if isinstance(widget, tk.Text) and (
        not hasattr(widget, "is_read_only") or not widget.is_read_only()
    ):
        return widget
    else:
        return None


def _writable_text_is_focused():
    return _get_focused_writable_text() is not None


def _selection_is_line_commented(text):
    sel_range = _get_focused_code_range(text)

    for lineno in range(sel_range.lineno, sel_range.end_lineno + 1):
        line = text.get(str(lineno) + ".0", str(lineno) + ".end")
        if not line.startswith(BLOCK_COMMENT_PREFIX):
            return False

    return True


def _select_lines(text, first_line, last_line):
    text.tag_remove("sel", "1.0", tk.END)
    text.tag_add("sel", str(first_line) + ".0", str(last_line) + ".end")


def _toggle_selection_comment(text):
    if _selection_is_line_commented(text):
        _uncomment_selection(text)
    else:
        _comment_selection(text)


def _comment_selection(text):
    """Adds ## in front of all selected lines if any lines are selected, 
    or just the current line otherwise"""

    sel_range = _get_focused_code_range(text)

    for lineno in range(sel_range.lineno, sel_range.end_lineno + 1):
        text.insert(str(lineno) + ".0", BLOCK_COMMENT_PREFIX)

    if sel_range.end_lineno > sel_range.lineno:
        _select_lines(text, sel_range.lineno, sel_range.end_lineno)

    text.edit_separator()


def _uncomment_selection(text):
    sel_range = _get_focused_code_range(text)

    for lineno in range(sel_range.lineno, sel_range.end_lineno + 1):
        line = text.get(str(lineno) + ".0", str(lineno) + ".end")
        if line.startswith(BLOCK_COMMENT_PREFIX):
            text.delete(
                str(lineno) + ".0", str(lineno) + "." + str(len(BLOCK_COMMENT_PREFIX))
            )


def _get_focused_code_range(text):
    if len(text.tag_ranges("sel")) > 0:
        lineno, col_offset = map(int, text.index(tk.SEL_FIRST).split("."))
        end_lineno, end_col_offset = map(int, text.index(tk.SEL_LAST).split("."))

        if end_lineno > lineno and end_col_offset == 0:
            # SelectAll includes nonexisting extra line
            end_lineno -= 1
            end_col_offset = int(text.index(str(end_lineno) + ".end").split(".")[1])
    else:
        lineno, col_offset = map(int, text.index(tk.INSERT).split("."))
        end_lineno, end_col_offset = lineno, col_offset

    return TextRange(lineno, col_offset, end_lineno, end_col_offset)


def _cmd_toggle_selection_comment():
    text = _get_focused_writable_text()
    if text is not None:
        _toggle_selection_comment(text)


def _cmd_comment_selection():
    text = _get_focused_writable_text()
    if text is not None:
        _comment_selection(text)


def _cmd_uncomment_selection():
    text = _get_focused_writable_text()
    if text is not None:
        _uncomment_selection(text)


def load_plugin() -> None:

    get_workbench().add_command(
        "toggle_comment",
        "edit",
        "Toggle comment",
        _cmd_toggle_selection_comment,
        default_sequence=select_sequence("<Control-Key-3>", "<Command-Key-3>"),
        tester=_writable_text_is_focused,
        group=50,
    )

    get_workbench().add_command(
        "comment_selection",
        "edit",
        "Comment out",
        _cmd_comment_selection,
        default_sequence="<Alt-Key-3>",
        tester=_writable_text_is_focused,
        group=50,
    )

    get_workbench().add_command(
        "uncomment_selection",
        "edit",
        "Uncomment",
        _cmd_uncomment_selection,
        default_sequence="<Alt-Key-4>",
        tester=_writable_text_is_focused,
        group=50,
    )
