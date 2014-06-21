# -*- coding: utf-8 -*-
 
import ui_utils
import tkinter as tk
from tkinter import ttk
import tkinter.font as tk_font

from ui_utils import TextWrapper, AutoScrollbar
from common import TextRange
from coloring import SyntaxColorer
from config import prefs

# line numbers taken from http://tkinter.unpythonic.net/wiki/A_Text_Widget_with_Line_Numbers 

# scrolling code copied from tkinter.scrolledtext
# (don't want to use scrolledtext directly, because I want to include margin in the same box) 
class CodeView(ttk.Frame, TextWrapper):
    def __init__(self, master, first_line_no=1, font_size=11,
                 auto_vert_scroll=False,
                 height=None):
        ttk.Frame.__init__(self, master)
        
        # attributes
        self.first_line_no = first_line_no
        self.filename = None
        self.file_encoding = "UTF-8"
        
        # child widgets
        if auto_vert_scroll:
            self.vbar = AutoScrollbar(self, orient=tk.VERTICAL)
        else:
            self.vbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vbar.grid(row=0, column=2, sticky=tk.NSEW)
        self.hbar = AutoScrollbar(self, orient=tk.HORIZONTAL)
        
        # TODO: show when necessary
        self.hbar.grid(row=1, column=0, sticky=tk.NSEW, columnspan=2)
        
        self.margin = tk.Text(self,
                width = 4,
                padx = 5,
                pady = 5,
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
                #background="gray",
                height=height,
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
                padx=5,
                pady=5,
                undo=True,
                autoseparators=False)
        
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
        
        self.colorer = None
        self.set_coloring(True)
        self.prepare_level_boxes()
        
        """
        self.text.tag_configure('statement', borderwidth=1, relief=tk.SOLID)
        self.text.tag_configure('statement_odd', borderwidth=1, relief=tk.SOLID, background="#FFFFFF")
        self.text.tag_configure('statement_even', borderwidth=1, relief=tk.SOLID, background="#FFFFFE")
        """
        self.text.tag_configure('before', background="#F8FC9A")
        self.text.tag_configure('after', background="#D7EDD3")
        self.text.tag_configure('exception', background="#FFBFD6")
        
        #self.current_statement_range = None
        self.active_statement_ranges = []
        #self.statement_tags = set()
    
    def get_content(self):
        return self.text.get("1.0", "end-1c") # -1c because Text always adds a newline itself
    
    def set_content(self, content):
        TextWrapper._user_text_delete(self, "1.0", tk.END)
        TextWrapper._user_text_insert(self, "1.0", content)
        self._update_line_numbers()
        self.text.edit_reset();
        
        if self.colorer:
            self.colorer.notify_range("1.0", "end")
        self.update_level_boxes()
    
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
            if self.colorer == None:
                self.colorer = SyntaxColorer(self.text)
        else:
            if self.colorer != None:
                self.colorer.removecolors()
                self.colorer = None
    
    def select_lines(self, start_line, end_line=None):
        self.select_range(TextRange(start_line - self.first_line_no + 1, 0, 
                          end_line - self.first_line_no + 1), "end")
    
    def select_all(self):
        self.text.tag_remove("sel", "1.0", tk.END)
        self.text.tag_add('sel', '1.0', tk.END)
    
    def handle_focus_message(self, text_range, msg=None):
        
        if text_range == None:
            self.clear_tags(['before', 'after', 'exception'])
            
        elif "statement" in msg.state or "suite" in msg.state:
            self.clear_tags(['before', 'after', 'exception'])
            self.text.tag_configure('before', background="#F8FC9A", borderwidth=1, relief=tk.SOLID)
             
            if msg.state.startswith("before"):
                tag = "before"
            elif msg.state.startswith("after"):
                tag = "after"
            else:
                tag = "exception"
            
            if (msg.state in ("before_statement", "before_statement_again")
                or (prefs["debugging.detailed_steps"]
                    and msg.state in ("after_statement",
                                      "after_suite",
                                      "before_suite"))):
                self.tag_range(text_range, tag, True)
            
            if msg.state == "before_statement":
                self.active_statement_ranges.append(text_range)
            elif msg.state == "after_statement":
                # TODO: what about exception??
                self.active_statement_ranges.pop()
        
        else:
            # if expression is in focus, statement will be shown without border
            self.text.tag_configure('before', background="#F8FC9A", borderwidth=0, relief=tk.SOLID)
            
            
            
    
    def tag_range(self, text_range, tag, see=False):
            first_line, first_col, last_line = self.get_text_range_block(text_range)
            
            for lineno in range(first_line, last_line+1):
                self.text.tag_add(tag,
                                  "%d.%d" % (lineno, first_col),
                                  "%d.0" % (lineno+1))
                
            self.text.update_idletasks()
            self.text.see("%d.0" % (first_line))
            #print("SEEING: " + "%d.0" % (first_line))
            if last_line - first_line < 3:
                # if it's safe to assume that whole code fits into screen
                # then scroll it down a bit so that expression view doesn't hide behind
                # lower edge of the editor
                self.text.update_idletasks()
                self.text.see("%d.0" % (first_line+3))
    
    def get_text_range_block(self, text_range):
        first_line = text_range.lineno - self.first_line_no + 1
        last_line = text_range.end_lineno - self.first_line_no + 1
        first_line_content = self.text.get("%d.0" % first_line, "%d.end" % first_line)
        if first_line_content.strip().startswith("elif "):
            first_col = first_line_content.find("elif ")
        else:
            first_col = text_range.col_offset
        
        return (first_line, first_col, last_line)
    
    def clear_tags(self, tags, from_index="1.0", to_index=tk.END):
        for tag in tags:
            self.text.tag_remove(tag, from_index, to_index)
    
    def clear_tags_for_text_range(self, tags, text_range):
        first_line, first_col, last_line = self.get_text_range_block(text_range)
        start_index = "%d.%d" % (first_line, first_col)
        end_index = "%d.0" % (last_line+1)
        self.clear_tags(tags, start_index, end_index)
    
    def select_range(self, text_range):
        self.text.tag_remove("sel", "1.0", tk.END)
        
        if text_range:
            start = str(text_range.lineno - self.first_line_no + 1) \
                + "." + str(text_range.col_offset)
            end = str(text_range.end_lineno - self.first_line_no + 1) \
                + "." + str(text_range.end_col_offset)
            self.text.tag_add("sel", start, end)
                                     
            self.text.see(start)
            
    def get_statement_tag(self, level, kind, odd=False):
        tag_name = "st_" + kind + str(level) + ("odd" if odd else "even")
        if tag_name not in self.statement_tags:
            if kind == "before":
                color = "#" + hex(0xF8FC9A - level)[2:]
            elif kind == "after":
                color = "#" + hex(0xD7EDD3 - level)[2:]
            elif kind == "exception":
                color = "#" + hex(0xFFBFD6 - level)[2:]
            else:
                color_level = hex(255 - level * 5 - (1 if odd else 0))[2:]
                color = "#" + color_level + color_level + color_level
                
            print("COLOOOOOOOOO", kind, color, level)
            self.statement_tags.add(tag_name)
            self.text.tag_configure(tag_name, background=color, borderwidth=1, relief=tk.SOLID)
            #self.text.tag_raise(tag_name)
        return tag_name
            
    
    def enter_execution_mode(self):
        self.active_statement_ranges = []
        self.read_only = True
        self.text.configure(insertwidth=0)
        #self.text.configure(background="LightYellow", insertwidth=0, insertbackground="Gray")

    def exit_execution_mode(self):
        self.active_statement_ranges = []
        self.read_only = False
        self.text.configure(insertwidth=2)
        self.text.configure(background="White", insertwidth=2, insertbackground="Black")

    def _user_text_insert(self, index, chars, tags=None):
        #cursor_pos = self.text.index(tk.INSERT)
        
        if self.read_only:
            self.bell()
            #print("CodeView._user_text_insert, read only") # TODO: log this?
            #self._show_read_only_warning()
        else:
            TextWrapper._user_text_insert(self, index, chars, tags)
            if self.colorer:
                self.colorer.on_insert(index, chars, tags)
            self._update_line_numbers()
            self.update_level_boxes()

    def _user_text_delete(self, index1, index2=None):
        # cursor_pos = self.text.index(tk.INSERT)
        
        if self.read_only:
            self.bell()
            print("CodeView._user_text_insert, read only")
            #self._show_read_only_warning()
        else:
            TextWrapper._user_text_delete(self, index1, index2)
            if self.colorer:
                self.colorer.on_delete(index1, index2)
            self._update_line_numbers()
            self.update_level_boxes()
    
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
    
    def on_text_key_press(self, e):
        TextWrapper.on_text_key_press(self, e)
        #print("KEY", repr(e.char))
        
        # replace tabs with spaces
        # TODO: keep tabs when inside string or when there are some
        # non-whitespace chars on current line left to the cursor
        if e.char in ("\t", "\n", "\r"):
            current_line = self.text.get("insert linestart", "insert lineend")
            #print("KEY", repr(e.char))
            if e.char == "\t":
                self.text.insert("insert", "    ");
                # TODO: delete selected text if there is any
                return "break"
            
            elif e.char in ("\n", "\r"):
                
                current_indent = ""
                for c in current_line:
                    if c in " \t":
                        current_indent += c
                    else:
                        break
                if current_line.strip().endswith(':'):
                    self.text.insert("insert", "\n" + current_indent + "    ")
                    return "break"
                else:
                    self.text.insert("insert", "\n" + current_indent)
                    return "break"
                # TODO: unindent in case of break, return, continue, raise, pass
                  
        elif e.keysym == "BackSpace":
            left_text = self.text.get("insert linestart", "insert")
            if left_text.endswith("    ") and len(left_text) % 4 == 0:
                self.text.delete("insert-4c", "insert")
                return "break"
                    
        
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
    
    
    def prepare_level_boxes(self):
        return
        for i in range(6):
            # boxes of different levels must have something different (here background)
            # otherwise they will be merged into one box
            self.text.tag_configure('level' + str(i), 
                                    background=hex(256*256*256-i).replace("0x", "#"),
                                    borderwidth=1,
                                    relief=tk.GROOVE)
    
    def update_level_boxes(self, first_line=1, last_line=None):
        return
        if last_line == None:
            last_line = int(self.text.index(tk.END).split('.')[0])
            
        for i in range(6):
            self.text.tag_remove('level' + str(i),
                                 str(first_line) + ".0",
                                 str(last_line+1) + ".0")
        
        # clean old boxes
        # setup new boxes
        # I can do it line-by-line because tk merges same level boxes 
        prev_max_level = 0
        
        self.text.update_idletasks()
        print("ASDFSF", self.text.bbox("1.1"))
        
        for lineno in range(first_line, last_line+1):
            line = self.text.get(str(lineno) + ".0", str(lineno+1) + ".0")
            level = 0
            
            # massage empty and comment lines
            if line.strip() == '' or line.strip()[0] == '#':
                required_pseudo_length = max(len(line), prev_max_level*4) 
                line = required_pseudo_length * " " + "\n"
            
            while line.startswith("    " * level):
                self.text.tag_add('level' + str(level), 
                                  str(lineno) + "." + str(level*4),
                                  str(lineno+1) + '.0')
                
                box = self.text.bbox(str(lineno) + "." + str(level*4))
                print(box, str(lineno) + "." + str(level*4))
                if box != None:
                    x, y, _, _ = box
                    hor_canvas = tk.Canvas(self.text, width=100, height=1, bd=0,
                                       takefocus=False, highlightthickness=0)
                    hor_canvas.place(x=x-7, y=y-2)
                    hor_canvas.create_line(0,0, 100,0, fill="#999999")
                    
                    hor_canvas = tk.Canvas(self.text, width=1, height=18, bd=0,
                                       takefocus=False, highlightthickness=0)
                    hor_canvas.place(x=x-7, y=y-2)
                    hor_canvas.create_line(0,0, 0,18, fill="#00aa00")
                    
                level += 1
                
            prev_max_level = level-1
              
                
                 
    
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



