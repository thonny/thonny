import io
import tokenize

from thonny import get_workbench
from thonny.codeview import CodeViewText
from thonny.shell import ShellText

_OPENERS = {")": "(", "]": "[", "}": "{"}


class ParenMatcher:
    def __init__(self, text):
        self.text = text
        self._update_scheduled = False

        self._full_source_paren_tokens = None
        self._unclosed_dirty = True
        self._surrounding_dirty = True

    def schedule_update(self):
        if not self._update_scheduled:
            self._update_scheduled = True
            self.text.after(500, self.perform_update)

    def perform_update(self):
        try:
            self.update_highlighting()
        finally:
            self._update_scheduled = False

    def invalidate_token_cache(self):
        self._full_source_paren_tokens = None

    def update_highlighting(self):
        if not self._surrounding_dirty and not self._unclosed_dirty:
            return

        self.text.tag_remove("surrounding_parens", "0.1", "end")

        if self._unclosed_dirty:
            self.text.tag_remove("unclosed_expression", "0.1", "end")

        if get_workbench().get_option("view.paren_highlighting"):
            self._update_highlighting_for_active_range()

    def _update_highlighting_for_active_range(self):
        start_index = "1.0"
        end_index = "end"
        remaining = self._highlight_surrounding(start_index, end_index)
        self._surrounding_dirty = False

        if self._unclosed_dirty:
            self._highlight_unclosed(remaining, start_index, end_index)
            self._unclosed_dirty = False

    def _highlight_surrounding(self, start_index, end_index):
        open_index, close_index, remaining = self.find_surrounding(start_index, end_index)
        if None not in [open_index, close_index]:
            self.text.tag_add("surrounding_parens", open_index)
            self.text.tag_add("surrounding_parens", close_index)

        return remaining

    def _highlight_unclosed(self, remaining, start_index, end_index):
        # anything remaining in the stack is an unmatched opener
        # since the list is ordered, we can highlight everything starting from the first element
        if len(remaining) > 0:
            opener = remaining[0]
            open_index = "%d.%d" % (opener.start[0], opener.start[1])
            self.text.tag_add("unclosed_expression", open_index, end_index)

    def _get_paren_tokens(self, start_index, end_index):
        if (
            self._full_source_paren_tokens is not None
            and start_index == "1.0"
            and end_index == "end"
        ):
            return self._full_source_paren_tokens

        start_row, start_col = map(int, start_index.split("."))
        source = self.text.get(start_index, end_index)

        # prepend source with empty lines and spaces to make
        # token rows and columns match with widget indices
        source = ("\n" * (start_row - 1)) + (" " * start_col) + source

        result = []
        try:
            tokens = tokenize.tokenize(io.BytesIO(source.encode("utf-8")).readline)
            for token in tokens:
                if token.string != "" and token.string in "()[]{}":
                    result.append(token)
        except Exception:
            # happens eg when parens are unbalanced or there is indentation error or ...
            pass

        if start_index == "1.0" and end_index == "end":
            self._full_source_paren_tokens = result

        return result

    def find_surrounding(self, start_index, end_index):

        stack = []
        opener, closer = None, None
        open_index, close_index = None, None

        for t in self._get_paren_tokens(start_index, end_index):
            if t.string in "([{":
                stack.append(t)
            elif len(stack) > 0:
                if stack[-1].string != _OPENERS[t.string]:
                    continue
                if not closer:
                    opener = stack.pop()
                    open_index = "%d.%d" % (opener.start[0], opener.start[1])
                    token_index = "%d.%d" % (t.start[0], t.start[1])
                    if self._is_insert_between_indices(open_index, token_index):
                        closer = t
                        close_index = token_index
                else:
                    stack.pop()

        return open_index, close_index, stack

    def _is_insert_between_indices(self, index1, index2):
        return self.text.compare("insert", ">=", index1) and self.text.compare(
            "insert-1c", "<=", index2
        )


class ShellParenMatcher(ParenMatcher):
    def _update_highlighting_for_active_range(self):

        # TODO: check that cursor is in this range
        index_parts = self.text.tag_prevrange("command", "end")

        if index_parts:
            start_index, end_index = index_parts
            remaining = self._highlight_surrounding(start_index, end_index)
            self._highlight_unclosed(remaining, start_index, "end")


def _update_highlighting(event, text_changed, update_surrounding, update_unclosed):
    text = event.widget
    if not hasattr(text, "paren_matcher"):
        if isinstance(text, CodeViewText):
            text.paren_matcher = ParenMatcher(text)
        elif isinstance(text, ShellText):
            text.paren_matcher = ShellParenMatcher(text)
        else:
            return

    if text_changed:
        text.paren_matcher.invalidate_token_cache()

    if update_surrounding:
        text.paren_matcher._surrounding_dirty = True

    if update_unclosed:
        text.paren_matcher._unclosed_dirty = True

    if text.paren_matcher._surrounding_dirty or text.paren_matcher._unclosed_dirty:
        text.paren_matcher.schedule_update()


def update_highlighting_full(event):
    _update_highlighting(event, True, True, True)


def update_highlighting_move(event):
    _update_highlighting(event, False, True, False)


def update_highlighting_edit_cw(event):
    if isinstance(event.text_widget, CodeViewText):
        event.widget = event.text_widget
        trivial = event.get("is_trivial_edit", False)
        _update_highlighting(event, True, not trivial, not trivial)


def load_plugin() -> None:
    wb = get_workbench()

    wb.set_default("view.paren_highlighting", True)
    wb.bind("TextInsert", update_highlighting_edit_cw, True)
    wb.bind("TextDelete", update_highlighting_edit_cw, True)
    wb.bind_class("CodeViewText", "<<CursorMove>>", update_highlighting_move, True)
    wb.bind_class("ShellText", "<<TextChange>>", update_highlighting_full, True)
    wb.bind_class("ShellText", "<<CursorMove>>", update_highlighting_full, True)
    wb.bind("<<UpdateAppearance>>", update_highlighting_full, True)
