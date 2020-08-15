import io
import time
import token as token_module

from thonny import get_workbench
from thonny.codeview import CodeViewText
from thonny.shell import ShellText

_OPENERS = {")": "(", "]": "[", "}": "{"}

TOKTYPES = {
    token_module.LPAR,
    token_module.RPAR,
    token_module.LBRACE,
    token_module.RBRACE,
    token_module.LSQB,
    token_module.RSQB,
}

BLANK_LINE_REGEX_STR = r"\n\s*\r?\n"
BLANK_LINE_REGEX_STR = r"^\s*$"

BLOCK_START_REGEX_STR = r"^\s*(class|def|while|elif|with|try|except|finally) "


class ParenMatcher:
    def __init__(self, text):
        self.text = text
        self._update_scheduling_id = None
        self._delayed_scheduling_id = None
        self._tokens_cache = {}

    def schedule_update(self, delay=None):
        if self._update_scheduling_id is not None:
            self.text.after_cancel(self._update_scheduling_id)

        if delay is not None:
            self._update_scheduling_id = self.text.after(delay, self.perform_update)
        else:
            self._update_scheduling_id = self.text.after_idle(self.perform_update)

    def perform_update(self):
        try:
            self.update_highlighting()
        finally:
            self._update_scheduled = False

    def invalidate_token_cache(self):
        self._tokens_cache = {}

    def update_highlighting(self):
        clear_highlighting(self.text)

        if get_workbench().get_option("view.paren_highlighting") and self.text.is_python_text():
            self._update_highlighting_for_active_range()

    def _update_highlighting_for_active_range(self):
        start_index = "1.0"
        end_index = self.text.index("end")

        # Try to reduce search range for better performance.
        index = self._find_block_start("@0,0 linestart", True)
        if index:
            start_index = index

        lower_right = "@%d,%d" % (self.text.winfo_width(), self.text.winfo_height())
        index = self._find_block_start(lower_right + " lineend", False)
        if index:
            end_index = index

        self._highlight(start_index, end_index)

    def _find_block_start(self, start_position, backwards):
        while True:
            index = self.text.search(
                BLOCK_START_REGEX_STR,
                start_position,
                regexp=True,
                backwards=backwards,
                stopindex="1.0" if backwards else "end",
            )
            if not index:
                break

            tags = self.text.tag_names(index)
            if "string3" in tags or "open_string3" in tags:
                # not a block start
                if backwards:
                    start_position = index
                else:
                    start_position = index + " +1c"
            else:
                break

        return index

    def _highlight(self, start_index, end_index):
        stack = []

        cursor_row, cursor_col = map(int, self.text.index("insert").split("."))

        for t in self._get_paren_tokens(start_index, end_index):
            if t.string in "([{":
                stack.append(t)
            elif not stack:
                # stack is empty, ie. found a closer without opener
                close_index = "%d.%d" % (t.start[0], t.end[1])
                self.text.tag_add("unclosed_expression", start_index, close_index)
                break
            elif stack[-1].string != _OPENERS[t.string]:
                # incorrect closure
                opener = stack[-1]
                open_index = "%d.%d" % opener.start
                self.text.tag_add("unclosed_expression", open_index, end_index)
                break
            else:
                # found a pair
                opener = stack[-1]
                closer = t

                # if cursor is right after opener or closer then highlight both
                if (
                    cursor_row == opener.start[0]
                    and cursor_col == opener.end[1]
                    or cursor_row == closer.start[0]
                    and cursor_col == closer.end[1]
                ):
                    self.text.tag_add("surrounding_parens", "%d.%d" % closer.start)
                    self.text.tag_add("surrounding_parens", "%d.%d" % opener.start)

                stack.pop()

        if stack:
            # something was left without closure
            opener = stack[-1]
            open_index = "%d.%d" % opener.start
            self.text.tag_add("unclosed_expression", open_index, end_index)

    def _get_paren_tokens(self, start_index, end_index):
        import tokenize

        if (start_index, end_index) in self._tokens_cache:
            return self._tokens_cache[(start_index, end_index)]

        start_row, start_col = map(int, start_index.split("."))
        source = self.text.get(start_index, end_index)
        # prepend source with empty lines and spaces to make
        # token rows and columns match with widget indices
        source = ("\n" * (start_row - 1)) + (" " * start_col) + source

        result = []
        try:
            tokens = tokenize.tokenize(io.BytesIO(source.encode("utf-8")).readline)
            for token in tokens:
                # if token.string != "" and token.string in "()[]{}":
                if token.exact_type in TOKTYPES:
                    result.append(token)
        except Exception:
            # happens eg when parens are unbalanced or there is indentation error or ...
            pass

        if start_index == "1.0" and end_index == "end":
            self._tokens_cache[(start_index, end_index)] = result

        return result


class ShellParenMatcher(ParenMatcher):
    def _update_highlighting_for_active_range(self):

        # TODO: check that cursor is in this range
        index_parts = self.text.tag_prevrange("command", "end")

        if index_parts:
            start_index, end_index = index_parts
            self._highlight(start_index, end_index)


def _update_highlighting(event, text_changed, need_update, delay=None):
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

    if need_update:
        text.paren_matcher.schedule_update(delay)


def update_highlighting_full(event):
    _update_highlighting(event, True, True)


def clear_highlighting(text):
    text.tag_remove("surrounding_parens", "0.1", "end")
    text.tag_remove("unclosed_expression", "0.1", "end")


_last_move_time = 0


def update_highlighting_move(event):
    global _last_move_time
    # needs delay because selecting with mouse causes many events
    # and I don't know how to distinguish selection from other moves
    t = time.time()
    if t - _last_move_time > 0.1:
        delay = None
    else:
        delay = 300
    _last_move_time = t
    _update_highlighting(event, False, True, delay=delay)


def update_highlighting_edit_cw(event):
    if isinstance(event.text_widget, CodeViewText):
        event.widget = event.text_widget
        trivial = event.get("trivial_for_parens", False)
        _update_highlighting(event, True, not trivial)
        if trivial:
            event.text_widget.tag_remove("surrounding_parens", "0.1", "end")


def load_plugin() -> None:
    wb = get_workbench()

    wb.set_default("view.paren_highlighting", True)
    wb.bind("TextInsert", update_highlighting_edit_cw, True)
    wb.bind("TextDelete", update_highlighting_edit_cw, True)
    wb.bind_class("CodeViewText", "<<VerticalScroll>>", update_highlighting_move, True)
    wb.bind_class("CodeViewText", "<<CursorMove>>", update_highlighting_move, True)
    wb.bind_class("ShellText", "<<TextChange>>", update_highlighting_full, True)
    wb.bind_class("ShellText", "<<CursorMove>>", update_highlighting_full, True)
    wb.bind("<<UpdateAppearance>>", update_highlighting_full, True)
