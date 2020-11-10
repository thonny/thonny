# -*- coding: utf-8 -*-
import codecs
import io
import os
import re
import sys
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Union  # @UnusedImport

from thonny import get_workbench, roughparse, tktextext, ui_utils
from thonny.common import TextRange
from thonny.tktextext import EnhancedText
from thonny.ui_utils import EnhancedTextWithLogging, scrollbar_style, ask_string

_syntax_options = {}  # type: Dict[str, Union[str, int]]
# BREAKPOINT_SYMBOL = "•" # Bullet
# BREAKPOINT_SYMBOL = "○" # White circle
BREAKPOINT_SYMBOL = "●"  # Black circle

OLD_MAC_LINEBREAK = re.compile("\r(?!\n)")
UNIX_LINEBREAK = re.compile("(?<!\r)\n")
WINDOWS_LINEBREAK = re.compile("\r\n")

NON_TEXT_CHARS = list(map(chr, range(32)))
NON_TEXT_CHARS.remove("\t")
NON_TEXT_CHARS.remove("\n")
NON_TEXT_CHARS.remove("\r")
NON_TEXT_CHARS.remove("\f")


class SyntaxText(EnhancedText):
    def __init__(self, master=None, cnf={}, **kw):
        self.file_type = "python"
        self._syntax_options = {}
        super().__init__(master=master, cnf=cnf, **kw)
        get_workbench().bind("SyntaxThemeChanged", self._reload_syntax_options, True)
        self._reload_syntax_options()

    def set_syntax_options(self, syntax_options):
        # clear old options
        for tag_name in self._syntax_options:
            self.tag_reset(tag_name)

        background = syntax_options.get("TEXT", {}).get("background")

        # apply new options
        for tag_name in syntax_options:
            opts = syntax_options[tag_name]

            if tag_name == "string3":
                # Needs explicit background to override uniline tags
                opts["background"] = background

            if tag_name == "TEXT":
                self.configure(**opts)
            else:
                self.tag_configure(tag_name, **opts)

        self._syntax_options = syntax_options

        if "current_line" in syntax_options:
            self.tag_lower("current_line")

        self.tag_raise("sel")
        self.tag_lower("stdout")

    def _reload_theme_options(self, event=None):
        super()._reload_theme_options(event)
        self._reload_syntax_options(event)

    def _reload_syntax_options(self, event=None):
        global _syntax_options
        self.set_syntax_options(_syntax_options)

    def destroy(self):
        super().destroy()
        get_workbench().unbind("SyntaxThemeChanged", self._reload_syntax_options)

    def perform_return(self, event):
        if self.file_type == "python":
            return perform_python_return(self, event)
        else:
            return perform_simple_return(self, event)

    def perform_smart_backspace(self, event):
        if self.file_type == "python":
            return EnhancedText.perform_smart_backspace(self, event)
        else:
            self._log_keypress_for_undo(event)
            # let the default action work
            return

    def should_indent_with_tabs(self):
        return get_workbench().get_option("edit.indent_with_tabs")

    def set_file_type(self, file_type):
        self.file_type = file_type

    def is_python_text(self):
        return self.file_type == "python"

    def update_tabs(self):
        tab_chars = 4
        tab_pixels = tk.font.nametofont(self["font"]).measure("n" * tab_chars)
        tabs = [tab_pixels]
        self.configure(tabs=tabs, tabstyle="wordprocessor")


class CodeViewText(EnhancedTextWithLogging, SyntaxText):
    """Provides opportunities for monkey-patching by plugins"""

    def __init__(self, master=None, cnf={}, **kw):

        super().__init__(
            master=master,
            tag_current_line=get_workbench().get_option("view.highlight_current_line"),
            cnf=cnf,
            **kw
        )
        # Allow binding to events of all CodeView texts
        self.bindtags(self.bindtags() + ("CodeViewText",))
        tktextext.fixwordbreaks(tk._default_root)

    def on_secondary_click(self, event=None):
        super().on_secondary_click(event)
        self.mark_set("insert", "@%d,%d" % (event.x, event.y))

        menu = get_workbench().get_menu("edit")
        try:
            from thonny.plugins.debugger import get_current_debugger

            debugger = get_current_debugger()
            if debugger is not None:
                menu = debugger.get_editor_context_menu()
        except ImportError:
            pass

        menu.tk_popup(event.x_root, event.y_root)


