# -*- coding: utf-8 -*-

"""
Adds debugging commands and features. 
"""

import ast
import logging
import os.path
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from typing import List, Union  # @UnusedImport

from thonny import (
    ast_utils,
    code,
    get_runner,
    get_workbench,
    memory,
    misc_utils,
    ui_utils,
)
from thonny.codeview import CodeView, get_syntax_options_for_tag
from thonny.common import DebuggerCommand, InlineCommand
from thonny.config_ui import ConfigurationPage
from thonny.memory import VariablesFrame
from thonny.misc_utils import shorten_repr
from thonny.tktextext import TextFrame
from thonny.ui_utils import select_sequence

_current_debugger = None


class Debugger:
    def __init__(self):
        self._last_progress_message = None
        self._last_brought_out_frame_id = None
        self._editor_context_menu = None

    def check_issue_command(self, command, **kwargs):
        cmd = DebuggerCommand(command, **kwargs)
        self._last_debugger_command = cmd

        if get_runner().is_waiting_debugger_command():
            logging.debug("_check_issue_debugger_command: %s", cmd)

            # tell VM the state we are seeing
            cmd.setdefault(
                frame_id=self._last_progress_message.stack[-1].id,
                breakpoints=code.get_current_breakpoints(),
                cursor_position=self.get_run_to_cursor_breakpoint(),
            )

            cmd.setdefault(
                state=self._last_progress_message.stack[-1].event,
                focus=self._last_progress_message.stack[-1].focus,
            )

            get_runner().send_command(cmd)
        else:
            logging.debug("Bad state for sending debugger command " + str(command))

    def get_run_to_cursor_breakpoint(self):
        return None

    def command_enabled(self, command):
        if not get_runner().is_waiting_debugger_command():
            return False

        if command == "run_to_cursor":
            return self.get_run_to_cursor_breakpoint() is not None
        elif command == "step_back":
            return (self._last_progress_message 
                    and self._last_progress_message["tracer_class"] == "NiceTracer")
        else:
            return True

    def handle_debugger_progress(self, msg):
        self._last_brought_out_frame_id = None

    def close(self) -> None:
        self._last_brought_out_frame_id = None

        if get_workbench().get_option("debugger.automatic_stack_view"):
            get_workbench().hide_view("StackView")

    def get_frame_by_id(self, frame_id):
        for frame_info in self._last_progress_message.stack:
            if frame_info.id == frame_id:
                return frame_info

        raise ValueError("Could not find frame %d" % frame_id)

    def bring_out_frame(self, frame_id, force=False):
        # called by StackView
        raise NotImplementedError()

    def get_editor_context_menu(self):
        def create_edit_command_handler(virtual_event_sequence):
            def handler(event=None):
                widget = get_workbench().focus_get()
                if widget:
                    return widget.event_generate(virtual_event_sequence)

                return None

            return handler

        if self._editor_context_menu is None:
            menu = tk.Menu(get_workbench())
            menu.add(
                "command",
                label="Run to cursor",
                command=lambda: self.check_issue_command("run_to_cursor"),
            )
            menu.add("separator")
            menu.add(
                "command", label="Copy", command=create_edit_command_handler("<<Copy>>")
            )
            menu.add(
                "command",
                label="Select all",
                command=create_edit_command_handler("<<SelectAll>>"),
            )
            self._editor_context_menu = menu

        return self._editor_context_menu


