# -*- coding: utf-8 -*-

import logging
import os.path
import re
import tkinter as tk
import traceback
from tkinter import ttk

from thonny import get_runner, get_workbench, memory, roughparse, ui_utils
from thonny.codeview import PythonText, get_syntax_options_for_tag
from thonny.common import InlineCommand, ToplevelCommand, ToplevelResponse
from thonny.misc_utils import (
    construct_cmd_line,
    parse_cmd_line,
    running_on_mac_os,
    shorten_repr,
)
from thonny.tktextext import index2line, TextFrame, TweakableText
from thonny.ui_utils import (
    EnhancedTextWithLogging,
    scrollbar_style,
    select_sequence, TextMenu, create_tooltip, show_dialog)
from _tkinter import TclError

_CLEAR_SHELL_DEFAULT_SEQ = select_sequence("<Control-l>", "<Command-k>")

# NB! Don't add parens without refactoring split procedure!
OUTPUT_SPLIT_REGEX = re.compile(r'(\x1B\[[0-?]*[ -/]*[@-~]|[\b\r])')

INT_REGEX = re.compile(r"\d+")
ANSI_COLOR_NAMES = {
    "0" : "black",
    "1" : "red",
    "2" : "green",
    "3" : "yellow",
    "4" : "blue",
    "5" : "magenta",
    "6" : "cyan",
    "7" : "white",
    "9" : "default",
}


class ShellView(ttk.Frame):
    def __init__(self, master, **kw):
        ttk.Frame.__init__(self, master, **kw)

        self.vert_scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, style=scrollbar_style("Vertical")
        )
        self.vert_scrollbar.grid(row=1, column=2, sticky=tk.NSEW)
        get_workbench().add_command(
            "clear_shell",
            "edit",
            "Clear shell",
            self.clear_shell,
            default_sequence=_CLEAR_SHELL_DEFAULT_SEQ,
            group=200,
        )
        
        get_workbench().set_default("shell.max_lines", 1000)
        get_workbench().set_default("shell.squeeze_threshold", 1000)

        self.text = ShellText(
            self,
            font="EditorFont",
            # foreground="white",
            # background="#666666",
            highlightthickness=0,
            # highlightcolor="LightBlue",
            borderwidth=0,
            yscrollcommand=self.vert_scrollbar.set,
            padx=4,
            insertwidth=2,
            height=10,
            undo=True,
        )

        get_workbench().event_generate("ShellTextCreated", text_widget=self.text)

        self.text.grid(row=1, column=1, sticky=tk.NSEW)
        self.vert_scrollbar["command"] = self.text.yview
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.notice = ttk.Label(self, text="", background="#ffff99", padding=3)

    def set_notice(self, text):
        if text is None:
            self.notice.grid_forget()
        else:
            self.notice["text"] = text
            if not self.notice.winfo_ismapped():
                self.notice.grid(
                    row=0, column=1, columnspan=2, sticky="nsew", pady=(0, 1)
                )
                # height of the text was reduced so adjust the scrolling
                # self.update()
                self.text.see("end")

    def focus_set(self):
        self.text.focus_set()

    def submit_python_code(self, cmd_line):
        self.text.submit_command(cmd_line, ())

    def submit_magic_command(self, cmd_line):
        if isinstance(cmd_line, list):
            cmd_line = construct_cmd_line(cmd_line)

        if not cmd_line.endswith("\n"):
            cmd_line += "\n"

        self.text.submit_command(cmd_line, ("magic",))

    def restart(self):
        self.text.restart()

    def clear_shell(self):
        self.text._clear_shell()

    def report_exception(self, prelude=None, conclusion=None):
        if prelude is not None:
            self.text.direct_insert("end", prelude + "\n", ("stderr",))

        self.text.direct_insert("end", traceback.format_exc() + "\n", ("stderr",))

        if conclusion is not None:
            self.text.direct_insert("end", conclusion + "\n", ("stderr",))

class ShellMenu(TextMenu):
    def add_extra_items(self):
        self.add_separator()
        self.add_command(label="Clear", command=self.text._clear_shell)
        
    def selection_is_read_only(self):
        return not self.text.selection_is_writable()

