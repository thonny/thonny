# coding=utf-8
"""Extensions for tk.Text"""

import time
import traceback
from logging import exception

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import font as tkfont
    from tkinter import TclError
except ImportError:
    import Tkinter as tk
    import ttk
    import tkFont as tkfont
    from Tkinter import TclError
    

class TweakableText(tk.Text):
    """Allows intercepting Text commands at Tcl-level"""
    def __init__(self, master=None, cnf={}, read_only=False, **kw):
        tk.Text.__init__(self, master=master, cnf=cnf, **kw)
        
        self._read_only = read_only
        
        self._original_widget_name = self._w + "_orig"
        self.tk.call("rename", self._w, self._original_widget_name)
        self.tk.createcommand(self._w, self._dispatch_tk_operation)
        self._tk_proxies = {}
        
        self._original_insert = self._register_tk_proxy_function("insert", self.intercept_insert)
        self._original_delete = self._register_tk_proxy_function("delete", self.intercept_delete)
        self._original_mark = self._register_tk_proxy_function("mark", self.intercept_mark)
    
    def _register_tk_proxy_function(self, operation, function):
        self._tk_proxies[operation] = function
        setattr(self, operation, function)
        
        def original_function(*args):
            self.tk.call((self._original_widget_name, operation) + args)
            
        return original_function
    
    def _dispatch_tk_operation(self, operation, *args):
        f = self._tk_proxies.get(operation)
        try:
            if f:
                return f(*args)
            else:
                return self.tk.call((self._original_widget_name, operation) + args)
            
        except TclError as e:
            # Some Tk internal actions (eg. paste and cut) can cause this error
            if (str(e).lower() == '''text doesn't contain any characters tagged with "sel"'''
                and operation in ["delete", "index", "get"] 
                and args in [("sel.first", "sel.last"), ("sel.first",)]):
                
                pass 
            else:
                traceback.print_exc()
            
            return "" # Taken from idlelib.WidgetRedirector
    
    def set_read_only(self, value):
        self._read_only = value
    
    def is_read_only(self):
        return self._read_only

    def set_content(self, chars):
        self.direct_delete("1.0", tk.END)
        self.direct_insert("1.0", chars)
        
    def intercept_mark(self, *args):
        self.direct_mark(*args)
    
    def intercept_insert(self, index, chars, tags=None):
        assert isinstance(chars, str)
        if chars >= "\uf704" and chars <= "\uf70d": # Function keys F1..F10 in Mac cause these
            pass
        elif self.is_read_only():
            self.bell()
        else:
            self.direct_insert(index, chars, tags)
    
    def intercept_delete(self, index1, index2=None):
        if index1 == "sel.first" and index2 == "sel.last" and not self.has_selection():
            return
        
        if self.is_read_only():
            self.bell()            
        elif self._is_erroneous_delete(index1, index2):
            pass
        else:
            self.direct_delete(index1, index2)
    
    def _is_erroneous_delete(self, index1, index2):
        """Paste can cause deletes where index1 is sel.start but text has no selection. This would cause errors"""
        return index1.startswith("sel.") and not self.has_selection()
    
    def direct_mark(self, *args):
        self._original_mark(*args)
        
        if args[:2] == ('set', 'insert'):
            self.event_generate("<<CursorMove>>")
    
    def index_sel_first(self):
        # Tk will give error without this check
        if self.tag_ranges("sel"):
            return self.index("sel.first")
        else:
            return None
    
    def index_sel_last(self):
        if self.tag_ranges("sel"):
            return self.index("sel.last")
        else:
            return None

    def has_selection(self):
        return len(self.tag_ranges("sel")) > 0
    
    def get_selection_indices(self):
        # If a selection is defined in the text widget, return (start,
        # end) as Tkinter text indices, otherwise return (None, None)
        if self.has_selection():
            return self.index("sel.first"), self.index("sel.last")
        else:
            return None, None
        
    def direct_insert(self, index, chars, tags=None):
        self._original_insert(index, chars, tags)
        self.event_generate("<<TextChange>>")
    
    def direct_delete(self, index1, index2=None):
        self._original_delete(index1, index2)
        self.event_generate("<<TextChange>>")
    