class SingleWindowDebugger(Debugger):
    def __init__(self):
        super().__init__()
        self._last_frame_visualizer = None
        # Make sure StackView is created
        get_workbench().get_view("StackView")

    def get_run_to_cursor_breakpoint(self):
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if editor:
            filename = editor.get_filename()
            selection = editor.get_code_view().get_selected_range()
            lineno = selection.lineno
            if filename and lineno:
                return filename, lineno

        return None

    def handle_debugger_progress(self, msg):
        super().handle_debugger_progress(msg)
        self._last_progress_message = msg
        self.bring_out_frame(self._last_progress_message.stack[-1].id, force=True)

        if get_workbench().get_option("debugger.automatic_stack_view"):
            if len(msg.stack) > 1:
                get_workbench().show_view("StackView")

        get_workbench().get_view("ExceptionView").set_exception(
            msg["exception_info"]["lines_with_frame_info"]
        )

    def close(self):
        super().close()
        if self._last_frame_visualizer is not None:
            self._last_frame_visualizer.close()
            self._last_frame_visualizer = None

    def bring_out_frame(self, frame_id, force=False):
        if not force and frame_id == self._last_brought_out_frame_id:
            return

        self._last_brought_out_frame_id = frame_id

        frame_info = self.get_frame_by_id(frame_id)

        if (
            self._last_frame_visualizer is not None
            and self._last_frame_visualizer._frame_id != frame_info.id
        ):
            self._last_frame_visualizer.close()
            self._last_frame_visualizer = None

        if self._last_frame_visualizer is None:
            self._last_frame_visualizer = EditorVisualizer(frame_info)

        self._last_frame_visualizer._update_this_frame(
            self._last_progress_message, frame_info
        )

        # show variables
        var_view = get_workbench().get_view("VariablesView")
        if frame_info.code_name == "<module>":
            var_view.show_globals(frame_info.globals, frame_info.module_name)
        else:
            var_view.show_frame_variables(
                frame_info.locals,
                frame_info.globals,
                frame_info.freevars,
                frame_info.module_name
                if frame_info.code_name == "<module>"
                else frame_info.code_name,
            )


class StackedWindowsDebugger(Debugger):
    def __init__(self):
        super().__init__()
        self._main_frame_visualizer = None

    def get_run_to_cursor_breakpoint(self):
        visualizer = self._get_topmost_selected_visualizer()
        if visualizer:
            assert isinstance(visualizer._text_frame, CodeView)
            code_view = visualizer._text_frame
            selection = code_view.get_selected_range()

            target_lineno = visualizer._firstlineno - 1 + selection.lineno
            return visualizer._filename, target_lineno
        else:
            return None

    def handle_debugger_progress(self, msg):
        super().handle_debugger_progress(msg)

        self._last_progress_message = msg

        main_frame_id = msg.stack[0].id

        # clear obsolete main frame visualizer
        if (
            self._main_frame_visualizer
            and self._main_frame_visualizer.get_frame_id() != main_frame_id
        ):
            self._main_frame_visualizer.close()
            self._main_frame_visualizer = None

        if not self._main_frame_visualizer:
            self._main_frame_visualizer = EditorVisualizer(msg.stack[0])

        self._main_frame_visualizer.update_this_and_next_frames(msg)

        self.bring_out_frame(msg.stack[-1].id, force=True)

        get_workbench().get_view("ExceptionView").set_exception(
            msg["exception_info"]["lines_with_frame_info"]
        )

    def close(self):
        super().close()
        if self._main_frame_visualizer is not None:
            self._main_frame_visualizer.close()
            self._main_frame_visualizer = None

    def _get_topmost_selected_visualizer(self):
        visualizer = self._main_frame_visualizer
        if visualizer is None:
            return None

        while visualizer._next_frame_visualizer is not None:
            visualizer = visualizer._next_frame_visualizer

        topmost_text_widget = visualizer._text
        focused_widget = get_workbench().focus_get()

        if focused_widget is None:
            return None
        elif focused_widget == topmost_text_widget:
            return visualizer
        else:
            return None

    def bring_out_frame(self, frame_id, force=False):
        if not force and frame_id == self._last_brought_out_frame_id:
            return

        self._last_brought_out_frame_id = frame_id

        self._main_frame_visualizer.bring_out_frame(frame_id)

        # show variables
        var_view = get_workbench().get_view("VariablesView")
        frame_info = self.get_frame_by_id(frame_id)
        var_view.show_globals(frame_info.globals, frame_info.module_name)


