# -*- coding: utf-8 -*-

import tkinter as tk
from thonny.common import TextRange
from thonny.globals import get_workbench
from thonny import tktextext
from thonny.ui_utils import EnhancedTextWithLogging

EDIT_BACKGROUND="white"
READ_ONLY_BACKGROUND="LightYellow"

class CodeViewText(EnhancedTextWithLogging):
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
        get_workbench().get_menu("edit").post(event.x_root, event.y_root)

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
