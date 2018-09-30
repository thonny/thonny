"""
Each text will get its on SyntaxColorer.

For performance reasons, coloring is updated in 2 phases:
    1. recolor single-line tokens on the modified line(s)
    2. recolor multi-line tokens (triple-quoted strings) in the whole text

First phase may insert wrong tokens inside triple-quoted strings, but the 
priorities of triple-quoted-string tags are higher and therefore user 
doesn't see these wrong taggings.

In Shell only current command entry is colored
    
Regexes are adapted from idlelib
"""

import re

from thonny import get_workbench
from thonny.codeview import CodeViewText
from thonny.shell import ShellText


class SyntaxColorer:
    def __init__(self, text):
        self.text = text
        self._compile_regexes()
        self._config_tags()
        self._update_scheduled = False
        self._dirty_ranges = set()
        self._use_coloring = True

    def _compile_regexes(self):
        from thonny.token_utils import (
            BUILTIN,
            COMMENT,
            MAGIC_COMMAND,
            STRING3,
            STRING3_DELIMITER,
            STRING_OPEN,
            KEYWORD,
            STRING_CLOSED,
            NUMBER,
        )

        self.uniline_regex = re.compile(
            KEYWORD
            + "|"
            + BUILTIN
            + "|"
            + NUMBER
            + "|"
            + COMMENT
            + "|"
            + MAGIC_COMMAND
            + "|"
            + STRING3_DELIMITER  # to avoid marking """ and ''' as single line string in uniline mode
            + "|"
            + STRING_CLOSED
            + "|"
            + STRING_OPEN,
            re.S,
        )  # @UndefinedVariable

        self.multiline_regex = re.compile(
            STRING3 + "|" + COMMENT + "|" + MAGIC_COMMAND
            # + "|" + STRING_CLOSED # need to include single line strings otherwise '"""' ... '""""' will give wrong result
            + "|"
            + STRING_OPEN,  # (seems that it works faster and also correctly with only open strings)
            re.S,
        )  # @UndefinedVariable

        self.id_regex = re.compile(r"\s+(\w+)", re.S)  # @UndefinedVariable

    def _config_tags(self):
        self.uniline_tagdefs = {
            "comment",
            "magic",
            "string",
            "open_string",
            "keyword",
            "number",
            "builtin",
            "definition",
        }
        self.multiline_tagdefs = {"string3", "open_string3"}
        self.text.tag_raise("sel")
        tags = self.text.tag_names()
        # take into account that without themes some tags may be undefined
        if "string3" in tags:
            self.text.tag_raise("string3")
        if "open_string3" in tags:
            self.text.tag_raise("open_string3")

    def schedule_update(self, event, use_coloring=True):
        self._use_coloring = use_coloring

        # Allow reducing work by remembering only changed lines
        if hasattr(event, "sequence"):
            if event.sequence == "TextInsert":
                index = self.text.index(event.index)
                start_row = int(index.split(".")[0])
                end_row = start_row + event.text.count("\n")
                start_index = "%d.%d" % (start_row, 0)
                end_index = "%d.%d" % (end_row + 1, 0)
            elif event.sequence == "TextDelete":
                index = self.text.index(event.index1)
                start_row = int(index.split(".")[0])
                start_index = "%d.%d" % (start_row, 0)
                end_index = "%d.%d" % (start_row + 1, 0)
        else:
            start_index = "1.0"
            end_index = "end"

        self._dirty_ranges.add((start_index, end_index))

        def perform_update():
            try:
                self._update_coloring()
            finally:
                self._update_scheduled = False
                self._dirty_ranges = set()

        if not self._update_scheduled:
            self._update_scheduled = True
            self.text.after_idle(perform_update)

    def _update_coloring(self):
        self._update_uniline_tokens("1.0", "end")
        self._update_multiline_tokens("1.0", "end")

    def _update_uniline_tokens(self, start, end):
        chars = self.text.get(start, end)

        # clear old tags
        for tag in self.uniline_tagdefs:
            self.text.tag_remove(tag, start, end)

        if not self._use_coloring:
            return

        for match in self.uniline_regex.finditer(chars):
            for token_type, token_text in match.groupdict().items():
                if token_text and token_type in self.uniline_tagdefs:
                    token_text = token_text.strip()
                    match_start, match_end = match.span(token_type)

                    self.text.tag_add(
                        token_type,
                        start + "+%dc" % match_start,
                        start + "+%dc" % match_end,
                    )

                    # Mark also the word following def or class
                    if token_text in ("def", "class"):
                        id_match = self.id_regex.match(chars, match_end)
                        if id_match:
                            id_match_start, id_match_end = id_match.span(1)
                            self.text.tag_add(
                                "definition",
                                start + "+%dc" % id_match_start,
                                start + "+%dc" % id_match_end,
                            )

    def _update_multiline_tokens(self, start, end):
        chars = self.text.get(start, end)
        # clear old tags
        for tag in self.multiline_tagdefs:
            self.text.tag_remove(tag, start, end)

        if not self._use_coloring:
            return

        # Count number of open multiline strings to be able to detect when string gets closed
        self.text.number_of_open_multiline_strings = 0

        interesting_token_types = list(self.multiline_tagdefs) + ["string3"]
        for match in self.multiline_regex.finditer(chars):
            for token_type, token_text in match.groupdict().items():
                if token_text and token_type in interesting_token_types:
                    token_text = token_text.strip()
                    match_start, match_end = match.span(token_type)
                    if token_type == "string3":
                        if (
                            token_text.startswith('"""')
                            and not token_text.endswith('"""')
                            or token_text.startswith("'''")
                            and not token_text.endswith("'''")
                            or len(token_text) == 3
                        ):
                            str_end = int(
                                float(self.text.index(start + "+%dc" % match_end))
                            )
                            file_end = int(float(self.text.index("end")))

                            if str_end == file_end:
                                token_type = "open_string3"
                                self.text.number_of_open_multiline_strings += 1
                            else:
                                token_type = None
                        elif len(token_text) >= 4 and token_text[-4] == "\\":
                            token_type = "open_string3"
                            self.text.number_of_open_multiline_strings += 1
                        else:
                            token_type = "string3"

                    token_start = start + "+%dc" % match_start
                    token_end = start + "+%dc" % match_end
                    # clear uniline tags
                    for tag in self.uniline_tagdefs:
                        self.text.tag_remove(tag, token_start, token_end)
                    # add tag
                    self.text.tag_add(token_type, token_start, token_end)


