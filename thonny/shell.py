# -*- coding: utf-8 -*-

import os.path
import re
from tkinter import ttk
import traceback

from thonny import memory
from thonny.common import ToplevelCommand, parse_shell_command
from thonny.misc_utils import running_on_mac_os, shorten_repr
from thonny.ui_utils import TextWrapper
import tkinter as tk
import tkinter.font as font
from thonny.globals import get_workbench, get_runner


class ShellView (ttk.Frame, TextWrapper):

    
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        
        
        self._before_io = True
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
        
        #log_user_event(ShellCreateEvent(self)) TODO:
        
        self.text.grid(row=0, column=1, sticky=tk.NSEW)
        self.text.bind("<Up>", self._arrow_up, "+")
        self.text.bind("<Down>", self._arrow_down, "+")
        self.text.bind("<KeyPress>", self._text_key_press, "+")
        self.text.bind("<KeyRelease>", self._text_key_release, "+")
        self.text.bind("<Home>", self.home_callback)
        self.vert_scrollbar['command'] = self.text.yview
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        TextWrapper.__init__(self)
        
        self.text["font"] = get_workbench().get_font("EditorFont")
        vert_spacing = 10
        io_indent = 16
        
        self.text.tag_configure("toplevel", font=get_workbench().get_font("EditorFont"))
        self.text.tag_configure("prompt", foreground="purple", font=get_workbench().get_font("BoldEditorFont"))
        self.text.tag_configure("command", foreground="black")
        self.text.tag_configure("automagic", foreground="DarkGray")
        #self.text.tag_configure("value", foreground="DarkGreen")
        #self.text.tag_configure("value", foreground="#B25300")
        self.text.tag_configure("value", foreground="DarkBlue") # TODO: see also _text_key_press and _text_key_release
        self.text.tag_configure("error", foreground="Red")
        
        self.text.tag_configure("io", lmargin1=io_indent, lmargin2=io_indent, rmargin=io_indent,
                                font=get_workbench().get_font("IOFont"))
        self.text.tag_configure("stdin", foreground="Blue")
        self.text.tag_configure("stdout", foreground="Black")
        self.text.tag_configure("stderr", foreground="Red")
        self.text.tag_configure("hyperlink", foreground="#3A66DD", underline=True)
        self.text.tag_bind("hyperlink", "<ButtonRelease-1>", self._handle_hyperlink)
        self.text.tag_bind("hyperlink", "<Enter>", self._hyperlink_enter)
        self.text.tag_bind("hyperlink", "<Leave>", self._hyperlink_leave)
        
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
        
        self._command_handlers = {}
    
        get_workbench().bind("InputRequest", self._handle_input_request, True)
        get_workbench().bind("ProgramOutput", self._handle_program_output, True)
        get_workbench().bind("ToplevelResult", self._handle_toplevel_result, True)
        

        
        

    def _handle_input_request(self, msg):
        self.text_mode = "io"
        self.text["font"] = get_workbench().get_font("IOFont") # otherwise the cursor is of toplevel size
        self.text.focus_set()
        self.text.mark_set("insert", "end")
        self.text.tag_remove("sel", "1.0", tk.END)
        self._current_input_request = msg
        self._try_submit_input() # try to use leftovers from previous request
        self.text.see("end")

    def _handle_program_output(self, msg):
        self.text_mode = "io"
        self.text["font"] = get_workbench().get_font("IOFont")
        
        # mark first line of io
        if self._before_io:
            self._insert_text_directly(msg.data[0], ("io", msg.stream_name, "vertically_spaced"))
            self._before_io = False
            self._insert_text_directly(msg.data[1:], ("io", msg.stream_name))
        else:
            self._insert_text_directly(msg.data, ("io", msg.stream_name))
        
        self.text.mark_set("output_end", self.text.index("end-1c"))
        self.text.see("end")
            
    def _handle_toplevel_result(self, msg):
        self.text_mode = "toplevel"
        self.text["font"] = get_workbench().get_font("EditorFont")
        self._before_io = True
        if hasattr(msg, "error"):
            self._insert_text_directly(msg.error + "\n", ("toplevel", "error"))
            
        if hasattr(msg, "value_info"):
            value_repr = shorten_repr(msg.value_info.repr, 10000)
            if value_repr != "None":
                if get_workbench().in_heap_mode():
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
                                   lambda _: get_workbench().event_generate(
                                        "ObjectSelect", object_id=msg.value_info.id))
                
                self.active_object_tags.add(object_tag)
        
        self.text.mark_set("output_end", self.text.index("end-1c"))
        self._insert_prompt()
        self._try_submit_input()
        self.text.see("end")
            
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
    
    
    
    def add_command(self, command, handler):
        self._command_handlers[command] = handler
        
    def submit_command(self, cmd_line):
        assert self._get_state() == "waiting_toplevel_command"
        self.text.delete("input_start", "end")
        self.text.insert("input_start", cmd_line, ("automagic",))
        self.text.see("end")
    
    def _get_state(self):
        return get_runner().get_state()
        
    def _user_text_insert(self, index, txt, tags=(), **kw):
        if (self._editing_allowed()
            and self._in_current_input_range(index)):
            #self._print_marks("before insert")
            # I want all marks to stay in place
            self.text.mark_gravity("input_start", tk.LEFT)
            self.text.mark_gravity("output_insert", tk.LEFT)
            
            if self._get_state() == "waiting_input":
                tags = tags + ("io", "stdin")
            else:
                tags = tags + ("toplevel", "command")
            
            # when going back and fixing in the middle of command and pressing ENTER there
            if txt == "\n":
                self.text.mark_set("insert", "insert lineend")
                index = "insert"
                
            TextWrapper._user_text_insert(self, index, txt, tags, **kw)
            
            # tag first char of io separately
            if self._get_state() == "waiting_input" and self._before_io:
                self.text.tag_add("vertically_spaced", index)
                self._before_io = False
            
            self._try_submit_input()
        else:
            self.bell()
            
    def _user_text_delete(self, index1, index2=None, **kw):
        if (self._editing_allowed() 
            and self._in_current_input_range(index1)
            and (index2 is None or self._in_current_input_range(index2))):
            TextWrapper._user_text_delete(self, index1, index2, **kw)
        else:
            self.bell()
    
    def _in_current_input_range(self, index):
        return self.text.compare(index, ">=", "input_start")
    
    def _insert_text_directly(self, txt, tags=()):
        # I want the insertion to go before marks 
        #self._print_marks("before output")
        self.text.mark_gravity("input_start", tk.RIGHT)
        self.text.mark_gravity("output_insert", tk.RIGHT)
        tags = tuple(tags)
        
        if "stderr" in tags or "error" in tags:
            # show lines pointing to source lines as hyperlinks
            for line in txt.splitlines(True):
                parts = re.split(r'(File .* line \d+.*)$', line, maxsplit=1)
                if len(parts) == 3 and "<pyshell" not in line:
                    self._insert_text_drctly(parts[0], tags)
                    self._insert_text_drctly(parts[1], tags + ("hyperlink",))
                    self._insert_text_drctly(parts[2], tags)
                else:
                    self._insert_text_drctly(line, tags)
        else:
            self._insert_text_drctly(txt, tags)
            
        #self._print_marks("after output")
        # output_insert mark will move automatically because of its gravity
    
    def _insert_text_drctly(self, txt, tags):
        if txt != "":
            TextWrapper._user_text_insert(self, "output_insert", txt, tags)
    
    def _try_submit_input(self):
        # see if there is already enough inputted text to submit
        input_text = self.text.get("input_start", "end-1c")
        submittable_text = self._extract_submittable_input(input_text)
        
        if submittable_text is not None:
            # user may have pasted more text than necessary for this request
            # leftover text will be kept in widget, waiting for next request.
            start_index = self.text.index("input_start")
            end_index = self.text.index("input_start+{0}c".format(len(submittable_text)))
            # apply correct tags (if it's leftover then it doesn't have them yet)
            if self._get_state() == "waiting_input":
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
        return self._get_state() in ('waiting_toplevel_command', 'waiting_input')
    
    def _extract_submittable_input(self, input_text):
        
        if self._get_state() == "waiting_toplevel_command":
            # TODO: support also multiline commands
            if "\n" in input_text:
                return input_text[:input_text.index("\n")+1]
            else:
                return None
        elif self._get_state() == "waiting_input":
            input_request = self._current_input_request
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
                    elif limit is not None and i+1 == limit:
                        return input_text[:i+1]
                    elif input_text[i] == "\n":
                        return input_text[:i+1]
                    else:
                        i += 1
            else:
                raise AssertionError("only readline is supported at the moment")
            
    
    
    def _submit_input(self, text_to_be_submitted):
        if self._get_state() == "waiting_toplevel_command":
            # register in history and count
            if text_to_be_submitted in self._command_history:
                self._command_history.remove(text_to_be_submitted)
            self._command_history.append(text_to_be_submitted)
            self._command_history_current_index = None # meaning command selection is not in process
            
            try:
                if text_to_be_submitted.startswith("%"):
                    command, _ = parse_shell_command(text_to_be_submitted)
                    if command in self._command_handlers:
                        self._command_handlers[command](text_to_be_submitted)
                    else:
                        self._insert_text_directly("Unknown magic command: " + command)
                        self._insert_prompt()
                else:
                    get_runner().send_command(
                        ToplevelCommand(command="python",
                                        cmd_line=text_to_be_submitted))
                
            except:
                #raise # TODO:
                get_workbench().report_exception()
                self._insert_prompt()
                
            get_workbench().event_generate("ShellCommand", command_text=text_to_be_submitted)
        else:
            get_runner().send_program_input(text_to_be_submitted)
            get_workbench().event_generate("ShellInput", input_text=text_to_be_submitted)
    
    
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
        
        if self._command_history_current_index is None:
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
        
        
        if self._command_history_current_index is None:
            self._command_history_current_index = len(self._command_history)-1
        else:
            self._command_history_current_index += 1

        self._propose_command(self._command_history[self._command_history_current_index].strip("\n"))
        return "break"
    
    def _propose_command(self, cmd_line):
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
    
    def home_callback(self, event):
        if self._in_current_input_range("insert"):
            # on input line, go to just after prompt
            self.text.mark_set("insert", "input_start")
            return "break"
    
    def _hyperlink_enter(self, event):
        self.text.config(cursor="hand2")
        
    def _hyperlink_leave(self, event):
        self.text.config(cursor="")
        
    def _handle_hyperlink(self, event):
        try:
            line = self.text.get("insert linestart", "insert lineend")
            matches = re.findall(r'File "([^"]+)", line (\d+)', line)
            if len(matches) == 1 and len(matches[0]) == 2:
                filename, lineno = matches[0]
                lineno = int(lineno)
                if os.path.exists(filename) and os.path.isfile(filename):
                    # TODO: better use events instead direct referencing
                    get_workbench().get_editor_notebook().show_file(filename, lineno)
        except:
            traceback.print_exc()
    
    
    def _invalidate_current_data(self):
        """
        Grayes out input & output displayed so far
        """
        end_index = self.text.index("output_end")
        
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
        
        

    

    
    