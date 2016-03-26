from thonny.code import EditorNotebook
from thonny.globals import get_workbench
from thonny.workbench import Workbench
from thonny.ast_utils import tokenize_with_char_offsets


_OPENERS = {')': '(', ']': '[', '}': '{'}
_HIGHLIGHT_CONF = ("PAREN_HIGHLIGHT", {"foreground": "White", "background": "DarkGray"})  # highlight tag configuration
_UNDERLINE_CONF = ("UNDERLINE", {"background": "LightGray"})


class ParenMatcher:

    def __init__(self):
        self.text = None
        self._remaining = None
        self.bound_ids = {}

    def _on_change(self, event):
        self.text.tag_delete(_HIGHLIGHT_CONF[0])
        self.text.tag_delete(_UNDERLINE_CONF[0])

        self._highlight_surrounding()
        self._highlight_unclosed()

    def _highlight_surrounding(self):
        indices = self._find_surrounding()
        if None in indices:
            return
        else:
            self.text.tag_config(_HIGHLIGHT_CONF[0], **_HIGHLIGHT_CONF[1])
            self.text.tag_add(_HIGHLIGHT_CONF[0], indices[0])
            self.text.tag_add(_HIGHLIGHT_CONF[0], indices[1])

    # highlights an unclosed bracket
    def _highlight_unclosed(self):
        # anything remaining in the stack is an unmatched opener
        # since the list is ordered, we can highlight everything starting from the first element
        if self._remaining:
            opener = self._remaining[0]
            open_index = "%d.%d" % (opener.lineno, opener.col_offset)
            self.text.tag_config(_UNDERLINE_CONF[0], **_UNDERLINE_CONF[1])
            self.text.tag_add(_UNDERLINE_CONF[0], open_index, "end")

    def _find_surrounding(self, src_str=None):
        if not src_str:
            src_str = self.text.get("1.0", "end")
        tokens = tokenize_with_char_offsets(
            src_str,
            filter_func=lambda x: x.string != "" and x.string in "()[]{}")

        stack = []
        opener, closer = None, None
        open_index, close_index = None, None

        for t in tokens:
            if t.string in "([{":
                stack.append(t)
            elif len(stack) > 0:
                if stack[-1].string != _OPENERS[t.string]:
                    self.text.bell()
                    continue
                if not closer:
                    opener = stack.pop()
                    open_index = "%d.%d" % (opener.lineno, opener.col_offset)
                    token_index = "%d.%d" % (t.lineno, t.col_offset)
                    if self._is_insert_between_indices(open_index, token_index):
                        closer = t
                        close_index = token_index
                else:
                    stack.pop()
        # used by _highlight_unclosed
        self._remaining = stack

        return open_index, close_index

    def _is_insert_between_indices(self, index1, index2):
        return self.text.compare("insert", ">=", index1) and \
               self.text.compare("insert-1c", "<=", index2)

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