class CodeViewSyntaxColorer(SyntaxColorer):
    def _update_coloring(self):
        for dirty_range in self._dirty_ranges:
            self._update_uniline_tokens(*dirty_range)

        # Multiline tokens need to be searched from the whole source
        open_before = getattr(self.text, "number_of_open_multiline_strings", 0)
        self._update_multiline_tokens("1.0", "end")
        open_after = getattr(self.text, "number_of_open_multiline_strings", 0)

        if open_after == 0 and open_before != 0:
            # recolor uniline tokens after closing last open multiline string
            self._update_uniline_tokens("1.0", "end")


class ShellSyntaxColorer(SyntaxColorer):
    def _update_coloring(self):
        parts = self.text.tag_prevrange("command", "end")

        if parts:
            end_row, end_col = map(int, self.text.index(parts[1]).split("."))

            if end_col != 0:  # if not just after the last linebreak
                end_row += 1  # then extend the range to the beginning of next line
                end_col = 0  # (otherwise open strings are not displayed correctly)

            start_index = parts[0]
            end_index = "%d.%d" % (end_row, end_col)

            self._update_uniline_tokens(start_index, end_index)
            self._update_multiline_tokens(start_index, end_index)


def update_coloring(event):
    if hasattr(event, "text_widget"):
        text = event.text_widget
    else:
        text = event.widget

    if not hasattr(text, "syntax_colorer"):
        if isinstance(text, ShellText):
            class_ = ShellSyntaxColorer
        elif isinstance(text, CodeViewText):
            class_ = CodeViewSyntaxColorer
        else:
            return

        text.syntax_colorer = class_(text)

    text.syntax_colorer.schedule_update(
        event, get_workbench().get_option("view.syntax_coloring")
    )


def load_plugin() -> None:
    wb = get_workbench()

    wb.set_default("view.syntax_coloring", True)
    wb.bind("TextInsert", update_coloring, True)
    wb.bind("TextDelete", update_coloring, True)
    wb.bind("<<UpdateAppearance>>", update_coloring, True)