class EnhancedText(TweakableText):
    """Text widget with extra navigation and editing aids. 
    Provides more comfortable deletion, indentation and deindentation,
    and undo handling. Not specific to Python code.
    
    Most of the code is adapted from idlelib.EditorWindow.
    """ 
    def __init__(self, master=None, cnf={}, **kw):
        # Parent class shouldn't autoseparate
        # TODO: take client provided autoseparators value into account 
        kw["autoseparators"] = False
        
        
        TweakableText.__init__(self, master=master, cnf=cnf, **kw)
        self.tabwidth = 8 # See comments in idlelib.EditorWindow 
        self.indentwidth = 4 
        self.usetabs = False
        
        self._last_event_kind = None
        self._last_key_time = None
        
        self._bind_editing_aids()
        self._bind_movement_aids()
        self._bind_selection_aids()
        self._bind_undo_aids()
        self._bind_mouse_aids()
    
    def _bind_mouse_aids(self):
        if _running_on_mac():
            self.bind("<Button-2>", self.on_secondary_click)
            self.bind("<Control-Button-1>", self.on_secondary_click)
        else:  
            self.bind("<Button-3>", self.on_secondary_click)
        
    
    def _bind_editing_aids(self):
        
        def if_not_readonly(fun):
            def dispatch(event):
                if not self.is_read_only():
                    return fun(event)
                else:
                    return "break"
            return dispatch
        
        self.bind("<Control-BackSpace>", if_not_readonly(self.delete_word_left), True)
        self.bind("<Control-Delete>", if_not_readonly(self.delete_word_right), True)
        self.bind("<BackSpace>", if_not_readonly(self.perform_smart_backspace), True)
        self.bind("<Return>", if_not_readonly(self.perform_return), True)
        self.bind("<KP_Enter>", if_not_readonly(self.perform_return), True)
        self.bind("<Tab>", if_not_readonly(self.perform_tab), True)
        try:
            # Is needed on eg. Ubuntu with Estonian keyboard
            self.bind("<ISO_Left_Tab>", if_not_readonly(self.perform_tab), True)
        except:
            pass
    
    def _bind_movement_aids(self):
        self.bind("<Home>", self.perform_smart_home, True)
        self.bind("<Left>", self.move_to_edge_if_selection(0), True)
        self.bind("<Right>", self.move_to_edge_if_selection(1), True)
        self.bind("<Next>", self.perform_page_down, True)
        self.bind("<Prior>", self.perform_page_up, True)
    
    def _bind_selection_aids(self):
        self.bind("<Command-a>" if _running_on_mac() else "<Control-a>",
                  self.select_all, True)
    
    def _bind_undo_aids(self):
        self.bind("<<Undo>>", self._on_undo, True)
        self.bind("<<Redo>>", self._on_redo, True)
        self.bind("<<Cut>>", self._on_cut, True)
        self.bind("<<Copy>>", self._on_copy, True)
        self.bind("<<Paste>>", self._on_paste, True)
        self.bind("<FocusIn>", self._on_get_focus, True)
        self.bind("<FocusOut>", self._on_lose_focus, True)
        self.bind("<Key>", self._on_key_press, True)
        self.bind("<1>", self._on_mouse_click, True)
        self.bind("<2>", self._on_mouse_click, True)
        self.bind("<3>", self._on_mouse_click, True)
        
    
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
        
        if chars.strip() != "": # there are non-whitespace chars somewhere to the left of the cursor
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
        text.delete("insert-%dc" % ncharsdeleted, "insert")
        if have < want:
            text.insert("insert", ' ' * (want - have))
        return "break"

    def perform_midline_tab(self, event=None):
        "autocompleter can put its magic here"
        # by default
        return self.perform_smart_tab(event)
    
    def perform_smart_tab(self, event=None):
        self._log_keypress_for_undo(event)
        
        # if intraline selection:
        #     delete it
        # elif multiline selection:
        #     do indent-region
        # else:
        #     indent one level
        
        first, last = self.get_selection_indices()
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

    def get_cursor_position(self):
        return map(int, self.index("insert").split("."))
    
    def get_line_count(self):
        return list(map(int, self.index("end-1c").split(".")))[0]

    def perform_return(self, event):
        self.insert("insert", "\n")
        return "break"
    
    def perform_page_down(self, event):
        # if last line is visible then go to last line 
        # (by default it doesn't move then)
        try:
            last_visible_idx = self.index("@0,%d" % self.winfo_height())
            row, _ = map(int, last_visible_idx.split("."))
            line_count = self.get_line_count()
            
            if (row == line_count 
                or row == line_count-1): # otherwise tk doesn't show last line
                self.mark_set("insert", "end")
        except:
            traceback.print_exc() 
    
    def perform_page_up(self, event):
        # if first line is visible then go there 
        # (by default it doesn't move then)    
        try:
            first_visible_idx = self.index("@0,0")
            row, _ = map(int, first_visible_idx.split("."))
            if row == 1:
                self.mark_set("insert", "1.0")
        except:
            traceback.print_exc() 
    
    def compute_smart_home_destination_index(self):
        """Is overridden in shell"""
        
        line = self.get("insert linestart", "insert lineend")
        for insertpt in range(len(line)):
            if line[insertpt] not in (' ','\t'):
                break
        else:
            insertpt=len(line)
            
        lineat = int(self.index("insert").split('.')[1])
        if insertpt == lineat:
            insertpt = 0
        return "insert linestart+"+str(insertpt)+"c"
    
    def perform_smart_home(self, event):
        if (event.state & 4) != 0 and event.keysym == "Home":
            # state&4==Control. If <Control-Home>, use the Tk binding.
            return
        
        dest = self.compute_smart_home_destination_index()
        
        if (event.state&1) == 0:
            # shift was not pressed
            self.tag_remove("sel", "1.0", "end")
        else:
            if not self.index_sel_first():
                # there was no previous selection
                self.mark_set("my_anchor", "insert")
            else:
                if self.compare(self.index_sel_first(), "<",
                                     self.index("insert")):
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
            if (self.has_selection() 
                and (event.state & 5) == 0): # no shift(==1) or control(==4) pressed
                try:
                    self.mark_set("insert", ("sel.first+1c", "sel.last-1c")[edge_index])
                except tk.TclError:
                    pass
                
        return move_at_edge
    
    def perform_tab(self, event=None):
        self._log_keypress_for_undo(event)
        if event.state & 0x0001: # shift is pressed (http://stackoverflow.com/q/32426250/261181)
            return self.dedent_region(event)
        else:
            # check whether there are letters before cursor on this line
            index = self.index("insert")
            left_text = self.get(index + " linestart", index)
            if left_text.strip() == "" or self.has_selection():
                return self.perform_smart_tab(event)    
            else:
                return self.perform_midline_tab(event)
    
    def indent_region(self, event=None):
        return self._change_indentation(True)

    def dedent_region(self, event=None):
        return self._change_indentation(False)
    
    def _change_indentation(self, increase=True):
        head, tail, chars, lines = self._get_region()
        
        # Text widget plays tricks if selection ends on last line
        # and content doesn't end with empty line,
        text_last_line = index2line(self.index("end-1c"))
        sel_last_line = index2line(tail)
        if sel_last_line >= text_last_line:
            while not self.get(head, "end").endswith("\n\n"):
                self.insert("end", "\n")
        
        for pos in range(len(lines)):
            line = lines[pos]
            if line:
                raw, effective = classifyws(line, self.tabwidth)
                if increase:
                    effective = effective + self.indentwidth
                else:
                    effective = max(effective - self.indentwidth, 0)
                lines[pos] = self._make_blanks(effective) + line[raw:]
        self._set_region(head, tail, chars, lines)
        return "break"
    
    
    def select_all(self, event):
        self.tag_remove("sel", "1.0", tk.END)
        self.tag_add('sel', '1.0', tk.END)
    
    def _reindent_to(self, column):
        # Delete from beginning of line to insert point, then reinsert
        # column logical (meaning use tabs if appropriate) spaces.
        if self.compare("insert linestart", "!=", "insert"):
            self.delete("insert linestart", "insert")
        if column:
            self.insert("insert", self._make_blanks(column))
        
    def _get_region(self):
        first, last = self.get_selection_indices()
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
        self.delete(head, tail)
        self.insert(head, newchars)
        self.tag_add("sel", head, "insert")
    
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

    def _on_undo(self, e):
        self._last_event_kind = "undo"
        
    def _on_redo(self, e):
        self._last_event_kind = "redo"
        
    def _on_cut(self, e):
        self._last_event_kind = "cut"
        self.edit_separator()        
        
    def _on_copy(self, e):
        self._last_event_kind = "copy"
        self.edit_separator()        
        
    def _on_paste(self, e):
        self._last_event_kind = "paste"
        self.edit_separator()    
        self.see("insert")  
        self.after_idle(lambda : self.see("insert"))  
    
    def _on_get_focus(self, e):
        self._last_event_kind = "get_focus"
        self.edit_separator()        
        
    def _on_lose_focus(self, e):
        self._last_event_kind = "lose_focus"
        self.edit_separator()        
    
    def _on_key_press(self, e):
        return self._log_keypress_for_undo(e)

    def _on_mouse_click(self, event):
        self.edit_separator()

    
    def on_secondary_click(self, event=None):
        "Use this for invoking context menu"
        self.focus_set()


