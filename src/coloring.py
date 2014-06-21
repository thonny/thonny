# copied from idlelib

import time
import re
import keyword
import builtins
import ui_utils
    
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
    sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    string = matches_any("STRING", [sq3string, dq3string, sqstring, dqstring])
    return kw + "|" + builtin + "|" + comment + "|" + string +\
           "|" + matches_any("SYNC", [r"\n"])

prog = re.compile(make_pat(), re.S)
idprog = re.compile(r"\s+(\w+)", re.S)
asprog = re.compile(r".*?\b(as)\b")

class SyntaxColorer:

    def __init__(self, text):
        self.text = text
        self.prog = prog
        self.idprog = idprog
        self.asprog = asprog
        self.LoadTagDefs()
        
        self.config_colors() # AA
        self.notify_range("1.0", "end") # AA

    """
    def setdelegate(self, delegate):
        if self.delegate is not None:
            self.unbind("<<toggle-auto-coloring>>")
        Delegator.setdelegate(self, delegate)
        if delegate is not None:
            self.config_colors()
            self.bind("<<toggle-auto-coloring>>", self.toggle_colorize_event)
            self.notify_range("1.0", "end")
        else:
            # No delegate - stop matches_any colorizing
            self.stop_colorizing = True
            self.allow_colorizing = False
    """

    def config_colors(self):
        for tag, cnf in self.tagdefs.items():
            if cnf:
                self.text.tag_configure(tag, **cnf)
        self.text.tag_raise('sel')

    def LoadTagDefs(self):
        self.tagdefs = {
            "SYNC": {'background':None,'foreground':None},
            "TODO": {'background':None,'foreground':None},
            
            "COMMENT": {'background':None,'foreground':"DarkGray"},
            "KEYWORD": {'background':None,'foreground':"#7f0055", "font":ui_utils.BOLD_EDITOR_FONT},
            #"KEYWORD": {'background':None,'foreground':"#ff7700", "font":ui_utils.BOLD_EDITOR_FONT},
            "BUILTIN": {'background':None,'foreground':None},
            #"STRING":  {'background':None,'foreground':"#00AA00"},
            "STRING":  {'background':None,'foreground':"DarkGreen"},
            "DEFINITION": {},
            "BREAK": {'background':None,'foreground':"Purple"},
            "ERROR": {'background':None,'foreground':"Red"},
            
            # The following is used by ReplaceDialog:
            "hit": {'background':"Yellow",'foreground':None}
            }

        if DEBUG: print('tagdefs',self.tagdefs)

    def on_insert(self, index, chars, tags=None):
        index = self.text.index(index)
        #self.notify_range(index, index + "+%dc" % len(chars))
        self.notify_range("1.0", "end")

    def on_delete(self, index1, index2=None):
        index1 = self.text.index(index1)
        #self.notify_range(index1)
        self.notify_range("1.0", "end")

    after_id = None
    allow_colorizing = True
    colorizing = False

    def notify_range(self, index1, index2=None):
        self.text.tag_add("TODO", index1, index2)
        if self.after_id:
            if DEBUG: print("colorizing already scheduled")
            return
        if self.colorizing:
            self.stop_colorizing = True
            if DEBUG: print("stop colorizing")
        if self.allow_colorizing:
            if DEBUG: print("schedule colorizing")
            self.after_id = self.text.after(1, self.recolorize)

    close_when_done = None # Window to be closed when done colorizing

    def close(self, close_when_done=None):
        if self.after_id:
            after_id = self.after_id
            self.after_id = None
            if DEBUG: print("cancel scheduled recolorizer")
            self.text.after_cancel(after_id)
        self.allow_colorizing = False
        self.stop_colorizing = True
        if close_when_done:
            if not self.colorizing:
                close_when_done.destroy()
            else:
                self.close_when_done = close_when_done

    def toggle_colorize_event(self, event):
        if self.after_id:
            after_id = self.after_id
            self.after_id = None
            if DEBUG: print("cancel scheduled recolorizer")
            self.text.after_cancel(after_id)
        if self.allow_colorizing and self.colorizing:
            if DEBUG: print("stop colorizing")
            self.stop_colorizing = True
        self.allow_colorizing = not self.allow_colorizing
        if self.allow_colorizing and not self.colorizing:
            self.after_id = self.text.after(1, self.recolorize)
        if DEBUG:
            print("auto colorizing turned",\
                  self.allow_colorizing and "on" or "off")
        return "break"

    def recolorize(self):
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
            self.recolorize_main()
            t1 = time.clock()
            if DEBUG: print("%.3f seconds" % (t1-t0))
        finally:
            self.colorizing = False
        if self.allow_colorizing and self.text.tag_nextrange("TODO", "1.0"):
            if DEBUG: print("reschedule colorizing")
            self.after_id = self.text.after(1, self.recolorize)
        if self.close_when_done:
            top = self.close_when_done
            self.close_when_done = None
            top.destroy()

    def recolorize_main(self):
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
                            a, b = m.span(key)
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

    def removecolors(self):
        for tag in self.tagdefs:
            self.text.tag_remove(tag, "1.0", "end")

