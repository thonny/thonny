# -*- coding: utf-8 -*-

import tkinter as tk
from thonny.common import TextRange
from thonny.globals import get_workbench
from thonny import tktextext, roughparse
from thonny.ui_utils import EnhancedTextWithLogging
from thonny.tktextext import EnhancedText

EDIT_BACKGROUND="white"
READ_ONLY_BACKGROUND="LightYellow"

class PythonText(EnhancedText):
    
    def perform_return(self, event):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        # slightly modified
        
        text = event.widget
        assert text is self
        
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
                i = i+1
            
            # is it only whitespace?
            if i == n:
                # start the new line with the same whitespace
                text.insert("insert", '\n' + left_part)
                return "break"
            
            # Turned out the left part contains visible chars
            # Remember the indent
            indent = left_part[:i]
            
            # Strip whitespace before insert point
            # (ie. after inserting the linebreak this line doesn't have trailing whitespace)
            while text.get("insert-1c", "insert") in [" ", "\t"]:
                text.delete("insert-1c", "insert")
                
            # start new line
            text.insert("insert", '\n')
    
            # adjust indentation for continuations and block
            # open/close first need to find the last stmt
            lno = tktextext.index2line(text.index('insert'))
            y = roughparse.RoughParser(text.indentwidth, text.tabwidth)
            
            for context in roughparse.NUM_CONTEXT_LINES:
                startat = max(lno - context, 1)
                startatindex = repr(startat) + ".0"
                rawtext = text.get(startatindex, "insert")
                y.set_str(rawtext)
                bod = y.find_good_parse_start(
                          False,
                          roughparse._build_char_in_string_func(startatindex))
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


class CodeViewText(EnhancedTextWithLogging, PythonText):
    """Provides opportunities for monkey-patching by plugins"""
    def __init__(self, master=None, cnf={}, **kw):
        if not "background" in kw:
            kw["background"] = EDIT_BACKGROUND
        
        EnhancedTextWithLogging.__init__(self, master=master, cnf=cnf, **kw)
        self._original_background = kw["background"]
        # Allow binding to events of all CodeView texts
        self.bindtags(self.bindtags() + ('CodeViewText',))
        tktextext.fixwordbreaks(tk._default_root)
    
    def set_read_only(self, value):
        EnhancedTextWithLogging.set_read_only(self, value)
        if value:
            self.configure(background=READ_ONLY_BACKGROUND)
        else:
            self.configure(background=self._original_background)

    
    def on_secondary_click(self, event):
        super().on_secondary_click(event)
        get_workbench().get_menu("edit").tk_popup(event.x_root, event.y_root)

class CodeView(tktextext.TextFrame):
    def __init__(self, master, propose_remove_line_numbers=False, **text_frame_args):
        tktextext.TextFrame.__init__(self, master, text_class=CodeViewText,
                                     undo=True, wrap=tk.NONE, background=EDIT_BACKGROUND,
                                     **text_frame_args)
        
        # TODO: propose_remove_line_numbers on paste??
        
        self.text.bind("<<TextChange>>", self._on_text_changed, True)
        
    def get_content(self):
        return self.text.get("1.0", "end-1c") # -1c because Text always adds a newline itself
    
    def set_content(self, content):
        self.text.direct_delete("1.0", tk.END)
        self.text.direct_insert("1.0", content)
        self.update_line_numbers()
        self.text.edit_reset();

        self.text.event_generate("<<TextChange>>")
    
    def _on_text_changed(self, event):
        self.update_line_numbers()
        self.update_margin_line()
    
    def select_lines(self, first_line, last_line):
        self.text.tag_remove("sel", "1.0", tk.END)
        self.text.tag_add("sel", "%s.0" % first_line, "%s.end" % last_line)
    
    def select_range(self, text_range):
        self.text.tag_remove("sel", "1.0", tk.END)
        
        if text_range:
            if isinstance(text_range, int):
                # it's line number
                start = str(text_range - self._first_line_number + 1) + ".0"
                end = str(text_range - self._first_line_number + 1) + ".end"
            elif isinstance(text_range, TextRange):
                start = "%s.%s" % (text_range.lineno - self._first_line_number + 1, text_range.col_offset)
                end = "%s.%s" % (text_range.end_lineno - self._first_line_number + 1, text_range.end_col_offset)
            else:
                assert isinstance(text_range, tuple)
                start, end  = text_range
                
            self.text.tag_add("sel", start, end)
            if isinstance(text_range, int):
                self.text.mark_set("insert", end) 
            self.text.see("%s -1 lines" % start)
            
    
    def get_selected_range(self):
        if self.text.has_selection():
            lineno, col_offset = map(int, self.text.index(tk.SEL_FIRST).split("."))
            end_lineno, end_col_offset = map(int, self.text.index(tk.SEL_LAST).split("."))
        else:
            lineno, col_offset = map(int, self.text.index(tk.INSERT).split("."))
            end_lineno, end_col_offset = lineno, col_offset
            
        return TextRange(lineno, col_offset, end_lineno, end_col_offset)
