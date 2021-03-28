# -*- coding: utf-8 -*-

import logging
import os.path
import re
import tkinter as tk
import traceback
from tkinter import ttk

from _tkinter import TclError

from thonny import get_runner, get_workbench, memory, roughparse, running, ui_utils
from thonny.codeview import get_syntax_options_for_tag, perform_python_return, SyntaxText
from thonny.common import (
    OBJECT_LINK_END,
    OBJECT_LINK_START,
    InlineCommand,
    ToplevelCommand,
    ToplevelResponse,
)
from thonny.languages import tr
from thonny.misc_utils import construct_cmd_line, parse_cmd_line, running_on_mac_os, shorten_repr
from thonny.running import EDITOR_CONTENT_TOKEN
from thonny.tktextext import TextFrame, TweakableText, index2line
from thonny.ui_utils import (
    CommonDialog,
    EnhancedTextWithLogging,
    TextMenu,
    create_tooltip,
    lookup_style_option,
    scrollbar_style,
    select_sequence,
    show_dialog,
    tr_btn,
    ems_to_pixels,
)

OBJECT_INFO_START_REGEX_STR = re.escape(OBJECT_LINK_START).replace("%d", r"-?\d+")
OBJECT_INFO_START_REGEX = re.compile(OBJECT_INFO_START_REGEX_STR)
OBJECT_INFO_END_REGEX_STR = re.escape(OBJECT_LINK_END)
OBJECT_INFO_END_REGEX = re.compile(OBJECT_INFO_END_REGEX_STR)

logger = logging.getLogger(__name__)

_CLEAR_SHELL_DEFAULT_SEQ = select_sequence("<Control-l>", "<Command-k>")

# NB! Don't add parens without refactoring split procedure!

TERMINAL_CONTROL_REGEX_STR = r"\x1B\[[0-?]*[ -/]*[@-~]|[\a\b\r]"
TERMINAL_CONTROL_REGEX = re.compile(TERMINAL_CONTROL_REGEX_STR)
OUTPUT_SPLIT_REGEX = re.compile(
    "(%s|%s|%s)"
    % (TERMINAL_CONTROL_REGEX_STR, OBJECT_INFO_START_REGEX_STR, OBJECT_INFO_END_REGEX_STR)
)
NUMBER_SPLIT_REGEX = re.compile(r"((?<!\w)[-+]?[0-9]*\.?[0-9]+\b)")
SIMPLE_URL_SPLIT_REGEX = re.compile(
    r"(https?:\/\/[\w\/.:\-\?#=%&]+[\w\/]|data:image\/[a-z]+;base64,[A-Za-z0-9\/=\+]+)"
)

INT_REGEX = re.compile(r"\d+")
ANSI_COLOR_NAMES = {
    "0": "black",
    "1": "red",
    "2": "green",
    "3": "yellow",
    "4": "blue",
    "5": "magenta",
    "6": "cyan",
    "7": "white",
    "9": "default",
}


class ShellView(tk.PanedWindow):
    def __init__(self, master):
        super().__init__(
            master,
            orient="horizontal",
            sashwidth=lookup_style_option("Sash", "sashthickness", ems_to_pixels(0.6)),
            background=lookup_style_option("TPanedWindow", "background"),
            borderwidth=0,
        )

        main_frame = tk.Frame(self)
        self.add(main_frame, minsize=100)

        self.vert_scrollbar = ttk.Scrollbar(
            main_frame, orient=tk.VERTICAL, style=scrollbar_style("Vertical")
        )
        self.vert_scrollbar.grid(row=1, column=2, sticky=tk.NSEW)
        get_workbench().add_command(
            "clear_shell",
            "edit",
            tr("Clear shell"),
            self.clear_shell,
            default_sequence=_CLEAR_SHELL_DEFAULT_SEQ,
            group=200,
        )

        get_workbench().set_default("shell.max_lines", 1000)
        get_workbench().set_default("shell.squeeze_threshold", 1000)
        get_workbench().set_default("shell.tty_mode", True)
        get_workbench().set_default("shell.auto_inspect_values", True)

        self.text = ShellText(
            main_frame,
            self,
            font="EditorFont",
            # foreground="white",
            # background="#666666",
            highlightthickness=0,
            # highlightcolor="LightBlue",
            borderwidth=0,
            yscrollcommand=self.set_scrollbar,
            padx=0,
            pady=0,
            insertwidth=2,
            height=10,
            undo=True,
        )

        get_workbench().event_generate("ShellTextCreated", text_widget=self.text)
        get_workbench().bind("TextInsert", self.text_inserted, True)
        get_workbench().bind("TextDelete", self.text_deleted, True)

        self.text.grid(row=1, column=1, sticky=tk.NSEW)
        self.vert_scrollbar["command"] = self.text.yview
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        self.notice = ttk.Label(self, text="", background="#ffff99", padding=3)

        self.init_plotter()
        self.menu = ShellMenu(self.text, self)

    def init_plotter(self):
        self.plotter = None
        get_workbench().set_default("view.show_plotter", False)
        get_workbench().set_default("view.shell_sash_position", 400)

        self.plotter_visibility_var = get_workbench().get_variable("view.show_plotter")

        def can_toggle():
            return self.winfo_ismapped()

        get_workbench().add_command(
            "toggle_plotter",
            "view",
            tr("Plotter"),
            self.toggle_plotter,
            can_toggle,
            flag_name="view.show_plotter",
            group=11,
        )

        self.update_plotter_visibility(True)

    def set_ignore_program_output(self, value):
        self.text._ignore_program_output = value

    def toggle_plotter(self):
        self.plotter_visibility_var.set(not self.plotter_visibility_var.get())
        self.update_plotter_visibility()

    def update_plotter_visibility(self, initializing_shell_view=False):
        if self.plotter_visibility_var.get():
            self.show_plotter(initializing_shell_view)
        else:
            self.hide_plotter()

    def show_plotter(self, initializing_shell_view=False):
        if not initializing_shell_view:
            get_workbench().show_view("ShellView", True)

        if self.plotter is None:
            self.plotter = PlotterCanvas(self, self.text)

        if not self.plotter.winfo_ismapped():
            self.add(self.plotter, minsize=100)

        self.sash_place(0, get_workbench().get_option("view.shell_sash_position"), 0)

        running.io_animation_required = True
        self.update_plotter()

    def hide_plotter(self):
        if self.plotter is None or not self.plotter.winfo_ismapped():
            return
        else:
            self.remove(self.plotter)
            running.io_animation_required = False

    def set_notice(self, text):
        if text is None:
            self.notice.grid_forget()
        else:
            self.notice["text"] = text
            if not self.notice.winfo_ismapped():
                self.notice.grid(row=0, column=1, columnspan=2, sticky="nsew", pady=(0, 1))
                # height of the text was reduced so adjust the scrolling
                # self.update()
                self.text.see("end")

    def print_error(self, txt):
        self.text._insert_text_directly(txt, ("io", "stderr"))
        self.text.see("end")

    def insert_command_link(self, txt, handler):
        self.text._insert_command_link(txt, handler)

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

    def has_pending_input(self):
        return self.text.has_pending_input()

    def report_exception(self, prelude=None, conclusion=None):
        if prelude is not None:
            self.text.direct_insert("end", prelude + "\n", ("stderr",))

        self.text.direct_insert("end", traceback.format_exc() + "\n", ("stderr",))

        if conclusion is not None:
            self.text.direct_insert("end", conclusion + "\n", ("stderr",))

    def set_scrollbar(self, *args):
        self.vert_scrollbar.set(*args)
        self.update_plotter()

    def text_deleted(self, event):
        if event.text_widget == self.text:
            self.update_plotter()

    def text_inserted(self, event):
        if (
            event.text_widget == self.text
            and "\n" in event.text
            # only when scrollbar doesn't move, because otherwise
            # the update gets triggered by scrollbar anyway
            and self.vert_scrollbar.get() == (0.0, 1.0)
        ):
            self.update_plotter()

    def update_plotter(self):
        if self.plotter is not None and self.plotter.winfo_ismapped():
            self.plotter.update_plot()

    def update_tabs(self):
        self.text.update_tabs()

    def resize_plotter(self):
        if len(self.panes()) > 1 and self.text.winfo_width() > 5:
            get_workbench().set_option("view.shell_sash_position", self.sash_coord(0)[0])