class FrameVisualizer:
    """
    Is responsible for stepping through statements and updating corresponding UI
    in Editor-s, FunctionCallDialog-s, ModuleDialog-s
    """

    def __init__(self, text_frame, frame_info):
        self._text_frame = text_frame
        self._text = text_frame.text
        self._frame_info = frame_info
        self._frame_id = frame_info.id
        self._filename = frame_info.filename
        self._firstlineno = None
        self._expression_box = ExpressionBox(text_frame)
        self._note_box = ui_utils.NoteBox(text_frame.winfo_toplevel())
        self._next_frame_visualizer = None
        self._text.set_read_only(True)
        self._line_debug = frame_info.current_statement is None

        self._reconfigure_tags()

    def _reconfigure_tags(self):
        for tag in ["active_focus", "exception_focus"]:
            conf = get_syntax_options_for_tag(tag).copy()
            if self._line_debug:
                # meaning data comes from line-debug
                conf["borderwidth"] = 0

            self._text.tag_configure(tag, **conf)

    def close(self):
        if self._next_frame_visualizer:
            self._next_frame_visualizer.close()
            self._next_frame_visualizer = None

        self._text.set_read_only(False)
        self._remove_focus_tags()
        self._expression_box.clear_debug_view()
        self.close_note()

    def get_frame_id(self):
        return self._frame_id

    def update_this_and_next_frames(self, msg):
        """Must not be used on obsolete frame"""

        # debug("State: %s, focus: %s", msg.state, msg.focus)

        frame_info, next_frame_info = self._find_this_and_next_frame(msg.stack)
        self._update_this_frame(msg, frame_info)

        # clear obsolete next frame visualizer
        if self._next_frame_visualizer and (
            not next_frame_info
            or self._next_frame_visualizer.get_frame_id() != next_frame_info.id
        ):
            self._next_frame_visualizer.close()
            self._next_frame_visualizer = None

        if next_frame_info and not self._next_frame_visualizer:
            self._next_frame_visualizer = self._create_next_frame_visualizer(
                next_frame_info
            )

        if self._next_frame_visualizer:
            self._next_frame_visualizer.update_this_and_next_frames(msg)

    def _remove_focus_tags(self):
        for name in [
            "exception_focus",
            "active_focus",
            "completed_focus",
            "suspended_focus",
            "sel",
        ]:
            self._text.tag_remove(name, "0.0", "end")

    def _update_this_frame(self, msg, frame_info):
        self._frame_info = frame_info
        self._remove_focus_tags()

        if frame_info.event == "line":
            if frame_info.id in msg["exception_info"]["affected_frame_ids"]:
                self._tag_range(frame_info.focus, "exception_focus")
            else:
                self._tag_range(frame_info.focus, "active_focus")
        else:
            if "statement" in frame_info.event:
                if msg["exception_info"]["msg"] is not None:
                    stmt_tag = "exception_focus"
                elif frame_info.event.startswith("before"):
                    stmt_tag = "active_focus"
                else:
                    stmt_tag = "completed_focus"
            else:
                assert "expression" in frame_info.event
                stmt_tag = "suspended_focus"

            self._tag_range(frame_info.current_statement, stmt_tag)

        self._expression_box.update_expression(msg, frame_info)

        if frame_info.id in msg["exception_info"]["affected_frame_ids"]:
            self._show_exception(
                msg["exception_info"]["lines_with_frame_info"], frame_info
            )

    def _show_exception(self, lines, frame_info):
        last_line_text = lines[-1][0]
        self.show_note(
            last_line_text.strip() + " ",
            ("...", lambda _: get_workbench().show_view("ExceptionView")),
            focus=frame_info.focus,
        )

    def _find_this_and_next_frame(self, stack):
        for i in range(len(stack)):
            if stack[i].id == self._frame_id:
                if i == len(stack) - 1:  # last frame
                    return stack[i], None
                else:
                    return stack[i], stack[i + 1]

        raise AssertionError("Frame doesn't exist anymore")

    def _tag_range(self, text_range, tag):
        # For most statements I want to highlight block of whole lines
        # but for pseudo-statements (like header in for-loop) I want to highlight only the indicated range

        line_prefix = self._text.get(
            "%d.0" % text_range.lineno,
            "%d.%d" % (text_range.lineno, text_range.col_offset),
        )
        if line_prefix.strip():
            # pseudo-statement
            first_line = text_range.lineno
            last_line = text_range.end_lineno
            self._text.tag_add(
                tag,
                "%d.%d" % (text_range.lineno, text_range.col_offset),
                "%d.%d" % (text_range.end_lineno, text_range.end_col_offset),
            )
        else:
            # normal statement
            first_line, first_col, last_line = self._get_text_range_block(text_range)

            for lineno in range(first_line, last_line + 1):
                self._text.tag_add(
                    tag, "%d.%d" % (lineno, first_col), "%d.0" % (lineno + 1)
                )

        self._text.update_idletasks()
        self._text.see("%d.0" % (last_line))
        self._text.see("%d.0" % (first_line))

        if last_line - first_line < 3:
            # if it's safe to assume that whole code fits into screen
            # then scroll it down a bit so that expression view doesn't hide behind
            # lower edge of the editor
            self._text.update_idletasks()
            self._text.see("%d.0" % (first_line + 3))

    def _get_text_range_block(self, text_range):
        first_line = text_range.lineno - self._firstlineno + 1
        last_line = (
            text_range.end_lineno
            - self._firstlineno
            + (1 if text_range.end_col_offset > 0 else 0)
        )
        first_line_content = self._text.get("%d.0" % first_line, "%d.end" % first_line)
        if first_line_content.strip().startswith("elif "):
            first_col = first_line_content.find("elif ")
        else:
            first_col = text_range.col_offset

        return (first_line, first_col, last_line)

    def _create_next_frame_visualizer(self, next_frame_info):
        if next_frame_info.code_name == "<module>":
            return ModuleLoadDialog(self._text, next_frame_info)
        else:
            dialog = FunctionCallDialog(self._text.master, next_frame_info)

            if self._expression_box.winfo_ismapped():
                dialog.title(self._expression_box.get_focused_text())
            else:
                dialog.title("Function call at " + hex(self._frame_id))

            return dialog

    def bring_out_frame(self, frame_id):
        if self._frame_id == frame_id:
            self.bring_out_this_frame()
        elif self._next_frame_visualizer is not None:
            self._next_frame_visualizer.bring_out_frame(frame_id)

    def bring_out_this_frame(self):
        pass

    def show_note(
        self, *content_items: Union[str, List], target=None, focus=None
    ) -> None:
        if target is None:
            target = self._text

        self._note_box.show_note(*content_items, target=target, focus=focus)

    def close_note(self):
        self._note_box.close()


