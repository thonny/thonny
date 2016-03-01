from thonny.code import EditorNotebook
from thonny.globals import get_workbench
from thonny.workbench import Workbench
from thonny.ast_utils import tokenize_with_char_offsets


_OPENERS = {')': '(', ']': '[', '}': '{'}
_HIGHLIGHT_CONF = ("PAREN_HIGHLIGHT", {"foreground": "Pink", "background": "DarkGray"})  # highlight tag configuration
_UNDERLINE_CONF = ("UNDERLINE", {"underline": 1})

class ParenMatcher:

    def __init__(self):
        self.text = None
        self.bound_ids = {}

    def _on_change(self, event):
        self.text.tag_delete(_HIGHLIGHT_CONF[0])
        self.text.tag_delete(_UNDERLINE_CONF[0])
        indices = self._find_surrounding()

        if None in indices:
            return
        else:
            if indices[1] != "end":
                self.text.tag_config(_HIGHLIGHT_CONF[0], **_HIGHLIGHT_CONF[1])
                self.text.tag_add(_HIGHLIGHT_CONF[0], indices[0])
                self.text.tag_add(_HIGHLIGHT_CONF[0], indices[1])
            else:
                self.text.tag_config(_UNDERLINE_CONF[0], **_UNDERLINE_CONF[1])
                self.text.tag_add(_UNDERLINE_CONF[0], indices[0], indices[1])

    def _find_surrounding(self):
        thokens = tokenize_with_char_offsets(
            self.text.get("1.0", "end"),
            filter_func=lambda x: x.string != "" and x.string in "()[]{}")

        stacks = {"(": [], "[": [], "{": []}

        opener = None
        closer = None

        for t in thokens:
            if t.string in "([{":
                stacks[t.string].append(t)
            else:
                s = stacks[_OPENERS[t.string]]
                if len(s) <= 0:
                    self.text.bell()
                    break
                opener = stacks[_OPENERS[t.string]].pop()
                if self._is_insert_between_indices("%d.%d" % (opener.lineno, opener.col_offset),
                                           "%d.%d" % (t.lineno, t.col_offset)):
                    closer = t
                    break
                opener = None

        if not opener:
            remaining = [x for s in stacks.values() for x in s]
            remaining.sort(key=lambda x: x.lineno)
            remaining.sort(key=lambda x: x.col_offset)

            if len(remaining) > 0:
                opener = remaining[0]

        open_index = "%d.%d" % (opener.lineno, opener.col_offset) if opener else None
        close_index = "%d.%d" % (closer.lineno, closer.col_offset) if closer else None

        if not close_index:
            close_index = "end"

        return open_index, close_index

    def _is_insert_between_indices(self, index1, index2):
        return self.text.compare("insert", ">=", index1) and \
               self.text.compare("insert", "<=", index2)

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


def load_plugin():
    wb = get_workbench()  # type:Workbench
    nb = wb.get_editor_notebook()  # type:EditorNotebook

    paren_matcher = ParenMatcher()

    nb.bind("<<NotebookTabChanged>>", paren_matcher._on_editor_change, True)
