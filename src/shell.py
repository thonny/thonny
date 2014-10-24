# -*- coding: utf-8 -*-

import os.path
import traceback
import ui_utils
from config import prefs
import memory

import tkinter as tk
from tkinter import ttk
import tkinter.font as font

from misc_utils import running_on_mac_os
from ui_utils import TextWrapper, generate_event
from common import InputRequest, ToplevelResponse, OutputEvent, parse_shell_command
from user_logging import log_user_event, ShellCreateEvent, ShellCommandEvent,\
    ShellInputEvent

class ShellFrame (ttk.Frame, TextWrapper):
    def __init__(self, master, vm, editor_book):
        ttk.Frame.__init__(self, master)
        
        self._vm = vm
        self._editor_book = editor_book
        self._before_io = True
        self._command_count = 0
        self._command_history = [] # actually not really history, because each command occurs only once
        self._command_history_current_index = None 
        self.text_mode = "toplevel"
        
        """
        self.margin = tk.Text(self,
                width = 4,
                padx = 4,
                highlightthickness = 0,
                takefocus = 0,
                bd = 0,
                #font = self.font,
                cursor = "dotbox",
                background = '#e0e0e0',
                foreground = '#999999',
                #state='disabled'
                )
        self.margin.grid(row=0, column=0)
        """
        
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vert_scrollbar.grid(row=0, column=2, sticky=tk.NSEW)
        editor_font = font.nametofont(name='TkFixedFont')
        self.text = tk.Text(self,
                            font=editor_font,
                            #foreground="white",
                            #background="#666666",
                            highlightthickness=0,
                            #highlightcolor="LightBlue",
                            borderwidth=0,
                            yscrollcommand=self.vert_scrollbar.set,
                            padx=4,
                            insertwidth=2,
                            height=10,
                            undo=True,
                            autoseparators=False)
        log_user_event(ShellCreateEvent(self))
        
        self.text.grid(row=0, column=1, sticky=tk.NSEW)
        self.text.bind("<Up>", self._arrow_up, "+")
        self.text.bind("<Down>", self._arrow_down, "+")
        self.text.bind("<KeyPress>", self._text_key_press, "+")
        self.text.bind("<KeyRelease>", self._text_key_release, "+")
        self.vert_scrollbar['command'] = self.text.yview
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        TextWrapper.__init__(self)
        
        self.text["font"] = ui_utils.EDITOR_FONT
        vert_spacing = 10
        io_indent = 16
        
        self.text.tag_configure("toplevel", font=ui_utils.EDITOR_FONT)
        self.text.tag_configure("prompt", foreground="purple", font=ui_utils.BOLD_EDITOR_FONT)
        self.text.tag_configure("command", foreground="black")
        self.text.tag_configure("automagic", foreground="DarkGray")
        #self.text.tag_configure("value", foreground="DarkGreen")
        #self.text.tag_configure("value", foreground="#B25300")
        self.text.tag_configure("value", foreground="DarkBlue") # TODO: see also _text_key_press and _text_key_release
        self.text.tag_configure("error", foreground="Red")
        
        self.text.tag_configure("io", lmargin1=io_indent, lmargin2=io_indent, rmargin=io_indent, font=ui_utils.IO_FONT)
        self.text.tag_configure("stdin", foreground="Blue")
        self.text.tag_configure("stdout", foreground="Black")
        self.text.tag_configure("stderr", foreground="Red")
        
        self.text.tag_configure("vertically_spaced", spacing1=vert_spacing)
        self.text.tag_configure("inactive", foreground="#aaaaaa")
        
        # create 3 marks: input_start shows the place where user entered but not-yet-submitted
        # input starts, output_end shows the end of last output,
        # output_insert shows where next incoming program output should be inserted
        self.text.mark_set("input_start", "end-1c")
        self.text.mark_gravity("input_start", tk.LEFT)
        
        self.text.mark_set("output_end", "end-1c")
        self.text.mark_gravity("output_end", tk.LEFT)
        
        self.text.mark_set("output_insert", "end-1c")
        self.text.mark_gravity("output_insert", tk.RIGHT)
        
        
        self.active_object_tags = set()
    
        
        
        

    def handle_vm_message(self, msg):
        if isinstance(msg, InputRequest):
            self.text_mode = "io"
            self.text["font"] = ui_utils.IO_FONT # otherwise the cursor is of toplevel size
            self.text.focus_set()
            self.text.mark_set("insert", "end")
            self.text.tag_remove("sel", "1.0", tk.END)
            self._try_submit_input() # try to use leftovers from previous request
            self.text.see("end")
            
        elif isinstance(msg, OutputEvent):
            self.text_mode = "io"
            self.text["font"] = ui_utils.IO_FONT
            
            # mark first line of io
            if self._before_io:
                self._insert_text_directly(msg.data[0], ("io", msg.stream_name, "vertically_spaced"))
                self._before_io = False
                self._insert_text_directly(msg.data[1:], ("io", msg.stream_name))
            else:
                self._insert_text_directly(msg.data, ("io", msg.stream_name))
            
            self.text.mark_set("output_end", self.text.index("end-1c"))
            self.text.see("end")
            
        elif isinstance(msg, ToplevelResponse):
            if self._editor_book.is_in_execution_mode():
                self._editor_book.exit_execution_mode() # TODO: only when it's about program exit?
            
            self.text_mode = "toplevel"
            self.text["font"] = ui_utils.EDITOR_FONT
            self._before_io = True
            if hasattr(msg, "error"):
                self._insert_text_directly(msg.error + "\n", ("toplevel", "error"))
                
            if hasattr(msg, "value_info"):
                value_repr = msg.value_info.short_repr
                if value_repr != "None":
                    if prefs["values_in_heap"]:
                        value_repr = memory.format_object_id(msg.value_info.id)
                    object_tag = "object_" + str(msg.value_info.id)
                    self._insert_text_directly(value_repr + "\n", ("toplevel",
                                                                   "value",
                                                                   object_tag))
                    if running_on_mac_os():
                        sequence = "<Command-Button-1>"
                    else:
                        sequence = "<Control-Button-1>"
                    self.text.tag_bind(object_tag, sequence,
                                       lambda _: generate_event(self, "<<ObjectSelect>>", msg.value_info.id))
                    
                    self.active_object_tags.add(object_tag)
            
            self.text.mark_set("output_end", self.text.index("end-1c"))
            self._insert_prompt()
            self._try_submit_input()
            self.text.see("end")
            
            # TODO: show cwd if it has changed
            """
            if hasattr(msg, "event") and msg.event == "reset":
                # make current dir visible (again)
                self.submit_magic_command("%cd " + self._vm.cwd + "\n")
            """
            
        else:
            pass
    
    def _insert_prompt(self):
        # if previous output didn't put a newline, then do it now
        if not self.text.index("output_insert").endswith(".0"):
            # TODO: show a symbol indicating unfinished line
            self._insert_text_directly("\n", ("io",))
        
        prompt_tags = ("toplevel", "prompt")
         
        # if previous line has value or io then add little space
        prev_line = self.text.index("output_insert - 1 lines")
        prev_line_tags = self.text.tag_names(prev_line)
        if "io" in prev_line_tags or "value" in prev_line_tags:
            prompt_tags += ("vertically_spaced",)
            #self.text.tag_add("last_result_line", prev_line)
        
        self._insert_text_directly(">>> ", prompt_tags)
        self.text.edit_reset();
    
    
    def submit_magic_command(self, cmd_line):
        assert self._vm.get_state() == "toplevel"
        self.text.delete("input_start", "end")
        self.text.insert("input_start", cmd_line, ("automagic",))
        self.text.see("end")

        
    def _user_text_insert(self, index, txt, tags=(), **kw):
        #print("insert", index, text, kw)
        if (self._editing_allowed()
            and self._in_current_input_range(index)):
            #self._print_marks("before insert")
            # I want all marks to stay in place
            self.text.mark_gravity("input_start", tk.LEFT)
            self.text.mark_gravity("output_insert", tk.LEFT)
            
            if self._vm.get_state() == "input":
                tags = tags + ("io", "stdin")
            else:
                tags = tags + ("toplevel", "command")
            
            TextWrapper._user_text_insert(self, index, txt, tags, **kw)
            
            # tag first char of io separately
            if self._vm.get_state() == "input" and self._before_io:
                self.text.tag_add("vertically_spaced", index)
                self._before_io = False
            
            self._try_submit_input()
        else:
            self.bell()
            print("Shell: can't insert", self._vm.get_state())
            
    def _user_text_delete(self, index1, index2=None, **kw):
        if (self._editing_allowed() 
            and self._in_current_input_range(index1)
            and (index2 == None or self._in_current_input_range(index2))):
            TextWrapper._user_text_delete(self, index1, index2, **kw)
        else:
            self.bell()
            print("Shell: can't delete", self._vm.get_state())
    
    def _in_current_input_range(self, index):
        return self.text.compare(index, ">=", "input_start")
    
    def _insert_text_directly(self, txt, tags=()):
        # I want the insertion to go before marks 
        #self._print_marks("before output")
        #print("inserting directly", txt, tags)
        self.text.mark_gravity("input_start", tk.RIGHT)
        self.text.mark_gravity("output_insert", tk.RIGHT)
        TextWrapper._user_text_insert(self, "output_insert", txt, tuple(tags))
        #self._print_marks("after output")
        # output_insert mark will move automatically because of its gravity
        
    
    def _try_submit_input(self):
        # see if there is already enough inputted text to submit
        input_text = self.text.get("input_start", "end-1c")
        submittable_text = self._extract_submittable_input(input_text)
        
        if submittable_text != None:
            # user may have pasted more text than necessary for this request
            # leftover text will be kept in widget, waiting for next request.
            start_index = self.text.index("input_start")
            end_index = self.text.index("input_start+{0}c".format(len(submittable_text)))
            # apply correct tags (if it's leftover then it doesn't have them yet)
            if self._vm.get_state() == "input":
                self.text.tag_add("io", start_index, end_index)
                self.text.tag_add("stdin", start_index, end_index)
            else:
                self.text.tag_add("toplevel", start_index, end_index)
                self.text.tag_add("command", start_index, end_index)
                
            
            
            # update start mark for next input range
            self.text.mark_set("input_start", end_index)
            
            # Move output_insert mark after the requested_text
            # Leftover input, if any, will stay after output_insert, 
            # so that any output that will come in before
            # next input request will go before leftover text
            self.text.mark_set("output_insert", end_index)
            
            # remove tags from leftover text
            for tag in ("io", "stdin", "toplevel", "command"):
                # don't remove automagic, because otherwise I can't know it's auto 
                self.text.tag_remove(tag, end_index, "end")
                
            self._submit_input(submittable_text)
            # tidy up the tags
            #self.text.tag_remove("pending_input", "1.0", "end")
            #self.text.tag_add("submitted_input", start_index, end_index)
            #self.text.tag_add("pending_input", end_index, "end-1c")
    
    def _editing_allowed(self):
        return self._vm.get_state() in ('toplevel', 'input')
    
    def _extract_submittable_input(self, input_text):
        
        if self._vm.get_state() == "toplevel":
            # TODO: support also multiline commands
            if "\n" in input_text:
                return input_text[:input_text.index("\n")+1]
            else:
                return None
        elif self._vm.get_state() == "input":
            input_request = self._vm.get_state_message()
            method = input_request.method
            limit = input_request.limit
            # TODO: what about EOF?
            if isinstance(limit, int) and limit < 0:
                limit = None
            
            if method == "readline":
                # TODO: is it correct semantics?
                i = 0
                if limit == 0:
                    return ""
                
                while True:
                    if i >= len(input_text):
                        return None
                    elif limit != None and i+1 == limit:
                        return input_text[:i+1]
                    elif input_text[i] == "\n":
                        return input_text[:i+1]
                    else:
                        i += 1
            else:
                raise AssertionError("only readline is supported at the moment")
            
    
                
    
    def _submit_input(self, text_to_be_submitted):
        if self._vm.get_state() == "toplevel":
            log_user_event(ShellCommandEvent(text_to_be_submitted))
            try:
                # if it's a file/script-related command, then editor_book wants to 
                # know about it first
                cmd = parse_shell_command(text_to_be_submitted)
                if cmd.command.lower() in ("run", "debug"):
                    if os.path.isabs(cmd.filename):
                        abs_filename = cmd.filename
                    else:
                        abs_filename = os.path.join(self._vm.cwd, cmd.filename)
                    self._editor_book.enter_execution_mode(abs_filename)
                    
                # register in history and count
                if hasattr(cmd, "cmd_line"):
                    cmd.id = self._command_count
                    self._command_count += 1
                    if cmd.cmd_line in self._command_history:
                        self._command_history.remove(cmd.cmd_line)
                    self._command_history.append(cmd.cmd_line)
                    self._command_history_current_index = None # meaning command selection is not in process
                
                cmd.globals_required = "__main__" # TODO: look what's selected
          
                if prefs["values_in_heap"]:
                    cmd.heap_required = True
                
                if cmd.command[0].isupper(): # this means reset
                    self._invalidate_current_data()
                    
                self._vm.send_command(cmd)
                
            except:
                #raise # TODO:
                self._insert_text_directly("Internal error: " + traceback.format_exc() + "\n", ("toplevel", "error"))
                self._insert_prompt()
        else:
            log_user_event(ShellInputEvent(text_to_be_submitted))
            self._vm.send_program_input(text_to_be_submitted)
    
    
    def change_font_size(self, delta): # TODO: should be elsewhere?
        for f in (ui_utils.IO_FONT, ui_utils.EDITOR_FONT, ui_utils.BOLD_EDITOR_FONT):
            f.configure(size=f.cget("size") + delta)
    
    def focus_set(self):
        self.text.focus()
    
    def is_focused(self):
        return self.focus_displayof() == self.text
    
    def _arrow_up(self, event):
        if not self._in_current_input_range("insert"):
            return
        
        if len(self._command_history) == 0 or self._command_history_current_index == 0:
            # can't take previous command
            return "break"
        
        if self._command_history_current_index == None:
            self._command_history_current_index = len(self._command_history)-1
        else:
            self._command_history_current_index -= 1
        
        self._propose_command(self._command_history[self._command_history_current_index].strip("\n"))
        return "break"
    
    def _arrow_down(self, event):
        if not self._in_current_input_range("insert"):
            return
        
        if (len(self._command_history) == 0 
            or self._command_history_current_index == len(self._command_history)-1):
            # can't take next command
            return "break"
        
        
        if self._command_history_current_index == None:
            self._command_history_current_index = len(self._command_history)-1
        else:
            self._command_history_current_index += 1

        self._propose_command(self._command_history[self._command_history_current_index].strip("\n"))
        return "break"
    
    def _propose_command(self, cmd_line):
        #print(command, self._command_history_current_index, self._command_history)
        self.text.delete("input_start", "end")
        self._user_text_insert("input_start", cmd_line)
    
    def _text_key_press(self, event):
        # TODO: this underline may confuse, when user is just copying on pasting
        # try to add this underline only when mouse is over the value
        """
        if event.keysym in ("Control_L", "Control_R", "Command"):  # TODO: check in Mac
            self.text.tag_configure("value", foreground="DarkBlue", underline=1)
        """
    
    def _text_key_release(self, event):
        if event.keysym in ("Control_L", "Control_R", "Command"):  # TODO: check in Mac
            self.text.tag_configure("value", foreground="DarkBlue", underline=0)
    
    def _invalidate_current_data(self):
        """
        Grayes out input & output displayed so far
        """
        end_index = self.text.index("output_end")
        #print("inva", end_index)
        
        self.text.tag_add("inactive", "1.0", end_index)
        self.text.tag_remove("value", "1.0", end_index)
        
        while len(self.active_object_tags) > 0:
            self.text.tag_remove(self.active_object_tags.pop(), "1.0", "end")
    
    def demo(self):
        TextWrapper._user_text_insert(self, "end", """Python 3.2.3
>>> %run "c:/my documents/kool/prog/katsetus.py"
Sisesta esimene arv: 4
Sisesta teine arv: 6
Nende arvude summa on 10
>>> " kalanaba ".trim()
"kalanaba"
>>>>>> 3 + 4
7
>>> 
""")
        promptfont = font.Font(family='Courier New', size=10, weight="bold")
        self.text.tag_add("prompt", "2.0", "2.4")
        self.text.tag_add("outprompt", "2.0", "2.4")
        self.text.tag_add("prompt", "6.0", "6.4")
        self.text.tag_add("prompt", "8.0", "8.7")
        self.text.tag_add("prompt", "10.0", "10.4")
        self.text.tag_configure("prompt", foreground="purple", 
                                spacing1=12, font=promptfont)
        self.text.tag_configure("outprompt", spacing3=12)
        
        self.text.tag_bind("prompt", "<Enter>", lambda _: self.text.configure(cursor="hand2"))
        self.text.tag_bind("prompt", "<Leave>", lambda _: self.text.configure(cursor="arrow"))
        
        self.text.tag_add("console", "3.0", "6.0")
        #self.text.tag_configure("console", foreground="white", background="#555555", relief=tk.RAISED, lmargin1=20)
        consolefont = font.Font(family='Consolas', size=8, weight="normal", slant="italic")
        self.text.tag_configure("console", lmargin1=16, font=consolefont, foreground="blue")
        
        

    
    """
    def _print_marks(self, prefix=""):
        print(prefix, "input_start is at", self.text.index("input_start"), self.text.mark_gravity("input_start"))
        print(prefix, "output_insert is at", self.text.index("output_insert"), self.text.mark_gravity("output_insert"))
    """
    
    """
    def test_insert(self):
        import random
        for _ in range(10):
            text = repr([random.random() for _ in range(1000)]) + "\n"
            self.text.insert("end", text)
        self.text.see("end")
    
    def test_insert3(self):
        self.text.insert("end", 10000 * (60* "*" + "\n"))
        self.text.see("end")
    
    def test_insert2(self):
        block_mode = False
        for i in range(10000):
            self.text.insert("end", str(i))
            
            if block_mode:
                self.text.insert("end", 60 * "*" + "\n")
            else:
                for _ in range(60):
                    self.text.insert("end", "*")
                self.text.insert("end", "\n")
#            self.text.see("end")
        self.text.see("end")
    """
    