class EditorVisualizer(FrameVisualizer):
    """
    Takes care of stepping in the editor 
    (main module in case of StackedWindowsDebugger) 
    """

    def __init__(self, frame_info):
        self.editor = (
            get_workbench()
            .get_editor_notebook()
            .show_file(frame_info.filename, set_focus=False)
        )
        FrameVisualizer.__init__(self, self.editor.get_code_view(), frame_info)
        self._firstlineno = 1

    def _update_this_frame(self, msg, frame_info):
        FrameVisualizer._update_this_frame(self, msg, frame_info)
        if msg.in_present:
            self._decorate_editor_title("")
        else:
            self._decorate_editor_title("   <<< REPLAYING >>> ")

    def _decorate_editor_title(self, suffix):
        self.editor.master.update_editor_title(
            self.editor, self.editor.get_title() + suffix
        )

    def bring_out_this_frame(self):
        get_workbench().focus_set()

    def close(self):
        super().close()
        self._decorate_editor_title("")


class ExpressionBox(tk.Text):
    def __init__(self, codeview):

        opts = dict(
            height=1,
            width=1,
            relief=tk.RAISED,
            background="#DCEDF2",
            borderwidth=1,
            highlightthickness=0,
            padx=7,
            pady=7,
            wrap=tk.NONE,
            font="EditorFont",
        )

        opts.update(get_syntax_options_for_tag("expression_box"))

        tk.Text.__init__(self, codeview.winfo_toplevel(), **opts)
        self._codeview = codeview

        self._last_focus = None
        self._last_root_expression = None

        self.tag_configure("value", get_syntax_options_for_tag("value"))
        self.tag_configure("before", get_syntax_options_for_tag("active_focus"))
        self.tag_configure("after", get_syntax_options_for_tag("completed_focus"))
        self.tag_configure("exception", get_syntax_options_for_tag("exception_focus"))
        self.tag_raise("exception", "before")
        self.tag_raise("exception", "after")

    def update_expression(self, msg, frame_info):
        focus = frame_info.focus
        event = frame_info.event

        if frame_info.current_root_expression is not None:
            self._load_expression(
                frame_info.filename, frame_info.current_root_expression
            )
            for subrange, value in frame_info.current_evaluations:
                self._replace(subrange, value)
            if "expression" in event:
                # Event may be also after_statement_again
                self._highlight_range(
                    focus,
                    event,
                    frame_info.id in msg["exception_info"]["affected_frame_ids"],
                )

            self._update_position(frame_info.current_root_expression)
            self._update_size()

        else:
            # hide and clear on non-expression events
            self.clear_debug_view()

        self._last_focus = focus
        self._last_root_expression = frame_info.current_root_expression

    def get_focused_text(self):
        if self._last_focus:
            start_mark = self._get_mark_name(
                self._last_focus.lineno, self._last_focus.col_offset
            )
            end_mark = self._get_mark_name(
                self._last_focus.end_lineno, self._last_focus.end_col_offset
            )
            return self.get(start_mark, end_mark)
        else:
            return ""

    def clear_debug_view(self):
        self.place_forget()
        self._main_range = None
        self._last_focus = None
        self._clear_expression()

    def _clear_expression(self):
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", "end")

        self.mark_unset(*self.mark_names())
        self.delete("1.0", "end")

    def _replace(self, focus, value):
        start_mark = self._get_mark_name(focus.lineno, focus.col_offset)
        end_mark = self._get_mark_name(focus.end_lineno, focus.end_col_offset)

        self.delete(start_mark, end_mark)

        id_str = memory.format_object_id(value.id)
        if get_workbench().in_heap_mode():
            value_str = id_str
        else:
            value_str = shorten_repr(value.repr, 100)

        object_tag = "object_" + str(value.id)
        self.insert(start_mark, value_str, ("value", object_tag))
        if misc_utils.running_on_mac_os():
            sequence = "<Command-Button-1>"
        else:
            sequence = "<Control-Button-1>"
        self.tag_bind(
            object_tag,
            sequence,
            lambda _: get_workbench().event_generate(
                "ObjectSelect", object_id=value.id
            ),
        )

    def _load_expression(self, filename, text_range):
        with open(filename, "rb") as fp:
            whole_source = fp.read()

        root = ast_utils.parse_source(whole_source, filename)
        main_node = ast_utils.find_expression(root, text_range)

        source = ast_utils.extract_text_range(whole_source, text_range)
        logging.debug("EV.load_exp: %s", (text_range, main_node, source))

        self._clear_expression()

        self.insert("1.0", source)

        # create node marks
        def _create_index(lineno, col_offset):
            local_lineno = lineno - main_node.lineno + 1
            if lineno == main_node.lineno:
                local_col_offset = col_offset - main_node.col_offset
            else:
                local_col_offset = col_offset

            return str(local_lineno) + "." + str(local_col_offset)

        for node in ast.walk(main_node):
            if "lineno" in node._attributes:
                index1 = _create_index(node.lineno, node.col_offset)
                index2 = _create_index(node.end_lineno, node.end_col_offset)

                start_mark = self._get_mark_name(node.lineno, node.col_offset)
                if not start_mark in self.mark_names():
                    self.mark_set(start_mark, index1)
                    # print("Creating mark", start_mark, index1)
                    self.mark_gravity(start_mark, tk.LEFT)

                end_mark = self._get_mark_name(node.end_lineno, node.end_col_offset)
                if not end_mark in self.mark_names():
                    self.mark_set(end_mark, index2)
                    # print("Creating mark", end_mark, index2)
                    self.mark_gravity(end_mark, tk.RIGHT)

    def _get_mark_name(self, lineno, col_offset):
        return str(lineno) + "_" + str(col_offset)

    def _get_tag_name(self, node_or_text_range):
        return (
            str(node_or_text_range.lineno)
            + "_"
            + str(node_or_text_range.col_offset)
            + "_"
            + str(node_or_text_range.end_lineno)
            + "_"
            + str(node_or_text_range.end_col_offset)
        )

    def _highlight_range(self, text_range, state, has_exception):
        logging.debug("EV._highlight_range: %s", text_range)
        self.tag_remove("after", "1.0", "end")
        self.tag_remove("before", "1.0", "end")
        self.tag_remove("exception", "1.0", "end")

        if state.startswith("after"):
            tag = "after"
        elif state.startswith("before"):
            tag = "before"
        else:
            return

        start_index = self._get_mark_name(text_range.lineno, text_range.col_offset)
        end_index = self._get_mark_name(
            text_range.end_lineno, text_range.end_col_offset
        )
        self.tag_add(tag, start_index, end_index)

        if has_exception:
            self.tag_add("exception", start_index, end_index)

    def _update_position(self, text_range):
        self._codeview.update_idletasks()
        text_line_number = text_range.lineno - self._codeview._first_line_number + 1
        bbox = self._codeview.text.bbox(
            str(text_line_number) + "." + str(text_range.col_offset)
        )

        if isinstance(bbox, tuple):
            x = bbox[0] - self._codeview.text.cget("padx") + 6
            y = bbox[1] - self._codeview.text.cget("pady") - 6
        else:
            x = 30
            y = 30

        widget = self._codeview.text
        while widget != self.winfo_toplevel():
            x += widget.winfo_x()
            y += widget.winfo_y()
            widget = widget.master

        self.place(x=x, y=y, anchor=tk.NW)
        self.update_idletasks()

    def _update_size(self):
        content = self.get("1.0", tk.END)
        lines = content.splitlines()
        self["height"] = len(lines)
        self["width"] = max(map(len, lines))


