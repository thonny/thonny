# -*- coding: utf-8 -*-
from __future__ import print_function, division 
import ui_utils
try:
    import tkinter as tk
    from tkinter import ttk
    import tkinter.font as tk_font
    from tkinter.messagebox import showwarning
except ImportError:
    import Tkinter as tk
    import ttk 
    import tkFont as tk_font
    from tkMessageBox import showwarning

from ui_utils import TextWrapper
from common import TextRange
from coloring import SyntaxColorer
from user_logging import log_user_event, TextDeleteEvent, TextInsertEvent

# line numbers taken from http://tkinter.unpythonic.net/wiki/A_Text_Widget_with_Line_Numbers 

# scrolling code copied from tkinter.scrolledtext
# (don't want to use scrolledtext directly, because I want to include margin in the same box) 
class CodeView(ttk.Frame, TextWrapper):
    def __init__(self, master, first_line_no=1, font_size=11):
        ttk.Frame.__init__(self, master)
        
        # attributes
        self.first_line_no = first_line_no
        self.filename = None
        self.file_encoding = "UTF-8"
        
        # child widgets
        self.vbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vbar.grid(row=0, column=2, sticky=tk.NSEW)
        self.hbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        
        # TODO: show when necessary
        #self.hbar.grid(row=1, column=0, sticky=tk.NSEW, columnspan=2)
        
        self.margin = tk.Text(self,
                width = 4,
                padx = 4,
                highlightthickness = 0,
                takefocus = 0,
                bd = 0,
                font = ui_utils.EDITOR_FONT,
                #cursor = "dotbox",
                background = '#e0e0e0',
                foreground = '#999999',
                #state='disabled'
                )
        
        #self.margin.grid(row=0, column=0, sticky=tk.NSEW)
        
        def _vertical_scrollbar_update(*args):
            self.vbar.set(*args)
            self.margin.yview(tk.MOVETO, args[0])
        
        self.text = tk.Text(self,
                #background="#ffffff",
                #background="#FEE5BF",
                spacing1=0,
                spacing3=0,
                highlightthickness=0,
                #highlightcolor="LightBlue",
                yscrollcommand=_vertical_scrollbar_update,
                xscrollcommand=self.hbar.set,
                borderwidth=0,
                font=ui_utils.EDITOR_FONT,
                wrap=tk.NONE,
                insertwidth=2,
                #selectborderwidth=2,
                inactiveselectbackground='gray',
                #highlightthickness=0, # TODO: try different in Mac and Linux
                #highlightcolor="gray",
                padx=4,
                undo=True)
        
        TextWrapper.__init__(self)
        
        self.read_only = False
        
        self.text.grid(row=0, column=1, sticky=tk.NSEW)
        
        def _vertical_scroll(*args):
            self.text.yview(*args)
            self.margin.yview(*args)
        self.vbar['command'] = _vertical_scroll # TODO: keep line count same in margin
        self.hbar['command'] = self.text.xview
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.colorer = SyntaxColorer(self.text)
        
    
    def get_content(self):
        return self.text.get("1.0", "end-1c") # -1c because Text always adds a newline itself
    
    def set_content(self, content):
        TextWrapper._user_text_delete(self, "1.0", tk.END)
        TextWrapper._user_text_insert(self, "1.0", content)
        self._update_line_numbers()
        self.text.edit_reset();
        
        self.colorer.notify_range("1.0", "end")
    
    def get_char_bbox(self, lineno, col_offset):
        self.text.update_idletasks()
        return self.text.bbox(str(lineno - self.first_line_no + 1) + "." + str(col_offset))
            
    
    def select_lines(self, start_line, end_line=None):
        self.select_range(TextRange(start_line - self.first_line_no + 1, 0, 
                          end_line - self.first_line_no + 1), "end")
    
    def show_focus_box(self, text_range):
        "TODO:"
        #print("*** focus", start_line, start_col, end_line, end_col)
        self.select_range(text_range)
    
    def select_range(self, text_range):
        self.text.tag_remove("sel", "1.0", tk.END)
        
        if text_range:
            start = str(text_range.lineno - self.first_line_no + 1) \
                + "." + str(text_range.col_offset)
            end = str(text_range.end_lineno - self.first_line_no + 1) \
                + "." + str(text_range.end_col_offset)
            self.text.tag_add("sel", start, end)
                                     
            self.text.see(start)
    
    def enter_execution_mode(self):
        self.read_only = True
        self.text.configure(background="LightYellow", insertwidth=0, insertbackground="Gray")

    def exit_execution_mode(self):
        self.read_only = False
        self.text.configure(background="White", insertwidth=2, insertbackground="Black")

    def _user_text_insert(self, index, chars, tags=None):
        #cursor_pos = self.text.index(tk.INSERT)
        
        if self.read_only:
            self.bell()
            #print("CodeView._user_text_insert, read only") # TODO: log this?
            #self._show_read_only_warning()
        else:
            TextWrapper._user_text_insert(self, index, chars, tags)
            self.colorer.on_insert(index, chars, tags)
            self._update_line_numbers()

    def _user_text_delete(self, index1, index2=None):
        # cursor_pos = self.text.index(tk.INSERT)
        
        if self.read_only:
            self.bell()
            print("CodeView._user_text_insert, read only")
            #self._show_read_only_warning()
        else:
            TextWrapper._user_text_delete(self, index1, index2)
            self.colorer.on_delete(index1, index2)
            self._update_line_numbers()
    
    def _update_line_numbers(self):
        text_line_count = int(self.text.index("end-1c").split(".")[0])
        
        self.margin.config(state='normal')
        self.margin.delete("1.0", "end")
        for i in range(text_line_count):
            self.margin.insert("end", str(i + self.first_line_no).rjust(3))
            if i < text_line_count-1:
                self.margin.insert("end", "\n") 
        self.margin.config(state='disabled')


    """
    def _show_read_only_warning(self):
        showwarning("Warning",
                "Editing during run/debug is not allowed")
    """
    
    
            
    def update_focus_boxes(self, boxes):
        """
        1) Removes boxes which are not among given boxes, creates missing boxes
        2) Highlights last box, removes highlighting from other boxes 
        """
        # TODO:
        pass

    def repl_demo(self):
        self.text.margin.config(state='normal')
        self.text.margin.delete("1.0", "end")
        self.text.margin.insert("1.0", ">>>")
        self.text.margin.config(state='disabled')
        
        #self.text.insert("1.0", "x = 23 * (3 + 2 ^ 2) - sin(3) - 1")
    
    def change_font_size(self, delta):
        self.font.configure(size=self.font.cget("size") + delta)
    
    def fact_demo(self):
        self.text.insert("1.0", """
def fact(n):
    if blah:
        if n == 0:
            return 1
        else:
            return fact(n-1) *n+ "kala"
    elif kala > pala:
        blah
        blah
    else:
        sahh

    print("Vastus on:", result)

""".strip() + "\n")
        
        return
    
        self.text.tag_add("active1", "1.0", "end")
        self.text.tag_configure("active1", borderwidth=1, relief=tk.RAISED)
        
        self.text.tag_add('active2', '2.4', '3.0')
        self.text.tag_add('active2', '3.4', '4.0')
        self.text.tag_add('active2', '4.4', '5.0')
        self.text.tag_add('active2', '5.4', '6.0')
        self.text.tag_add('active2', '6.4', '7.0')
        self.text.tag_add('active2', '7.4', '8.0')
        self.text.tag_add('active2', '8.4', '9.0')
        self.text.tag_add('active2', '9.4', '10.0')
        self.text.tag_add('active2', '10.4', '11.0')
        self.text.tag_add('active2', '11.4', '12.0')
        self.text.tag_configure('active2', background="#FFFFFE", borderwidth=1, relief=tk.RAISED)
        
        self.text.tag_add('active3', '3.8', '4.0')
        self.text.tag_add('active3', '4.8', '5.0')
        self.text.tag_add('active3', '5.8', '6.0')
        self.text.tag_add('active3', '6.8', '7.0')
        self.text.tag_configure('active3', background="#FFFFFD", borderwidth=1, relief=tk.RAISED)
        #self.text.tag_add('active3', '8.8', '9.0')
        #self.text.tag_add('active3', '9.8', '10.0')
        
        #self.text.tag_add('active4', '8.8', '9.0')
        self.text.tag_configure('active4', background="#FFFFFC", borderwidth=1, relief=tk.RAISED)


        self.text.tag_add('active', '6.12', '6.39')
#        self.text.tag_configure('active', background="#FFFFAF")
        self.text.tag_configure('active', background="#FFFFAF", borderwidth=1, relief=tk.RAISED)
        
        self.text.tag_add('inactive', '6.19', '6.33')
        self.text.tag_configure("inactive", underline=True, foreground="blue")

        
        supfont = tk_font.Font(family='Consolas', size=8, weight="normal", slant="italic")
        self.text.tag_add('superscript', '6.33', '6.39')
        self.text.tag_configure('superscript', offset=7, font=supfont, underline=False, foreground="red")