class ShellMenu(TextMenu):
    def __init__(self, target, view):
        self.view = view
        TextMenu.__init__(self, target)

    def add_extra_items(self):
        self.add_separator()
        self.add_command(label=tr("Clear"), command=self.text._clear_shell)

        def toggle_from_menu():
            # I don't like that Tk menu toggles checbutton variable
            # automatically before calling the handler.
            # So I revert the toggle before calling the actual handler.
            # This way the handler doesn't have to worry whether it
            # needs to toggle the variable or not, and it can choose to
            # decline the toggle.
            self.view.plotter_visibility_var.set(not self.view.plotter_visibility_var.get())
            self.view.toggle_plotter()

        self.add_checkbutton(
            label=tr("Show Plotter"),
            command=toggle_from_menu,
            variable=self.view.plotter_visibility_var,
        )

    def selection_is_read_only(self):
        return not self.text.selection_is_writable()


class BaseShellText(EnhancedTextWithLogging, SyntaxText):
    """Passive version of ShellText. Used also for preview"""

    def __init__(self, master, view=None, cnf={}, **kw):
        self.view = view
        self._ignore_program_output = False
        self._link_handler_count = 0
        kw["tabstyle"] = "wordprocessor"
        super().__init__(master, cnf, **kw)

        self._command_history = (
            []
        )  # actually not really history, because each command occurs only once
        self._command_history_current_index = None

        # logs of IO events for current toplevel block
        # (enables undoing and redoing the events)
        self._applied_io_events = []
        self._queued_io_events = []
        self._images = set()

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

        self.update_tty_mode()

        self.bind("<Up>", self._arrow_up, True)
        self.bind("<Down>", self._arrow_down, True)
        self.bind("<KeyPress>", self._text_key_press, True)
        self.bind("<KeyRelease>", self._text_key_release, True)

        prompt_font = tk.font.nametofont("BoldEditorFont")
        x_padding = 4
        io_vert_spacing = 10
        io_indent = 16 + x_padding
        self.io_indent = io_indent
        code_indent = prompt_font.measure(">>> ") + x_padding

        self.tag_configure("command", lmargin1=code_indent, lmargin2=code_indent)
        self.tag_configure(
            "io", lmargin1=io_indent, lmargin2=io_indent, rmargin=io_indent, font="IOFont"
        )
        self.update_margin_color()

        self.tag_configure("after_io_or_value", spacing1=io_vert_spacing)
        self.tag_configure("before_io", spacing3=io_vert_spacing)

        self.tag_configure("prompt", lmargin1=x_padding, lmargin2=x_padding)
        self.tag_configure("value", lmargin1=x_padding, lmargin2=x_padding)
        self.tag_configure("restart_line", wrap="none", lmargin1=x_padding, lmargin2=x_padding)

        self.tag_configure("welcome", lmargin1=x_padding, lmargin2=x_padding)

        # Underline on the font looks better than underline on the tag,
        # therefore Shell doesn't use configured "hyperlink" style directly
        hyperlink_opts = get_syntax_options_for_tag("hyperlink").copy()
        if hyperlink_opts.get("underline"):
            hyperlink_opts["font"] = "UnderlineIOFont"
            del hyperlink_opts["underline"]
        self.tag_configure("io_hyperlink", **hyperlink_opts)

        # create 3 marks: input_start shows the place where user entered but not-yet-submitted
        # input starts, output_end shows the end of last output,
        # output_insert shows where next incoming program output should be inserted
        self.mark_set("input_start", "end-1c")
        self.mark_gravity("input_start", tk.LEFT)

        self.mark_set("output_end", "end-1c")
        self.mark_gravity("output_end", tk.LEFT)

        self.mark_set("output_insert", "end-1c")
        self.mark_gravity("output_insert", tk.RIGHT)

        self.mark_set("command_io_start", "1.0")
        self.mark_gravity("command_io_start", "left")

        self.active_extra_tags = []

        self.update_tabs()

        self.tag_raise("io_hyperlink")
        self.tag_raise("underline")
        self.tag_raise("strikethrough")
        self.tag_raise("intense_io")
        self.tag_raise("italic_io")
        self.tag_raise("intense_italic_io")
        self.tag_raise("sel")

    def is_python_text(self):
        return True

    def submit_command(self, cmd_line, tags):
        # assert get_runner().is_waiting_toplevel_command()
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
        if self._ignore_program_output:
            # This output will be handled elsewhere
            return
        # Discard but not too often, as toplevel response will discard anyway
        if int(float(self.index("end"))) > get_workbench().get_option("shell.max_lines") + 100:
            self._discard_old_content()

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
        if welcome_text and welcome_text:
            preceding = self.get("output_insert -1 c", "output_insert")
            if preceding.strip() and not preceding.endswith("\n"):
                self._insert_text_directly("\n")
            self._insert_text_directly(welcome_text, ("welcome",))
            self.see("end")

        self.mark_set("output_end", self.index("end-1c"))
        self._discard_old_content()
        self._update_visible_io(None)
        self._reset_ansi_attributes()
        self._io_cursor_offset = 0
        self._insert_prompt()
        self._try_submit_input()  # Trying to submit leftover code (eg. second magic command)
        self.see("end")

        # import os
        # import psutil
        # process = psutil.Process(os.getpid())
        # print("MEM", process.memory_info().rss // (1024*1024))

    def _handle_fancy_debugger_progress(self, msg):
        if msg.in_present or msg.io_symbol_count is None:
            self._update_visible_io(None)
        else:
            self._update_visible_io(msg.io_symbol_count)

    def _get_squeeze_threshold(self):
        return get_workbench().get_option("shell.squeeze_threshold")

    def _append_to_io_queue(self, data, stream_name):
        # Make sure ANSI CSI codes and object links are stored as separate events
        # TODO: try to complete previously submitted incomplete code
        parts = re.split(OUTPUT_SPLIT_REGEX, data)
        for part in parts:
            if part:  # split may produce empty string in the beginning or start
                # split the data so that very long lines separated
                for block in re.split("(.{%d,})" % (self._get_squeeze_threshold() + 1), part):
                    if block:
                        self._queued_io_events.append((block, stream_name))

    def _update_visible_io(self, target_num_visible_chars):
        current_num_visible_chars = sum(map(lambda x: len(x[0]), self._applied_io_events))

        if (
            target_num_visible_chars is not None
            and target_num_visible_chars < current_num_visible_chars
        ):
            # hard to undo complex renderings (squeezed texts and ANSI codes)
            # easier to clean everything and start again
            self._queued_io_events = self._applied_io_events + self._queued_io_events
            self._applied_io_events = []
            self.direct_delete("command_io_start", "output_end")
            current_num_visible_chars = 0
            self._reset_ansi_attributes()

        while self._queued_io_events and current_num_visible_chars != target_num_visible_chars:
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

    def _apply_io_event(self, data, stream_name):
        if not data:
            return

        original_data = data

        if self.tty_mode and re.match(TERMINAL_CONTROL_REGEX, data):
            if data == "\a":
                get_workbench().bell()
            elif data == "\b":
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
                logger.warning("Don't know what to do with %r" % data)

        elif re.match(OBJECT_INFO_START_REGEX, data):
            id_str = data[data.index("=") + 1 : data.index("]")]
            self.active_extra_tags.append("value")
            self.active_extra_tags.append(id_str)
            if get_workbench().get_option("shell.auto_inspect_values"):
                get_workbench().event_generate("ObjectSelect", object_id=int(id_str))

            if get_workbench().in_heap_mode():
                self._insert_text_directly(
                    memory.format_object_id(int(id_str)), tuple(self.active_extra_tags)
                )

        elif re.match(OBJECT_INFO_END_REGEX, data):
            try:
                self.active_extra_tags.pop()
                self.active_extra_tags.pop()
            except Exception as e:
                # This may fail, when the source code of Thonny's MP helper is printed
                # because of an error.
                logger.exception("Could not close object info", exc_info=e)

        elif "value" in self.active_extra_tags and get_workbench().in_heap_mode():
            # id was already printed and value should be suppressed
            pass
        else:
            if "value" in self.active_extra_tags:
                tags = set(self.active_extra_tags)
            else:
                tags = set(self.active_extra_tags) | {"io", stream_name}

            if stream_name == "stdout" and self.tty_mode:
                tags |= self._get_ansi_tags()

            non_url_length = len(data)
            for url_match in SIMPLE_URL_SPLIT_REGEX.finditer(data):
                non_url_length -= url_match.end() - url_match.start()

            if (
                non_url_length > self._get_squeeze_threshold()
                and "\n" not in data
                and not (data.startswith(OBJECT_LINK_START))
            ):
                self._io_cursor_offset = 0  # ignore the effect of preceding \r and \b
                actual_text = data
                button_text = actual_text[:70] + " …"
                btn = tk.Label(
                    self,
                    text=button_text,
                    # width=len(button_text),
                    cursor="arrow",
                    borderwidth=2,
                    relief="raised",
                    font="IOFont",
                )
                btn.bind("<1>", lambda e: self._show_squeezed_text(btn), True)
                btn.contained_text = actual_text
                btn.tags = tags
                self._squeeze_buttons.add(btn)
                create_tooltip(btn, "%d characters squeezed. " % len(data) + "Click for details.")

                # TODO: refactor
                # (currently copied from insert_text_directly)
                self.mark_gravity("input_start", tk.RIGHT)
                self.mark_gravity("output_insert", tk.RIGHT)

                self.window_create("output_insert", window=btn)
                for tag_name in tags:
                    self.tag_add(tag_name, "output_insert -1 chars")
                data = ""

            elif self._io_cursor_offset < 0:
                overwrite_len = min(len(data), -self._io_cursor_offset)

                if 0 <= data.find("\n") < overwrite_len:
                    overwrite_len = data.find("\n")

                overwrite_data = data[:overwrite_len]
                self.direct_insert(
                    "output_insert -%d chars" % -self._io_cursor_offset, overwrite_data, tuple(tags)
                )
                del_start = self.index("output_insert -%d chars" % -self._io_cursor_offset)
                del_end = self.index(
                    "output_insert -%d chars" % (-self._io_cursor_offset - overwrite_len)
                )
                self.direct_delete(del_start, del_end)

                # compute leftover data to be printed normally
                data = data[overwrite_len:]

                if "\n" in data:
                    # cursor offset doesn't apply on new line
                    self._io_cursor_offset = 0
                else:
                    # offset becomes closer to 0
                    self._io_cursor_offset += overwrite_len

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
            logging.warning("bad CSI cursor positioning: %s", marker)
            # do nothing
            return

        try:
            delta = int(ints[0])
        except ValueError:
            logging.warning("bad CSI cursor positioning: %s", marker)
            return

        if marker.endswith("D"):
            delta = -delta

        self._change_io_cursor_offset(delta)

    def _change_io_cursor_offset(self, delta):
        line = self.get("output_insert linestart", "output_insert")
        if delta == "line":
            self._io_cursor_offset = -len(line)
        else:
            self._io_cursor_offset += delta
            if self._io_cursor_offset < -len(line):
                # cap
                self._io_cursor_offset = -len(line)

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
            if code in [
                "30",
                "31",
                "32",
                "33",
                "34",
                "35",
                "36",
                "37",
                "90",
                "91",
                "92",
                "93",
                "94",
                "95",
                "96",
                "97",
            ]:
                self._ansi_foreground = code
            elif code == "39":
                self._ansi_foreground = None
            elif code in [
                "40",
                "41",
                "42",
                "43",
                "44",
                "45",
                "46",
                "47",
                "100",
                "101",
                "102",
                "103",
                "104",
                "105",
                "106",
                "107",
            ]:
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
        if self.winfo_ismapped():
            return

        focused_view = get_workbench().focus_get()
        get_workbench().show_view("ShellView")
        if focused_view is not None:
            focused_view.focus()

    def update_tabs(self):
        tab_chars = 8
        tab_pixels = tk.font.nametofont("IOFont").measure("n" * tab_chars)

        offset = self.io_indent
        tabs = [offset]
        for _ in range(20):
            offset += tab_pixels
            tabs.append(offset)

        self.tag_configure("io", tabs=tabs, tabstyle="wordprocessor")

    def restart(self):
        self._insert_text_directly(
            # "\n============================== RESTART ==============================\n",
            "\n" + "─" * 200 + "\n",
            # "\n" + "═"*200 + "\n",
            ("magic", "restart_line"),
        )
        self.see("end")

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
                return self._in_current_input_range(
                    self.index("sel.first")
                ) and self._in_current_input_range(self.index("sel.last"))
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
            if "\n" not in whole_input and self._code_is_ready_for_submission(whole_input):
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
                    perform_python_return(self, event)

            self._try_submit_input()

        return "break"

    def on_secondary_click(self, event=None):
        super().on_secondary_click(event)
        if self.view:
            self.view.menu.tk_popup(event.x_root, event.y_root)

    def _in_current_input_range(self, index):
        try:
            return self.compare(index, ">=", "input_start")
        except Exception:
            return False

    def _insert_command_link(self, txt, handler):
        self._link_handler_count += 1
        command_tag = "link_handler_%s" % self._link_handler_count

        self.direct_insert("output_insert", txt, ("io_hyperlink", command_tag))
        self.tag_bind(command_tag, "<1>", handler)

    def _insert_text_directly(self, txt, tags=()):
        def _insert(txt, tags):
            if txt != "":
                self.direct_insert("output_insert", txt, tags)

        def _insert_and_highlight_urls(txt, tags):
            parts = SIMPLE_URL_SPLIT_REGEX.split(txt)
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    _insert(part, tags)
                else:
                    if part.startswith("data:image/"):
                        token = ";base64,"
                        data = part[part.index(token) + len(token) :]
                        try:
                            img = tk.PhotoImage(data=data)
                            self._images.add(img)  # to avoit it being gc-d"""
                            self.image_create("output_insert", image=img)
                            for tag in tags:
                                self.tag_add(tag, "output_insert -1 chars")
                        except TclError:
                            _insert(part, tags + ("io_hyperlink",))
                    else:
                        _insert(part, tags + ("io_hyperlink",))

        # I want the insertion to go before marks
        # self._print_marks("before output")
        self.mark_gravity("input_start", tk.RIGHT)
        self.mark_gravity("output_insert", tk.RIGHT)
        tags = tuple(tags)

        # Make stacktrace clickable
        if "stderr" in tags or "error" in tags or ("File" in txt and "line" in txt):
            # show lines pointing to source lines as hyperlinks
            for line in txt.splitlines(True):
                parts = re.split(r"(File .* line \d+.*)$", line, maxsplit=1)
                if len(parts) == 3 and "<pyshell" not in line:
                    _insert(parts[0], tags)
                    _insert(parts[1], tags + ("io_hyperlink",))
                    _insert(parts[2], tags)
                else:
                    parts = re.split(r"(\'[^\']+\.pyw?\')", line, flags=re.IGNORECASE)
                    if len(parts) == 3 and os.path.exists(os.path.expanduser(parts[1][1:-1])):
                        match = re.search(r"\S", line)
                        _insert(line[: match.start()], tags)
                        _insert(line[match.start() :], tags + ("io_hyperlink",))
                    else:
                        _insert_and_highlight_urls(line, tags)
        else:
            _insert_and_highlight_urls(txt, tags)

        # self._print_marks("after output")
        # output_insert mark will move automatically because of its gravity

    def has_pending_input(self):
        pending = self.get("input_start", "end-1c")
        return bool(pending)

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
        return get_runner() is not None

    def _extract_submittable_input(self, input_text, tail):

        if get_runner().is_waiting_toplevel_command():
            if input_text.endswith("\n"):
                if input_text.strip().startswith("%") or input_text.strip().startswith("!"):
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
        if parser.get_continuation_type() != roughparse.C_NONE or parser.is_block_opener():
            return False

        # Multiline compound statements need to end with empty line to be considered
        # complete.
        lines = source.splitlines()
        # strip starting empty and comment lines
        while len(lines) > 0 and (lines[0].strip().startswith("#") or lines[0].strip() == ""):
            lines.pop(0)

        compound_keywords = ["if", "while", "for", "with", "try", "def", "class", "async", "await"]
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
            "SHELL: submitting %r in state %s", text_to_be_submitted, get_runner().get_state()
        )
        if get_runner().is_waiting_toplevel_command():
            # register in history and count
            if text_to_be_submitted in self._command_history:
                self._command_history.remove(text_to_be_submitted)
            self._command_history.append(text_to_be_submitted)

            # meaning command selection is not in process
            self._command_history_current_index = None

            self.update_tty_mode()

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
                    cmd_args = argv[1:]

                    if len(cmd_args) >= 2 and cmd_args[0] == "-c":
                        # move source argument to source attribute
                        source = cmd_args[1]
                        cmd_args = [cmd_args[0]] + cmd_args[2:]
                        if source == EDITOR_CONTENT_TOKEN:
                            source = (
                                get_workbench().get_editor_notebook().get_current_editor_content()
                            )
                    else:
                        source = None

                    get_workbench().event_generate("MagicCommand", cmd_line=text_to_be_submitted)
                    get_runner().send_command(
                        ToplevelCommand(
                            command_name,
                            args=cmd_args,
                            args_str=args_str,
                            cmd_line=cmd_line,
                            tty_mode=self.tty_mode,
                            source=source,
                        )
                    )
                elif cmd_line.startswith("!"):
                    argv = parse_cmd_line(cmd_line[1:])
                    get_workbench().event_generate("SystemCommand", cmd_line=text_to_be_submitted)
                    get_runner().send_command(
                        ToplevelCommand(
                            "execute_system_command",
                            argv=argv,
                            cmd_line=cmd_line,
                            tty_mode=self.tty_mode,
                        )
                    )
                else:
                    get_runner().send_command(
                        ToplevelCommand(
                            "execute_source", source=text_to_be_submitted, tty_mode=self.tty_mode
                        )
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

            get_workbench().event_generate("ShellCommand", command_text=text_to_be_submitted)
        else:
            assert get_runner().is_running()
            get_runner().send_program_input(text_to_be_submitted)
            get_workbench().event_generate("ShellInput", input_text=text_to_be_submitted)
            self._applied_io_events.append((text_to_be_submitted, "stdin"))

    def _arrow_up(self, event):
        if not get_runner().is_waiting_toplevel_command():
            return None

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
        if not get_runner().is_waiting_toplevel_command():
            return None

        if not self._in_current_input_range("insert"):
            return None

        insert_line = index2line(self.index("insert"))
        last_line = index2line(self.index("end-1c"))
        if insert_line != last_line:
            # we're in the middle of a multiline command
            return None

        if (
            len(self._command_history) == 0
            or self._command_history_current_index is None
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

    def _on_backend_restart(self, event=None):
        # make sure dead values are not clickable anymore
        self.tag_remove("value", "0.1", "end")

    def compute_smart_home_destination_index(self):
        """Is used by EnhancedText"""

        if self._in_current_input_range("insert"):
            # on input line, go to just after prompt
            return "input_start"
        else:
            return super().compute_smart_home_destination_index()

    def _value_click(self, event):
        pos = "@%d,%d" % (event.x, event.y)
        tags = self.tag_names(pos)
        for tag in tags:
            if tag.isnumeric() or tag[0] == "-" and tag[1:].isnumeric():
                get_workbench().show_view("ObjectInspector", set_focus=False)
                get_workbench().update_idletasks()
                get_workbench().event_generate("ObjectSelect", object_id=int(tag))

    def _value_mouse_up(self, event):
        pos = "@%d,%d" % (event.x, event.y)
        rng = self.tag_prevrange("value", pos)
        if not rng:
            return

        # select whole value unless user has started a partial selection
        # if not self.tag_nextrange("sel", rng[0], rng[1]):
        #    self.tag_remove("sel", "1.0", "end")
        #    self.tag_add("sel", rng[0], rng[1])

    def _handle_hyperlink(self, event):
        import webbrowser

        try:
            line = self.get("insert linestart", "insert lineend")
            # Python stacktrace
            matches = list(re.finditer(r'File "(?P<file>[^"]+)", line (?P<line>\d+)', line))
            if not matches:
                # Friendly traceback
                matches = list(
                    re.finditer(
                        r"\b(?P<line>\d+)\b.+'(?P<file>[^\']+\.pyw?)'", line, flags=re.IGNORECASE
                    )
                )

            if len(matches) == 1:
                filename = os.path.expanduser(matches[0].group("file"))
                lineno = int(matches[0].group("line"))
                if os.path.exists(filename) and os.path.isfile(filename):
                    # TODO: better use events instead direct referencing
                    get_workbench().get_editor_notebook().show_file(
                        filename, lineno, set_focus=False
                    )
            else:
                r = self.tag_prevrange("io_hyperlink", "@%d,%d" % (event.x, event.y))
                if r and len(r) == 2:
                    url = self.get(r[0], r[1])
                    if SIMPLE_URL_SPLIT_REGEX.match(url):
                        webbrowser.open(url)

        except Exception as e:
            logger.exception("Could not handle hyperlink click", exc_info=e)

    def _show_user_exception(self, user_exception):
        for line, frame_id, *_ in user_exception["items"]:

            tags = ("io", "stderr")
            if frame_id is not None:
                frame_tag = "frame_%d" % frame_id

                def handle_frame_click(event, frame_id=frame_id):
                    get_runner().send_command(InlineCommand("get_frame_info", frame_id=frame_id))
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
            pass  # TODO: disable stepping back

        self._clear_content(proposed_cut)

    def _clear_content(self, cut_idx):
        proposed_cut_float = float(cut_idx)
        for btn in list(self._squeeze_buttons):
            try:
                idx = self.index(btn)
                if idx is None or idx == "" or float(idx) < proposed_cut_float:
                    self._squeeze_buttons.remove(btn)
                    # looks like the widgets are not fully GC-d.
                    # At least avoid leaking big chunks of texts
                    btn.contained_text = None
                    btn.destroy()
            except Exception as e:
                logger.warning("Problem with a squeeze button, removing it", exc_info=e)
                if btn in self._squeeze_buttons:
                    self._squeeze_buttons.remove(btn)

        self.direct_delete("0.1", cut_idx)

    def _on_mouse_move(self, event=None):
        tags = self.tag_names("@%d,%d" % (event.x, event.y))
        if "value" in tags or "io_hyperlink" in tags:
            if self.cget("cursor") != "hand2":
                self.config(cursor="hand2")
        else:
            if self.cget("cursor"):
                self.config(cursor="")

    def _invalidate_current_data(self):
        """
        Grayes out input & output displayed so far
        """
        end_index = self.index("output_end")

        self.tag_add("inactive", "1.0", end_index)
        self.tag_remove("value", "1.0", end_index)

        while len(self.active_extra_tags) > 0:
            self.tag_remove(self.active_extra_tags.pop(), "1.0", "end")

    def get_lines_above_viewport_bottom(self, tag_name, n):
        end_index = self.index("@%d,%d lineend" % (self.winfo_height(), self.winfo_height()))
        start_index = self.index(end_index + " -50 lines")

        result = ""
        while True:
            r = self.tag_nextrange(tag_name, start_index, end_index)
            if not r:
                break
            result += self.get(r[0], r[1])
            start_index = r[1]

        return result

    def update_tty_mode(self):
        self.tty_mode = get_workbench().get_option("shell.tty_mode")

    def set_syntax_options(self, syntax_options):
        super().set_syntax_options(syntax_options)
        self.update_margin_color()

    def update_margin_color(self):
        if ui_utils.get_tk_version_info() >= (8, 6, 6):
            self.tag_configure("io", lmargincolor=get_syntax_options_for_tag("TEXT")["background"])

    def _hide_trailing_output(self, msg):
        pos = self.search(msg.text, index="end", backwards=True)
        if pos:
            end_pos = self.index("%s + %d chars" % (pos, len(msg.text)))
            if end_pos == self.index("output_end"):
                self.direct_delete(pos, end_pos)


class ShellText(BaseShellText):
    def __init__(self, master, view, cnf={}, **kw):
        super().__init__(master, view, cnf=cnf, **kw)
        self.bindtags(self.bindtags() + ("ShellText",))

        self.tag_bind("value", "<1>", self._value_click)
        self.tag_bind("value", "<ButtonRelease-1>", self._value_mouse_up)
        self.tag_bind("io_hyperlink", "<ButtonRelease-1>", self._handle_hyperlink)

        self.bind("<Motion>", self._on_mouse_move, True)

        get_workbench().bind("InputRequest", self._handle_input_request, True)
        get_workbench().bind("ProgramOutput", self._handle_program_output, True)
        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)
        get_workbench().bind("DebuggerResponse", self._handle_fancy_debugger_progress, True)
        get_workbench().bind("BackendRestart", self._on_backend_restart, True)
        get_workbench().bind("HideTrailingOutput", self._hide_trailing_output, True)


class SqueezedTextDialog(CommonDialog):
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

        explanation_label = ttk.Label(
            mainframe,
            text=tr(
                "For performance reasons, Shell avoids showing "
                + "very long lines in full (see Tools => Options => Shell).\n"
                + "Here you can interact with the original text fragment."
            ),
        )
        explanation_label.grid(row=0, column=0, sticky="nsew", padx=padding, pady=padding)

        self._wrap_var = tk.BooleanVar(False)
        self.wrap_checkbox = ttk.Checkbutton(
            mainframe,
            text=tr("Wrap text (may be slow)"),
            variable=self._wrap_var,
            onvalue=True,
            offvalue=False,
            command=self._on_wrap_changed,
        )
        self.wrap_checkbox.grid(row=1, padx=padding, pady=(0, padding // 2), sticky="w")

        self.text_frame = TextFrame(
            mainframe,
            text_class=TweakableText,
            height=10,
            width=80,
            relief="sunken",
            borderwidth=1,
            wrap="none",
        )
        self.text_frame.grid(row=2, column=0, padx=padding, sticky="nsew")
        self.text_frame.text.insert("1.0", button.contained_text)
        self.text_frame.text.set_read_only(True)

        button_frame = ttk.Frame(mainframe)
        button_frame.grid(row=3, column=0, padx=padding, pady=padding, sticky="nswe")
        button_frame.columnconfigure(2, weight=1)

        copy_caption = tr_btn("Copy to clipboard")
        copy_button = ttk.Button(
            button_frame, text=copy_caption, width=len(copy_caption), command=self._on_copy
        )
        copy_button.grid(row=0, column=1, sticky="w", padx=(0, padding))

        expand_caption = tr_btn("Expand in Shell")
        expand_button = ttk.Button(
            button_frame, text=expand_caption, width=len(expand_caption), command=self._on_expand
        )
        expand_button.grid(row=0, column=2, sticky="e", padx=padding)

        close_button = ttk.Button(button_frame, text=tr_btn("Close"), command=self._on_close)
        close_button.grid(row=0, column=3, sticky="e")

        self.bind("<Escape>", self._on_close, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.title(tr("Squeezed text (%d characters)") % len(self.content))

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


class PlotterCanvas(tk.Canvas):
    def __init__(self, master, text):
        self.master = master
        self.background = get_syntax_options_for_tag("TEXT")["background"]
        self.foreground = get_syntax_options_for_tag("TEXT")["foreground"]
        super().__init__(
            master,
            background=self.background,
            borderwidth=0,
            height=10000,  # size of the virtual drawing area
            width=10000,
            highlightthickness=0,
        )
        self.text = text

        self.x_scale = None
        self.x_scale = None
        self.range_start = -1
        self.range_end = 2
        self.range_block_size = 0
        self.value_range = 2
        self.last_legend = None
        self.font = tk.font.nametofont("TkDefaultFont")
        self.linespace = self.font.metrics("linespace")
        self.y_padding = self.linespace
        self.x_padding_left = -1  # makes sharper cut for partly hidden line
        self.x_padding_right = self.linespace
        self.fresh_range = True

        self.colors = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]
        self.range_block_sizes = [
            0.1,
            0.25,
            0.5,
            1,
            5,
            10,
            25,
            50,
            100,
            250,
            500,
            1000,
            2500,
            5000,
            10000,
        ]
        self.bind("<Configure>", self.on_resize, True)
        self.bind("<Button-1>", self.reset_range, True)

        self.create_close_button()

        get_workbench().bind("SyntaxThemeChanged", self.reload_theme_options, True)

    def create_close_button(self):
        self.close_img = get_workbench().get_image("tab-close")
        self.close_active_img = get_workbench().get_image("tab-close-active")

        self.close_rect = self.create_rectangle(
            self.winfo_width() - self.close_img.width() - self.linespace,
            self.linespace / 2,
            self.winfo_width(),
            self.linespace / 2 + self.close_img.height(),
            fill=self.background,
            width=0,
            tags=("close",),
        )

        self.close_button = self.create_image(
            self.winfo_width() - self.linespace / 2,
            self.linespace / 2,
            anchor="ne",
            image=self.close_img,
            activeimage=self.close_active_img,
            tags=("close",),
        )

        self.tag_bind("close", "<1>", self.on_close)

    def update_close_button(self):
        self.coords(
            self.close_rect,
            self.winfo_width() - self.close_img.width() - self.linespace / 1.5,
            self.linespace / 2,
            self.winfo_width() - self.linespace / 2,
            self.linespace / 2 + self.close_img.height(),
        )
        self.coords(self.close_button, self.winfo_width() - self.linespace / 2, self.linespace / 2)

    def on_close(self, event):
        self.master.toggle_plotter()

    def reset_range(self, event=None):
        self.fresh_range = True

    def get_num_steps(self):
        return 30

    def update_plot(self, force_clean=False):
        data_lines = []
        bottom_index = self.text.index(
            "@%d,%d" % (self.text.winfo_width(), self.text.winfo_height())
        )
        bottom_lineno = int(float(bottom_index))

        for i in range(bottom_lineno - self.get_num_steps(), bottom_lineno + 1):
            line_start_index = "%d.0" % i
            if i < 1 or "stdout" not in self.text.tag_names(line_start_index):
                data_lines.append(([], []))
            else:
                content = self.text.get(line_start_index, line_start_index + " lineend")
                data_lines.append(self.extract_pattern_and_numbers(content))

        # data_lines need to be transposed
        segments_by_color = []
        for i in range(100):
            segments = list(self.extract_series_segments(data_lines, i))
            if segments:
                segments_by_color.append(segments)
            else:
                break

        self.delete("segment")

        self.update_range(segments_by_color, force_clean)
        segment_count = self.draw_segments(segments_by_color)
        self.update_legend(data_lines, force_clean)

        self.delete("info")
        if segment_count == 0:
            info_text = (
                tr("Plotter visualizes series of\n" + "numbers printed to the Shell.")
                + "\n\n"
                + tr("See Help for details.")
            )

            self.create_text_with_background(
                self.winfo_width() / 2,
                self.winfo_height() / 2,
                text=info_text,
                anchor="center",
                justify="center",
                tags=("info",),
            )
            # self.delete("guide", "tick", "legend")
            # self.range_start = 0
            # self.range_end = 0
            self.tag_raise("info")

        self.fresh_range = False

    def update_legend(self, data_lines, force_clean=False):
        legend = None
        i = len(data_lines) - 2  # one before last
        while i >= 0:
            legend = data_lines[i][0]
            if legend and legend == data_lines[i + 1][0]:
                # found last legend, which covers at least 2 consecutive points
                break
            i -= 1

        if self.last_legend == legend and not force_clean:
            # just make sure it remains topmost
            self.tag_raise("legend")
            return

        self.delete("legend")

        if legend is None:
            return

        # add horizontal padding
        # legend[0] = " " + legend[0]
        # legend[-1] = legend[-1] + " "

        marker = "●"  # "●" "•"
        marker_width = self.font.measure(marker)
        full_text_width = self.font.measure(marker.join(legend))

        y = self.winfo_height() - self.linespace // 2
        x = self.winfo_width() - full_text_width - self.linespace

        self.create_rectangle(
            x - self.linespace // 4,
            y - self.linespace,
            x + full_text_width + self.linespace // 4,
            y,
            fill=self.background,
            width=0,
            tags=("legend",),
        )

        for i, part in enumerate(legend):
            if i > 0:
                self.create_text(
                    x,
                    y,
                    text=marker,
                    anchor="sw",
                    fill=self.colors[(i - 1) % len(self.colors)],
                    tags=("legend",),
                )
                x += marker_width

            self.create_text(x, y, text=part, anchor="sw", tags=("legend",), fill=self.foreground)
            x += self.font.measure(part)

        self.last_legend = legend

    def draw_segments(self, segments_by_color):
        count = 0
        for color, segments in enumerate(segments_by_color):
            for pos, nums in segments:
                self.draw_segment(color, pos, nums)
                count += 1

        # raise certain elements above segments
        self.tag_raise("tick")
        self.tag_raise("close")
        return count

    def draw_segment(self, color, pos, nums):

        x = self.x_padding_left + pos * self.x_scale

        args = []
        for num in nums:
            y = self.y_padding + (self.range_end - num) * self.y_scale
            args.extend([x, y])
            x += self.x_scale

        self.create_line(
            *args,
            width=2,
            fill=self.colors[color % len(self.colors)],
            tags=("segment",),
            # arrow may be confusing
            # and doesn't play nice with distinguising between
            # scrollback view and fresh_range view
            # arrow="last",
            # arrowshape=(3,5,3)
        )
        # self.current_segment_ids.append(line_id)

    def update_range(self, segments_by_color, clean):
        if not segments_by_color:
            return

        range_start = 2 ** 15
        range_end = -(2 ** 15)

        # if new block is using 3/4 of the width,
        # then don't consider old block's values anymore
        interest_position = 0
        for start_pos, nums in reversed(segments_by_color[0]):
            if start_pos < self.get_num_steps() / 10:
                interest_position = start_pos
                break

        assert isinstance(interest_position, int)
        for segments in segments_by_color:
            for start_pos, nums in segments:
                if start_pos >= interest_position:
                    range_start = min(range_start, *nums)
                    range_end = max(range_end, *nums)

        if interest_position == 0 and not self.fresh_range:
            # meaning we still care about old line's values
            range_start = min(range_start, self.range_start)
            range_end = max(range_end, self.range_end)

        if range_end == range_start:
            range_end += 1

        if (
            not clean
            and not self.fresh_range
            and self.x_scale is not None
            and range_end == self.range_end
            and range_start == self.range_start
        ):
            # don't recompute as nothing was changed
            return

        value_range = range_end - range_start
        range_block_size = value_range // 4
        # prefer round blocks
        for size in self.range_block_sizes:
            if size * 4 >= value_range:
                range_block_size = size
                break

        # extend to range block boundary
        if range_end % range_block_size != 0:
            range_end -= range_end % -range_block_size

        if range_start % range_block_size != 0:
            range_start -= range_start % range_block_size

        # not sure about these assertions when using floats
        # assert range_start % range_block_size == 0
        # assert range_end % range_block_size == 0, "range_end: %s, bs: %s" % (range_end, range_block_size)

        # remember
        self.range_start = range_start
        self.range_end = range_end
        self.value_range = range_end - range_start
        self.range_block_size = range_block_size

        available_height = self.winfo_height() - 2 * self.y_padding
        available_width = self.winfo_width() - self.x_padding_left - self.x_padding_right
        num_steps = self.get_num_steps()

        self.x_scale = available_width / (num_steps - 1)
        self.y_scale = available_height / self.value_range

        self.update_guides_and_ticks()

    def update_guides_and_ticks(self):
        self.delete("guide", "tick")
        value = self.range_start
        while value <= self.range_end:
            y = self.y_padding + (self.range_end - value) * self.y_scale

            # guide
            self.create_line(
                0, y, self.winfo_width(), y, tags=("guide",), dash=(2, 2), fill="#aaaaaa"
            )

            # tick
            if value == int(value):
                value = int(value)

            caption = " " + str(value) + " "
            self.create_text_with_background(
                self.linespace // 2, y, caption, anchor="w", tags=("tick",)
            )
            value += self.range_block_size

    def extract_pattern_and_numbers(self, line):
        parts = NUMBER_SPLIT_REGEX.split(line)
        if len(parts) < 2:
            return ([], [])

        assert len(parts) % 2 == 1

        pattern = []
        numbers = []
        for i in range(0, len(parts), 2):
            pattern.append(parts[i])

        for i in range(1, len(parts), 2):
            numbers.append(float(parts[i]))

        return (pattern, numbers)

    def extract_series_segments(self, data_lines, series_nr):
        """Yields numbers which form connected multilines on graph
        Each segment is pair of starting position and numbers"""
        segment = (0, [])
        prev_pattern = None
        for i, (pattern, nums) in enumerate(data_lines):
            if len(nums) <= series_nr or pattern != prev_pattern:
                # break the segment
                if len(segment[1]) > 1:
                    yield segment
                segment = (i, [])

            if len(nums) > series_nr:
                segment[1].append(nums[series_nr])

            prev_pattern = pattern

        if len(segment[1]) > 1:
            yield segment

    def create_text_with_background(
        self, x, y, text, anchor="w", justify="left", background=None, tags=()
    ):
        if background is None:
            background = self.background

        width = 0
        lines = text.splitlines()
        for line in lines:
            width = max(width, self.font.measure(line))

        height = len(lines) * self.linespace

        rect_x = x
        rect_y = y
        if anchor == "center":
            rect_x = x - width / 2
            rect_y = y - height / 2
        elif anchor == "w":
            rect_y = y - height / 2
        else:
            "TODO:"

        self.create_rectangle(
            rect_x, rect_y, rect_x + width, rect_y + height, fill=background, width=0, tags=tags
        )
        self.create_text(
            x, y, anchor=anchor, text=text, tags=tags, fill=self.foreground, justify=justify
        )

    def reload_theme_options(self, event):
        self.background = get_syntax_options_for_tag("TEXT")["background"]
        self.foreground = get_syntax_options_for_tag("TEXT")["foreground"]
        self.configure(background=self.background)
        self.itemconfig(self.close_rect, fill=self.background)
        self.update_plot(True)

    def on_resize(self, event):
        if self.winfo_width() > 10:
            get_workbench().set_option("view.plotter_width", self.winfo_width())
        self.update_plot(True)
        self.update_close_button()
        self.master.resize_plotter()