class DialogVisualizer(tk.Toplevel, FrameVisualizer):
    def __init__(self, master, frame_info):
        tk.Toplevel.__init__(self, master)

        self.transient(master)
        if misc_utils.running_on_windows():
            self.wm_attributes("-toolwindow", 1)

        # TODO: take size from prefs
        editor_notebook = get_workbench().get_editor_notebook()
        if master.winfo_toplevel() == get_workbench():
            position_reference = editor_notebook
        else:
            # align to previous frame
            position_reference = master.winfo_toplevel()

        self.geometry(
            "{}x{}+{}+{}".format(
                editor_notebook.winfo_width(),
                editor_notebook.winfo_height() - 20,
                position_reference.winfo_rootx(),
                position_reference.winfo_rooty(),
            )
        )
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<FocusIn>", self._on_focus, True)

        self._init_layout_widgets(master, frame_info)
        FrameVisualizer.__init__(self, self._text_frame, frame_info)
        self._firstlineno = frame_info.firstlineno

        self._load_code(frame_info)
        self._text_frame.text.focus()

    def _init_layout_widgets(self, master, frame_info):
        self.main_frame = ttk.Frame(
            self
        )  # just a backgroud behind padding of main_pw, without this OS X leaves white border
        self.main_frame.grid(sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.main_pw = ui_utils.AutomaticPanedWindow(
            self.main_frame, orient=tk.VERTICAL
        )
        self.main_pw.grid(sticky=tk.NSEW, padx=10, pady=10)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        self._code_book = ttk.Notebook(self.main_pw)
        self._text_frame = CodeView(
            self._code_book, first_line_number=frame_info.firstlineno, font="EditorFont"
        )
        self._code_book.add(self._text_frame, text="Source")
        self.main_pw.add(self._code_book, minsize=100)

    def _load_code(self, frame_info):
        self._text_frame.set_content(frame_info.source)

    def _update_this_frame(self, msg, frame_info):
        FrameVisualizer._update_this_frame(self, msg, frame_info)

    def bring_out_this_frame(self):
        self.focus_set()  # no effect when clicking on stack view
        var_view = get_workbench().get_view("VariablesView")
        var_view.show_globals(self._frame_info.globals, self._frame_info.module_name)

    def _on_focus(self, event):
        # TODO: bring out main frame when main window gets focus
        self.bring_out_this_frame()

    def _on_close(self):
        showinfo(
            "Can't close yet", 
            'Use "Stop" command if you want to cancel debugging',
            parent=get_workbench()
        )

    def close(self):
        FrameVisualizer.close(self)
        self.destroy()


class FunctionCallDialog(DialogVisualizer):
    def __init__(self, master, frame_info):
        DialogVisualizer.__init__(self, master, frame_info)

    def _init_layout_widgets(self, master, frame_info):
        DialogVisualizer._init_layout_widgets(self, master, frame_info)
        self._locals_book = ttk.Notebook(self.main_pw)
        self._locals_frame = VariablesFrame(self._locals_book)
        self._locals_book.add(self._locals_frame, text="Local variables")
        self.main_pw.add(self._locals_book, minsize=100)

    def _load_code(self, frame_info):
        DialogVisualizer._load_code(self, frame_info)

        function_label = frame_info.code_name

        # change tab label
        self._code_book.tab(self._text_frame, text=function_label)

    def _update_this_frame(self, msg, frame_info):
        DialogVisualizer._update_this_frame(self, msg, frame_info)
        self._locals_frame.update_variables(frame_info.locals)


class ModuleLoadDialog(DialogVisualizer):
    def __init__(self, text_frame, frame_info):
        DialogVisualizer.__init__(self, text_frame, frame_info)


class StackView(ui_utils.TreeFrame):
    def __init__(self, master):
        super().__init__(
            master,
            ("function", "location", "id"),
            displaycolumns=("function", "location"),
        )

        # self.tree.configure(show="tree")
        self.tree.column("#0", width=0, anchor=tk.W, stretch=False)
        self.tree.column("function", width=120, anchor=tk.W, stretch=False)
        self.tree.column("location", width=450, anchor=tk.W, stretch=True)

        self.tree.heading("function", text="Function", anchor=tk.W)
        self.tree.heading("location", text="Location", anchor=tk.W)

        get_workbench().bind("DebuggerResponse", self._update_stack, True)
        get_workbench().bind(
            "ToplevelResponse", lambda e=None: self._clear_tree(), True
        )

    def _update_stack(self, msg):
        self._clear_tree()
        for frame in msg.stack:
            lineno = frame.focus.lineno

            node_id = self.tree.insert("", "end")
            self.tree.set(node_id, "function", frame.code_name)
            self.tree.set(
                node_id,
                "location",
                "%s, line %s" % (os.path.basename(frame.filename), lineno),
            )
            self.tree.set(node_id, "id", frame.id)

        # select last frame
        self.tree.see(node_id)
        self.tree.selection_add(node_id)
        self.tree.focus(node_id)

    def on_select(self, event):
        iid = self.tree.focus()
        if iid != "":
            # assuming id is in the last column
            frame_id = self.tree.item(iid)["values"][-1]
            if _current_debugger is not None:
                _current_debugger.bring_out_frame(frame_id)


class ExceptionView(TextFrame):
    def __init__(self, master):
        super().__init__(
            master,
            borderwidth=0,
            relief="solid",
            undo=False,
            read_only=True,
            font="TkDefaultFont",
            foreground=get_syntax_options_for_tag("stderr")["foreground"],
            highlightthickness=0,
            padx=5,
            pady=5,
            wrap="char",
            horizontal_scrollbar=False,
        )

        self.text.tag_configure("hyperlink", **get_syntax_options_for_tag("hyperlink"))
        self.text.tag_bind("hyperlink", "<Enter>", self._hyperlink_enter)
        self.text.tag_bind("hyperlink", "<Leave>", self._hyperlink_leave)
        get_workbench().bind("ToplevelResponse", self._on_toplevel_response, True)

        self._prev_exception = None

        self._show_description()

    def _show_description(self):
        self.text.configure(foreground=get_syntax_options_for_tag("TEXT")["foreground"])
        self.text.direct_insert(
            "end",
            "If last command raised an exception then this view will show the stacktrace.",
        )

    def set_exception(self, exception_lines_with_frame_info):
        if exception_lines_with_frame_info == self._prev_exception:
            return

        self.text.direct_delete("1.0", "end")

        if exception_lines_with_frame_info is None:
            self._show_description()
            return

        self.text.configure(
            foreground=get_syntax_options_for_tag("stderr")["foreground"]
        )
        for line, frame_id, filename, lineno in exception_lines_with_frame_info:

            if frame_id is not None:
                frame_tag = "frame_%d" % frame_id

                def handle_frame_click(
                    event, frame_id=frame_id, filename=filename, lineno=lineno
                ):
                    get_runner().send_command(
                        InlineCommand("get_frame_info", frame_id=frame_id)
                    )
                    if os.path.exists(filename):
                        get_workbench().get_editor_notebook().show_file(
                            filename, lineno, set_focus=False
                        )

                self.text.tag_bind(frame_tag, "<1>", handle_frame_click, True)

                start = max(line.find("File"), 0)
                end = line.replace("\r", "").find("\n")
                if end < 10:
                    end = len(line)

                self.text.direct_insert("end", line[:start])
                self.text.direct_insert(
                    "end", line[start:end], ("hyperlink", frame_tag)
                )
                self.text.direct_insert("end", line[end:])

            else:
                self.text.direct_insert("end", line)

        self._prev_exception = exception_lines_with_frame_info

    def _on_toplevel_response(self, msg):
        if "user_exception" in msg:
            self.set_exception(msg["user_exception"]["items"])
        else:
            self.set_exception(None)

    def _hyperlink_enter(self, event):
        self.text.config(cursor="hand2")

    def _hyperlink_leave(self, event):
        self.text.config(cursor="")


def _debugger_command_enabled(command):
    if _current_debugger is None:
        return False
    else:
        return _current_debugger.command_enabled(command)


def _issue_debugger_command(command):
    if _current_debugger is None:
        raise AssertionError("Trying to send debugger command without debugger")
    else:
        return _current_debugger.check_issue_command(command)


def _start_debug_enabled():
    return (
        _current_debugger is None
        and get_workbench().get_editor_notebook().get_current_editor() is not None
        and "debug" in get_runner().supported_features()
    )


def _request_debug(command_name):
    # Don't assume Debug command gets issued after this
    # This may just call the %cd command
    # or the user may deny saving current editor 
    get_runner().execute_current(command_name)

def _debug_accepted(event):
    # Called when proxy accepted the debug command
    global _current_debugger
    cmd = event.command
    if cmd.get("name") in ["Debug", "FastDebug"]:
        assert _current_debugger is None
        if get_workbench().get_option("debugger.single_window"):
            _current_debugger = SingleWindowDebugger()
        else:
            _current_debugger = StackedWindowsDebugger()

def _handle_debugger_progress(msg):
    global _current_debugger
    assert _current_debugger is not None
    _current_debugger.handle_debugger_progress(msg)

def _handle_toplevel_response(msg):
    global _current_debugger
    if _current_debugger is not None:
        _current_debugger.close()
        _current_debugger = None    

class DebuggerConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        self.add_checkbox(
            "debugger.single_window",
            "Use editors and Stack view for presenting call frames",
            tooltip="Presents the concept of stack like most professional IDE-s",
        )
        self.add_checkbox(
            "debugger.automatic_stack_view",
            "Open and close Stack view automatically",
            tooltip="Opens the Stack view on first call and "
            + "closes it when program returns to main frame.",
        )


def get_current_debugger():
    return _current_debugger


def load_plugin() -> None:

    get_workbench().set_default("debugger.single_window", False)
    get_workbench().set_default("debugger.automatic_stack_view", True)

    get_workbench().add_command(
        "debug",
        "run",
        "Debug current script (nicer)",
        lambda: _request_debug("Debug"),
        caption="Debug",
        tester=_start_debug_enabled,
        default_sequence="<Control-F5>",
        group=10,
        image="debug-current-script",
        include_in_toolbar=True,
    )

    get_workbench().add_command(
        "debuglite",
        "run",
        "Debug current script (faster)",
        lambda: _request_debug("FastDebug"),
        caption="Fast-debug",
        tester=_start_debug_enabled,
        default_sequence="<Shift-F5>",
        group=10,
    )

    get_workbench().add_command(
        "step_over",
        "run",
        "Step over",
        lambda: _issue_debugger_command("step_over"),
        caption="Over",
        tester=lambda: _debugger_command_enabled("step_over"),
        default_sequence="<F6>",
        group=30,
        image="step-over",
        include_in_toolbar=True,
    )

    get_workbench().add_command(
        "step_into",
        "run",
        "Step into",
        lambda: _issue_debugger_command("step_into"),
        caption="Into",
        tester=lambda: _debugger_command_enabled("step_into"),
        default_sequence="<F7>",
        group=30,
        image="step-into",
        include_in_toolbar=True,
    )

    get_workbench().add_command(
        "step_out",
        "run",
        "Step out",
        lambda: _issue_debugger_command("step_out"),
        caption="Out",
        tester=lambda: _debugger_command_enabled("step_out"),
        group=30,
        image="step-out",
        include_in_toolbar=True,
    )

    get_workbench().add_command(
        "resume",
        "run",
        "Resume",
        lambda: _issue_debugger_command("resume"),
        caption="Resume",
        tester=lambda: _debugger_command_enabled("resume"),
        default_sequence="<F8>",
        group=30,
        image="resume",
        include_in_toolbar=True,
    )

    get_workbench().add_command(
        "run_to_cursor",
        "run",
        "Run to cursor",
        lambda: _issue_debugger_command("run_to_cursor"),
        tester=lambda: _debugger_command_enabled("run_to_cursor"),
        default_sequence=select_sequence("<Control-F8>", "<Control-F8>"),
        group=30,
        image="run-to-cursor",
        include_in_toolbar=False,
    )

    get_workbench().add_command(
        "step_back",
        "run",
        "Step back",
        lambda: _issue_debugger_command("step_back"),
        caption="Back",
        tester=lambda: _debugger_command_enabled("step_back"),
        default_sequence=select_sequence("<Control-b>", "<Command-b>"),
        group=30,
    )

    get_workbench().add_view(StackView, "Stack", "se")
    get_workbench().add_view(ExceptionView, "Exception", "s")
    get_workbench().add_configuration_page("Debugger", DebuggerConfigurationPage)
    get_workbench().bind("DebuggerResponse", _handle_debugger_progress, True)
    get_workbench().bind("ToplevelResponse", _handle_toplevel_response, True)
    get_workbench().bind("CommandAccepted", _debug_accepted, True)
    
