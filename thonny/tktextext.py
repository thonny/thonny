"""Extensions for tk.Text"""

import tkinter as tk
from tkinter import ttk
import time

class TweakableText(tk.Text):
    """Allows intercepting Text commands at Tcl-level"""
    def __init__(self, master=None, cnf={}, read_only=False, **kw):
        tk.Text.__init__(self, master=master, cnf=cnf, **kw)
        
        self._read_only = read_only
        
        self._original_widget_name = self._w + "_orig"
        self.tk.call("rename", self._w, self._original_widget_name)
        self.tk.createcommand(self._w, self._dispatch_tk_operation)
        self._tk_proxies = {}
        
        self._original_internal_insert = self._register_tk_proxy_function("insert", self.internal_insert)
        self._original_internal_delete = self._register_tk_proxy_function("delete", self.internal_delete)
        self._original_internal_mark = self._register_tk_proxy_function("mark", self.internal_mark)
    
    def _register_tk_proxy_function(self, operation, function):
        self._tk_proxies[operation] = function
        setattr(self, operation, function)
        
        def original_function(*args):
            self.tk.call((self._original_widget_name, operation) + args)
            
        return original_function
    
    def _dispatch_tk_operation(self, operation, *args):
        f = self._tk_proxies.get(operation)
        if f:
            return f(*args)
        else:
            return self.tk.call((self._original_widget_name, operation) + args)
    
    def set_read_only(self, value):
        self._read_only = value
    
    def is_read_only(self):
        return self._read_only

    def internal_mark(self, *args):
        self._original_internal_mark(*args)
    
    def internal_insert(self, index, chars, tags=()):
        if not self.is_read_only():
            self._original_internal_insert(index, chars, tags)
    
    def internal_delete(self, from_index, to_index=None):
        if not self.is_read_only():
            self._original_internal_delete(from_index, to_index)
    
    def direct_mark(self, *args):
        self._original_internal_mark(*args)
    
    def direct_insert(self, index, chars, tags=()):
        self._original_internal_insert(index, chars, tags)
    
    def direct_delete(self, from_index, to_index=None):
        self._original_internal_delete(from_index, to_index)
    


