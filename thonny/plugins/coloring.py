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
import keyword
import builtins

from thonny.globals import get_workbench
from thonny.shell import ShellText
from thonny.codeview import CodeViewText

def matches_any(name, alternates):
    "Return a named group pattern matching list of alternates."
    return "(?P<%s>" % name + "|".join(alternates) + ")"

class SyntaxColorer:
    def __init__(self, text, main_font, bold_font):
        self.text = text
        self._compile_regexes()
        self._config_colors(main_font, bold_font)
        self._update_scheduled = False
        self._dirty_ranges = set()
    
    def _compile_regexes(self):
        kw = r"\b" + matches_any("KEYWORD", keyword.kwlist) + r"\b"
        builtinlist = [str(name) for name in dir(builtins)
                                            if not name.startswith('_') and \
                                            name not in keyword.kwlist]
        
        # TODO: move builtin handling to global-local
        builtin = r"([^.'\"\\#]\b|^)" + matches_any("BUILTIN", builtinlist) + r"\b"
        comment = matches_any("COMMENT", [r"#[^\n]*"])
        magic_command = matches_any("MAGIC_COMMAND", [r"^%[^\n]*"]) # used only in shell
        stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR|rb|rB|Rb|RB)?"
        
        sqstring_open = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*\n?"
        sqstring_closed = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'"
        
        dqstring_open = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*\n?'
        dqstring_closed = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"'
        
        sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
        dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
        
        sq3delimiter = stringprefix + "'''"
        dq3delimiter = stringprefix + '"""'
        
        string_open = matches_any("STRING_OPEN", [sqstring_open, dqstring_open])
        string_closed = matches_any("STRING_CLOSED", [sqstring_closed, dqstring_closed])
        string3_delimiter = matches_any("DELIMITER3", [sq3delimiter, dq3delimiter])
        string3 = matches_any("STRING3", [dq3string, sq3string])
        
        self.uniline_regex = re.compile(
            kw 
            + "|" + builtin 
            + "|" + comment 
            + "|" + magic_command 
            + "|" + string3_delimiter # to avoid marking """ and ''' as single line string in uniline mode
            + "|" + string_closed 
            + "|" + string_open
            , re.S)
        
        self.multiline_regex = re.compile(
            string3
            + "|" + comment 
            + "|" + magic_command 
            #+ "|" + string_closed # need to include single line strings otherwise '"""' ... '""""' will give wrong result
            + "|" + string_open # (seems that it works faster and also correctly with only open strings)
            , re.S)
        
        self.id_regex = re.compile(r"\s+(\w+)", re.S)

    def _config_colors(self, main_font, bold_font):
        string_foreground = "DarkGreen"
        open_string_background = "#c3f9d3"
        self.uniline_tagdefs = {
            "COMMENT"       : {"font":main_font, 'background':None, 'foreground':"DarkGray", },
            "MAGIC_COMMAND" : {"font":main_font, 'background':None, 'foreground':"DarkGray", },
            "STRING_CLOSED" : {"font":main_font, 'background':None, 'foreground':string_foreground, },
            "STRING_OPEN"   : {"font":main_font, 'background': open_string_background, "foreground": string_foreground},
            "KEYWORD"       : {"font":bold_font, 'background':None, 'foreground':"#7f0055", },
            "BUILTIN"       : {"font":main_font, 'background':None, 'foreground':None},
            #"DEFINITION"    : {},
            }
        
        self.multiline_tagdefs = {
            "STRING_CLOSED3": self.uniline_tagdefs["STRING_CLOSED"],
            "STRING_OPEN3"  : self.uniline_tagdefs["STRING_OPEN"],
            }
        
        # Note that order of configuring is important for managing correct tag priorities
        # (as STRING_*3 must have higher priority than other tags, as its 
        # text may also contain other tags)
        for tagdefs in [self.multiline_tagdefs, self.uniline_tagdefs]:
            for tag, cnf in tagdefs.items():
                if cnf:
                    self.text.tag_configure(tag, **cnf)
        
        self.text.tag_raise("STRING_CLOSED3", "KEYWORD")
        self.text.tag_raise("STRING_OPEN3", "KEYWORD")
        self.text.tag_raise("STRING_CLOSED3", "STRING_CLOSED")
        self.text.tag_raise("STRING_OPEN3", "STRING_OPEN")
        self.text.tag_raise('sel')

    def schedule_update(self, event):
        
        # Allow reducing work by remembering only changed lines
        if event.sequence == "TextInsert":
            index = self.text.index(event.index)
            start_row = int(index.split(".")[0])
            end_row = start_row + event.text.count("\n")
            start_index = "%d.%d" % (start_row, 0)
            end_index = "%d.%d" % (end_row + 1, 0)
        elif event.sequence == "TextDelete":
            assert event.index1 != None
            index = self.text.index(event.index1)
            assert index != None
            print(event.index1, type(event.index1))
            print(index, type(index), event)
            start_row = int(index.split(".")[0])
            start_index = "%d.%d" % (start_row, 0)
            end_index = "%d.%d" % (start_row + 1, 0)
        else:
            return
        
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
        
        for match in self.uniline_regex.finditer(chars):
            for token_type, token_text in match.groupdict().items():
                if token_text and token_type in self.uniline_tagdefs:
                    token_text = token_text.strip()
                    match_start, match_end = match.span(token_type)
                    
                    self.text.tag_add(token_type,
                             start + "+%dc" % match_start,
                             start + "+%dc" % match_end)
                    
                    # Mark also the word following def or class
                    if token_text in ("def", "class"):
                        id_match = self.id_regex.match(chars, match_end)
                        if id_match:
                            id_match_start, id_match_end = id_match.span(1)
                            self.text.tag_add("DEFINITION",
                                         start + "+%dc" % id_match_start,
                                         start + "+%dc" % id_match_end)
                
        
         
    def _update_multiline_tokens(self, start, end):
        chars = self.text.get(start, end)
        # clear old tags
        for tag in self.multiline_tagdefs:
            self.text.tag_remove(tag, start, end)
        
        interesting_token_types = list(self.multiline_tagdefs.keys()) + ["STRING3"]
        for match in self.multiline_regex.finditer(chars):
            for token_type, token_text in match.groupdict().items():
                if token_text and token_type in interesting_token_types:
                    token_text = token_text.strip()
                    match_start, match_end = match.span(token_type)
                    if token_type == "STRING3":
                        if (token_text.startswith('"""') and not token_text.endswith('"""')
                            or token_text.startswith("'''") and not token_text.endswith("'''")
                            or len(token_text) == 3):
                            str_end = int(float(self.text.index(start + "+%dc" % match_end)))
                            file_end = int(float(self.text.index("end")))

                            if str_end == file_end:
                                token_type = "STRING_OPEN3"
                            else:
                                token_type = None
                        elif len(token_text) >= 4 and token_text[-4] == "\\":
                            token_type = "STRING_OPEN3"
                        else:
                            token_type = "STRING_CLOSED3"
                    
                    self.text.tag_add(token_type,
                             start + "+%dc" % match_start,
                             start + "+%dc" % match_end)
        

