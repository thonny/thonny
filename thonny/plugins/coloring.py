# copied from idlelib and modified

import time
import re
import keyword
import builtins
import tkinter as tk

from thonny.globals import get_workbench
from thonny.shell import ShellText

DEBUG = False


def matches_any(name, alternates):
    "Return a named group pattern matching list of alternates."
    return "(?P<%s>" % name + "|".join(alternates) + ")"


def make_pat():
    kw = r"\b" + matches_any("KEYWORD", keyword.kwlist) + r"\b"
    builtinlist = [str(name) for name in dir(builtins)
                                        if not name.startswith('_') and \
                                        name not in keyword.kwlist]

    # self.file = open("file") :
    # 1st 'file' colorized normal, 2nd as builtin, 3rd as string
    builtin = r"([^.'\"\\#]\b|^)" + matches_any("BUILTIN", builtinlist) + r"\b"
    comment = matches_any("COMMENT", [r"#[^\n]*"])
    stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR|rb|rB|Rb|RB)?"

    sqstring_open = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*\n?"
    sqstring_closed = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'"

    dqstring_open = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*\n?'
    dqstring_closed = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"'

    sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'

    string_open = matches_any("STRING_OPEN", [sqstring_open, dqstring_open])
    string_closed = matches_any("STRING_CLOSED", [sqstring_closed, dqstring_closed])

    return kw + "|" + builtin + "|" + comment + "|" + matches_any("STRING3", [dq3string, sq3string]) + "|" + \
           string_closed + "|" + string_open + "|" + matches_any("SYNC", [r"\n"])


