# coding=utf-8
"""Extensions for tk.Text"""

import platform
import time
import tkinter as tk
import traceback
from logging import exception
from tkinter import TclError, messagebox
from tkinter import font as tkfont
from tkinter import ttk


class TweakableText(tk.Text):
    """Allows intercepting Text commands at Tcl-level"""

    def __init__(self, master=None, cnf={}, read_only=False, **kw):
        super().__init__(master=master, cnf=cnf, **kw)

        self._read_only = read_only
        self._suppress_events = False

        self._original_widget_name = self._w + "_orig"
        self.tk.call("rename", self._w, self._original_widget_name)
        self.tk.createcommand(self._w, self._dispatch_tk_operation)
        self._tk_proxies = {}

        self._original_insert = self._register_tk_proxy_function(
            "insert", self.intercept_insert
        )
        self._original_delete = self._register_tk_proxy_function(
            "delete", self.intercept_delete
        )
        self._original_mark = self._register_tk_proxy_function(
            "mark", self.intercept_mark
        )

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
            if (
                str(e).lower()
                == '''text doesn't contain any characters tagged with "sel"'''
                and operation in ["delete", "index", "get"]
                and args in [("sel.first", "sel.last"), ("sel.first",)]
            ):

                pass
            else:
                exception(
                    "[_dispatch_tk_operation] operation: "
                    + operation
                    + ", args:"
                    + repr(args)
                )
                # traceback.print_exc()

            return ""  # Taken from idlelib.WidgetRedirector

    def set_read_only(self, value):
        self._read_only = value

    def is_read_only(self):
        return self._read_only

    def set_content(self, chars):
        self.direct_delete("1.0", tk.END)
        self.direct_insert("1.0", chars)

    def set_insertwidth(self, new_width):
        """Change cursor width
        
        NB! Need to be careful with setting text["insertwidth"]!
        My first straightforward solution caused unexplainable
        infinite loop of insertions and deletions in the text
        (Repro: insert a line and a word, select that word and then do Ctrl-Z).
        
        This solution seems safe but be careful!
        """
        if self._suppress_events:
            return

        if self["insertwidth"] != new_width:
            old_suppress = self._suppress_events
            try:
                self._suppress_events = True
                self.config(insertwidth=new_width)
            finally:
                self._suppress_events = old_suppress

    def intercept_mark(self, *args):
        self.direct_mark(*args)

    def intercept_insert(self, index, chars, tags=None, **kw):
        assert isinstance(chars, str)
        if (
            chars >= "\uf704" and chars <= "\uf70d"
        ):  # Function keys F1..F10 in Mac cause these
            pass
        elif self.is_read_only():
            self.bell()
        else:
            self.direct_insert(index, chars, tags, **kw)

    def intercept_delete(self, index1, index2=None, **kw):
        if index1 == "sel.first" and index2 == "sel.last" and not self.has_selection():
            return

        if self.is_read_only():
            self.bell()
        elif self._is_erroneous_delete(index1, index2):
            pass
        else:
            self.direct_delete(index1, index2, **kw)

    def _is_erroneous_delete(self, index1, index2):
        """Paste can cause deletes where index1 is sel.start but text has no selection. This would cause errors"""
        return index1.startswith("sel.") and not self.has_selection()

    def direct_mark(self, *args):
        self._original_mark(*args)

        if args[:2] == ("set", "insert") and not self._suppress_events:
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

    def direct_insert(self, index, chars, tags=None, **kw):
        self._original_insert(index, chars, tags, **kw)
        if not self._suppress_events:
            self.event_generate("<<TextChange>>")

    def direct_delete(self, index1, index2=None, **kw):
        self._original_delete(index1, index2, **kw)
        if not self._suppress_events:
            self.event_generate("<<TextChange>>")