class ShellText(EnhancedTextWithLogging, PythonText):
    def __init__(self, master, cnf={}, **kw):

        super().__init__(master, cnf, **kw)
        self.bindtags(self.bindtags() + ("ShellText",))

        self._command_history = (
            []
        )  # actually not really history, because each command occurs only once
        self._command_history_current_index = None
        
        # logs of IO events for current toplevel block
        # (enables undoing and redoing the events)
        self._applied_io_events = []
        self._queued_io_events = []
        
        self._ansi_foreground = None
        self._ansi_background = None
        self._ansi_inverse = False
        self._ansi_intensity = None
        self._ansi_italic = False
        self._ansi_underline = False
        self._ansi_conceal = False
        self._ansi_strikethrough = False
        self._io_cursor_offset = 0
        self._squeeze_buttons = set()
        
        self.bind("<Up>", self._arrow_up, True)
        self.bind("<Down>", self._arrow_down, True)
        self.bind("<KeyPress>", self._text_key_press, True)
        self.bind("<KeyRelease>", self._text_key_release, True)

        prompt_font = tk.font.nametofont("BoldEditorFont")
        io_vert_spacing = 10
        io_indent = 16
        code_indent = prompt_font.measure(">>> ")

        self.tag_configure("command", lmargin1=code_indent, lmargin2=code_indent)
        self.tag_configure(
            "io",
            lmargin1=io_indent,
            lmargin2=io_indent,
            rmargin=io_indent,
            font="IOFont",
        )
        if ui_utils.get_tk_version_info() >= (8, 6, 6):
            self.tag_configure(
                "io", lmargincolor=get_syntax_options_for_tag("TEXT")["background"]
            )

        self.tag_bind("hyperlink", "<ButtonRelease-1>", self._handle_hyperlink)
        self.tag_bind("hyperlink", "<Enter>", self._hyperlink_enter)
        self.tag_bind("hyperlink", "<Leave>", self._hyperlink_leave)
        self.tag_raise("hyperlink")

        self.tag_configure("after_io_or_value", spacing1=io_vert_spacing)
        self.tag_configure("before_io", spacing3=io_vert_spacing)
        
        # Underline on font looks better than underline on tag
        io_hyperlink_font = tk.font.nametofont("IOFont").copy()
        io_hyperlink_font.configure(underline=get_syntax_options_for_tag("hyperlink").get("underline", True))
        self.tag_configure("io_hyperlink", 
                           underline=False,
                           font=io_hyperlink_font)
        self.tag_raise("io_hyperlink", "hyperlink")

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

        self._last_welcome_text = None

        get_workbench().bind("InputRequest", self._handle_input_request, True)
        get_workbench().bind("ProgramOutput", self._handle_program_output, True)
        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)
        get_workbench().bind(
            "DebuggerResponse", self._handle_fancy_debugger_progress, True
        )

        self._menu = ShellMenu(self)
        
        self.tag_raise("underline")
        self.tag_raise("strikethrough")
        self.tag_raise("intense_io")
        self.tag_raise("italic_io")
        self.tag_raise("intense_italic_io")
        self.tag_raise("sel")
        

    def submit_command(self, cmd_line, tags):
        assert get_runner().is_waiting_toplevel_command()
        self.delete("input_start", "end")
        self.insert("input_start", cmd_line, tags)
        self.see("end")
        self.mark_set("insert", "end")
        self._try_submit_input()

    def _handle_input_request(self, msg):
        self._ensure_visible()
        self.focus_set()
        self.mark_set("insert", "end")
        self.tag_remove("sel", "1.0", tk.END)
        self._try_submit_input()  # try to use leftovers from previous request
        self.see("end")

    def _handle_program_output(self, msg):
        self._ensure_visible()
        self._append_to_io_queue(msg.data, msg.stream_name)
        
        if not self._applied_io_events:
            # this is first line of io, add padding below command line
            self.tag_add("before_io", "output_insert -1 line linestart") 
            
        self._update_visible_io(None)

    def _handle_toplevel_response(self, msg: ToplevelResponse) -> None:
        if msg.get("error"):
            self._insert_text_directly(msg["error"] + "\n", ("toplevel", "stderr"))
            self._ensure_visible()

        if "user_exception" in msg:
            self._show_user_exception(msg["user_exception"])
            self._ensure_visible()

        welcome_text = msg.get("welcome_text")
        if welcome_text and welcome_text != self._last_welcome_text:
            self._insert_text_directly(welcome_text, ("comment",))
            self._last_welcome_text = welcome_text

        if "value_info" in msg:
            num_stripped_question_marks = getattr(msg, "num_stripped_question_marks", 0)
            if num_stripped_question_marks > 0:
                # show the value in object inspector
                get_workbench().event_generate(
                    "ObjectSelect", object_id=msg["value_info"].id
                )
            else:
                # show the value in shell
                value_repr = shorten_repr(msg["value_info"].repr, 10000)
                if value_repr != "None":
                    if get_workbench().in_heap_mode():
                        value_repr = memory.format_object_id(msg["value_info"].id)
                    object_tag = "object_" + str(msg["value_info"].id)
                    self._insert_text_directly(
                        value_repr + "\n", ("toplevel", "value", object_tag)
                    )
                    if running_on_mac_os():
                        sequence = "<Command-Button-1>"
                    else:
                        sequence = "<Control-Button-1>"
                    self.tag_bind(
                        object_tag,
                        sequence,
                        lambda _: get_workbench().event_generate(
                            "ObjectSelect", object_id=msg["value_info"].id
                        ),
                    )

                    self.active_object_tags.add(object_tag)

        self.mark_set("output_end", self.index("end-1c"))
        self._discard_old_content()
        self._update_visible_io(None)
        self._reset_ansi_attributes()
        self._io_cursor_offset = 0
        self._insert_prompt()
        self._try_submit_input()  # Trying to submit leftover code (eg. second magic command)
        self.see("end")
        
        #import os
        #import psutil
        #process = psutil.Process(os.getpid())
        #print("MEM", process.memory_info().rss // (1024*1024))          

    def _handle_fancy_debugger_progress(self, msg):
        if msg.in_present or msg.io_symbol_count is None:
            self._update_visible_io(None)
        else:
            self._update_visible_io(msg.io_symbol_count)
    
    def _get_squeeze_threshold(self):
        return get_workbench().get_option("shell.squeeze_threshold")
    
    def _append_to_io_queue(self, data, stream_name):
        # Make sure ANSI CSI codes are stored as separate events
        # TODO: try to complete previously submitted incomplete code
        
        parts = re.split(OUTPUT_SPLIT_REGEX, data)
        for part in parts:
            if part: # split may produce empty string in the beginning or start
                # split the data so that very long lines separated
                for block in re.split("(.{%d,})" % (self._get_squeeze_threshold() + 1), part):
                    if block:
                        self._queued_io_events.append((block, stream_name))
    
    def _update_visible_io(self, target_num_visible_chars):
        current_num_visible_chars = sum(map(lambda x: len(x[0]), self._applied_io_events))
        
        if (target_num_visible_chars is not None
            and target_num_visible_chars < current_num_visible_chars):
            # hard to undo complex renderings (squeezed texts and ANSI codes)
            # easier to clean everything and start again
            self._queued_io_events = self._applied_io_events + self._queued_io_events
            self._applied_io_events = []
            self.direct_delete("command_io_start", "output_end")
            current_num_visible_chars = 0
            self._reset_ansi_attributes()
        
        
        while (self._queued_io_events
               and current_num_visible_chars != target_num_visible_chars):
            data, stream_name = self._queued_io_events.pop(0)
            
            if target_num_visible_chars is not None:
                leftover_count = current_num_visible_chars + len(data) - target_num_visible_chars 
             
                if leftover_count > 0:
                    # add suffix to the queue
                    self._queued_io_events.insert(0, (data[-leftover_count:], stream_name))
                    data = data[:-leftover_count]
        
            self._apply_io_event(data, stream_name)
            current_num_visible_chars += len(data)
    
        self.mark_set("output_end", self.index("end-1c"))
        self.see("end")
    
    def _apply_io_event(self, data, stream_name, extra_tags=set()):
        if not data:
            return
        
        original_data = data
        
        if re.match(OUTPUT_SPLIT_REGEX, data):
            if data == "\b":
                self._change_io_cursor_offset(-1)
            elif data == "\r":
                self._change_io_cursor_offset("line")
            elif data.endswith("D") or data.endswith("C"):
                self._change_io_cursor_offset_csi(data) 
            elif stream_name == "stdout":
                # According to https://github.com/tartley/colorama/blob/master/demos/demo04.py
                # codes sent to stderr shouldn't affect later output in stdout
                # It makes sense, but Ubuntu terminal does not confirm it.
                # For now I'm just trimming stderr color codes 
                self._update_ansi_attributes(data)
                
        else:
            tags = extra_tags | {"io", stream_name}
            if stream_name == "stdout":
                tags |= self._get_ansi_tags()
                
            if len(data) > self._get_squeeze_threshold() and "\n" not in data: 
                self._io_cursor_offset = 0 # ignore the effect of preceding \r and \b
                button_text = (data[:40] + " …") 
                btn = tk.Label(self,
                                 text=button_text,
                                 #width=len(button_text),
                                 cursor="arrow",
                                 borderwidth=2,
                                 relief="raised",
                                 font="IOFont",
                                 )
                btn.bind("<1>", lambda e:self._show_squeezed_text(btn), True)
                btn.contained_text = data
                btn.tags = tags
                self._squeeze_buttons.add(btn)
                create_tooltip(btn, "%d characters squeezed. " % len(data) + "Click for details.")
                self.window_create("output_insert", window=btn)
                data = ""
            
            elif self._io_cursor_offset < 0:
                overwrite_len = min(len(data), -self._io_cursor_offset)
                
                if 0 <= data.find("\n") < overwrite_len:
                    overwrite_len = data.find("\n")
                    
                overwrite_data = data[:overwrite_len]
                self.direct_insert("output_insert -%d chars" % -self._io_cursor_offset,
                                   overwrite_data, tuple(tags))
                del_start = self.index("output_insert -%d chars" % -self._io_cursor_offset)
                del_end = self.index("output_insert -%d chars" % 
                                        (-self._io_cursor_offset - overwrite_len))
                self.direct_delete(del_start, del_end)
                
                # compute leftover data to be printed normally
                data = data[overwrite_len:]
                
                if "\n" in data:
                    # cursor offset doesn't apply on new line
                    self._io_cursor_offset = 0
                else:
                    # offset becomes closer to 0
                    self._io_cursor_offset + overwrite_len
                
            elif self._io_cursor_offset > 0:
                # insert spaces before actual data 
                # NB! Print without formatting tags 
                self._insert_text_directly(" " * self._io_cursor_offset, ("io", stream_name))
                self._io_cursor_offset = 0
            
            if data:
                # if any data is still left, then this should be output normally
                self._insert_text_directly(data, tuple(tags))
                
            
        self._applied_io_events.append((original_data, stream_name))
    
    def _show_squeezed_text(self, button):
        dlg = SqueezedTextDialog(self, button)
        show_dialog(dlg)
    
    def _change_io_cursor_offset_csi(self, marker):
        ints = re.findall(INT_REGEX, marker)
        if len(ints) != 1:
            logging.warn("bad CSI cursor positioning: %s", marker)
            # do nothing
            return
        
        try:
            delta = int(ints[0])
        except ValueError:
            logging.warn("bad CSI cursor positioning: %s", marker)
            return
        
        if marker.endswith("D"):
            delta = -delta
        
        self._change_io_cursor_offset(delta)        
            
    def _change_io_cursor_offset(self, delta):
        line = self.get("output_insert linestart", "output_insert")
        if delta == "line":
            self._io_cursor_offset = - len(line)
        else:
            self._io_cursor_offset += delta
            if self._io_cursor_offset < - len(line):
                # cap
                self._io_cursor_offset = - len(line) 
    
    def _reset_ansi_attributes(self):
        self._ansi_foreground = None
        self._ansi_background = None
        self._ansi_inverse = False
        self._ansi_intensity = None
        self._ansi_italic = False
        self._ansi_underline = False
        self._ansi_conceal = False
        self._ansi_strikethrough = False
        
    def _update_ansi_attributes(self, marker):
        if not marker.endswith("m"):
            # ignore
            return 
        
        codes = re.findall(INT_REGEX, marker)
        if not codes:
            self._reset_ansi_attributes()
            
        while codes:
            code = codes.pop(0)
            
            if code == "0":
                self._reset_ansi_attributes()
            elif code in ["1", "2"]:
                self._ansi_intensity = code
            elif code == "3":
                self._ansi_italic = True
            elif code == "4":
                self._ansi_underline = True
            elif code == "7": 
                self._ansi_inverse = True
            elif code == "8":
                self._ansi_conceal = True
            elif code == "9":
                self._ansi_strikethrough = True
            elif code == "22":
                self._ansi_intensity = None
            elif code == "23":
                self._ansi_italic = False
            elif code == "24":
                self._ansi_underline = False
            elif code == "27":
                self._ansi_inverse = False
            elif code == "28":
                self._ansi_conceal = False
            elif code == "29":
                self._ansi_strikethrough = False
            if code in ["30", "31", "32", "33", "34", "35", "36", "37",
                        "90", "91", "92", "93", "94", "95", "96", "97"]:
                self._ansi_foreground = code
            elif code == "39":
                self._ansi_foreground = None
            elif code in ["40", "41", "42", "43", "44", "45", "46", "47",
                          "100", "101", "102", "103", "104", "105", "106", "107"]:
                self._ansi_background = code
            elif code == "49":
                self._ansi_background = None
            elif code in ["38", "48"]:
                # multipart code, ignore for now,
                # but make sure all arguments are ignored
                if not codes:
                    # nothing follows, ie. invalid code
                    break
                mode = codes.pop(0)
                if mode == "5":
                    # 256-color code, just ignore for now
                    if not codes:
                        break
                    codes = codes[1:]
                elif mode == "2":
                    # 24-bit code, ignore
                    if len(codes) < 3:
                        # invalid code
                        break
                    codes = codes[3:]
            else:
                # ignore other codes
                pass
    
    def _get_ansi_tags(self):
        result = set()
        
        if self._ansi_foreground:
            fg = ANSI_COLOR_NAMES[self._ansi_foreground[-1]]
            if self._ansi_intensity == "1" or self._ansi_foreground[0] == "9":
                fg = "bright_" + fg
            elif self._ansi_intensity == "2":
                fg = "dim_" + fg
        else:
            fg = "fore" 
            if self._ansi_intensity == "1":
                fg = "bright_" + fg
            elif self._ansi_intensity == "2":
                fg = "dim_" + fg
            
        if self._ansi_background:
            bg = ANSI_COLOR_NAMES[self._ansi_background[-1]]
            if self._ansi_background.startswith("10"):
                bg = "bright_" + bg
        else:
            bg = "back" 
        
        if self._ansi_inverse:
            result.add(fg + "_bg")
            result.add(bg + "_fg")
        else:
            if fg != "fore":
                result.add(fg + "_fg")
            if bg != "back":
                result.add(bg + "_bg")
                
        if self._ansi_intensity == "1" and self._ansi_italic:
            result.add("intense_italic_io")
        elif self._ansi_intensity == "1":
            result.add("intense_io")
        elif self._ansi_italic:
            result.add("italic_io")
            
        if self._ansi_underline:
            result.add("underline")
                
        if self._ansi_strikethrough:
            result.add("strikethrough")
                
        return result

    def _insert_prompt(self):
        # if previous output didn't put a newline, then do it now
        if not self.index("output_insert").endswith(".0"):
            self._insert_text_directly("\n", ("io",))

        prompt_tags = ("toplevel", "prompt")

        # if previous line has value or io then add little space
        prev_line = self.index("output_insert - 1 lines")
        prev_line_tags = self.tag_names(prev_line)
        if "io" in prev_line_tags or "value" in prev_line_tags:
            prompt_tags += ("after_io_or_value",)

        self._insert_text_directly(">>> ", prompt_tags)
        self.edit_reset()
    
    def _ensure_visible(self):
        focused_view = get_workbench().focus_get()
        get_workbench().show_view("ShellView")
        if focused_view is not None:
            focused_view.focus()

    def restart(self):
        self._insert_text_directly(
            "\n========================= RESTART =========================\n",
            ("magic",),
        )

    def intercept_insert(self, index, txt, tags=()):
        # pylint: disable=arguments-differ
        if self._editing_allowed() and self._in_current_input_range(index):
            # self._print_marks("before insert")
            # I want all marks to stay in place
            self.mark_gravity("input_start", tk.LEFT)
            self.mark_gravity("output_insert", tk.LEFT)

            if get_runner().is_waiting_toplevel_command():
                tags = tags + ("toplevel", "command")
            else:
                tags = tags + ("io", "stdin")

            EnhancedTextWithLogging.intercept_insert(self, index, txt, tags)

            if not get_runner().is_waiting_toplevel_command():
                if not self._applied_io_events:
                    # tag preceding command line differently
                    self.tag_add("before_io", "input_start -1 lines linestart")

                self._try_submit_input()

            self.see("insert")
        else:
            get_workbench().bell()

    def intercept_delete(self, index1, index2=None, **kw):
        if index1 == "sel.first" and index2 == "sel.last" and not self.has_selection():
            return

        if (
            self._editing_allowed()
            and self._in_current_input_range(index1)
            and (index2 is None or self._in_current_input_range(index2))
        ):
            self.direct_delete(index1, index2, **kw)
        else:
            get_workbench().bell()
    
    def selection_is_writable(self):
        try:
            if not self.has_selection():
                return self._in_current_input_range(self.index("insert"))
            else:
                return (
                    self._in_current_input_range(self.index("sel.first"))
                    and self._in_current_input_range(self.index("sel.last")))
        except TclError:
            return True
        

    def perform_return(self, event):
        if get_runner().is_running():
            # if we are fixing the middle of the input string and pressing ENTER
            # then we expect the whole line to be submitted not linebreak to be inserted
            # (at least that's how IDLE works)
            self.mark_set("insert", "end")  # move cursor to the end

            # Do the return without auto indent
            EnhancedTextWithLogging.perform_return(self, event)

            self._try_submit_input()

        elif get_runner().is_waiting_toplevel_command():
            # Same with editin middle of command, but only if it's a single line command
            whole_input = self.get("input_start", "end-1c")  # asking the whole input
            if "\n" not in whole_input and self._code_is_ready_for_submission(
                whole_input
            ):
                self.mark_set("insert", "end")  # move cursor to the end
                # Do the return without auto indent
                EnhancedTextWithLogging.perform_return(self, event)
            else:
                # Don't want auto indent when code is ready for submission
                source = self.get("input_start", "insert")
                tail = self.get("insert", "end")

                if self._code_is_ready_for_submission(source + "\n", tail):
                    # No auto-indent
                    EnhancedTextWithLogging.perform_return(self, event)
                else:
                    # Allow auto-indent
                    PythonText.perform_return(self, event)

            self._try_submit_input()

        return "break"

    def on_secondary_click(self, event=None):
        super().on_secondary_click(event)
        self._menu.tk_popup(event.x_root, event.y_root)

    def _in_current_input_range(self, index):
        try:
            return self.compare(index, ">=", "input_start")
        except Exception:
            return False

    def _insert_text_directly(self, txt, tags=()):
        if "\a" in txt:
            get_workbench().bell()
            # TODO: elide bell character

        def _insert(txt, tags):
            if txt != "":
                self.direct_insert("output_insert", txt, tags)

        # I want the insertion to go before marks
        # self._print_marks("before output")
        self.mark_gravity("input_start", tk.RIGHT)
        self.mark_gravity("output_insert", tk.RIGHT)
        tags = tuple(tags)

        if "stderr" in tags or "error" in tags:
            # show lines pointing to source lines as hyperlinks
            for line in txt.splitlines(True):
                parts = re.split(r"(File .* line \d+.*)$", line, maxsplit=1)
                if len(parts) == 3 and "<pyshell" not in line:
                    _insert(parts[0], tags)
                    _insert(parts[1], tags + ("hyperlink", "io_hyperlink",))
                    _insert(parts[2], tags)
                else:
                    _insert(line, tags)
        else:
            _insert(txt, tags)

        # self._print_marks("after output")
        # output_insert mark will move automatically because of its gravity

    def _try_submit_input(self):
        # see if there is already enough inputted text to submit
        input_text = self.get("input_start", "insert")
        tail = self.get("insert", "end")

        # user may have pasted more text than necessary for this request
        submittable_text = self._extract_submittable_input(input_text, tail)

        if submittable_text is not None:
            if get_runner().is_waiting_toplevel_command():
                # clean up the tail
                if len(tail) > 0:
                    assert tail.strip() == ""
                    self.delete("insert", "end-1c")

            # leftover text will be kept in widget, waiting for next request.
            start_index = self.index("input_start")
            end_index = self.index("input_start+{0}c".format(len(submittable_text)))

            # apply correct tags (if it's leftover then it doesn't have them yet)
            if get_runner().is_running():
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
                # don't remove magic, because otherwise I can't know it's auto
                self.tag_remove(tag, end_index, "end")

            self._submit_input(submittable_text)

    def _editing_allowed(self):
        # TODO: get rid of this
        return True

    def _extract_submittable_input(self, input_text, tail):

        if get_runner().is_waiting_toplevel_command():
            if input_text.endswith("\n"):
                if input_text.strip().startswith("%") or input_text.strip().startswith(
                    "!"
                ):
                    # if several magic command are submitted, then take only first
                    return input_text[: input_text.index("\n") + 1]
                elif self._code_is_ready_for_submission(input_text, tail):
                    return input_text
                else:
                    return None
            else:
                return None

        elif get_runner().is_running():
            i = 0
            while True:
                if i >= len(input_text):
                    return None
                elif input_text[i] == "\n":
                    return input_text[: i + 1]
                else:
                    i += 1

        return None

    def _code_is_ready_for_submission(self, source, tail=""):
        # Ready to submit if ends with empty line
        # or is complete single-line code

        if tail.strip() != "":
            return False

        # First check if it has unclosed parens, unclosed string or ending with : or \
        parser = roughparse.RoughParser(self.indent_width, self.tabwidth)
        parser.set_str(source.rstrip() + "\n")
        if (
            parser.get_continuation_type() != roughparse.C_NONE
            or parser.is_block_opener()
        ):
            return False

        # Multiline compound statements need to end with empty line to be considered
        # complete.
        lines = source.splitlines()
        # strip starting empty and comment lines
        while len(lines) > 0 and (
            lines[0].strip().startswith("#") or lines[0].strip() == ""
        ):
            lines.pop(0)

        compound_keywords = [
            "if",
            "while",
            "for",
            "with",
            "try",
            "def",
            "class",
            "async",
            "await",
        ]
        if len(lines) > 0:
            first_word = lines[0].strip().split()[0]
            if first_word in compound_keywords and not source.replace(" ", "").replace(
                "\t", ""
            ).endswith("\n\n"):
                # last line is not empty
                return False

        return True

    def _submit_input(self, text_to_be_submitted):
        logging.debug(
            "SHELL: submitting %r in state %s",
            text_to_be_submitted,
            get_runner().get_state(),
        )
        if get_runner().is_waiting_toplevel_command():
            # register in history and count
            if text_to_be_submitted in self._command_history:
                self._command_history.remove(text_to_be_submitted)
            self._command_history.append(text_to_be_submitted)
            self._command_history_current_index = (
                None
            )  # meaning command selection is not in process

            cmd_line = text_to_be_submitted.strip()
            try:
                if cmd_line.startswith("%"):
                    parts = cmd_line.split(" ", maxsplit=1)
                    if len(parts) == 2:
                        args_str = parts[1].strip()
                    else:
                        args_str = ""
                    argv = parse_cmd_line(cmd_line[1:])
                    command_name = argv[0]
                    get_workbench().event_generate(
                        "MagicCommand", cmd_line=text_to_be_submitted
                    )
                    get_runner().send_command(
                        ToplevelCommand(
                            command_name,
                            args=argv[1:],
                            args_str=args_str,
                            cmd_line=cmd_line,
                        )
                    )
                elif cmd_line.startswith("!"):
                    argv = parse_cmd_line(cmd_line[1:])
                    get_workbench().event_generate(
                        "SystemCommand", cmd_line=text_to_be_submitted
                    )
                    get_runner().send_command(
                        ToplevelCommand(
                            "execute_system_command", argv=argv, cmd_line=cmd_line
                        )
                    )
                else:
                    get_runner().send_command(
                        ToplevelCommand("execute_source", source=text_to_be_submitted)
                    )

                # remember the place where the output of this command started
                self.mark_set("command_io_start", "output_insert")
                self.mark_gravity("command_io_start", "left")
                # discard old io events
                self._applied_io_events = []
                self._queued_io_events = []
            except Exception:
                get_workbench().report_exception()
                self._insert_prompt()

            get_workbench().event_generate(
                "ShellCommand", command_text=text_to_be_submitted
            )
        else:
            assert get_runner().is_running()
            get_runner().send_program_input(text_to_be_submitted)
            get_workbench().event_generate(
                "ShellInput", input_text=text_to_be_submitted
            )
            self._applied_io_events.append((text_to_be_submitted, "stdin"))

    def _arrow_up(self, event):
        if not self._in_current_input_range("insert"):
            return None

        insert_line = index2line(self.index("insert"))
        input_start_line = index2line(self.index("input_start"))
        if insert_line != input_start_line:
            # we're in the middle of a multiline command
            return None

        if len(self._command_history) == 0 or self._command_history_current_index == 0:
            # can't take previous command
            return "break"

        if self._command_history_current_index is None:
            self._command_history_current_index = len(self._command_history) - 1
        else:
            self._command_history_current_index -= 1

        cmd = self._command_history[self._command_history_current_index]
        if cmd[-1] == "\n":
            cmd = cmd[:-1]  # remove the submission linebreak
        self._propose_command(cmd)
        return "break"

    def _arrow_down(self, event):
        if not self._in_current_input_range("insert"):
            return None

        insert_line = index2line(self.index("insert"))
        last_line = index2line(self.index("end-1c"))
        if insert_line != last_line:
            # we're in the middle of a multiline command
            return None

        if (
            len(self._command_history) == 0
            # FIXME: _command_history_current_index may be None
            or self._command_history_current_index >= len(self._command_history) - 1
        ):
            # can't take next command
            self._command_history_current_index = len(self._command_history)
            self._propose_command("")
            return "break"

        if self._command_history_current_index is None:
            self._command_history_current_index = len(self._command_history) - 1
        else:
            self._command_history_current_index += 1

        self._propose_command(
            self._command_history[self._command_history_current_index].strip("\n")
        )
        return "break"

    def _propose_command(self, cmd_line):
        self.delete("input_start", "end")
        self.intercept_insert("input_start", cmd_line)
        self.see("insert")

    def _text_key_press(self, event):
        # Ctrl should underline values
        # TODO: this underline may confuse, when user is just copying on pasting
        # try to add this underline only when mouse is over the value

        # TODO: take theme into account
        """
        if event.keysym in ("Control_L", "Control_R", "Command"):  # TODO: check in Mac
            self.tag_configure("value", foreground="DarkBlue", underline=1)
        """

    def _text_key_release(self, event):
        # Remove value underlining
        # TODO: take theme into account
        """
        if event.keysym in ("Control_L", "Control_R", "Command"):  # TODO: check in Mac
            self.tag_configure("value", foreground="DarkBlue", underline=0)
        """

    def _clear_shell(self):
        end_index = self.index("output_end")
        self._clear_content(end_index)

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
                    get_workbench().get_editor_notebook().show_file(
                        filename, lineno, set_focus=False
                    )
        except Exception:
            traceback.print_exc()

    def _show_user_exception(self, user_exception):

        for line, frame_id, *_ in user_exception["items"]:

            tags = ("io", "stderr")
            if frame_id is not None:
                frame_tag = "frame_%d" % frame_id

                def handle_frame_click(event, frame_id=frame_id):
                    get_runner().send_command(
                        InlineCommand("get_frame_info", frame_id=frame_id)
                    )
                    return "break"

                # TODO: put first line with frame tag and rest without
                tags += (frame_tag,)
                self.tag_bind(frame_tag, "<ButtonRelease-1>", handle_frame_click, True)

            self._insert_text_directly(line, tags)
    
    def _discard_old_content(self):
        max_lines = max(get_workbench().get_option("shell.max_lines"), 0)
        proposed_cut = self.index("end -%d lines linestart" % max_lines)
        if proposed_cut == "1.0":
            return
        
        
        
        # would this keep current block intact? 
        next_prompt = self.tag_nextrange("prompt", proposed_cut, "end")
        if not next_prompt:
            pass # TODO: disable stepping back
        
        self._clear_content(proposed_cut)
    
    def _clear_content(self, cut_idx):
        proposed_cut_float = float(cut_idx)
        for btn in list(self._squeeze_buttons):
            btn_pos = float(self.index(btn))
            if btn_pos < proposed_cut_float:
                self._squeeze_buttons.remove(btn)
                # looks like the widgets are not fully GC-d.
                # At least avoid leaking big chunks of texts
                btn.contained_text = None 
                btn.destroy()
                
            
        self.direct_delete("0.1", cut_idx)
            
            
    def _invalidate_current_data(self):
        """
        Grayes out input & output displayed so far
        """
        end_index = self.index("output_end")

        self.tag_add("inactive", "1.0", end_index)
        self.tag_remove("value", "1.0", end_index)

        while len(self.active_object_tags) > 0:
            self.tag_remove(self.active_object_tags.pop(), "1.0", "end")