class CodeView(tktextext.EnhancedTextFrame):
    def __init__(self, master, propose_remove_line_numbers=False, **text_frame_args):
        super().__init__(
            master,
            text_class=CodeViewText,
            undo=True,
            wrap=tk.NONE,
            vertical_scrollbar_style=scrollbar_style("Vertical"),
            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            **text_frame_args
        )

        # TODO: propose_remove_line_numbers on paste??

        assert self._first_line_number is not None

        get_workbench().bind("SyntaxThemeChanged", self._reload_theme_options, True)
        self._original_newlines = os.linesep
        self._reload_theme_options()
        self._gutter.bind("<Double-Button-1>", self._toggle_breakpoint, True)
        # self.text.tag_configure("breakpoint_line", background="pink")
        self._gutter.tag_configure("breakpoint", foreground="crimson")

        editor_font = tk.font.nametofont("EditorFont")
        spacer_font = editor_font.copy()
        spacer_font.configure(size=editor_font.cget("size") // 4)
        self._gutter.tag_configure("spacer", font=spacer_font)
        self._gutter.tag_configure("active", font="BoldEditorFont")
        self._gutter.tag_raise("spacer")

    def get_content(self):
        return self.text.get("1.0", "end-1c")  # -1c because Text always adds a newline itself

    def detect_encoding(self, data):
        enc = self.detect_encoding_without_check(data)
        try:
            codecs.lookup(enc)
            return enc
        except LookupError:
            messagebox.showerror(
                "Error", "Unknown encoding '%s'. Using utf-8 instead" % enc, master=self
            )
            return "utf-8"

    def detect_encoding_without_check(self, data):
        if self.text.is_python_text():
            import tokenize

            encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
            return encoding
        else:
            ENCODING_MARKER = re.compile(
                br"(charset|coding)[\t ]*[=: ][\t ]*[\"\']?([a-z][0-9a-z-_ ]*[0-9a-z])[\"\'\n\r\t ]?",
                re.IGNORECASE,
            )

            for line in data[:1024].splitlines():
                match = ENCODING_MARKER.search(line)
                if match and len(match.group(2)) > 2:
                    return match.group(2).decode("ascii", errors="replace")

            return "UTF-8"

    def set_file_type(self, file_type):
        self.text.set_file_type(file_type)

    def get_content_as_bytes(self):
        content = self.get_content()

        # convert all linebreaks to original format
        content = OLD_MAC_LINEBREAK.sub(self._original_newlines, content)
        content = WINDOWS_LINEBREAK.sub(self._original_newlines, content)
        content = UNIX_LINEBREAK.sub(self._original_newlines, content)

        return content.encode(self.detect_encoding(content.encode("ascii", errors="replace")))

    def set_content_as_bytes(self, data, keep_undo=False):

        encoding = self.detect_encoding(data)
        while True:
            try:
                chars = data.decode(encoding)
                if self.looks_like_text(chars):
                    self.set_content(chars, keep_undo)
                    return True
            except UnicodeDecodeError:
                pass

            encoding = ask_string(
                "Bad encoding",
                "Could not read as %s text.\nYou could try another encoding" % encoding,
                initial_value=encoding,
                options=get_proposed_encodings(),
                master=self.winfo_toplevel(),
            )
            if not encoding:
                return False

    def looks_like_text(self, chars):
        if not chars:
            return True

        non_text_char_count = 0
        for ch in chars:
            if ch in NON_TEXT_CHARS:
                non_text_char_count += 1

        return non_text_char_count / len(chars) < 0.01

    def set_content(self, content, keep_undo=False):
        content, self._original_newlines = tweak_newlines(content)

        self.text.direct_delete("1.0", tk.END)
        self.text.direct_insert("1.0", content)

        if not keep_undo:
            self.text.edit_reset()

    def _toggle_breakpoint(self, event):
        index = "@%d,%d" % (event.x, event.y)
        start_index = index + " linestart"
        end_index = index + " lineend"

        if self.text.tag_nextrange("breakpoint_line", start_index, end_index):
            self.text.tag_remove("breakpoint_line", start_index, end_index)
        else:
            line_content = self.text.get(start_index, end_index).strip()
            if line_content and line_content[0] != "#":
                self.text.tag_add("breakpoint_line", start_index, end_index)

        self.update_gutter(clean=True)

    def _clean_selection(self):
        self.text.tag_remove("sel", "1.0", "end")
        self._gutter.tag_remove("sel", "1.0", "end")

    def _text_changed(self, event):
        self.update_gutter(
            clean=self.text._last_event_changed_line_count
            and self.text.tag_ranges("breakpoint_line")
        )

    def compute_gutter_line(self, lineno, plain=False):
        if plain:
            yield str(lineno) + " ", ()
        else:
            visual_line_number = self._first_line_number + lineno - 1
            linestart = str(visual_line_number) + ".0"

            yield str(lineno), ()

            if self.text.tag_nextrange("breakpoint_line", linestart, linestart + " lineend"):
                yield BREAKPOINT_SYMBOL, ("breakpoint",)
            else:
                yield " ", ()

    def select_range(self, text_range):
        self.text.tag_remove("sel", "1.0", tk.END)

        if text_range:
            if isinstance(text_range, int):
                # it's line number
                start = str(text_range - self._first_line_number + 1) + ".0"
                end = str(text_range - self._first_line_number + 1) + ".end"
            elif isinstance(text_range, TextRange):
                start = "%s.%s" % (
                    text_range.lineno - self._first_line_number + 1,
                    text_range.col_offset,
                )
                end = "%s.%s" % (
                    text_range.end_lineno - self._first_line_number + 1,
                    text_range.end_col_offset,
                )
            else:
                assert isinstance(text_range, tuple)
                start, end = text_range

            self.text.tag_add("sel", start, end)
            if isinstance(text_range, int):
                self.text.mark_set("insert", end)
            self.text.see("%s -1 lines" % start)

    def get_breakpoint_line_numbers(self):
        result = set()
        for num_line in self._gutter.get("1.0", "end").splitlines():
            if BREAKPOINT_SYMBOL in num_line:
                result.add(int(num_line.replace(BREAKPOINT_SYMBOL, "")))
        return result

    def get_selected_range(self):
        if self.text.has_selection():
            lineno, col_offset = map(int, self.text.index(tk.SEL_FIRST).split("."))
            end_lineno, end_col_offset = map(int, self.text.index(tk.SEL_LAST).split("."))
        else:
            lineno, col_offset = map(int, self.text.index(tk.INSERT).split("."))
            end_lineno, end_col_offset = lineno, col_offset

        return TextRange(lineno, col_offset, end_lineno, end_col_offset)

    def destroy(self):
        super().destroy()
        get_workbench().unbind("SyntaxThemeChanged", self._reload_theme_options)

    def _reload_gutter_theme_options(self, event=None):
        # super()._reload_gutter_theme_options(event)
        if "GUTTER" in _syntax_options:
            opts = _syntax_options["GUTTER"].copy()
            if "background" in opts and "selectbackground" not in opts:
                opts["selectbackground"] = opts["background"]
                opts["inactiveselectbackground"] = opts["background"]
            if "foreground" in opts and "selectforeground" not in opts:
                opts["selectforeground"] = opts["foreground"]

            self._gutter.configure(opts)

            if "background" in opts:
                background = opts["background"]
                self._margin_line.configure(background=background)
                self._gutter.tag_configure("sel", background=background)

        if "breakpoint" in _syntax_options:
            self._gutter.tag_configure("breakpoint", _syntax_options["breakpoint"])


def set_syntax_options(syntax_options):
    global _syntax_options
    _syntax_options = syntax_options
    get_workbench().event_generate("SyntaxThemeChanged")


def get_syntax_options_for_tag(tag, **base_options):
    global _syntax_options
    if tag in _syntax_options:
        base_options.update(_syntax_options[tag])
    return base_options


def tweak_newlines(content):
    cr_count = len(OLD_MAC_LINEBREAK.findall(content))
    lf_count = len(UNIX_LINEBREAK.findall(content))
    crlf_count = len(WINDOWS_LINEBREAK.findall(content))

    if cr_count > 0 and lf_count == 0 and crlf_count == 0:
        original_newlines = "\r"
    elif crlf_count > 0 and lf_count == 0 and cr_count == 0:
        original_newlines = "\r\n"
    elif lf_count > 0 and crlf_count == 0 and cr_count == 0:
        original_newlines = "\n"
    else:
        original_newlines = os.linesep

    content = OLD_MAC_LINEBREAK.sub("\n", content)
    content = WINDOWS_LINEBREAK.sub("\n", content)

    return content, original_newlines


def perform_python_return(text: EnhancedText, event):
    # copied from idlelib.EditorWindow (Python 3.4.2)
    # slightly modified
    # pylint: disable=lost-exception

    assert text is event.widget
    assert isinstance(text, EnhancedText)

    try:
        # delete selection
        first, last = text.get_selection_indices()
        if first and last:
            text.delete(first, last)
            text.mark_set("insert", first)

        # Strip whitespace after insert point
        # (ie. don't carry whitespace from the right of the cursor over to the new line)
        while text.get("insert") in [" ", "\t"]:
            text.delete("insert")

        left_part = text.get("insert linestart", "insert")
        # locate first non-white character
        i = 0
        n = len(left_part)
        while i < n and left_part[i] in " \t":
            i = i + 1

        # is it only whitespace?
        if i == n:
            # start the new line with the same whitespace
            text.insert("insert", "\n" + left_part)
            return "break"

        # Turned out the left part contains visible chars
        # Remember the indent
        indent = left_part[:i]

        # Strip whitespace before insert point
        # (ie. after inserting the linebreak this line doesn't have trailing whitespace)
        while text.get("insert-1c", "insert") in [" ", "\t"]:
            text.delete("insert-1c", "insert")

        # start new line
        text.insert("insert", "\n")

        # adjust indentation for continuations and block
        # open/close first need to find the last stmt
        lno = tktextext.index2line(text.index("insert"))
        y = roughparse.RoughParser(text.indent_width, text.tabwidth)

        for context in roughparse.NUM_CONTEXT_LINES:
            startat = max(lno - context, 1)
            startatindex = repr(startat) + ".0"
            rawtext = text.get(startatindex, "insert")
            y.set_str(rawtext)
            bod = y.find_good_parse_start(
                False, roughparse._build_char_in_string_func(startatindex)
            )
            if bod is not None or startat == 1:
                break
        y.set_lo(bod or 0)

        c = y.get_continuation_type()
        if c != roughparse.C_NONE:
            # The current stmt hasn't ended yet.
            if c == roughparse.C_STRING_FIRST_LINE:
                # after the first line of a string; do not indent at all
                pass
            elif c == roughparse.C_STRING_NEXT_LINES:
                # inside a string which started before this line;
                # just mimic the current indent
                text.insert("insert", indent)
            elif c == roughparse.C_BRACKET:
                # line up with the first (if any) element of the
                # last open bracket structure; else indent one
                # level beyond the indent of the line with the
                # last open bracket
                text._reindent_to(y.compute_bracket_indent())
            elif c == roughparse.C_BACKSLASH:
                # if more than one line in this stmt already, just
                # mimic the current indent; else if initial line
                # has a start on an assignment stmt, indent to
                # beyond leftmost =; else to beyond first chunk of
                # non-whitespace on initial line
                if y.get_num_lines_in_stmt() > 1:
                    text.insert("insert", indent)
                else:
                    text._reindent_to(y.compute_backslash_indent())
            else:
                assert 0, "bogus continuation type %r" % (c,)
            return "break"

        # This line starts a brand new stmt; indent relative to
        # indentation of initial line of closest preceding
        # interesting stmt.
        indent = y.get_base_indent_string()
        text.insert("insert", indent)
        if y.is_block_opener():
            text.perform_smart_tab(event)
        elif indent and y.is_block_closer():
            text.perform_smart_backspace(event)
        return "break"
    finally:
        text.see("insert")
        text.event_generate("<<NewLine>>")
        return "break"


def perform_simple_return(text: EnhancedText, event):
    assert text is event.widget
    assert isinstance(text, EnhancedText)

    text._log_keypress_for_undo(event)

    try:
        # delete selection
        first, last = text.get_selection_indices()
        if first and last:
            text.delete(first, last)
            text.mark_set("insert", first)

        # Strip whitespace after insert point
        # (ie. don't carry whitespace from the right of the cursor over to the new line)
        while text.get("insert") in [" ", "\t"]:
            text.delete("insert")

        left_part = text.get("insert linestart", "insert")
        # locate first non-white character
        i = 0
        n = len(left_part)
        while i < n and left_part[i] in " \t":
            i = i + 1

        # start the new line with the same whitespace
        text.insert("insert", "\n" + left_part[:i])
        return "break"

    finally:
        text.see("insert")
        text.event_generate("<<NewLine>>")
        return "break"


class BinaryFileException(RuntimeError):
    pass


def get_proposed_encodings():
    # https://w3techs.com/technologies/overview/character_encoding
    result = [
        "UTF-8",
        "ISO-8859-1",
        "Windows-1251",
        "Windows-1252",
        "GB2312",
        "Shift JIS",
        "GBK",
        "EUC-KR",
        "ISO-8859-9",
        "Windows-1254",
        "EUC-JP",
        "Big5",
        "ISO-8859-2  ",
        "Windows-1250",
        "Windows-874",
        "Windows-1256",
        "ISO-8859-15",
        "US-ASCII",
        "Windows-1255",
        "TIS-620",
        "ISO-8859-7",
        "Windows-1253",
        "UTF-16",
        "KOI8-R",
        "GB18030",
        "Windows-1257",
        "KS C 5601",
        "UTF-7",
        "ISO-8859-8",
        "Windows-31J",
        "ISO-8859-5",
        "ISO-8859-6",
        "ISO-8859-4",
        "ANSI_X3.110-1983",
        "ISO-8859-3",
        "KOI8-U",
        "Big5 HKSCS",
        "ISO-2022-JP",
        "Windows-1258",
        "ISO-8859-13",
        "ISO-8859-14",
        "Windows-949",
        "ISO-8859-10",
        "ISO-8859-11",
        "ISO-8859-16",
    ]

    sys_enc = sys.getdefaultencoding()
    for item in result[:]:
        if item.lower() == sys_enc.lower():
            result.remove(item)
            sys_enc = item

    result.insert(0, sys_enc)
    return result