class EnhancedText(TweakableText):
    """Text widget with extra navigation and editing aids. 
    Provides more comfortable deletion, indentation and deindentation,
    and undo handling. Not specific to Python code.
    
    Most of the code is adapted from idlelib.EditorWindow.
    """

    def __init__(self, master=None, style="Text", tag_current_line=False,
                 indent_with_tabs=False, replace_tabs=False, cnf={}, **kw):
        # Parent class shouldn't autoseparate
        # TODO: take client provided autoseparators value into account
        kw["autoseparators"] = False
        self._style = style
        self._original_options = kw.copy()

        super().__init__(master=master, cnf=cnf, **kw)
        self.tabwidth = 8  # See comments in idlelib.editor.EditorWindow
        self.indent_width = 4
        self.indent_with_tabs = indent_with_tabs
        self.replace_tabs = replace_tabs

        self._last_event_kind = None
        self._last_key_time = None

        self._bind_editing_aids()
        self._bind_movement_aids()
        self._bind_selection_aids()
        self._bind_undo_aids()
        self._bind_mouse_aids()

        self._ui_theme_change_binding = self.bind(
            "<<ThemeChanged>>", self._reload_theme_options, True
        )

        self._initial_configuration = self.configure()
        self._regular_insertwidth = self["insertwidth"]
        self._reload_theme_options()

        self._should_tag_current_line = tag_current_line
        if tag_current_line:
            self.bind("<<CursorMove>>", self._tag_current_line, True)
            self.bind("<<TextChange>>", self._tag_current_line, True)
            self._tag_current_line()

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
        self.bind("<Control-d>", self._redirect_ctrld, True)
        self.bind("<BackSpace>", if_not_readonly(self.perform_smart_backspace), True)
        self.bind("<Return>", if_not_readonly(self.perform_return), True)
        self.bind("<KP_Enter>", if_not_readonly(self.perform_return), True)
        self.bind("<Tab>", if_not_readonly(self.perform_tab), True)
        try:
            # Is needed on eg. Ubuntu with Estonian keyboard
            self.bind("<ISO_Left_Tab>", if_not_readonly(self.perform_tab), True)
        except Exception:
            pass

        if platform.system() == "Windows":
            self.bind("<KeyPress>", self._insert_untypable_characters_on_windows, True)

    def _bind_movement_aids(self):
        self.bind("<Home>", self.perform_smart_home, True)
        self.bind("<Left>", self.move_to_edge_if_selection(0), True)
        self.bind("<Right>", self.move_to_edge_if_selection(1), True)
        self.bind("<Next>", self.perform_page_down, True)
        self.bind("<Prior>", self.perform_page_up, True)

    def _bind_selection_aids(self):
        self.bind(
            "<Command-a>" if _running_on_mac() else "<Control-a>", self.select_all, True
        )

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

    def _redirect_ctrld(self, event):
        # I want to disable the deletion effect of CtrlD in the text but still
        # keep the event for other purposes
        self.event_generate("<<CtrlDInText>>")
        return "break"

    def tag_reset(self, tag_name):
        empty_conf = {key: "" for key in self.tag_configure(tag_name)}
        self.tag_configure(empty_conf)

    def select_lines(self, first_line, last_line):
        self.tag_remove("sel", "1.0", tk.END)
        self.tag_add("sel", "%s.0" % first_line, "%s.end" % last_line)

    def delete_word_left(self, event):
        self.event_generate("<Meta-Delete>")
        self.edit_separator()
        return "break"

    def delete_word_right(self, event):
        self.event_generate("<Meta-d>")
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
        if chars == "":
            if text.compare("insert", ">", "1.0"):
                # easy: delete preceding newline
                text.delete("insert-1c")
            else:
                text.bell()  # at start of buffer
            return "break"

        if (
            chars.strip() != ""
        ):  # there are non-whitespace chars somewhere to the left of the cursor
            # easy: delete preceding real char
            text.delete("insert-1c")
            self._log_keypress_for_undo(event)
            return "break"

        # Ick.  It may require *inserting* spaces if we back up over a
        # tab character!  This is written to be clear, not fast.
        have = len(chars.expandtabs(self.tabwidth))
        assert have > 0
        want = ((have - 1) // self.indent_width) * self.indent_width
        # Debug prompt is multilined....
        # if self.context_use_ps1:
        #    last_line_of_prompt = sys.ps1.split('\n')[-1]
        # else:
        last_line_of_prompt = ""
        ncharsdeleted = 0
        while 1:
            if chars == last_line_of_prompt:
                break
            chars = chars[:-1]
            ncharsdeleted = ncharsdeleted + 1
            have = len(chars.expandtabs(self.tabwidth))
            if have <= want or chars[-1] not in " \t":
                break
        text.delete("insert-%dc" % ncharsdeleted, "insert")
        if have < want:
            text.insert("insert", " " * (want - have))
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
            self._reindent_to(effective + self.indent_width)
        else:
            # tab to the next 'stop' within or to right of line's text:
            if self.indent_with_tabs:
                pad = "\t"
            else:
                effective = len(prefix.expandtabs(self.tabwidth))
                n = self.indent_width
                pad = " " * (n - effective % n)
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

            if (
                row == line_count or row == line_count - 1
            ):  # otherwise tk doesn't show last line
                self.mark_set("insert", "end")
        except Exception:
            traceback.print_exc()

    def perform_page_up(self, event):
        # if first line is visible then go there
        # (by default it doesn't move then)
        try:
            first_visible_idx = self.index("@0,0")
            row, _ = map(int, first_visible_idx.split("."))
            if row == 1:
                self.mark_set("insert", "1.0")
        except Exception:
            traceback.print_exc()

    def compute_smart_home_destination_index(self):
        """Is overridden in shell"""

        line = self.get("insert linestart", "insert lineend")
        for insertpt in range(len(line)):
            if line[insertpt] not in (" ", "\t"):
                break
        else:
            insertpt = len(line)

        lineat = int(self.index("insert").split(".")[1])
        if insertpt == lineat:
            insertpt = 0
        return "insert linestart+" + str(insertpt) + "c"

    def perform_smart_home(self, event):
        if (event.state & 4) != 0 and event.keysym == "Home":
            # state&4==Control. If <Control-Home>, use the Tk binding.
            return None

        dest = self.compute_smart_home_destination_index()

        if (event.state & 1) == 0:
            # shift was not pressed
            self.tag_remove("sel", "1.0", "end")
        else:
            if not self.index_sel_first():
                # there was no previous selection
                self.mark_set("my_anchor", "insert")
            else:
                if self.compare(self.index_sel_first(), "<", self.index("insert")):
                    self.mark_set("my_anchor", "sel.first")  # extend back
                else:
                    self.mark_set("my_anchor", "sel.last")  # extend forward
            first = self.index(dest)
            last = self.index("my_anchor")
            if self.compare(first, ">", last):
                first, last = last, first
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
            if (
                self.has_selection() and (event.state & 5) == 0
            ):  # no shift(==1) or control(==4) pressed
                try:
                    self.mark_set("insert", ("sel.first+1c", "sel.last-1c")[edge_index])
                except tk.TclError:
                    pass

        return move_at_edge

    def perform_tab(self, event=None):
        self._log_keypress_for_undo(event)
        if (
            event.state & 0x0001
        ):  # shift is pressed (http://stackoverflow.com/q/32426250/261181)
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
                    effective = effective + self.indent_width
                else:
                    effective = max(effective - self.indent_width, 0)
                lines[pos] = self._make_blanks(effective) + line[raw:]
        self._set_region(head, tail, chars, lines)
        return "break"

    def select_all(self, event):
        self.tag_remove("sel", "1.0", tk.END)
        self.tag_add("sel", "1.0", tk.END)

    def set_read_only(self, value):
        if value == self.is_read_only():
            return

        TweakableText.set_read_only(self, value)
        self._reload_theme_options()
        if self._should_tag_current_line:
            self._tag_current_line()

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

        if (
            event_kind != self._last_event_kind
            or e.char in ("\r", "\n", " ", "\t")
            or e.keysym in ["Return", "KP_Enter"]
            or time.time() - self._last_key_time > 2
        ):
            self.edit_separator()

        self._last_event_kind = event_kind
        self._last_key_time = time.time()

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
        if self.indent_with_tabs:
            ntabs, nspaces = divmod(n, self.tabwidth)
            return "\t" * ntabs + " " * nspaces
        else:
            return " " * n

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
        try:
            if self.has_selection():
                self.direct_delete("sel.first", "sel.last")
        except Exception:
            pass

        self._last_event_kind = "paste"
        self.edit_separator()
        self.see("insert")
        self.after_idle(lambda: self.see("insert"))

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

    def _tag_current_line(self, event=None):
        self.tag_remove("current_line", "1.0", "end")

        # Let's show current line only with readable text
        # (this fits well with Thonny debugger,
        # otherwise debugger focus box and current line interact in an ugly way)
        if self._should_tag_current_line and not self.is_read_only():
            # we may be on the same line as with prev event but tag needs extension
            lineno = int(self.index("insert").split(".")[0])
            self.tag_add("current_line", str(lineno) + ".0", str(lineno + 1) + ".0")

    def on_secondary_click(self, event=None):
        "Use this for invoking context menu"
        self.focus_set()

    def _reload_theme_options(self, event=None):

        style = ttk.Style()

        states = []
        if self.is_read_only():
            states.append("readonly")

        # Following crashes when a combobox is focused
        # if self.focus_get() == self:
        #    states.append("focus")

        if "background" not in self._initial_configuration:
            background = style.lookup(self._style, "background", states)
            if background:
                self.configure(background=background)

        if "foreground" not in self._initial_configuration:
            foreground = style.lookup(self._style, "foreground", states)
            if foreground:
                self.configure(foreground=foreground)
                self.configure(insertbackground=foreground)

    def _insert_untypable_characters_on_windows(self, event):
        if event.state == 131084:  # AltGr or Ctrl+Alt
            lang_id = get_keyboard_language()
            char = _windows_altgr_chars_by_lang_id_and_keycode.get(lang_id, {}).get(
                event.keycode, None
            )
            if char is not None:
                self.insert("insert", char)

    def destroy(self):
        self.unbind("<<ThemeChanged>>", self._ui_theme_change_binding)
        super().destroy()

    def direct_insert(self, index, chars, tags=None, **kw):
        chars = self.check_convert_tabs_to_spaces(chars)
        super().direct_insert(index, chars, tags, **kw)
    
    def check_convert_tabs_to_spaces(self, chars):
        tab_count = chars.count("\t")
        if not self.replace_tabs or tab_count == 0:
            return chars
        else:
            
            if messagebox.askyesno("Convert tabs to spaces?",
                                   "Thonny (according to Python recommendation) uses spaces for indentation, "
                                   + "but the text you are about to insert/open contains %d tab characters. " % tab_count
                                   + "To avoid confusion, it's better to convert them into spaces (unless you know they should be kept as tabs).\n\n" 
                                   + "Do you want me to replace each tab with %d spaces?\n\n" % self.indent_width,
                                   parent=tk._default_root):
                return chars.expandtabs(self.indent_width)
            else:
                return chars

class TextFrame(ttk.Frame):
    "Decorates text with scrollbars, line numbers and print margin"

    def __init__(
        self,
        master,
        line_numbers=False,
        line_length_margin=0,
        first_line_number=1,
        text_class=EnhancedText,
        horizontal_scrollbar=True,
        vertical_scrollbar=True,
        vertical_scrollbar_class=ttk.Scrollbar,
        horizontal_scrollbar_class=ttk.Scrollbar,
        vertical_scrollbar_style=None,
        horizontal_scrollbar_style=None,
        borderwidth=0,
        relief="sunken",
        gutter_background="#e0e0e0",
        gutter_foreground="#999999",
        **text_options
    ):
        ttk.Frame.__init__(self, master=master, borderwidth=borderwidth, relief=relief)

        final_text_options = {
            "borderwidth": 0,
            "insertwidth": 2,
            "spacing1": 0,
            "spacing3": 0,
            "highlightthickness": 0,
            "inactiveselectbackground": "gray",
            "padx": 5,
            "pady": 5,
        }
        final_text_options.update(text_options)
        self.text = text_class(self, **final_text_options)
        self.text.grid(row=0, column=2, sticky=tk.NSEW)

        self._gutter = tk.Text(
            self,
            width=5,
            padx=0,
            pady=5,
            highlightthickness=0,
            bd=0,
            takefocus=False,
            font=self.text["font"],
            background="#e0e0e0",
            foreground=gutter_foreground,
            selectbackground=gutter_background,
            selectforeground=gutter_foreground,
            cursor="arrow",
            state="disabled",
            undo=False,
            wrap="none",
        )
        self._gutter.bind("<ButtonRelease-1>", self.on_gutter_click)
        self._gutter.bind("<Button-1>", self.on_gutter_click)
        self._gutter.bind("<Button1-Motion>", self.on_gutter_motion)
        self._gutter["yscrollcommand"] = self._gutter_scroll

        # need tags for justifying and rmargin
        self._gutter.tag_configure("content", justify="right", rmargin=3)

        # gutter will be gridded later
        assert first_line_number is not None
        self._first_line_number = first_line_number
        self.set_gutter_visibility(line_numbers)

        if vertical_scrollbar:
            self._vbar = vertical_scrollbar_class(
                self, orient=tk.VERTICAL, style=vertical_scrollbar_style
            )
            self._vbar.grid(row=0, column=3, sticky=tk.NSEW)
            self._vbar["command"] = self._vertical_scroll
            self.text["yscrollcommand"] = self._vertical_scrollbar_update

        if horizontal_scrollbar:
            self._hbar = horizontal_scrollbar_class(
                self, orient=tk.HORIZONTAL, style=horizontal_scrollbar_style
            )
            self._hbar.grid(row=1, column=0, sticky=tk.NSEW, columnspan=3)
            self._hbar["command"] = self._horizontal_scroll
            self.text["xscrollcommand"] = self._horizontal_scrollbar_update

        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        self._recommended_line_length = line_length_margin
        margin_line_color = ttk.Style().lookup(
            "Gutter", "background", default="LightGray"
        )
        self._margin_line = tk.Canvas(
            self.text,
            borderwidth=0,
            width=1,
            height=2000,
            highlightthickness=0,
            background=margin_line_color,
        )
        self.update_margin_line()

        self.text.bind("<<TextChange>>", self._text_changed, True)
        self.text.bind("<<CursorMove>>", self._cursor_moved, True)

        self._ui_theme_change_binding = self.bind(
            "<<ThemeChanged>>", self._reload_theme_options, True
        )
        self._reload_theme_options()

        # TODO: add context menu?

    def focus_set(self):
        self.text.focus_set()

    def set_gutter_visibility(self, value):
        if value and not self._gutter.winfo_ismapped():
            self._gutter.grid(row=0, column=0, sticky=tk.NSEW)
        elif not value and self._gutter.winfo_ismapped():
            self._gutter.grid_forget()

        # insert first line number (NB! Without trailing linebreak. See update_gutter)
        self._gutter.config(state="normal")
        self._gutter.delete("1.0", "end")
        for content, tags in self.compute_gutter_line(self._first_line_number):
            self._gutter.insert("end", content, ("content",) + tags)
        self._gutter.config(state="disabled")

        self.update_gutter()

    def set_line_length_margin(self, value):
        self._recommended_line_length = value
        self.update_margin_line()

    def _text_changed(self, event):
        "# TODO: make more efficient"
        self.update_gutter()
        self.update_margin_line()

    def _cursor_moved(self, event):
        self._update_gutter_active_line()

    def _vertical_scrollbar_update(self, *args):
        self._vbar.set(*args)
        self._gutter.yview(tk.MOVETO, args[0])

    def _gutter_scroll(self, *args):
        # FIXME: this doesn't work properly
        # Can't scroll to bottom when line numbers are not visible
        # and can't type normally at the bottom, when line numbers are visible
        return
        # self._vbar.set(*args)
        # self.text.yview(tk.MOVETO, args[0])

    def _horizontal_scrollbar_update(self, *args):
        self._hbar.set(*args)
        self.update_margin_line()

    def _vertical_scroll(self, *args):
        self.text.yview(*args)
        self._gutter.yview(*args)

    def _horizontal_scroll(self, *args):
        self.text.xview(*args)
        self.update_margin_line()

    def update_gutter(self, clean=True):
        # TODO: make it more efficient
        # by default clean only if line counts in gutter and text differ

        if clean:
            self._gutter.config(state="normal")
            self._gutter.delete("1.0", "end")
            # need to add first item separately, because Text can't report 0 rows
            for content, tags in self.compute_gutter_line(self._first_line_number):
                self._gutter.insert("end-1c", content, tags + ("content",))

            self._gutter.config(state="disabled")

        text_line_count = int(self.text.index("end").split(".")[0])
        gutter_line_count = int(self._gutter.index("end").split(".")[0])

        if text_line_count != gutter_line_count:
            self._gutter.config(state="normal")

            # NB! Text acts weird with last symbol
            # (don't really understand whether it automatically keeps a newline there or not)
            # Following seems to ensure both Text-s have same height
            if text_line_count > gutter_line_count:
                delta = text_line_count - gutter_line_count
                start = gutter_line_count + self._first_line_number - 1
                for i in range(start, start + delta):
                    self._gutter.insert("end-1c", "\n", ("content",))
                    for content, tags in self.compute_gutter_line(i):
                        self._gutter.insert("end-1c", content, ("content",) + tags)
            else:
                self._gutter.delete(line2index(text_line_count) + "-1c", "end-1c")

            self._gutter.config(state="disabled")

        # synchronize gutter scroll position with text
        # https://mail.python.org/pipermail/tkinter-discuss/2010-March/002197.html
        first, _ = self.text.yview()
        self._gutter.yview_moveto(first)
        self._update_gutter_active_line()

    def _update_gutter_active_line(self):
        self._gutter.tag_remove("active", "1.0", "end")
        insert = self.text.index("insert")
        self._gutter.tag_add("active", insert + " linestart", insert + " lineend")

    def compute_gutter_line(self, lineno):
        yield str(lineno), ("line_number",)

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

                margin_line_visible_col = (
                    self._recommended_line_length - first_visible_col
                )
                delta = first_visible_col_x
            except Exception:
                # fall back to ignoring scroll position
                margin_line_visible_col = self._recommended_line_length
                delta = 0

            if margin_line_visible_col > -1:
                x = (
                    get_text_font(self.text).measure(
                        (margin_line_visible_col - 1) * "M"
                    )
                    + delta
                    + self.text["padx"]
                )
            else:
                x = -10

            # print(first_visible_col, first_visible_col_x)

            self._margin_line.place(y=-10, x=x)

    def on_gutter_click(self, event=None):
        try:
            linepos = self._gutter.index("@%s,%s" % (event.x, event.y)).split(".")[0]
            self.text.mark_set("insert", "%s.0" % linepos)
            self._gutter.mark_set("gutter_selection_start", "%s.0" % linepos)
            if (
                event.type == "4"
            ):  # In Python 3.6 you can use tk.EventType.ButtonPress instead of "4"
                self.text.tag_remove("sel", "1.0", "end")
        except tk.TclError:
            exception("on_gutter_click")

    def on_gutter_motion(self, event=None):
        try:
            linepos = int(
                self._gutter.index("@%s,%s" % (event.x, event.y)).split(".")[0]
            )
            gutter_selection_start = int(
                self._gutter.index("gutter_selection_start").split(".")[0]
            )
            self.text.select_lines(
                min(gutter_selection_start, linepos),
                max(gutter_selection_start - 1, linepos - 1),
            )
            self.text.mark_set("insert", "%s.0" % linepos)
        except tk.TclError:
            exception("on_gutter_motion")

    def _reload_theme_options(self, event=None):

        style = ttk.Style()
        background = style.lookup("GUTTER", "background")
        if background:
            self._gutter.configure(background=background, selectbackground=background)
            self._margin_line.configure(background=background)

        foreground = style.lookup("GUTTER", "foreground")
        if foreground:
            self._gutter.configure(foreground=foreground, selectforeground=foreground)

    def destroy(self):
        self.unbind("<<ThemeChanged>>", self._ui_theme_change_binding)
        super().destroy()


def get_text_font(text):
    font = text["font"]
    if isinstance(font, str):
        return tkfont.nametofont(font)
    else:
        return font


def classifyws(s, tabwidth):
    raw = effective = 0
    for ch in s:
        if ch == " ":
            raw = raw + 1
            effective = effective + 1
        elif ch == "\t":
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
    root.tk.call("tcl_wordBreakAfter", "a b", 0)  # make sure word.tcl is loaded
    # TODO: IDLE updated following to
    # root.tk.call('set', 'tcl_wordchars', r'\w')
    # root.tk.call('set', 'tcl_nonwordchars', r'\W')
    root.tk.call("set", "tcl_wordchars", u"[a-zA-Z0-9_À-ÖØ-öø-ÿĀ-ſƀ-ɏА-я]")
    root.tk.call("set", "tcl_nonwordchars", u"[^a-zA-Z0-9_À-ÖØ-öø-ÿĀ-ſƀ-ɏА-я]")


def rebind_control_a(root):
    # Tk 8.6 has <<SelectAll>> event but 8.5 doesn't
    # http://stackoverflow.com/questions/22907200/remap-default-keybinding-in-tkinter
    def control_a(event):
        widget = event.widget
        if isinstance(widget, tk.Text):
            widget.tag_remove("sel", "1.0", "end")
            widget.tag_add("sel", "1.0", "end")

    root.bind_class("Text", "<Control-a>", control_a)


def _running_on_mac():
    return tk._default_root.call("tk", "windowingsystem") == "aqua"


def get_keyboard_language():
    # https://stackoverflow.com/a/42047820/261181
    if platform.system() != "Windows":
        raise NotImplementedError("Can provide keyboard language only on Windows")

    import ctypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
    # Made up of 0xAAABBBB, AAA = HKL (handle object) & BBBB = language ID
    klid = user32.GetKeyboardLayout(thread_id)
    # Language ID -> low 10 bits, Sub-language ID -> high 6 bits
    # Extract language ID from KLID
    lid = klid & (2 ** 16 - 1)

    return lid


_windows_altgr_chars_by_lang_id_and_keycode = {
    # https://docs.microsoft.com/en-us/windows/desktop/intl/language-identifier-constants-and-strings
    0x0425: {191: "^"}  # AltGr+Ä
}
