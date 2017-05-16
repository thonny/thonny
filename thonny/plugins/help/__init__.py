import tkinter as tk
import tkinter.font
import os.path
from tkinter import ttk
from thonny import tktextext
from thonny.globals import get_workbench

class HelpView(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        
        main_font = tkinter.font.nametofont("TkDefaultFont")
        
        bold_font = main_font.copy()
        bold_font.configure(weight="bold", size=main_font.cget("size"))
        
        h1_font = main_font.copy()
        h1_font.configure(size=main_font.cget("size") * 2, weight="bold")
        
        h2_font = main_font.copy()
        h2_font.configure(size=round(main_font.cget("size") * 1.5), weight="bold")
        
        h3_font = main_font.copy()
        h3_font.configure(size=main_font.cget("size"), weight="bold")
        
        self.text = tktextext.TweakableText(self, border=0, padx=15, pady=15,
                                            font=main_font,
                                            wrap="word")
        
        self.text.tag_configure("h1", font=h1_font)
        self.text.tag_configure("h2", font=h2_font)
        self.text.tag_configure("h3", font=h3_font)
        self.text.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._vbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self._vbar.grid(row=0, column=1, sticky=tk.NSEW)
        self._vbar['command'] = self.text.yview 
        self.text['yscrollcommand'] = self._vbar.set  
        
        
        self.load_rst_file("help.rst")
        
    
    def clear(self):
        self.text.direct_delete("1.0", "end")
    
    def load_rst(self, source):
        
        def is_symbol_line(line, symbol, min_count=3):
            line = line.rstrip()
            return (line.startswith(symbol) 
                    and line.replace(symbol, "") == ""
                    and len(line) >= min_count)
        
        self.clear()
        lines = source.splitlines(True)
        i = 0
        while i < len(lines):
            if is_symbol_line(lines[i], "="):
                self.append_chars(lines[i+1], "h1")
                assert is_symbol_line(lines[i+2], "=")
                i += 3
            elif (i < len(lines)-1 
                  and is_symbol_line(lines[i+1], "=")):
                self.append_chars(lines[i], "h2")
                i += 2
            elif (i < len(lines)-1 
                  and is_symbol_line(lines[i+1], "-")):
                self.append_chars(lines[i], "h3")
                i += 2
            else:
                self.append_rst_line(lines[i])
                i += 1
    
    def append_chars(self, chars, tag=None):
        if tag:
            self.text.direct_insert("end", chars, (tag,))
        else:
            self.text.direct_insert("end", chars)
    
    def append_rst_line(self, source):
        self.append_chars(source)
    
    def load_rst_file(self, filename):
        if not os.path.isabs(filename):
            filename = os.path.join(os.path.dirname(__file__), filename) 
            
        with open(filename, encoding="UTF-8") as fp:
            self.load_rst(fp.read())


def open_help():
    get_workbench().show_view("HelpView")

def load_plugin():
    get_workbench().add_view(HelpView, "Help", "ne")
    get_workbench().add_command("help_contents", "help", "Help contents",
                                open_help,
                                group=30)
    