class TextFrame(ttk.Frame):
    "Decorates text with scrollbars, line numbers and print margin"
    def __init__(self, master, line_numbers=False, line_length_margin=0,
                 first_line_number=1, text_class=EnhancedText,
                 horizontal_scrollbar=True, vertical_scrollbar=True,
                 vertical_scrollbar_class=ttk.Scrollbar,
                 horizontal_scrollbar_class=ttk.Scrollbar,
                 **text_options):
        ttk.Frame.__init__(self, master=master)
        
        final_text_options = {'borderwidth' : 0,
                              'insertwidth' : 2,
                              'spacing1' : 0,
                              'spacing3' : 0,
                              'highlightthickness' : 0,
                              'inactiveselectbackground' : 'gray',
                              'padx' : 5,
                              'pady' : 5
                               }
        final_text_options.update(text_options)
        self.text = text_class(self, **final_text_options)
        self.text.grid(row=0, column=1, sticky=tk.NSEW)

        self._margin = tk.Text(self, width=4, padx=5, pady=5,
                               highlightthickness=0, bd=0, takefocus=False,
                               font=self.text['font'],
                               background='#e0e0e0', foreground='#999999',
                               selectbackground='#e0e0e0', selectforeground='#999999',
                               cursor='arrow',
                               state='disabled',
                               undo=False
                               )
        self._margin.bind("<ButtonRelease-1>", self.on_margin_click)
        self._margin.bind("<Button-1>", self.on_margin_click)
        self._margin.bind("<Button1-Motion>", self.on_margin_motion)
        self._margin['yscrollcommand'] = self._margin_scroll
        
        # margin will be gridded later
        self._first_line_number = first_line_number
        self.set_line_numbers(line_numbers)
        
        if vertical_scrollbar:
            self._vbar = vertical_scrollbar_class(self, orient=tk.VERTICAL)
            self._vbar.grid(row=0, column=2, sticky=tk.NSEW)
            self._vbar['command'] = self._vertical_scroll 
            self.text['yscrollcommand'] = self._vertical_scrollbar_update  
        
        if horizontal_scrollbar:
            self._hbar = horizontal_scrollbar_class(self, orient=tk.HORIZONTAL)
            self._hbar.grid(row=1, column=0, sticky=tk.NSEW, columnspan=2)
            self._hbar['command'] = self._horizontal_scroll
            self.text['xscrollcommand'] = self._horizontal_scrollbar_update    
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._recommended_line_length=line_length_margin
        self._margin_line = tk.Canvas(self.text, borderwidth=0, width=1, height=1200, 
                                     highlightthickness=0, background="lightgray")
        self.update_margin_line()
        
        self.text.bind("<<TextChange>>", self._text_changed, True)
        
        # TODO: add context menu?

    def focus_set(self):
        self.text.focus_set()
    
    def set_line_numbers(self, value):
        if value and not self._margin.winfo_ismapped():
            self._margin.grid(row=0, column=0, sticky=tk.NSEW)
            self.update_line_numbers()
        elif not value and self._margin.winfo_ismapped():
            self._margin.grid_forget()
        
        # insert first line number (NB! Without trailing linebreak. See update_line_numbers) 
        self._margin.config(state='normal')
        self._margin.delete("1.0", "end")
        self._margin.insert("1.0", str(self._first_line_number))
        self._margin.config(state='disabled')

        self.update_line_numbers()
    
    def set_line_length_margin(self, value):
        self._recommended_line_length = value
        self.update_margin_line()
    
    def _text_changed(self, event):
        self.update_line_numbers()
        self.update_margin_line()
    
    def _vertical_scrollbar_update(self, *args):
        self._vbar.set(*args)
        self._margin.yview(tk.MOVETO, args[0])
        
    def _margin_scroll(self, *args):
        # FIXME: this doesn't work properly
        # Can't scroll to bottom when line numbers are not visible
        # and can't type normally at the bottom, when line numbers are visible 
        return
        #self._vbar.set(*args)
        #self.text.yview(tk.MOVETO, args[0])
        
    def _horizontal_scrollbar_update(self,*args):
        self._hbar.set(*args)
        self.update_margin_line()
    
    def _vertical_scroll(self,*args):
        self.text.yview(*args)
        self._margin.yview(*args)
        
    def _horizontal_scroll(self,*args):
        self.text.xview(*args)
        self.update_margin_line()
    
    def update_line_numbers(self):
        text_line_count = int(self.text.index("end").split(".")[0])
        margin_line_count = int(self._margin.index("end").split(".")[0])
        
        if text_line_count != margin_line_count:
            self._margin.config(state='normal')
            
            # NB! Text acts weird with last symbol 
            # (don't really understand whether it automatically keeps a newline there or not)
            # Following seems to ensure both Text-s have same height
            if text_line_count > margin_line_count:
                delta = text_line_count - margin_line_count
                start = margin_line_count + self._first_line_number - 1
                for i in range(start, start + delta):
                    self._margin.insert("end-1c", "\n" + str(i))
            
            else:
                self._margin.delete(line2index(text_line_count)+"-1c", "end-1c")
                
            self._margin.config(state='disabled')
        
        # synchronize margin scroll position with text
        # https://mail.python.org/pipermail/tkinter-discuss/2010-March/002197.html
        first, _ = self.text.yview()
        self._margin.yview_moveto(first)


    def update_margin_line(self):
        if self._recommended_line_length == 0:
            self._margin_line.place_forget()
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
                x = (get_text_font(self.text).measure((margin_line_visible_col-1) * "M") 
                     + delta + self.text["padx"])
            else:
                x = -10
            
            #print(first_visible_col, first_visible_col_x)
            
            self._margin_line.place(y=-10, x=x)

    def on_margin_click(self, event=None):
        try:
            linepos = self._margin.index("@%s,%s" % (event.x, event.y)).split(".")[0]
            self.text.mark_set("insert", "%s.0" % linepos)
            self._margin.mark_set("margin_selection_start", "%s.0" % linepos)
            if event.type == "4": # In Python 3.6 you can use tk.EventType.ButtonPress instead of "4" 
                self.text.tag_remove("sel", "1.0", "end")
        except tk.TclError:
            exception()

    def on_margin_motion(self, event=None):
        try:
            linepos = int(self._margin.index("@%s,%s" % (event.x, event.y)).split(".")[0])
            margin_selection_start = int(self._margin.index("margin_selection_start").split(".")[0])
            self.select_lines(min(margin_selection_start, linepos), max(margin_selection_start - 1, linepos - 1))
            self.text.mark_set("insert", "%s.0" % linepos)
        except tk.TclError:
            exception()
        