class SyntaxColorer:
    def __init__(self, text, main_font, bold_font):
        self.text = text
        self.prog = re.compile(make_pat(), re.S)
        self.idprog = re.compile(r"\s+(\w+)", re.S)
        self.asprog = re.compile(r".*?\b(as)\b")
        self._load_tag_defs(main_font, bold_font)
        self._config_colors()
        self.notify_active_range()

    def notify_active_range(self):
        self._notify_range("1.0", "end")

    def _config_colors(self):
        for tag, cnf in self.tagdefs.items():
            if cnf:
                self.text.tag_configure(tag, **cnf)
        self.text.tag_raise('sel')

    def _load_tag_defs(self, main_font, bold_font):
        self.tagdefs = {
            "SYNC": {'background':None,'foreground':None},
            "TODO": {'background':None,'foreground':None},

            "COMMENT": {'background':None,'foreground':"DarkGray"},
            "KEYWORD": {'background':None,'foreground':"#7f0055", "font":bold_font},
            #"KEYWORD": {'background':None,'foreground':"#ff7700", "font":ui_utils.BOLD_EDITOR_FONT},
            "BUILTIN": {'background':None,'foreground':None},
            #"STRING":  {'background':None,'foreground':"#00AA00"},
            "STRING_CLOSED":  {'background':None,'foreground':"DarkGreen"},
            "STRING_OPEN": {'background': "#c3f9d3", "foreground": "DarkGreen"},
            "DEFINITION": {},
            "BREAK": {'background':None,'foreground':"Purple"},
            "ERROR": {'background':None,'foreground':"Red"},

            # The following is used by ReplaceDialog:
            "hit": {'background':"Yellow",'foreground':None}
            }

        if DEBUG: print('tagdefs',self.tagdefs)

    after_id = None
    allow_colorizing = True
    colorizing = False
    
    def _notify_range(self, index1, index2=None):
        self.text.tag_add("TODO", index1, index2)
        if self.after_id:
            if DEBUG: print("colorizing already scheduled")
            return
        if self.colorizing:
            self.stop_colorizing = True
            if DEBUG: print("stop colorizing")
        if self.allow_colorizing:
            if DEBUG: print("schedule colorizing")
            self.after_id = self.text.after(1, self._recolorize)

    close_when_done = None # Window to be closed when done colorizing

    def _recolorize(self):
        self.after_id = None
        """ AA
        if not self.delegate:
            if DEBUG: print("no delegate")
            return
        """
        if not self.allow_colorizing:
            if DEBUG: print("auto colorizing is off")
            return
        if self.colorizing:
            if DEBUG: print("already colorizing")
            return
        try:
            self.stop_colorizing = False
            self.colorizing = True
            if DEBUG: print("colorizing...")
            t0 = time.clock()
            self._recolorize_main()
            t1 = time.clock()
            if DEBUG: print("%.3f seconds" % (t1-t0))
        finally:
            self.colorizing = False
        if self.allow_colorizing and self.text.tag_nextrange("TODO", "1.0"):
            if DEBUG: print("reschedule colorizing")
            self.after_id = self.text.after(1, self._recolorize)
        if self.close_when_done:
            top = self.close_when_done
            self.close_when_done = None
            top.destroy()

    def _recolorize_main(self):
        next_index = "1.0"
        while True:
            item = self.text.tag_nextrange("TODO", next_index)
            if not item:
                break
            head, tail = item
            self.text.tag_remove("SYNC", head, tail)
            item = self.text.tag_prevrange("SYNC", head)
            if item:
                head = item[1]
            else:
                head = "1.0"

            chars = ""
            next_index = head
            lines_to_get = 1
            ok = False
            while not ok:
                mark = next_index
                next_index = self.text.index(mark + "+%d lines linestart" %
                                         lines_to_get)
                lines_to_get = min(lines_to_get * 2, 100)
                ok = "SYNC" in self.text.tag_names(next_index + "-1c")
                line = self.text.get(mark, next_index)
                ##print head, "get", mark, next_index, "->", repr(line)
                if not line:
                    return
                for tag in self.tagdefs:
                    self.text.tag_remove(tag, mark, next_index)
                chars = chars + line
                m = self.prog.search(chars)
                while m:
                    for key, value in m.groupdict().items():
                        if value:
                            value = value.strip()
                            a, b = m.span(key)
                            if key == "STRING3":
                                if (value.startswith('"""') and not value.endswith('"""') or
                                             value.startswith("'''") and not value.endswith("'''")):
                                    str_end = int(float(self.text.index(head + "+%dc" % b)))
                                    file_end = int(float(self.text.index("end")))

                                    if str_end == file_end:
                                        key = "STRING_OPEN"
                                    else:
                                        key = None
                                elif len(value) >= 4 and value[-4] == "\\":
                                    key = "STRING_OPEN"
                                else:
                                    key = "STRING_CLOSED"
                            if key is not None:
                                self.text.tag_add(key,
                                         head + "+%dc" % a,
                                         head + "+%dc" % b)
                            if value in ("def", "class"):
                                m1 = self.idprog.match(chars, b)
                                if m1:
                                    a, b = m1.span(1)
                                    self.text.tag_add("DEFINITION",
                                                 head + "+%dc" % a,
                                                 head + "+%dc" % b)
                            elif value == "import":
                                # color all the "as" words on same line, except
                                # if in a comment; cheap approximation to the
                                # truth
                                if '#' in chars:
                                    endpos = chars.index('#')
                                else:
                                    endpos = len(chars)
                                while True:
                                    m1 = self.asprog.match(chars, b, endpos)
                                    if not m1:
                                        break
                                    a, b = m1.span(1)
                                    self.text.tag_add("KEYWORD",
                                                 head + "+%dc" % a,
                                                 head + "+%dc" % b)
                    m = self.prog.search(chars, m.end())
                if "SYNC" in self.text.tag_names(next_index + "-1c"):
                    head = next_index
                    chars = ""
                else:
                    ok = False
                if not ok:
                    # We're in an inconsistent state, and the call to
                    # update may tell us to stop.  It may also change
                    # the correct value for "next_index" (since this is a
                    # line.col string, not a true mark).  So leave a
                    # crumb telling the next_index invocation to resume here
                    # in case update tells us to leave.
                    self.text.tag_add("TODO", next_index)
                self.text.update()
                if self.stop_colorizing:
                    if DEBUG: print("colorizing stopped")
                    return

class ShellSyntaxColorer(SyntaxColorer):
    def notify_active_range(self):
        SyntaxColorer.notify_active_range(self)

def update_coloring(event):
    assert isinstance(event.widget, tk.Text)
    text = event.widget
    
    if not hasattr(text, "syntax_colorer"):
        if isinstance(text, ShellText):
            class_ = ShellSyntaxColorer
        else:
            class_ = SyntaxColorer
            
        text.syntax_colorer = class_(text, get_workbench().get_font("EditorFont"),
                            get_workbench().get_font("BoldEditorFont"))
    
    text.syntax_colorer.notify_active_range()

def load_plugin():
    wb = get_workbench() 

    wb.bind_class("CodeViewText", "<<TextChange>>", update_coloring, True)
