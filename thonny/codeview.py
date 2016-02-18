# -*- coding: utf-8 -*-

import tkinter as tk
from idlelib import PyParse, ParenMatch

from thonny.coloring import SyntaxColorer
from thonny.common import TextRange
from thonny.globals import get_workbench
from thonny.misc_utils import running_on_mac_os
from thonny import tktextext
from thonny.ui_utils import TextWrapper



class CodeView(tktextext.TextFrame):
    def __init__(self, master, propose_remove_line_numbers=False, **text_frame_args):
        tktextext.TextFrame.__init__(self, master, **text_frame_args)
        
        # TODO: propose_remove_line_numbers
        
        self.colorer = None
        self.set_coloring(True)
        self.set_up_paren_matching()
        
        self.text.bind("<Return>", self.newline_and_indent_event, True)
        
        tktextext.fixwordbreaks(tk._default_root)
        
        if running_on_mac_os():
            self.text.bind("<Button-2>", self._open_context_menu)
            self.text.bind("<Control-Button-1>", self._open_context_menu)
        else:  
            self.text.bind("<Button-3>", self._open_context_menu)

        
    def get_content(self):
        return self.text.get("1.0", "end-1c") # -1c because Text always adds a newline itself
    
    def set_content(self, content):
        self.text.direct_delete("1.0", tk.END)
        self.text.direct_insert("1.0", content)
        self.update_line_numbers()
        self.text.edit_reset();
        
        if self.colorer:
            self.colorer.notify_range("1.0", "end")
    
    def intercept_insert(self, index, chars, tags=None):
        if self.is_read_only():
            self.bell()
        else:
            self.direct_insert(index, chars, tags)
            
            if self.colorer:
                self.colorer.on_insert(index, chars, tags)
            
            if self.paren_matcher: 
                try:
                    if chars in (")", "]", "}"):
                        self.paren_matcher.paren_closed_event(None)
                    else:
                        self.remove_paren_highlight()
                except:
                    pass
            
            self.update_line_numbers()
            self.update_margin_line()
            self.text.see(index)

    def intercept_delete(self, index1, index2=None):
        if self.is_read_only():
            self.bell()
        else:
            self.direct_insert(self, index1, index2)
            if self.colorer:
                self.colorer.on_delete(index1, index2)
            self.update_line_numbers()
            self.update_margin_line()
    def get_char_bbox(self, lineno, col_offset):
        self.text.update_idletasks()
        bbox = self.text.bbox(str(lineno - self.first_line_no + 1) 
                              + "."
                              + str(col_offset))
        if isinstance(bbox, tuple):
            return (bbox[0] - self.text.cget("padx"), bbox[1] - self.text.cget("pady"))
        else:
            return (0,0)
            
    def set_coloring(self, value):
        if value:
            if self.colorer is None:
                self.colorer = SyntaxColorer(self.text, 
                                             get_workbench().get_font("EditorFont"),
                                             get_workbench().get_font("BoldEditorFont"))
        else:
            if self.colorer is not None:
                self.colorer.removecolors()
                self.colorer = None
    
    def set_up_paren_matching(self):
        self.text_frame = self # ParenMatch assumes the existence of this attribute
        self.paren_matcher = ParenMatch.ParenMatch(self)
        self.paren_matcher.set_style("expression")
        ParenMatch.ParenMatch.HILITE_CONFIG = {'background': 'lightgray'}
        
        # paren_closed_event is called in _user_text_insert
        # because KeyRelease doesn't give necessary info with Estonian keyboard
        # restore_event call is also there

    
    def select_lines(self, first_line, last_line):
        self.text.tag_remove("sel", "1.0", tk.END)
        self.text.tag_add("sel", 
                          str(first_line) + ".0",
                          str(last_line) + ".end")
    
    def select_range(self, text_range):
        self.text.tag_remove("sel", "1.0", tk.END)
        
        if text_range:
            if isinstance(text_range, int):
                # it's line number
                start = str(text_range - self.first_line_no + 1) + ".0"
                end = str(text_range - self.first_line_no + 1) + ".end"
            elif isinstance(text_range, TextRange):
                start = str(text_range.lineno - self.first_line_no + 1) \
                    + "." + str(text_range.col_offset)
                end = str(text_range.end_lineno - self.first_line_no + 1) \
                    + "." + str(text_range.end_col_offset)
            else:
                assert isinstance(text_range, tuple)
                start, end  = text_range
                
            self.text.tag_add("sel", start, end)
            if isinstance(text_range, int):
                self.text.mark_set("insert", end) 
            self.text.see(start + " -1 lines")
            
    def on_text_mouse_click(self, event):
        TextWrapper.on_text_mouse_click(self, event)
        self.remove_paren_highlight()
        
    
    def remove_paren_highlight(self): 
        if self.paren_matcher:
            try: 
                self.paren_matcher.restore_event(None)
            except:
                pass
        

    
    

    def get_selected_range(self):
        if self.text.has_selection():
            lineno, col_offset = map(int, self.text.index(tk.SEL_FIRST).split("."))
            end_lineno, end_col_offset = map(int, self.text.index(tk.SEL_LAST).split("."))
        else:
            lineno, col_offset = map(int, self.text.index(tk.INSERT).split("."))
            end_lineno, end_col_offset = lineno, col_offset
            
        return TextRange(lineno, col_offset, end_lineno, end_col_offset)
    
    def _open_context_menu(self, event):
        get_workbench().get_menu("edit").post(event.x_root, event.y_root)

    def newline_and_indent_event(self, event):
        self.log_keypress_for_undo(event)
        # copied from idlelib.EditorWindow (Python 3.4.2)
        # slightly modified
        
        text = self.text
        first, last = self.get_selection_indices()
        text.undo_block_start()
        try:
            if first and last:
                text.delete(first, last)
                text.mark_set("insert", first)
            line = text.get("insert linestart", "insert")
            i, n = 0, len(line)
            while i < n and line[i] in " \t":
                i = i+1
            if i == n:
                # the cursor is in or at leading indentation in a continuation
                # line; just inject an empty line at the start
                text.insert("insert linestart", '\n')
                return "break"
            indent = line[:i]
            # strip whitespace before insert point unless it's in the prompt
            i = 0
            
            #last_line_of_prompt = sys.ps1.split('\n')[-1]
            while line and line[-1] in " \t" : #and line != last_line_of_prompt:
                line = line[:-1]
                i = i+1
            if i:
                text.delete("insert - %d chars" % i, "insert")
            # strip whitespace after insert point
            while text.get("insert") in " \t":
                text.delete("insert")
            # start new line
            text.insert("insert", '\n')

            # adjust indentation for continuations and block
            # open/close first need to find the last stmt
            lno = tktextext.index2line(text.index('insert'))
            y = PyParse.Parser(self.indentwidth, self.tabwidth)
            
            for context in [50, 500, 5000000]:
                startat = max(lno - context, 1)
                startatindex = repr(startat) + ".0"
                rawtext = text.get(startatindex, "insert")
                y.set_str(rawtext)
                bod = y.find_good_parse_start(
                          False,
                          self._build_char_in_string_func(startatindex))
                if bod is not None or startat == 1:
                    break
            y.set_lo(bod or 0)
            #else:
            #    r = text.tag_prevrange("console", "insert")
            #    if r:
            #        startatindex = r[1]
            #    else:
            #        startatindex = "1.0"
            #    rawtext = text.get(startatindex, "insert")
            #    y.set_str(rawtext)
            #    y.set_lo(0)

            c = y.get_continuation_type()
            if c != PyParse.C_NONE:
                # The current stmt hasn't ended yet.
                if c == PyParse.C_STRING_FIRST_LINE:
                    # after the first line of a string; do not indent at all
                    pass
                elif c == PyParse.C_STRING_NEXT_LINES:
                    # inside a string which started before this line;
                    # just mimic the current indent
                    text.insert("insert", indent)
                elif c == PyParse.C_BRACKET:
                    # line up with the first (if any) element of the
                    # last open bracket structure; else indent one
                    # level beyond the indent of the line with the
                    # last open bracket
                    self.reindent_to(y.compute_bracket_indent())
                elif c == PyParse.C_BACKSLASH:
                    # if more than one line in this stmt already, just
                    # mimic the current indent; else if initial line
                    # has a start on an assignment stmt, indent to
                    # beyond leftmost =; else to beyond first chunk of
                    # non-whitespace on initial line
                    if y.get_num_lines_in_stmt() > 1:
                        text.insert("insert", indent)
                    else:
                        self.reindent_to(y.compute_backslash_indent())
                else:
                    assert 0, "bogus continuation type %r" % (c,)
                return "break"

            # This line starts a brand new stmt; indent relative to
            # indentation of initial line of closest preceding
            # interesting stmt.
            indent = y.get_base_indent_string()
            text.insert("insert", indent)
            if y.is_block_opener():
                self.smart_indent_event(event)
            elif indent and y.is_block_closer():
                self.smart_backspace_event(event)
            return "break"
        finally:
            text.see("insert")
            text.undo_block_stop()
            text.event_generate("<<NewLine>>")

    def _build_char_in_string_func(self, startindex):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        
        # Our editwin provides a _is_char_in_string function that works
        # with a Tk text index, but PyParse only knows about offsets into
        # a string. This builds a function for PyParse that accepts an
        # offset.

        def inner(offset, _startindex=startindex,
                  _icis=self._is_char_in_string):
            return _icis(_startindex + "+%dc" % offset)
        return inner
    
    
    def _is_char_in_string(self, text_index):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        # Slightly modified
        
        # Is character at text_index in a Python string?  Return 0 for
        # "guaranteed no", true for anything else.  This info is expensive
        # to compute ab initio, but is probably already known by the
        # platform's colorizer.
        
        if self.colorer:
            # Return true iff colorizer hasn't (re)gotten this far
            # yet, or the character is tagged as being in a string
            return self.text.tag_prevrange("TODO", text_index) or \
                   "STRING" in self.text.tag_names(text_index)
        else:
            # The colorizer is missing: assume the worst
            return 1
        
    