def get_text_font(text):
    font = text["font"]
    if isinstance(font, str):
        return tkfont.nametofont(font)
    else:
        return font


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

def line2index(line):
    return str(float(line))

def fixwordbreaks(root):
    # Adapted from idlelib.EditorWindow (Python 3.4.2)
    # Modified to include non-ascii chars
    
    # Make sure that Tk's double-click and next/previous word
    # operations use our definition of a word (i.e. an identifier)
    tk = root.tk
    tk.call('tcl_wordBreakAfter', 'a b', 0) # make sure word.tcl is loaded
    tk.call('set', 'tcl_wordchars',     u'[a-zA-Z0-9_À-ÖØ-öø-ÿĀ-ſƀ-ɏА-я]')
    tk.call('set', 'tcl_nonwordchars', u'[^a-zA-Z0-9_À-ÖØ-öø-ÿĀ-ſƀ-ɏА-я]')

def rebind_control_a(root):
    # Tk 8.6 has <<SelectAll>> event but 8.5 doesn't
    # http://stackoverflow.com/questions/22907200/remap-default-keybinding-in-tkinter
    def control_a(event):
        widget = event.widget
        if isinstance(widget, tk.Text):
            widget.tag_remove("sel","1.0","end")
            widget.tag_add("sel","1.0","end")
        
    root.bind_class("Text", "<Control-a>", control_a)
    

def _running_on_mac():
    return tk._default_root.call('tk', 'windowingsystem') == "aqua"

if __name__ == "__main__":
    # demo
    root = tk.Tk()
    frame = TextFrame(root, read_only=False, wrap=tk.NONE,
                      line_numbers=True, line_length_margin=13,
                      text_class=TweakableText)
    frame.grid()
    text = frame.text
    
    text.direct_insert("1.0", "Essa\n    'tessa\nkossa\nx=34+(45*89*(a+45)")
    text.tag_configure('string', background='yellow')
    text.tag_add("string", "2.0", "3.0")
    
    
    text.tag_configure('paren', underline=True)
    text.tag_add("paren", "4.6", "5.0")
    
    root.mainloop()