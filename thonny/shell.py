# -*- coding: utf-8 -*-

import os.path
import re
from tkinter import ttk
import traceback

from thonny import memory, roughparse
from thonny.common import ToplevelCommand, parse_shell_command
from thonny.misc_utils import running_on_mac_os, shorten_repr
from thonny.ui_utils import EnhancedTextWithLogging
import tkinter as tk
from thonny.globals import get_workbench, get_runner
from thonny.codeview import EDIT_BACKGROUND, PythonText
from thonny.tktextext import index2line


class ShellView (ttk.Frame):
    def __init__(self, master, **kw):
        ttk.Frame.__init__(self, master, **kw)
        
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vert_scrollbar.grid(row=0, column=2, sticky=tk.NSEW)
        self.text = ShellText(self,
                            font=get_workbench().get_font("EditorFont"),
                            #foreground="white",
                            #background="#666666",
                            highlightthickness=0,
                            #highlightcolor="LightBlue",
                            borderwidth=0,
                            yscrollcommand=self.vert_scrollbar.set,
                            padx=4,
                            insertwidth=2,
                            height=10,
                            undo=True)
        
        get_workbench().event_generate("ShellTextCreated", text_widget=self.text)
        get_workbench().add_command("clear_shell", "edit", "Clear shell",
                                    self.clear_shell,
                                    group=200)
        
        self.text.grid(row=0, column=1, sticky=tk.NSEW)
        self.vert_scrollbar['command'] = self.text.yview
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def focus_set(self):
        self.text.focus_set()
    
    def add_command(self, command, handler):
        self.text.add_command(command, handler)

    def submit_command(self, cmd_line):
        self.text.submit_command(cmd_line)
    
    def clear_shell(self):
        self.text._clear_shell()