class SqueezedTextDialog(tk.Toplevel):
    def __init__(self, master, button):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.button = button
        self.content = button.contained_text
        self.shell_text = master
        
        padding = 20
        
        mainframe = ttk.Frame(self)
        mainframe.grid(row=0, column=0, sticky="nsew")
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(2, weight=1)
        
        explanation_label = ttk.Label(mainframe, 
                                      text="For performance reasons, Shell avoids showing "
                                        + "very long lines in full (see Tools => Options => Shell).\n"
                                        + "Here you can interact with the original text fragment.")
        explanation_label.grid(row=0, column=0, sticky="nsew", padx=padding, pady=padding)
        
        self._wrap_var = tk.BooleanVar(False)
        self.wrap_checkbox = ttk.Checkbutton(mainframe, text="Wrap text (may be slow)",
                                             variable=self._wrap_var,
                                             onvalue=True,
                                             offvalue=False,
                                             command=self._on_wrap_changed)
        self.wrap_checkbox.grid(row=1, padx=padding, pady=(0,padding//2), sticky="w")
        
        self.text_frame = TextFrame(mainframe, text_class=TweakableText, height=10, width=80,
                                    relief="sunken", borderwidth=1,
                                    wrap="none")
        self.text_frame.grid(row=2, column=0, padx=padding)
        self.text_frame.text.insert("1.0", button.contained_text)
        self.text_frame.text.set_read_only(True)
        
        button_frame = ttk.Frame(mainframe)
        button_frame.grid(row=3, column=0, padx=padding, pady=padding, sticky="nswe")
        button_frame.columnconfigure(2, weight=1)
        
        copy_caption = "Copy to clipboard"
        copy_button = ttk.Button(button_frame, text=copy_caption,
                                 width=len(copy_caption), 
                                 command=self._on_copy)
        copy_button.grid(row=0, column=1, sticky="w", padx=(0, padding))
        
        expand_caption = "Expand in Shell"
        expand_button = ttk.Button(button_frame, text=expand_caption,
                                   width=len(expand_caption),
                                   command=self._on_expand)
        expand_button.grid(row=0, column=2, sticky="e", padx=padding)
        
        close_button = ttk.Button(button_frame, text="Close", 
                                  command=self._on_close)
        close_button.grid(row=0, column=3, sticky="e")

        self.bind("<Escape>", self._on_close, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.title("Squeezed text (%d characters)" % len(self.content))
    
    def _on_wrap_changed(self):
        if self._wrap_var.get():
            self.text_frame.text.configure(wrap="word")
        else:
            self.text_frame.text.configure(wrap="none")
    
    def _on_expand(self):
        index = self.shell_text.index(self.button)
        self.shell_text.direct_delete(index, index + " +1 chars")
        self.shell_text.direct_insert(index, self.content, tuple(self.button.tags))
        self.destroy()
        
        # looks like the widgets are not fully GC-d.
        # At least avoid leaking big chunks of texts
        self.button.contained_text = None
        self.button.destroy()
        
    
    def _on_copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.content)
    
    def _on_close(self, event=None):
        self.destroy()
        
        