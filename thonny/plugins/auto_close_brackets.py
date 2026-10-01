"""
Auto-close brackets and quotes.

Type an opening bracket or quote and the closing one gets added automatically,
cursor in between. Off by default -- toggle is in Tools > Options > General.

A few things this handles beyond the basic insert:
- typing a closing char that's already there just steps over it
- backspace on an empty pair like () deletes both sides
- typing an opener over a selection wraps it
- selecting a single bracket/quote and typing a different one swaps both ends
  (e.g. select the " in "string", type ', get 'string')
- won't auto-close a quote right after a letter (don't stays don't) or inside
  an existing string/comment

Note on the backspace handling: Thonny's own Backspace handler
(perform_smart_backspace in tktextext.py) always returns "break", so a normal
binding added after it would never fire. To get around that we put our
handlers on a bindtag that runs before Thonny's own, instead of editing any
core files.

Quote-swap only matches within the same line, and skips anything that looks
like a triple-quoted string -- those can span multiple lines and aren't
handled here.
"""

from thonny import get_workbench

OPTION_NAME = "edit.auto_close_brackets"
BINDTAG = "AutoCloseBrackets"

BRACKETS = {"(": ")", "[": "]", "{": "}"}
CLOSERS = set(BRACKETS.values())
CLOSER_TO_OPENER = {v: k for k, v in BRACKETS.items()}
QUOTES = {'"', "'"}
PAIR = {**BRACKETS, '"': '"', "'": "'"}

BRACKET_FAMILY = {
    "(": ("(", ")"),
    ")": ("(", ")"),
    "[": ("[", "]"),
    "]": ("[", "]"),
    "{": ("{", "}"),
    "}": ("{", "}"),
}

WORD_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")

# tags Thonny's syntax highlighter uses for strings/comments
STRING_OR_COMMENT_TAGS = {"string", "string3", "open_string", "open_string3", "comment"}


def _enabled():
    try:
        return get_workbench().get_option(OPTION_NAME)
    except Exception:
        return False


def _char_after(text):
    return text.get("insert", "insert+1c")


def _char_before(text):
    return text.get("insert-1c", "insert")


def _has_selection(text):
    return bool(text.tag_ranges("sel"))


def _get_single_char_selection(text):
    if not _has_selection(text):
        return None
    start = text.index("sel.first")
    end = text.index("sel.last")
    if text.compare(end, "==", f"{start}+1c"):
        return start, text.get(start)
    return None


def _in_string_or_comment(text):
    return any(t in STRING_OR_COMMENT_TAGS for t in text.tag_names("insert-1c"))


# --- matching logic for the swap feature ---


def _find_matching_bracket(text, sel_start, sel_char):
    if sel_char in BRACKETS:
        opener, closer = sel_char, BRACKETS[sel_char]
        depth = 1
        idx = text.index(f"{sel_start}+1c")
        end = text.index("end")
        while text.compare(idx, "<", end):
            c = text.get(idx)
            if c == opener:
                depth += 1
            elif c == closer:
                depth -= 1
                if depth == 0:
                    return idx
            idx = text.index(f"{idx}+1c")
        return None
    elif sel_char in CLOSERS:
        closer = sel_char
        opener = CLOSER_TO_OPENER[closer]
        depth = 1
        idx = text.index(f"{sel_start}-1c")
        start = text.index("1.0")
        while True:
            c = text.get(idx)
            if c == closer:
                depth += 1
            elif c == opener:
                depth -= 1
                if depth == 0:
                    return idx
            if text.compare(idx, "<=", start):
                break
            idx = text.index(f"{idx}-1c")
        return None
    return None


def _is_escaped(text, idx):
    # odd number of backslashes right before idx, same line
    count = 0
    pos = idx
    line_start = text.index(f"{idx} linestart")
    while text.compare(pos, ">", line_start):
        pos = text.index(f"{pos}-1c")
        if text.get(pos) == "\\":
            count += 1
        else:
            break
    return count % 2 == 1


def _looks_like_triple_quote(text, idx, quote_char):
    triple = quote_char * 3
    windows = (
        text.get(f"{idx}-2c", f"{idx}+1c"),
        text.get(f"{idx}-1c", f"{idx}+2c"),
        text.get(idx, f"{idx}+3c"),
    )
    return triple in windows


def _find_matching_quote(text, sel_start, quote_char):
    if _looks_like_triple_quote(text, sel_start, quote_char):
        return None

    line_start = text.index(f"{sel_start} linestart")
    line_end = text.index(f"{sel_start} lineend")

    occurrences = []
    idx = line_start
    while text.compare(idx, "<", line_end):
        if text.get(idx) == quote_char and not _is_escaped(text, idx):
            occurrences.append(idx)
        idx = text.index(f"{idx}+1c")

    if sel_start not in occurrences or len(occurrences) < 2:
        return None

    pos = occurrences.index(sel_start)
    if pos % 2 == 0 and pos + 1 < len(occurrences):
        return occurrences[pos + 1]
    if pos % 2 == 1:
        return occurrences[pos - 1]
    return None