class EnhancedText(TweakableText):
    """Text widget with extra navigation and editing aids. 
    Provides more comfortable deletion, indentation and deindentation,
    and undo handling. Not specific to Python code.
    
    Most of the code is adapted from idlelib.EditorWindow.
    """ 
    def __init__(self, master=None, cnf={}, **kw):
        TweakableText.__init__(self, master=master, cnf=cnf, **kw)
        self.tabwidth = 8 # See comments in idlelib.EditorWindow 
        self.indentwidth = 4 
        self.usetabs = False
        
        self._last_event_kind = None
        self._last_key_time = None
        self._started_undo_blocks = 0        
        
        self._bind_editing_aids()
        self._bind_movement_aids()
    
    def _bind_editing_aids(self):
        self.bind("<Control-BackSpace>", self.delete_word_left, True)
        self.bind("<Option-BackSpace>", self.delete_word_left, True)
        self.bind("<Control-Delete>", self.delete_word_right, True)
        self.bind("<Option-Delete>", self.delete_word_right, True)
        self.bind("<BackSpace>", self.perform_smart_backspace, True)
        self.bind("<Return>", self.perform_return, True)
        self.bind("<Tab>", self.indent_or_dedent, True)
    
    def _bind_movement_aids(self):
        self.bind("<Home>", self.perform_smart_home, True)
        self.bind("<Left>", self.move_to_edge_if_selection(0), True)
        self.bind("<Right>", self.move_to_edge_if_selection(1), True)
        
    
    def delete_word_left(self, event):
        self.event_generate('<Meta-Delete>')
        self.edit_separator()
        return "break"

    def delete_word_right(self, event):
        self.event_generate('<Meta-d>')
        self.edit_separator()
        return "break"

    def perform_smart_backspace(self, event):
        self._log_keypress_for_undo(event)
        
        text = self
        first, last = self._get_selection_indices()
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
            self._log_keypress_for_undo(event)
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
        text._undo_block_start()
        text.delete("insert-%dc" % ncharsdeleted, "insert")
        if have < want:
            text.insert("insert", ' ' * (want - have))
        text._undo_block_stop()
        return "break"
    
    def perform_smart_tab(self, event=None):
        self._log_keypress_for_undo(event)
        
        # if intraline selection:
        #     delete it
        # elif multiline selection:
        #     do indent-region
        # else:
        #     indent one level
        
        first, last = self._get_selection_indices()
        self._undo_block_start()
        try:
            if first and last:
                if index2line(first) != index2line(last):
                    return self.indent_region(event)
                self.delete(first, last)
                self.mark_set("insert", first)
            prefix = self.get("insert linestart", "insert")
            raw, effective = classifyws(prefix, self.tabwidth)
            if raw == len(prefix):
                # only whitespace to the left
                self._reindent_to(effective + self.indentwidth)
            else:
                # tab to the next 'stop' within or to right of line's text:
                if self.usetabs:
                    pad = '\t'
                else:
                    effective = len(prefix.expandtabs(self.tabwidth))
                    n = self.indentwidth
                    pad = ' ' * (n - effective % n)
                self.insert("insert", pad)
            self.see("insert")
            return "break"
        finally:
            self._undo_block_stop()

    def perform_return(self, event):
        # Override this for Python
        pass
    
    def perform_smart_home(self, event):
        if (event.state & 4) != 0 and event.keysym == "Home":
            # state&4==Control. If <Control-Home>, use the Tk binding.
            return
        
        line = self.get("insert linestart", "insert lineend")
        for insertpt in range(len(line)):
            if line[insertpt] not in (' ','\t'):
                break
        else:
            insertpt=len(line)
            
        lineat = int(self.index("insert").split('.')[1])
        if insertpt == lineat:
            insertpt = 0
        dest = "insert linestart+"+str(insertpt)+"c"
        if (event.state&1) == 0:
            # shift was not pressed
            self.tag_remove("sel", "1.0", "end")
        else:
            if not self.index("sel.first"):
                # there was no previous selection
                self.mark_set("my_anchor", "insert")
            else:
                if self.compare(self.text.index("sel.first"), "<",
                                     self.text.index("insert")):
                    self.mark_set("my_anchor", "sel.first") # extend back
                else:
                    self.mark_set("my_anchor", "sel.last") # extend forward
            first = self.index(dest)
            last = self.index("my_anchor")
            if self.compare(first,">",last):
                first,last = last,first
            self.tag_remove("sel", "1.0", "end")
            self.tag_add("sel", first, last)
        self.mark_set("insert", dest)
        self.see("insert")
        return "break"

    def move_to_edge_if_selection(self, edge_index):
        """Cursor move begins at start or end of selection

        When a left/right cursor key is pressed create and return to Tkinter a
        function which causes a cursor move from the associated edge of the
        selection.
        """
        def move_at_edge(event):
            if (len(self.tag_ranges("sel")) > 0 # selection exists
                and (event.state & 5) == 0): # no shift(==1) or control(==4) pressed
                try:
                    #self.index("sel.first")
                    self.mark_set("insert", ("sel.first+1c", "sel.last-1c")[edge_index])
                except tk.TclError:
                    pass
                
        return move_at_edge
    
    def indent_or_dedent(self, event=None):
        self._log_keypress_for_undo(event)
        if event.state in [1,9]: # shift is pressed (1 in Mac, 9 in Win)
            return self.dedent_region(event)
        else:
            return self.perform_smart_tab(event)    
    
    def indent_region(self, event=None):
        head, tail, chars, lines = self._get_region()
        for pos in range(len(lines)):
            line = lines[pos]
            if line:
                raw, effective = classifyws(line, self.tabwidth)
                effective = effective + self.indentwidth
                lines[pos] = self._make_blanks(effective) + line[raw:]
        self._set_region(head, tail, chars, lines)
        return "break"

    def dedent_region(self, event=None):
        head, tail, chars, lines = self._get_region()
        for pos in range(len(lines)):
            line = lines[pos]
            if line:
                raw, effective = classifyws(line, self.tabwidth)
                effective = max(effective - self.indentwidth, 0)
                lines[pos] = self._make_blanks(effective) + line[raw:]
        self._set_region(head, tail, chars, lines)
        return "break"
    
    def _reindent_to(self, column):
        # Delete from beginning of line to insert point, then reinsert
        # column logical (meaning use tabs if appropriate) spaces.
        self._undo_block_start()
        if self.compare("insert linestart", "!=", "insert"):
            self.delete("insert linestart", "insert")
        if column:
            self.insert("insert", self._make_blanks(column))
        self._undo_block_stop()
        
    def _get_region(self):
        first, last = self._get_selection_indices()
        if first and last:
            head = self.index(first + " linestart")
            tail = self.index(last + "-1c lineend +1c")
        else:
            head = self.index("insert linestart")
            tail = self.index("insert lineend +1c")
        chars = self.get(head, tail)
        lines = chars.split("\n")
        return head, tail, chars, lines

    def _set_region(self, head, tail, chars, lines):
        newchars = "\n".join(lines)
        if newchars == chars:
            self.bell()
            return
        self.tag_remove("sel", "1.0", "end")
        self.mark_set("insert", head)
        self._undo_block_start()
        self.delete(head, tail)
        self.insert(head, newchars)
        self._undo_block_stop()
        self.tag_add("sel", head, "insert")
    
    def _undo_block_start(self):
        self._started_undo_blocks += 1
    
    def _undo_block_stop(self):
        self._started_undo_blocks -= 1
        if self._started_undo_blocks == 0:
            #self.add_undo_separator() # TODO: get rid of idlelib heritage
            pass
        
    def _log_keypress_for_undo(self, e):
        if e is None:
            return
        
        # NB! this may not execute if the event is cancelled in another handler
        event_kind = self._get_event_kind(e)
        
        if (event_kind != self._last_event_kind
            or e.char in ("\r", "\n", " ", "\t")
            or e.keysym in ["Return", "KP_Enter"]
            or time.time() - self.last_key_time > 2
            ):
            self.edit_separator()
            
        self._last_event_kind = event_kind
        self.last_key_time = time.time()

    def _get_event_kind(self, event):
        if event.keysym in ("BackSpace", "Delete"):
            return "delete"
        elif event.char:
            return "insert"
        else:
            # eg. e.keysym in ("Left", "Up", "Right", "Down", "Home", "End", "Prior", "Next"):
            return "other_key"

    def _make_blanks(self, n):
        # Make string that displays as n leading blanks.
        if self.usetabs:
            ntabs, nspaces = divmod(n, self.tabwidth)
            return '\t' * ntabs + ' ' * nspaces
        else:
            return ' ' * n
        
    def _get_selection_indices(self):
        # If a selection is defined in the text widget, return (start,
        # end) as Tkinter text indices, otherwise return (None, None)
        try:
            first = self.index("sel.first")
            last = self.index("sel.last")
            return first, last
        except tk.TclError:
            return None, None

class TextFrame(ttk.Frame):
    def __init__(self, master, text, **kw):
        ttk.Frame.__init__(self, master=master, **kw)
        self._text = text
    "TODO: this will decorate given text with scrollbars, line numbers and print margin"

def classifyws(s, tabwidth):
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
    return int(float(index))