class CodeViewSyntaxColorer(SyntaxColorer):
    def _update_coloring(self):
        for dirty_range in self._dirty_ranges:
            self._update_uniline_tokens(*dirty_range)
        
        # Multiline tokens need to be searched from the whole source
        self._update_multiline_tokens("1.0", "end")

class ShellSyntaxColorer(SyntaxColorer):
    def _update_coloring(self):
        parts = self.text.tag_prevrange("command", "end")
        
        if parts:
            end_row, end_col = map(int, self.text.index(parts[1]).split("."))
            
            if end_col != 0: # if not just after the last linebreak
                end_row += 1 # then extend the range to the beginning of next line
                end_col = 0  # (otherwise open strings are not displayed correctly)
            
            start_index = parts[0]
            end_index = "%d.%d" % (end_row, end_col)
            
            self._update_uniline_tokens(start_index, end_index)
            self._update_multiline_tokens(start_index, end_index)

def update_coloring(event):
    text = event.text_widget
    
    if not hasattr(text, "syntax_colorer"):
        if isinstance(text, ShellText):
            class_ = ShellSyntaxColorer
        elif isinstance(text, CodeViewText):
            class_ = CodeViewSyntaxColorer
        else:
            return
        
        text.syntax_colorer = class_(text, get_workbench().get_font("EditorFont"),
                            get_workbench().get_font("BoldEditorFont"))
    
    text.syntax_colorer.schedule_update(event)

def load_plugin():
    wb = get_workbench() 

    wb.bind("TextInsert", update_coloring, True)
    wb.bind("TextDelete", update_coloring, True)
