# -*- coding: utf-8 -*-

import os.path
import tkinter as tk
from tkinter import ttk, Canvas
from idlelib import PyParse, ParenMatch

from thonny.ui_utils import TextWrapper, AutoScrollbar
from thonny.common import TextRange
from thonny.coloring import SyntaxColorer
from thonny.globals import get_workbench
from thonny.misc_utils import running_on_mac_os

BLOCK_COMMENT_PREFIX = "##"

# line numbers taken from http://tkinter.unpythonic.net/wiki/A_Text_Widget_with_Line_Numbers 

# scrolling code copied from tkinter.scrolledtext
# (don't want to use scrolledtext directly, because I want to include margin in the same box) 
class CodeView(ttk.Frame, TextWrapper):
    # TODO: make it independent from Thonny ???
    def __init__(self, master, first_line_no=1, font_size=11,
                 auto_vert_scroll=False,
                 height=None,
                 propose_remove_line_numbers=False,
                 editor=None):
        ttk.Frame.__init__(self, master)
        
        self._editor = editor # TODO: can I get rid of this?
        
        # attributes
        self.first_line_no = first_line_no
        self.filename = None
        self.file_encoding = "UTF-8"
        
        self.tabwidth = 8 # See comments in idlelib.EditorWindow 
        self.indentwidth = 4 
        self.usetabs = False
        
        # child widgets
        if auto_vert_scroll:
            self.vbar = AutoScrollbar(self, orient=tk.VERTICAL)
        else:
            self.vbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vbar.grid(row=0, column=2, sticky=tk.NSEW)
        self.hbar = AutoScrollbar(self, orient=tk.HORIZONTAL)
        self.hbar.grid(row=1, column=0, sticky=tk.NSEW, columnspan=2)
        
        self.margin = tk.Text(self,
                width = 4,
                padx = 5,
                pady = 5,
                highlightthickness = 0,
                takefocus = 0,
                bd = 0,
                font = get_workbench().get_font("EditorFont"),
                #cursor = "dotbox",
                background = '#e0e0e0',
                foreground = '#999999',
                #state='disabled'
                )
        
        # TODO: not necessary here self.margin.grid(row=0, column=0, sticky=tk.NSEW)
        
        def _vertical_scrollbar_update(*args):
            self.vbar.set(*args)
            self.margin.yview(tk.MOVETO, args[0])
            
        def _horizontal_scrollbar_update(*args):
            self.hbar.set(*args)
            self._update_margin_line()
        
        self.text = tk.Text(self,
                #background="#ffffff",
                #background="#FEE5BF",
                #background="gray",
                height=height,
                spacing1=0,
                spacing3=0,
                highlightthickness=0,
                #highlightcolor="LightBlue",
                yscrollcommand=_vertical_scrollbar_update,
                xscrollcommand=_horizontal_scrollbar_update,
                borderwidth=0,
                font=get_workbench().get_font("EditorFont"),
                wrap=tk.NONE,
                insertwidth=2,
                #selectborderwidth=2,
                inactiveselectbackground='gray',
                #highlightthickness=0, # TODO: try different in Mac and Linux
                #highlightcolor="gray",
                padx=5,
                pady=5,
                undo=True,
                autoseparators=False)
        
        TextWrapper.__init__(self, propose_remove_line_numbers)
        
        self.read_only = False
        
        self.text.grid(row=0, column=1, sticky=tk.NSEW)
        
        def _vertical_scroll(*args):
            self.text.yview(*args)
            self.margin.yview(*args)
            
        def _horizontal_scroll(*args):
            self.text.xview(*args)
            self._update_margin_line()
            
        self.vbar['command'] = _vertical_scroll # TODO: keep line count same in margin
        self.hbar['command'] = _horizontal_scroll
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.colorer = None
        self.set_coloring(True)
        self.set_up_paren_matching()
        
        
        self.num_context_lines = 50, 500, 5000000 # See idlelib.EditorWindow
        self.context_use_ps1 = False
        
        # TODO: Check Mac bindings
        self.text.bind("<Control-BackSpace>", self.del_word_left, True)
        self.text.bind("<Control-Delete>", self.del_word_right, True)
        self.text.bind("<Home>", self.home_callback, True)
        self.text.bind("<Left>", self.move_at_edge_if_selection(0), True)
        self.text.bind("<Right>", self.move_at_edge_if_selection(1), True)
        self.text.bind("<Tab>", self.indent_or_dedent_event, True)
        self.text.bind("<Return>", self.newline_and_indent_event, True)
        self.text.bind("<BackSpace>", self.smart_backspace_event, True)
        
        fixwordbreaks(tk._default_root)
        
        if running_on_mac_os():
            self.text.bind("<Button-2>", self._open_context_menu)
            self.text.bind("<Control-Button-1>", self._open_context_menu)
        else:  
            self.text.bind("<Button-3>", self._open_context_menu)

        self._recommended_line_length=0
        self.margin_line = Canvas(self.text, borderwidth=0, width=1, height=1200, 
                                   highlightthickness=0, background="lightgray")
        # TODO: not necessary self.margin_line.place(x=600, y=-10)
        self._update_margin_line()
        
    def del_word_left(self, event):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        self.text.event_generate('<Meta-Delete>')
        self.add_undo_separator()
        return "break"

    def del_word_right(self, event):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        self.text.event_generate('<Meta-d>')
        self.add_undo_separator()
        return "break"

    """
    def remove_selection(self, event=None):
        # copied from idlelib.EditorWindow
        self.text.tag_remove("sel", "1.0", "end")
        self.text.see("insert")
    """

    def move_at_edge_if_selection(self, edge_index):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        """Cursor move begins at start or end of selection

        When a left/right cursor key is pressed create and return to Tkinter a
        function which causes a cursor move from the associated edge of the
        selection.

        """
        self_text_index = self.text.index
        self_text_mark_set = self.text.mark_set
        edges_table = ("sel.first+1c", "sel.last-1c")
        def move_at_edge(event):
            if (event.state & 5) == 0: # no shift(==1) or control(==4) pressed
                try:
                    self_text_index("sel.first")
                    self_text_mark_set("insert", edges_table[edge_index])
                except tk.TclError:
                    pass
        return move_at_edge
    
    
    def indent_or_dedent_event(self, event):
        self.log_keypress_for_undo(event)
        if event.state in [1,9]: # shift is pressed (1 in Mac, 9 in Win)
            return self.dedent_region_event(event)
        else:
            return self.smart_indent_event(event)    
    
    def indent_region_event(self, event):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        head, tail, chars, lines = self.get_region()
        for pos in range(len(lines)):
            line = lines[pos]
            if line:
                raw, effective = classifyws(line, self.tabwidth)
                effective = effective + self.indentwidth
                lines[pos] = self._make_blanks(effective) + line[raw:]
        self.set_region(head, tail, chars, lines)
        return "break"

    def dedent_region_event(self, event):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        
        head, tail, chars, lines = self.get_region()
        for pos in range(len(lines)):
            line = lines[pos]
            if line:
                raw, effective = classifyws(line, self.tabwidth)
                effective = max(effective - self.indentwidth, 0)
                lines[pos] = self._make_blanks(effective) + line[raw:]
        self.set_region(head, tail, chars, lines)
        return "break"
    
    def home_callback(self, event):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        
        if (event.state & 4) != 0 and event.keysym == "Home":
            # state&4==Control. If <Control-Home>, use the Tk binding.
            return
        
        line = self.text.get("insert linestart", "insert lineend")
        for insertpt in range(len(line)):
            if line[insertpt] not in (' ','\t'):
                break
        else:
            insertpt=len(line)
            
        lineat = int(self.text.index("insert").split('.')[1])
        if insertpt == lineat:
            insertpt = 0
        dest = "insert linestart+"+str(insertpt)+"c"
        if (event.state&1) == 0:
            # shift was not pressed
            self.text.tag_remove("sel", "1.0", "end")
        else:
            if not self.text.index("sel.first"):
                # there was no previous selection
                self.text.mark_set("my_anchor", "insert")
            else:
                if self.text.compare(self.text.index("sel.first"), "<",
                                     self.text.index("insert")):
                    self.text.mark_set("my_anchor", "sel.first") # extend back
                else:
                    self.text.mark_set("my_anchor", "sel.last") # extend forward
            first = self.text.index(dest)
            last = self.text.index("my_anchor")
            if self.text.compare(first,">",last):
                first,last = last,first
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", first, last)
        self.text.mark_set("insert", dest)
        self.text.see("insert")
        return "break"

    
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
            lno = index2line(text.index('insert'))
            y = PyParse.Parser(self.indentwidth, self.tabwidth)
            
            #if not self.context_use_ps1:
            for context in self.num_context_lines:
                startat = max(lno - context, 1)
                startatindex = repr(startat) + ".0"
                rawtext = text.get(startatindex, "insert")
                y.set_str(rawtext)
                bod = y.find_good_parse_start(
                          self.context_use_ps1,
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
        
        # Our editwin provides a is_char_in_string function that works
        # with a Tk text index, but PyParse only knows about offsets into
        # a string. This builds a function for PyParse that accepts an
        # offset.

        def inner(offset, _startindex=startindex,
                  _icis=self.is_char_in_string):
            return _icis(_startindex + "+%dc" % offset)
        return inner
    
    def _make_blanks(self, n):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        
        # Make string that displays as n leading blanks.
        if self.usetabs:
            ntabs, nspaces = divmod(n, self.tabwidth)
            return '\t' * ntabs + ' ' * nspaces
        else:
            return ' ' * n
        
    def reindent_to(self, column):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        
        # Delete from beginning of line to insert point, then reinsert
        # column logical (meaning use tabs if appropriate) spaces.
        text = self.text
        text.undo_block_start()
        if text.compare("insert linestart", "!=", "insert"):
            text.delete("insert linestart", "insert")
        if column:
            text.insert("insert", self._make_blanks(column))
        text.undo_block_stop()


    def smart_backspace_event(self, event):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        # Slightly modified
        self.log_keypress_for_undo(event)
        
        text = self.text
        first, last = self.get_selection_indices()
        if first and last:
            text.delete(first, last)
            text.mark_set("insert", first)
            return "break"
        # Delete whitespace left, until hitting a real char or closest
        # preceding virtual tab stop.
        chars = text.get("insert linestart", "insert")
        if chars == '':
            if text.compare("insert", ">", "1.0"):
                # easy: delete preceding newline
                text.delete("insert-1c")
            else:
                text.bell()     # at start of buffer
            return "break"
        if  chars[-1] not in " \t":
            # easy: delete preceding real char
            text.delete("insert-1c")
            self.log_keypress_for_undo(event)
            return "break"
        # Ick.  It may require *inserting* spaces if we back up over a
        # tab character!  This is written to be clear, not fast.
        tabwidth = self.tabwidth
        have = len(chars.expandtabs(tabwidth))
        assert have > 0
        want = ((have - 1) // self.indentwidth) * self.indentwidth
        # Debug prompt is multilined....
        #if self.context_use_ps1:
        #    last_line_of_prompt = sys.ps1.split('\n')[-1]
        #else:
        last_line_of_prompt = ''
        ncharsdeleted = 0
        while 1:
            if chars == last_line_of_prompt:
                break
            chars = chars[:-1]
            ncharsdeleted = ncharsdeleted + 1
            have = len(chars.expandtabs(tabwidth))
            if have <= want or chars[-1] not in " \t":
                break
        text.undo_block_start()
        text.delete("insert-%dc" % ncharsdeleted, "insert")
        if have < want:
            text.insert("insert", ' ' * (want - have))
        text.undo_block_stop()
        return "break"
    
    def smart_indent_event(self, event):
        self.log_keypress_for_undo(event)
        
        # copied from idlelib.EditorWindow (Python 3.4.2)
        
        # if intraline selection:
        #     delete it
        # elif multiline selection:
        #     do indent-region
        # else:
        #     indent one level
        text = self.text
        first, last = self.get_selection_indices()
        text.undo_block_start()
        try:
            if first and last:
                if index2line(first) != index2line(last):
                    return self.indent_region_event(event)
                text.delete(first, last)
                text.mark_set("insert", first)
            prefix = text.get("insert linestart", "insert")
            raw, effective = classifyws(prefix, self.tabwidth)
            if raw == len(prefix):
                # only whitespace to the left
                self.reindent_to(effective + self.indentwidth)
            else:
                # tab to the next 'stop' within or to right of line's text:
                if self.usetabs:
                    pad = '\t'
                else:
                    effective = len(prefix.expandtabs(self.tabwidth))
                    n = self.indentwidth
                    pad = ' ' * (n - effective % n)
                text.insert("insert", pad)
            text.see("insert")
            return "break"
        finally:
            text.undo_block_stop()

    def get_region(self):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        text = self.text
        first, last = self.get_selection_indices()
        if first and last:
            head = text.index(first + " linestart")
            tail = text.index(last + "-1c lineend +1c")
        else:
            head = text.index("insert linestart")
            tail = text.index("insert lineend +1c")
        chars = text.get(head, tail)
        lines = chars.split("\n")
        return head, tail, chars, lines

    def set_region(self, head, tail, chars, lines):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        text = self.text
        newchars = "\n".join(lines)
        if newchars == chars:
            text.bell()
            return
        text.tag_remove("sel", "1.0", "end")
        text.mark_set("insert", head)
        text.undo_block_start()
        text.delete(head, tail)
        text.insert(head, newchars)
        text.undo_block_stop()
        text.tag_add("sel", head, "insert")
    
    def get_selection_indices(self):
        # copied from idlelib.EditorWindow (Python 3.4.2)
        
        # If a selection is defined in the text widget, return (start,
        # end) as Tkinter text indices, otherwise return (None, None)
        try:
            first = self.text.index("sel.first")
            last = self.text.index("sel.last")
            return first, last
        except tk.TclError:
            return None, None
    
    def is_char_in_string(self, text_index):
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
        
        
    def set_show_line_numbers(self, value):
        if value and not self.margin.winfo_ismapped():
            self.margin.grid(row=0, column=0, sticky=tk.NSEW)
            self._update_line_numbers()
        elif not value and self.margin.winfo_ismapped():
            self.margin.grid_forget()
    
    def set_line_length_margin(self, value):
        self._recommended_line_length = value
        self._update_margin_line()
        
    def get_content(self):
        return self.text.get("1.0", "end-1c") # -1c because Text always adds a newline itself
    
    def set_content(self, content):
        TextWrapper._user_text_delete(self, "1.0", tk.END)
        TextWrapper._user_text_insert(self, "1.0", content)
        self._update_line_numbers()
        self.text.edit_reset();
        
        if self.colorer:
            self.colorer.notify_range("1.0", "end")
    
    def get_char_bbox(self, lineno, col_offset):
        self.text.update_idletasks()
        bbox = self.text.bbox(str(lineno - self.first_line_no + 1) 
                              + "."
                              + str(col_offset))
        if isinstance(bbox, tuple):
            return (bbox[0] - self.text.cget("padx"), bbox[1] - self.text.cget("pady"))
        else:
            return (0,0)
            
    def focus_set(self):
        self.text.focus_set()
    
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

    
    def select_all(self):
        self.text.tag_remove("sel", "1.0", tk.END)
        self.text.tag_add('sel', '1.0', tk.END)
        
        # this can be confusing with big files:
        #self.text.mark_set("insert", "1.0")
        #self.text.see("insert") 
    
    
            
            
    
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
        
    def _user_text_insert(self, index, chars, tags=None):
        #cursor_pos = self.text.index(tk.INSERT)
        
        if self.read_only:
            self.bell()
            #self._show_read_only_warning()
        else:
            TextWrapper._user_text_insert(self, index, chars, tags)
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
            
            self._update_line_numbers()
            self._update_margin_line()
            self.text.see(index)

    def _user_text_delete(self, index1, index2=None):
        # cursor_pos = self.text.index(tk.INSERT)
        
        if self.read_only:
            self.bell()
            #self._show_read_only_warning()
        else:
            TextWrapper._user_text_delete(self, index1, index2)
            if self.colorer:
                self.colorer.on_delete(index1, index2)
            self._update_line_numbers()
            self._update_margin_line()
    
    def _update_line_numbers(self):
        text_line_count = int(self.text.index("end-1c").split(".")[0])
        
        self.margin.config(state='normal')
        self.margin.delete("1.0", "end")
        for i in range(text_line_count):
            self.margin.insert("end", str(i + self.first_line_no).rjust(3))
            if i < text_line_count-1:
                self.margin.insert("end", "\n") 
        self.margin.config(state='disabled')


    def _update_margin_line(self):
        if self._recommended_line_length == 0:
            self.margin_line.place_forget()
        else:
            try:
                self.text.update_idletasks()
                # How far left has text been scrolled
                first_visible_idx = self.text.index("@0,0")
                first_visible_col = int(first_visible_idx.split(".")[1])
                bbox = self.text.bbox(first_visible_idx)
                first_visible_col_x = bbox[0]
                
                margin_line_visible_col = self._recommended_line_length - first_visible_col
                delta = first_visible_col_x
            except:
                # fall back to ignoring scroll position
                margin_line_visible_col = self._recommended_line_length
                delta = 0
            
            if margin_line_visible_col > -1:
                x = (get_workbench().get_font("EditorFont").measure((margin_line_visible_col-1) * "M") 
                     + delta + self.text["padx"])
            else:
                x = -10
            
            #print(first_visible_col, first_visible_col_x)
            
            self.margin_line.place(y=-10, x=x)
            
    """
    def _show_read_only_warning(self):
        showwarning("Warning",
                "Editing during run/debug is not allowed")
    """
    
    def selection_is_line_commented(self):
        sel_range = self.get_selected_range(True)
        
        for lineno in range(sel_range.lineno, sel_range.end_lineno+1):
            line = self.text.get(str(lineno) + '.0', str(lineno) + '.end')
            if not line.startswith(BLOCK_COMMENT_PREFIX):
                return False
        
        return True
        
    
    def toggle_selection_comment(self):
        if self.selection_is_line_commented():
            self.uncomment_selection()
        else:
            self.comment_selection()
        
    
    def comment_selection(self):
        """Adds ## in front of all selected lines if any lines are selected, 
        or just the current line otherwise"""
        
        sel_range = self.get_selected_range(True)

        for lineno in range(sel_range.lineno, sel_range.end_lineno+1):
            self.text.insert(str(lineno) + '.0', BLOCK_COMMENT_PREFIX)
        
        if sel_range.end_lineno > sel_range.lineno:
            self.select_lines(sel_range.lineno, sel_range.end_lineno)
        
        self.text.edit_separator()
            

    def uncomment_selection(self):
        sel_range = self.get_selected_range(True)
        
        for lineno in range(sel_range.lineno, sel_range.end_lineno+1):
            line = self.text.get(str(lineno) + '.0', str(lineno) + '.end')
            if line.startswith(BLOCK_COMMENT_PREFIX):
                self.text.delete(str(lineno) + ".0",
                                 str(lineno) + "." + str(len(BLOCK_COMMENT_PREFIX)))

    def get_selected_range(self, exclude_last_line_start=False):
        if tk.SEL in self.text.tag_names() and self.text.index(tk.SEL_FIRST):
            lineno, col_offset = map(int, self.text.index(tk.SEL_FIRST).split("."))
            end_lineno, end_col_offset = map(int, self.text.index(tk.SEL_LAST).split("."))
            
            if exclude_last_line_start and end_lineno > lineno and end_col_offset == 0:
                # SelectAll includes nonexisting extra line
                end_lineno -= 1
                end_col_offset = int(self.text.index(str(end_lineno) + ".end").split(".")[1])
        else:
            lineno, col_offset = map(int, self.text.index(tk.INSERT).split("."))
            end_lineno, end_col_offset = lineno, col_offset
            
        return TextRange(lineno, col_offset, end_lineno, end_col_offset)
    
    def _open_context_menu(self, event):
        get_workbench().get_menu("edit").post(event.x_root, event.y_root)

    

def fixwordbreaks(root):
    # Copied from idlelib.EditorWindow (Python 3.4.2)
    # Modified to include non-ascii chars
    
    # Make sure that Tk's double-click and next/previous word
    # operations use our definition of a word (i.e. an identifier)
    tk = root.tk
    tk.call('tcl_wordBreakAfter', 'a b', 0) # make sure word.tcl is loaded
    tk.call('set', 'tcl_wordchars',     '[a-zA-Z0-9_À-ÖØ-öø-ÿĀ-ſƀ-ɏА-я]')
    tk.call('set', 'tcl_nonwordchars', '[^a-zA-Z0-9_À-ÖØ-öø-ÿĀ-ſƀ-ɏА-я]')

def classifyws(s, tabwidth):
    # copied from idlelib.EditorWindow (Python 3.4.2)
    raw = effective = 0
    for ch in s:
        if ch == ' ':
            raw = raw + 1
            effective = effective + 1
        elif ch == '\t':
            raw = raw + 1
            effective = (effective // tabwidth + 1) * tabwidth
        else:
            break
    return raw, effective

def index2line(index):
    # copied from idlelib.EditorWindow (Python 3.4.2)
    return int(float(index))