class ShellText(EnhancedTextWithLogging, PythonText):
    
    def __init__(self, master, cnf={}, **kw):
        if not "background" in kw:
            kw["background"] = EDIT_BACKGROUND
            
        EnhancedTextWithLogging.__init__(self, master, cnf, **kw)
        self.bindtags(self.bindtags() + ('ShellText',))
        
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
        
        self.bind("<Up>", self._arrow_up, True)
        self.bind("<Down>", self._arrow_down, True)
        self.bind("<KeyPress>", self._text_key_press, True)
        self.bind("<KeyRelease>", self._text_key_release, True)
        
        prompt_font = get_workbench().get_font("BoldEditorFont")
        vert_spacing = 10
        io_indent = 16
        code_indent = prompt_font.measure(">>> ")
        
        
        self.tag_configure("toplevel", font=get_workbench().get_font("EditorFont"))
        self.tag_configure("prompt", foreground="purple", font=prompt_font)
        self.tag_configure("command", foreground="black",
                           lmargin1=code_indent, lmargin2=code_indent)
        self.tag_configure("welcome", foreground="DarkGray")
        self.tag_configure("automagic", foreground="DarkGray")
        #self.tag_configure("value", foreground="DarkGreen")
        #self.tag_configure("value", foreground="#B25300")
        self.tag_configure("value", foreground="DarkBlue") # TODO: see also _text_key_press and _text_key_release
        self.tag_configure("error", foreground="Red")
        
        self.tag_configure("io", lmargin1=io_indent, lmargin2=io_indent, rmargin=io_indent,
                                font=get_workbench().get_font("IOFont"))
        self.tag_configure("stdin", foreground="Blue")
        self.tag_configure("stdout", foreground="Black")
        self.tag_configure("stderr", foreground="Red")
        self.tag_configure("hyperlink", foreground="#3A66DD", underline=True)
        self.tag_bind("hyperlink", "<ButtonRelease-1>", self._handle_hyperlink)
        self.tag_bind("hyperlink", "<Enter>", self._hyperlink_enter)
        self.tag_bind("hyperlink", "<Leave>", self._hyperlink_leave)
        
        self.tag_configure("vertically_spaced", spacing1=vert_spacing)
        self.tag_configure("inactive", foreground="#aaaaaa")
        
        # create 3 marks: input_start shows the place where user entered but not-yet-submitted
        # input starts, output_end shows the end of last output,
        # output_insert shows where next incoming program output should be inserted
        self.mark_set("input_start", "end-1c")
        self.mark_gravity("input_start", tk.LEFT)
        
        self.mark_set("output_end", "end-1c")
        self.mark_gravity("output_end", tk.LEFT)
        
        self.mark_set("output_insert", "end-1c")
        self.mark_gravity("output_insert", tk.RIGHT)
        
        
        self.active_object_tags = set()
        
        self._command_handlers = {}
        
        self._last_configuration = None
    
        get_workbench().bind("InputRequest", self._handle_input_request, True)
        get_workbench().bind("ProgramOutput", self._handle_program_output, True)
        get_workbench().bind("ToplevelResult", self._handle_toplevel_result, True)
        
        self._init_menu()
    
    def _init_menu(self):
        self._menu = tk.Menu(self, tearoff=False)
        self._menu.add_command(label="Clear shell", command=self._clear_shell)
    
    def add_command(self, command, handler):
        self._command_handlers[command] = handler
        
    def submit_command(self, cmd_line):
        assert get_runner().get_state() == "waiting_toplevel_command"
        self.delete("input_start", "end")
        self.insert("input_start", cmd_line, ("automagic",))
        self.see("end")
        self._try_submit_input()
    
    def _handle_input_request(self, msg):
        self.text_mode = "io"
        self["font"] = get_workbench().get_font("IOFont") # otherwise the cursor is of toplevel size
        self.focus_set()
        self.mark_set("insert", "end")
        self.tag_remove("sel", "1.0", tk.END)
        self._current_input_request = msg
        self._try_submit_input() # try to use leftovers from previous request
        self.see("end")

    def _handle_program_output(self, msg):
        self.text_mode = "io"
        self["font"] = get_workbench().get_font("IOFont")
        
        # mark first line of io
        if self._before_io:
            self._insert_text_directly(msg.data[0], ("io", msg.stream_name, "vertically_spaced"))
            self._before_io = False
            self._insert_text_directly(msg.data[1:], ("io", msg.stream_name))
        else:
            self._insert_text_directly(msg.data, ("io", msg.stream_name))
        
        self.mark_set("output_end", self.index("end-1c"))
        self.see("end")
            
    def _handle_toplevel_result(self, msg):
        self.text_mode = "toplevel"
        self["font"] = get_workbench().get_font("EditorFont")
        self._before_io = True
        if hasattr(msg, "error"):
            self._insert_text_directly(msg.error + "\n", ("toplevel", "error"))
        
        if hasattr(msg, "welcome_text"):
            configuration = get_workbench().get_option("run.backend_configuration") 
            
            if (configuration != self._last_configuration
                and not (self._last_configuration is None and not configuration)):
                    self._insert_text_directly(msg.welcome_text, ("welcome",))
                    
            self._last_configuration = get_workbench().get_option("run.backend_configuration")
            
        
        if hasattr(msg, "value_info"):
            value_repr = shorten_repr(msg.value_info["repr"], 10000)
            if value_repr != "None":
                if get_workbench().in_heap_mode():
                    value_repr = memory.format_object_id(msg.value_info["id"])
                object_tag = "object_" + str(msg.value_info["id"])
                self._insert_text_directly(value_repr + "\n", ("toplevel",
                                                               "value",
                                                               object_tag))
                if running_on_mac_os():
                    sequence = "<Command-Button-1>"
                else:
                    sequence = "<Control-Button-1>"
                self.tag_bind(object_tag, sequence,
                                   lambda _: get_workbench().event_generate(
                                        "ObjectSelect", object_id=msg.value_info["id"]))
                
                self.active_object_tags.add(object_tag)
        
        self.mark_set("output_end", self.index("end-1c"))
        self._insert_prompt()
        self._try_submit_input() # Trying to submit leftover code (eg. second magic command)
        self.see("end")
            
    def _insert_prompt(self):
        # if previous output didn't put a newline, then do it now
        if not self.index("output_insert").endswith(".0"):
            # TODO: show a symbol indicating unfinished line
            self._insert_text_directly("\n", ("io",))
        
        prompt_tags = ("toplevel", "prompt")
         
        # if previous line has value or io then add little space
        prev_line = self.index("output_insert - 1 lines")
        prev_line_tags = self.tag_names(prev_line)
        if "io" in prev_line_tags or "value" in prev_line_tags:
            prompt_tags += ("vertically_spaced",)
            #self.tag_add("last_result_line", prev_line)
        
        self._insert_text_directly(">>> ", prompt_tags)
        self.edit_reset();
    
    def intercept_insert(self, index, txt, tags=()):
        if (self._editing_allowed()
            and self._in_current_input_range(index)):
            #self._print_marks("before insert")
            # I want all marks to stay in place
            self.mark_gravity("input_start", tk.LEFT)
            self.mark_gravity("output_insert", tk.LEFT)
            
            if get_runner().get_state() == "waiting_input":
                tags = tags + ("io", "stdin")
            else:
                tags = tags + ("toplevel", "command")
            
            super().intercept_insert(index, txt, tags)
            
            # tag first char of io separately
            if get_runner().get_state() == "waiting_input" and self._before_io:
                self.tag_add("vertically_spaced", index)
                self._before_io = False
                self._try_submit_input()
            
            self.see("insert")
        else:
            self.bell()
            
    def intercept_delete(self, index1, index2=None, **kw):
        if (self._editing_allowed() 
            and self._in_current_input_range(index1)
            and (index2 is None or self._in_current_input_range(index2))):
            self.direct_delete(index1, index2, **kw)
        else:
            self.bell()
    
    def perform_return(self, event):
        # if we are fixing the middle of single-line command and pressing ENTER 
        # then we expect the command to be submitted not linebreak to be inserted
        # (at least that's how IDLE works)
        source = self.get("input_start", "end-1c")
        if (get_runner().get_state() == "waiting_toplevel_command"
            and "\n" not in source
            and self._code_is_ready_for_submission(source)):
            self.mark_set("insert", "end") # move cursor 
                                       
        PythonText.perform_return(self, event)
        self._try_submit_input()
        return "break"
    
    def on_secondary_click(self, event):
        super().on_secondary_click(event)
        self._menu.tk_popup(event.x_root, event.y_root)
        
    def _in_current_input_range(self, index):
        try:
            return self.compare(index, ">=", "input_start")
        except:
            return False
    
    def _insert_text_directly(self, txt, tags=()):
        # I want the insertion to go before marks 
        #self._print_marks("before output")
        self.mark_gravity("input_start", tk.RIGHT)
        self.mark_gravity("output_insert", tk.RIGHT)
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
            self.direct_insert("output_insert", txt, tags)
    
    def _try_submit_input(self):
        # see if there is already enough inputted text to submit
        input_text = self.get("input_start", "end-1c")
        
        # user may have pasted more text than necessary for this request
        submittable_text = self._extract_submittable_input(input_text)
        
        if submittable_text is not None:
            # make sure submittable text ends with newline
            # (auto indenter may have put something more there)
            
            
            # leftover text will be kept in widget, waiting for next request.
            start_index = self.index("input_start")
            end_index = self.index("input_start+{0}c".format(len(submittable_text)))
            
            # apply correct tags (if it's leftover then it doesn't have them yet)
            if get_runner().get_state() == "waiting_input":
                self.tag_add("io", start_index, end_index)
                self.tag_add("stdin", start_index, end_index)
            else:
                self.tag_add("toplevel", start_index, end_index)
                self.tag_add("command", start_index, end_index)
                
            
            
            # update start mark for next input range
            self.mark_set("input_start", end_index)
            
            # Move output_insert mark after the requested_text
            # Leftover input, if any, will stay after output_insert, 
            # so that any output that will come in before
            # next input request will go before leftover text
            self.mark_set("output_insert", end_index)
            
            # remove tags from leftover text
            for tag in ("io", "stdin", "toplevel", "command"):
                # don't remove automagic, because otherwise I can't know it's auto 
                self.tag_remove(tag, end_index, "end")
                
            self._submit_input(submittable_text)
            # tidy up the tags
            #self.tag_remove("pending_input", "1.0", "end")
            #self.tag_add("submitted_input", start_index, end_index)
            #self.tag_add("pending_input", end_index, "end-1c")
    
    def _editing_allowed(self):
        return get_runner().get_state() in ('waiting_toplevel_command', 'waiting_input')
    
    def _extract_submittable_input(self, input_text):
        
        if get_runner().get_state() == "waiting_toplevel_command":
            if input_text.endswith("\n"):
                if input_text.strip().startswith("%"):
                    # if several magic command are submitted, then take only first
                    return input_text[:input_text.index("\n")+1]
                elif self._code_is_ready_for_submission(input_text):
                    return input_text
                else:
                    return None
            else:
                return None
            
        elif get_runner().get_state() == "waiting_input":
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
    
    def _code_is_ready_for_submission(self, source):
        # Ready to submit if ends with empty line 
        # or is complete single-line code
        
        # First check if it has unclosed parens, unclosed string or ending with : or \
        parser = roughparse.RoughParser(self.indentwidth, self.tabwidth)
        parser.set_str(source.rstrip() + "\n")
        if (parser.get_continuation_type() != roughparse.C_NONE
                or parser.is_block_opener()):
            return None
        
        # Multiline compound statements need to end with empty line to be considered
        # complete.
        lines = source.splitlines()
        # strip starting empty and comment lines
        while (len(lines) > 0
               and (lines[0].strip().startswith("#")
                    or lines[0].strip() == "")):
            lines.pop(0)
        
        compound_keywords = ["if", "while", "for", "with", "try", "def", "class", "async", "await"]
        if len(lines) > 0:
            first_word = lines[0].strip().split()[0]
            if (first_word in compound_keywords
                and lines[-1].strip() != ""):
                # last line is not empty
                return None
        
        # Not compound statement
        return source
    
    def _submit_input(self, text_to_be_submitted):
        if get_runner().get_state() == "waiting_toplevel_command":
            # register in history and count
            if text_to_be_submitted in self._command_history:
                self._command_history.remove(text_to_be_submitted)
            self._command_history.append(text_to_be_submitted)
            self._command_history_current_index = None # meaning command selection is not in process
            
            try:
                if text_to_be_submitted.startswith("%"):
                    command, _ = parse_shell_command(text_to_be_submitted)
                    get_workbench().event_generate("MagicCommand", cmd_line=text_to_be_submitted)
                    if command in self._command_handlers:
                        self._command_handlers[command](text_to_be_submitted)
                        get_workbench().event_generate("AfterKnownMagicCommand", cmd_line=text_to_be_submitted)
                    else:
                        self._insert_text_directly("Unknown magic command: " + command)
                        self._insert_prompt()
                else:
                    get_runner().send_command(
                        ToplevelCommand(command="execute_source",
                                        source=text_to_be_submitted))
                
            except:
                #raise # TODO:
                get_workbench().report_exception()
                self._insert_prompt()
                
            get_workbench().event_generate("ShellCommand", command_text=text_to_be_submitted)
        else:
            assert get_runner().get_state() == "waiting_input"
            get_runner().send_program_input(text_to_be_submitted)
            get_workbench().event_generate("ShellInput", input_text=text_to_be_submitted)
    
    
    def _arrow_up(self, event):
        if not self._in_current_input_range("insert"):
            return

        insert_line = index2line(self.index("insert"))
        input_start_line = index2line(self.index("input_start"))
        if insert_line != input_start_line:
            # we're in the middle of a multiline command
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
        
        insert_line = index2line(self.index("insert"))
        last_line = index2line(self.index("end-1c"))
        if insert_line != last_line:
            # we're in the middle of a multiline command
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
        self.delete("input_start", "end")
        self.intercept_insert("input_start", cmd_line)
        self.see("insert")
    
    def _text_key_press(self, event):
        # TODO: this underline may confuse, when user is just copying on pasting
        # try to add this underline only when mouse is over the value
        """
        if event.keysym in ("Control_L", "Control_R", "Command"):  # TODO: check in Mac
            self.tag_configure("value", foreground="DarkBlue", underline=1)
        """
    
    def _text_key_release(self, event):
        if event.keysym in ("Control_L", "Control_R", "Command"):  # TODO: check in Mac
            self.tag_configure("value", foreground="DarkBlue", underline=0)

    def _clear_shell(self):
        end_index = self.index("output_end")
        self.direct_delete("1.0", end_index)

    def should_indent_after_empty_line(self):
        return False

    def compute_smart_home_destination_index(self):
        """Is used by EnhancedText"""
        
        if self._in_current_input_range("insert"):
            # on input line, go to just after prompt
            return "input_start"
        else:
            return super().compute_smart_home_destination_index()
    
    def _hyperlink_enter(self, event):
        self.config(cursor="hand2")
        
    def _hyperlink_leave(self, event):
        self.config(cursor="")
        
    def _handle_hyperlink(self, event):
        try:
            line = self.get("insert linestart", "insert lineend")
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
        end_index = self.index("output_end")
        
        self.tag_add("inactive", "1.0", end_index)
        self.tag_remove("value", "1.0", end_index)
        
        while len(self.active_object_tags) > 0:
            self.tag_remove(self.active_object_tags.pop(), "1.0", "end")
        
        

    

    
    