def _swap_char_at(text, index, new_char):
    text.delete(index, f"{index}+1c")
    text.insert(index, new_char)


def _handle_single_char_swap(text, typed_char, sel_start, sel_char):
    if sel_char in BRACKETS or sel_char in CLOSERS:
        new_open, new_close = BRACKET_FAMILY.get(typed_char, (None, None))
        if new_open is None:
            return None
        partner = _find_matching_bracket(text, sel_start, sel_char)
        if partner is None:
            return None
        if sel_char in BRACKETS:
            opener_index, closer_index = sel_start, partner
        else:
            opener_index, closer_index = partner, sel_start
        _swap_char_at(text, opener_index, new_open)
        _swap_char_at(text, closer_index, new_close)
        text.tag_remove("sel", "1.0", "end")
        text.mark_set("insert", f"{sel_start}+1c")
        return "break"

    if sel_char in QUOTES:
        if typed_char not in QUOTES:
            return None
        partner = _find_matching_quote(text, sel_start, sel_char)
        if partner is None:
            return None
        _swap_char_at(text, sel_start, typed_char)
        _swap_char_at(text, partner, typed_char)
        text.tag_remove("sel", "1.0", "end")
        text.mark_set("insert", f"{sel_start}+1c")
        return "break"

    return None


# --- the simpler stuff: insert pairs, type-over, wrap selections ---


def _wrap_selection(text, opener, closer):
    start = text.index("sel.first")
    selected = text.get(start, "sel.last")
    text.edit_separator()
    text.delete(start, "sel.last")
    text.insert(start, opener + selected + closer)
    inner_end = "%s+%dc" % (start, len(selected) + 1)
    text.tag_remove("sel", "1.0", "end")
    text.tag_add("sel", "%s+1c" % start, inner_end)
    text.mark_set("insert", inner_end)
    return "break"


def _handle_opener(text, opener):
    if _has_selection(text):
        return _wrap_selection(text, opener, BRACKETS[opener])
    text.insert("insert", opener + BRACKETS[opener])
    text.mark_set("insert", "insert-1c")
    return "break"


def _handle_quote(text, quote):
    if _has_selection(text):
        return _wrap_selection(text, quote, quote)
    if _char_after(text) == quote:
        text.mark_set("insert", "insert+1c")
        return "break"
    if _char_before(text) in WORD_CHARS:
        return None
    if _in_string_or_comment(text):
        return None
    text.insert("insert", quote + quote)
    text.mark_set("insert", "insert-1c")
    return "break"


def _handle_closer(text, closer):
    if _char_after(text) == closer:
        text.mark_set("insert", "insert+1c")
        return "break"
    return None


def _on_key(event):
    if not _enabled():
        return None

    text = event.widget
    ch = event.char
    if not ch or len(ch) != 1:
        return None

    is_relevant = ch in BRACKETS or ch in QUOTES or ch in CLOSERS
    if not is_relevant:
        return None

    single = _get_single_char_selection(text)
    if single is not None:
        sel_start, sel_char = single
        if sel_char in BRACKETS or sel_char in CLOSERS or sel_char in QUOTES:
            result = _handle_single_char_swap(text, ch, sel_start, sel_char)
            if result == "break":
                return "break"
            # no partner found -- fall through to normal handling, which for
            # a 1-char selection means wrapping it instead

    if ch in BRACKETS:
        return _handle_opener(text, ch)
    if ch in QUOTES:
        return _handle_quote(text, ch)
    if ch in CLOSERS:
        return _handle_closer(text, ch)
    return None


def _on_backspace(event):
    if not _enabled():
        return None

    text = event.widget
    if _has_selection(text):
        return None
    prev = _char_before(text)
    if prev in PAIR and _char_after(text) == PAIR[prev]:
        text.edit_separator()
        text.delete("insert-1c", "insert+1c")
        return "break"
    return None


def _on_editor_text_created(event):
    text = event.text_widget
    if BINDTAG not in text.bindtags():
        text.bindtags((BINDTAG,) + text.bindtags())


def load_plugin():
    get_workbench().set_default(OPTION_NAME, False)
    get_workbench().bind_class(BINDTAG, "<Key>", _on_key, True)
    get_workbench().bind_class(BINDTAG, "<BackSpace>", _on_backspace, True)
    get_workbench().bind("EditorTextCreated", _on_editor_text_created, True)
