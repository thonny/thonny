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

from _tkinter import TclError

from thonny import (
    ast_utils,
    editors,
    get_runner,
    get_workbench,
    memory,
    misc_utils,
    running,
    ui_utils,
)
from thonny.codeview import CodeView, SyntaxText, get_syntax_options_for_tag
from thonny.common import DebuggerCommand, InlineCommand
from thonny.languages import tr
from thonny.memory import VariablesFrame
from thonny.misc_utils import running_on_mac_os, running_on_rpi, shorten_repr
from thonny.tktextext import TextFrame
from thonny.ui_utils import CommonDialog, select_sequence
from thonny.ui_utils import select_sequence, CommonDialog, get_tk_version_info
from _tkinter import TclError

_current_debugger = None

RESUME_COMMAND_CAPTION = ""  # Init later when gettext is loaded


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

            # tell MainCPythonBackend the state we are seeing
            cmd.setdefault(
                frame_id=self._last_progress_message.stack[-1].id,
                breakpoints=self.get_effective_breakpoints(command),
                state=self._last_progress_message.stack[-1].event,
                focus=self._last_progress_message.stack[-1].focus,
                allow_stepping_into_libraries=get_workbench().get_option(
                    "debugger.allow_stepping_into_libraries"
                ),
            )
            if command == "run_to_cursor":
                # cursor position was added as another breakpoint
                cmd.name = "resume"

            get_runner().send_command(cmd)
            if command == "resume":
                self.clear_last_frame()
        else:
            logging.debug("Bad state for sending debugger command " + str(command))

    def get_run_to_cursor_breakpoint(self):
        return None

    def get_effective_breakpoints(self, command):
        result = editors.get_current_breakpoints()

        if command == "run_to_cursor":
            bp = self.get_run_to_cursor_breakpoint()
            if bp is not None:
                filename, lineno = bp
                result.setdefault(filename, set())
                result[filename].add(lineno)

        return result

    def command_enabled(self, command):
        if not get_runner().is_waiting_debugger_command():
            return False

        if command == "run_to_cursor":
            return self.get_run_to_cursor_breakpoint() is not None
        elif command == "step_back":
            return (
                self._last_progress_message
                and self._last_progress_message["tracer_class"] == "NiceTracer"
            )
        else:
            return True

    def handle_debugger_progress(self, msg):
        self._last_brought_out_frame_id = None

    def handle_debugger_return(self, msg):
        pass

    def close(self) -> None:
        self._last_brought_out_frame_id = None

        if get_workbench().get_option("debugger.automatic_stack_view"):
            get_workbench().hide_view("StackView")

    def clear_last_frame(self):
        pass

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
                label=tr("Run to cursor"),
                command=lambda: self.check_issue_command("run_to_cursor"),
            )
            menu.add("separator")
            menu.add("command", label="Copy", command=create_edit_command_handler("<<Copy>>"))
            menu.add(
                "command",
                label=tr("Select all"),
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

    def clear_last_frame(self):
        if self._last_frame_visualizer is not None:
            self._last_frame_visualizer.clear()

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

        self._last_frame_visualizer._update_this_frame(self._last_progress_message, frame_info)

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

    def handle_debugger_return(self, msg):
        if (
            self._last_frame_visualizer is not None
            and self._last_frame_visualizer.get_frame_id() == msg.get("frame_id")
        ):
            self._last_frame_visualizer.close()


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

    def clear_last_frame(self):
        visualizer = self._get_topmost_visualizer()
        if visualizer is not None:
            visualizer.clear()

    def _get_topmost_visualizer(self):
        visualizer = self._main_frame_visualizer
        if visualizer is None:
            return None

        while visualizer._next_frame_visualizer is not None:
            visualizer = visualizer._next_frame_visualizer

        return visualizer

    def _get_topmost_selected_visualizer(self):
        visualizer = self._get_topmost_visualizer()
        if visualizer is None:
            return None

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

    def handle_debugger_return(self, msg):
        if self._main_frame_visualizer is None:
            return

        self._main_frame_visualizer.close(msg["frame_id"])
        if msg["frame_id"] == self._main_frame_visualizer.get_frame_id():
            self._main_frame_visualizer = None


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
        if running_on_mac_os():
            self._expression_box = ToplevelExpressionBox(text_frame)
        else:
            self._expression_box = PlacedExpressionBox(text_frame)

        self._note_box = ui_utils.NoteBox(text_frame.winfo_toplevel())
        self._next_frame_visualizer = None
        self._prev_frame_visualizer = None
        self._text.set_read_only(True)
        self._line_debug = frame_info.current_statement is None

        self._reconfigure_tags()

    def _translate_lineno(self, lineno):
        return lineno - self._firstlineno + 1

    def _reconfigure_tags(self):
        for tag in ["active_focus", "exception_focus"]:
            conf = get_syntax_options_for_tag(tag).copy()
            if self._line_debug:
                # meaning data comes from line-debug
                conf["borderwidth"] = 0

            self._text.tag_configure(tag, **conf)

    def close(self, frame_id=None):
        if self._next_frame_visualizer:
            self._next_frame_visualizer.close(frame_id)
            if frame_id is None or self._next_frame_visualizer.get_frame_id() == frame_id:
                self._next_frame_visualizer = None

        if frame_id is None or frame_id == self._frame_id:
            self._text.set_read_only(False)
            self.clear()
            # self._expression_box.destroy()

    def clear(self):
        self.remove_focus_tags()
        self.hide_expression_box()
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
            not next_frame_info or self._next_frame_visualizer.get_frame_id() != next_frame_info.id
        ):
            self._next_frame_visualizer.close()
            self._next_frame_visualizer = None

        if next_frame_info and not self._next_frame_visualizer:
            self._next_frame_visualizer = self._create_next_frame_visualizer(next_frame_info)
            self._next_frame_visualizer._prev_frame_visualizer = self

        if self._next_frame_visualizer:
            self._next_frame_visualizer.update_this_and_next_frames(msg)

    def remove_focus_tags(self):
        for name in [
            "exception_focus",
            "active_focus",
            "completed_focus",
            "suspended_focus",
            "sel",
        ]:
            self._text.tag_remove(name, "0.0", "end")

    def hide_expression_box(self):
        if self._expression_box is not None:
            self._expression_box.clear_debug_view()

    def _update_this_frame(self, msg, frame_info):
        self._frame_info = frame_info
        self.remove_focus_tags()

        if frame_info.event == "line":
            if (
                frame_info.id in msg["exception_info"]["affected_frame_ids"]
                and msg["exception_info"]["is_fresh"]
            ):
                self._tag_range(frame_info.focus, "exception_focus")
            else:
                self._tag_range(frame_info.focus, "active_focus")
        else:
            if "statement" in frame_info.event:
                if msg["exception_info"]["msg"] is not None and msg["exception_info"]["is_fresh"]:
                    stmt_tag = "exception_focus"
                elif frame_info.event.startswith("before"):
                    stmt_tag = "active_focus"
                else:
                    stmt_tag = "completed_focus"
            else:
                assert "expression" in frame_info.event
                stmt_tag = "suspended_focus"

            if frame_info.current_statement is not None:
                self._tag_range(frame_info.current_statement, stmt_tag)
            else:
                logging.warning("Missing current_statement: %s", frame_info)

        self._expression_box.update_expression(msg, frame_info)

        if (
            frame_info.id in msg["exception_info"]["affected_frame_ids"]
            and msg["exception_info"]["is_fresh"]
        ):
            self._show_exception(msg["exception_info"]["lines_with_frame_info"], frame_info)
        else:
            self.close_note()

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

        self._text.tag_raise(tag)

        line_prefix = self._text.get(
            "%d.0" % self._translate_lineno(text_range.lineno),
            "%d.%d" % (self._translate_lineno(text_range.lineno), text_range.col_offset),
        )
        if line_prefix.strip():
            # pseudo-statement
            first_line = self._translate_lineno(text_range.lineno)
            last_line = self._translate_lineno(text_range.end_lineno)
            self._text.tag_add(
                tag,
                "%d.%d" % (first_line, text_range.col_offset),
                "%d.%d" % (last_line, text_range.end_col_offset),
            )
        else:
            # normal statement
            first_line, first_col, last_line = self._get_text_range_block(text_range)

            for lineno in range(first_line, last_line + 1):
                self._text.tag_add(tag, "%d.%d" % (lineno, first_col), "%d.0" % (lineno + 1))

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
            text_range.end_lineno - self._firstlineno + (1 if text_range.end_col_offset > 0 else 0)
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
                dialog.title(tr("Function call at %s") % hex(self._frame_id))

            return dialog

    def bring_out_frame(self, frame_id):
        if self._frame_id == frame_id:
            self.bring_out_this_frame()
        elif self._next_frame_visualizer is not None:
            self._next_frame_visualizer.bring_out_frame(frame_id)

    def bring_out_this_frame(self):
        pass

    def show_note(self, *content_items: Union[str, List], target=None, focus=None) -> None:
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
            get_workbench().get_editor_notebook().show_file(frame_info.filename, set_focus=False)
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
        self.editor.master.update_editor_title(self.editor, self.editor.get_title() + suffix)

    def bring_out_this_frame(self):
        get_workbench().focus_set()

    def clear(self):
        super().clear()
        self._decorate_editor_title("")


class BaseExpressionBox:
    def __init__(self, codeview, text):
        self.text = text

        self._codeview = codeview

        self._last_focus = None
        self._last_root_expression = None

        self.text.tag_configure("value", get_syntax_options_for_tag("value"))
        self.text.tag_configure("before", get_syntax_options_for_tag("active_focus"))
        self.text.tag_configure("after", get_syntax_options_for_tag("completed_focus"))
        self.text.tag_configure("exception", get_syntax_options_for_tag("exception_focus"))
        self.text.tag_raise("exception", "before")
        self.text.tag_raise("exception", "after")

    def get_text_options(self):
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
        return opts

    def update_expression(self, msg, frame_info):
        focus = frame_info.focus
        event = frame_info.event

        if frame_info.current_root_expression is not None:

            if self._last_root_expression != frame_info.current_root_expression:
                # can happen, eg. when focus jumps from the last expr in while body
                # to while test expression
                self.clear_debug_view()

            with open(frame_info.filename, "rb") as fp:
                whole_source = fp.read()

            lines = whole_source.splitlines()
            if len(lines) < frame_info.current_root_expression.end_lineno:
                # it must be on a synthetical line which is not actually present in the editor
                self.clear_debug_view()
                return

            self._load_expression(
                whole_source, frame_info.filename, frame_info.current_root_expression
            )
            for subrange, value in frame_info.current_evaluations:
                self._replace(subrange, value)
            if "expression" in event:
                # Event may be also after_statement_again
                self._highlight_range(
                    focus,
                    event,
                    (
                        frame_info.id in msg["exception_info"]["affected_frame_ids"]
                        and msg["exception_info"]["is_fresh"]
                    ),
                )
                self._last_focus = focus

            self._update_position(frame_info.current_root_expression)
            self._update_size()

        else:
            # hide and clear on non-expression events
            self.clear_debug_view()

        self._last_root_expression = frame_info.current_root_expression

    def get_focused_text(self):
        if self._last_focus:
            start_mark = self._get_mark_name(self._last_focus.lineno, self._last_focus.col_offset)
            end_mark = self._get_mark_name(
                self._last_focus.end_lineno, self._last_focus.end_col_offset
            )
            return self.text.get(start_mark, end_mark)
        else:
            return ""

    def clear_debug_view(self):
        self._main_range = None
        self._last_focus = None
        self._clear_expression()

    def _clear_expression(self):
        for tag in self.text.tag_names():
            self.text.tag_remove(tag, "1.0", "end")

        self.text.mark_unset(*self.text.mark_names())
        self.text.delete("1.0", "end")

    def _replace(self, focus, value):
        start_mark = self._get_mark_name(focus.lineno, focus.col_offset)
        end_mark = self._get_mark_name(focus.end_lineno, focus.end_col_offset)

        self.text.delete(start_mark, end_mark)

        id_str = memory.format_object_id(value.id)
        if get_workbench().in_heap_mode():
            value_str = id_str
        else:
            value_str = shorten_repr(value.repr, 100)

        object_tag = "object_" + str(value.id)
        self.text.insert(start_mark, value_str, ("value", object_tag))
        if misc_utils.running_on_mac_os():
            sequence = "<Command-Button-1>"
        else:
            sequence = "<Control-Button-1>"
        self.text.tag_bind(
            object_tag,
            sequence,
            lambda _: get_workbench().event_generate("ObjectSelect", object_id=value.id),
        )

    def _load_expression(self, whole_source, filename, text_range):

        root = ast_utils.parse_source(whole_source, filename)
        main_node = ast_utils.find_expression(root, text_range)

        source = ast_utils.extract_text_range(whole_source, text_range)
        logging.debug("EV.load_exp: %s", (text_range, main_node, source))

        self._clear_expression()

        self.text.insert("1.0", source)

        # create node marks
        def _create_index(lineno, col_offset):
            local_lineno = lineno - main_node.lineno + 1
            if lineno == main_node.lineno:
                local_col_offset = col_offset - main_node.col_offset
            else:
                local_col_offset = col_offset

            return str(local_lineno) + "." + str(local_col_offset)

        for node in ast.walk(main_node):
            if "lineno" in node._attributes and hasattr(node, "end_lineno"):
                index1 = _create_index(node.lineno, node.col_offset)
                index2 = _create_index(node.end_lineno, node.end_col_offset)

                start_mark = self._get_mark_name(node.lineno, node.col_offset)
                if not start_mark in self.text.mark_names():
                    self.text.mark_set(start_mark, index1)
                    # print("Creating mark", start_mark, index1)
                    self.text.mark_gravity(start_mark, tk.LEFT)

                end_mark = self._get_mark_name(node.end_lineno, node.end_col_offset)
                if not end_mark in self.text.mark_names():
                    self.text.mark_set(end_mark, index2)
                    # print("Creating mark", end_mark, index2)
                    self.text.mark_gravity(end_mark, tk.RIGHT)

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
        self.text.tag_remove("after", "1.0", "end")
        self.text.tag_remove("before", "1.0", "end")
        self.text.tag_remove("exception", "1.0", "end")

        if state.startswith("after"):
            tag = "after"
        elif state.startswith("before"):
            tag = "before"
        else:
            return

        start_index = self._get_mark_name(text_range.lineno, text_range.col_offset)
        end_index = self._get_mark_name(text_range.end_lineno, text_range.end_col_offset)
        self.text.tag_add(tag, start_index, end_index)

        if has_exception:
            self.text.tag_add("exception", start_index, end_index)

    def _update_position(self, text_range):
        self._codeview.update_idletasks()
        text_line_number = text_range.lineno - self._codeview._first_line_number + 1
        bbox = self._codeview.text.bbox(str(text_line_number) + "." + str(text_range.col_offset))

        if isinstance(bbox, tuple):
            x = bbox[0] - self._codeview.text.cget("padx") + 6
            y = bbox[1] - self._codeview.text.cget("pady") - 6
        else:
            x = 30
            y = 30

        self._set_position_make_visible(x, y)

    def _update_size(self):
        content = self.text.get("1.0", tk.END)
        lines = content.splitlines()
        self.text["height"] = len(lines)
        self.text["width"] = max(map(len, lines))

    def _set_position_make_visible(self, rel_x, rel_y):
        raise NotImplementedError()


class PlacedExpressionBox(BaseExpressionBox, tk.Text):
    def __init__(self, codeview):
        tk.Text.__init__(self, codeview.winfo_toplevel(), self.get_text_options())
        BaseExpressionBox.__init__(self, codeview, self)

    def clear_debug_view(self):
        if self.winfo_ismapped():
            self.place_forget()

        super().clear_debug_view()

    def _set_position_make_visible(self, rel_x, rel_y):
        x = rel_x
        y = rel_y

        widget = self._codeview.text
        while widget != self.master:
            x += widget.winfo_x()
            y += widget.winfo_y()
            widget = widget.master

        if not self.winfo_ismapped():
            self.place(x=x, y=y, anchor=tk.NW)
            self.update()


class ToplevelExpressionBox(BaseExpressionBox, tk.Toplevel):
    def __init__(self, codeview):
        tk.Toplevel.__init__(self, codeview.winfo_toplevel())
        text = tk.Text(self, **self.get_text_options())
        BaseExpressionBox.__init__(self, codeview, text)
        self.text.grid()

        if running_on_mac_os():
            try:
                # NB! Must be the first thing to do after creation
                # https://wiki.tcl-lang.org/page/MacWindowStyle
                self.tk.call(
                    "::tk::unsupported::MacWindowStyle", "style", self._w, "help", "noActivates"
                )
            except TclError:
                pass
        else:
            raise RuntimeError("Should be used only on Mac")

        self.resizable(False, False)
        if get_tk_version_info() >= (8, 6, 10) and running_on_mac_os():
            # self.wm_overrideredirect(1) # Tkinter wrapper can give error in 3.9.2
            self.tk.call("wm", "overrideredirect", self._w, 1)
        self.wm_transient(codeview.winfo_toplevel())
        self.lift()

    def clear_debug_view(self):
        if self.winfo_ismapped():
            self.withdraw()

        super().clear_debug_view()

    def _set_position_make_visible(self, rel_x, rel_y):
        """
        widget = self._codeview.text
        while widget is not None:
            x += widget.winfo_x()
            y += widget.winfo_y()
            widget = widget.master
        """
        x = rel_x + self._codeview.text.winfo_rootx()
        y = rel_y + self._codeview.text.winfo_rooty()

        if not self.winfo_ismapped():
            self.update()
            self.deiconify()
        self.geometry("+%d+%d" % (x, y))

    def get_text_options(self):
        opts = super().get_text_options()
        opts["relief"] = "flat"
        opts["borderwidth"] = 0
        return opts


class DialogVisualizer(CommonDialog, FrameVisualizer):
    def __init__(self, master, frame_info):
        CommonDialog.__init__(self, master)

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
        self.update()

    def _init_layout_widgets(self, master, frame_info):
        self.main_frame = ttk.Frame(
            self
        )  # just a background behind padding of main_pw, without this OS X leaves white border
        self.main_frame.grid(sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.main_pw = ui_utils.AutomaticPanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.main_pw.grid(sticky=tk.NSEW, padx=10, pady=10)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        self._code_book = ttk.Notebook(self.main_pw)
        self._text_frame = CodeView(
            self._code_book, first_line_number=frame_info.firstlineno, font="EditorFont"
        )
        self._code_book.add(self._text_frame, text=tr("Source code"))
        self.main_pw.add(self._code_book, minsize=200)
        self._code_book.preferred_size_in_pw = 400

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
            tr("Can't close yet"),
            tr('Use "Stop" command if you want to cancel debugging'),
            master=self,
        )

    def close(self, frame_id=None):
        super().close()

        if frame_id is None or frame_id == self._frame_id:
            self.destroy()


class FunctionCallDialog(DialogVisualizer):
    def __init__(self, master, frame_info):
        DialogVisualizer.__init__(self, master, frame_info)

    def _init_layout_widgets(self, master, frame_info):
        DialogVisualizer._init_layout_widgets(self, master, frame_info)
        self._locals_book = ttk.Notebook(self.main_pw)
        self._locals_frame = VariablesFrame(self._locals_book)
        self._locals_book.preferred_size_in_pw = 200
        self._locals_book.add(self._locals_frame, text=tr("Local variables"))
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
            master, ("function", "location", "id"), displaycolumns=("function", "location")
        )

        # self.tree.configure(show="tree")
        self.tree.column("#0", width=0, anchor=tk.W, stretch=False)
        self.tree.column("function", width=120, anchor=tk.W, stretch=False)
        self.tree.column("location", width=450, anchor=tk.W, stretch=True)

        self.tree.heading("function", text=tr("Function"), anchor=tk.W)
        self.tree.heading("location", text=tr("Location"), anchor=tk.W)

        get_workbench().bind("DebuggerResponse", self._update_stack, True)
        get_workbench().bind("ToplevelResponse", lambda e=None: self._clear_tree(), True)
        get_workbench().bind("debugger_return_response", self._handle_debugger_return, True)

    def _update_stack(self, msg):
        self._clear_tree()

        node_id = None
        for frame in msg.stack:
            lineno = frame.focus.lineno

            node_id = self.tree.insert("", "end")
            self.tree.set(node_id, "function", frame.code_name)
            self.tree.set(
                node_id, "location", "%s, line %s" % (os.path.basename(frame.filename), lineno)
            )
            self.tree.set(node_id, "id", frame.id)

        # select last frame
        if node_id is not None:
            self.tree.see(node_id)
            self.tree.selection_add(node_id)
            self.tree.focus(node_id)

    def _handle_debugger_return(self, msg):
        delete = False
        for iid in self.tree.get_children():
            if self.tree.set(iid, "id") == msg["frame_id"]:
                # start deleting from this frame
                delete = True

            if delete:
                self.tree.delete(iid)

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
            text_class=SyntaxText,
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
            tr("If last command raised an exception then this view will show the stacktrace."),
        )

    def set_exception(self, exception_lines_with_frame_info):
        if exception_lines_with_frame_info == self._prev_exception:
            return

        self.text.direct_delete("1.0", "end")

        if exception_lines_with_frame_info is None:
            self._show_description()
            return

        self.text.configure(foreground=get_syntax_options_for_tag("stderr")["foreground"])
        for line, frame_id, filename, lineno in exception_lines_with_frame_info:

            if frame_id is not None:
                frame_tag = "frame_%d" % frame_id

                def handle_frame_click(event, frame_id=frame_id, filename=filename, lineno=lineno):
                    get_runner().send_command(InlineCommand("get_frame_info", frame_id=frame_id))
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
                self.text.direct_insert("end", line[start:end], ("hyperlink", frame_tag))
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
        and "debug" in get_runner().get_supported_features()
    )


def _request_debug(command_name):
    # Don't assume Debug command gets issued after this
    # This may just call the %cd command
    # or the user may deny saving current editor
    if get_workbench().in_simple_mode():
        get_workbench().show_view("VariablesView")

    get_runner().execute_current(command_name)


def _debug_accepted(event):
    # Called when proxy accepted the debug command
    global _current_debugger
    cmd = event.command
    if cmd.get("name") in ["Debug", "FastDebug"]:
        assert _current_debugger is None
        if get_workbench().get_option("debugger.frames_in_separate_windows"):
            _current_debugger = StackedWindowsDebugger()
        else:
            _current_debugger = SingleWindowDebugger()


def _handle_debugger_progress(msg):
    global _current_debugger
    assert _current_debugger is not None
    _current_debugger.handle_debugger_progress(msg)
    _update_run_or_resume_button()


def _handle_toplevel_response(msg):
    global _current_debugger
    if _current_debugger is not None:
        _current_debugger.close()
        _current_debugger = None

    _update_run_or_resume_button()


def _handle_debugger_return(msg):
    global _current_debugger
    assert _current_debugger is not None
    _current_debugger.handle_debugger_return(msg)


def _run_or_resume():
    state = get_runner().get_state()
    if state == "waiting_debugger_command":
        _issue_debugger_command("resume")
    elif state == "waiting_toplevel_command":
        get_runner().cmd_run_current_script()


def _run_or_resume_enabled():
    return get_runner().cmd_run_current_script_enabled() or _debugger_command_enabled("resume")


def _update_run_or_resume_button():
    if not get_workbench().in_simple_mode():
        return

    state = get_runner().get_state()
    if state == "waiting_debugger_command":
        caption = RESUME_COMMAND_CAPTION
        image = get_workbench().get_image("resume")
    elif state == "waiting_toplevel_command":
        caption = running.RUN_COMMAND_CAPTION
        image = get_workbench().get_image("run-current-script")
    else:
        return

    button = get_workbench().get_toolbar_button("runresume")
    button.configure(text=caption, image=image)


def get_current_debugger():
    return _current_debugger


def run_preferred_debug_command():
    preferred_debugger = get_workbench().get_option("debugger.preferred_debugger").lower()
    if preferred_debugger == "faster":
        return _request_debug("FastDebug")
    elif preferred_debugger == "birdseye":
        from thonny.plugins.birdseye_frontend import debug_with_birdseye

        return debug_with_birdseye()
    else:
        return _request_debug("Debug")


def load_plugin() -> None:

    global RESUME_COMMAND_CAPTION
    RESUME_COMMAND_CAPTION = tr("Resume")

    if get_workbench().in_simple_mode():
        get_workbench().set_default("debugger.frames_in_separate_windows", False)
    else:
        get_workbench().set_default("debugger.frames_in_separate_windows", True)

    get_workbench().set_default("debugger.automatic_stack_view", True)
    get_workbench().set_default(
        "debugger.preferred_debugger", "faster" if running_on_rpi() else "nicer"
    )
    get_workbench().set_default("debugger.allow_stepping_into_libraries", False)

    get_workbench().add_command(
        "runresume",
        "run",
        tr("Run / resume"),
        _run_or_resume,
        caption=running.RUN_COMMAND_CAPTION,
        tester=_run_or_resume_enabled,
        default_sequence=None,
        group=10,
        image="run-current-script",
        include_in_menu=False,
        include_in_toolbar=get_workbench().in_simple_mode(),
        alternative_caption=RESUME_COMMAND_CAPTION,
    )

    get_workbench().add_command(
        "debug_preferred",
        "run",
        tr("Debug current script"),
        run_preferred_debug_command,
        caption=tr("Debug"),
        tester=_start_debug_enabled,
        group=10,
        image="debug-current-script",
        include_in_menu=False,
        include_in_toolbar=True,
    )

    get_workbench().add_command(
        "debug_nicer",
        "run",
        tr("Debug current script (nicer)"),
        lambda: _request_debug("Debug"),
        caption="Debug (nicer)",
        tester=_start_debug_enabled,
        default_sequence="<Control-F5>",
        group=10,
        # image="debug-current-script",
    )

    get_workbench().add_command(
        "debug_faster",
        "run",
        tr("Debug current script (faster)"),
        lambda: _request_debug("FastDebug"),
        caption="Debug (faster)",
        tester=_start_debug_enabled,
        default_sequence="<Shift-F5>",
        group=10,
    )

    get_workbench().add_command(
        "step_over",
        "run",
        tr("Step over"),
        lambda: _issue_debugger_command("step_over"),
        caption=tr("Over"),
        tester=lambda: _debugger_command_enabled("step_over"),
        default_sequence="<F6>",
        group=30,
        image="step-over",
        include_in_toolbar=True,
    )

    get_workbench().add_command(
        "step_into",
        "run",
        tr("Step into"),
        lambda: _issue_debugger_command("step_into"),
        caption=tr("Into"),
        tester=lambda: _debugger_command_enabled("step_into"),
        default_sequence="<F7>",
        group=30,
        image="step-into",
        include_in_toolbar=True,
    )

    get_workbench().add_command(
        "step_out",
        "run",
        tr("Step out"),
        lambda: _issue_debugger_command("step_out"),
        caption=tr("Out"),
        tester=lambda: _debugger_command_enabled("step_out"),
        group=30,
        image="step-out",
        include_in_toolbar=True,
    )

    get_workbench().add_command(
        "resume",
        "run",
        RESUME_COMMAND_CAPTION,
        lambda: _issue_debugger_command("resume"),
        caption=RESUME_COMMAND_CAPTION,
        tester=lambda: _debugger_command_enabled("resume"),
        default_sequence="<F8>",
        group=30,
        image="resume",
        include_in_toolbar=not get_workbench().in_simple_mode(),
    )

    get_workbench().add_command(
        "run_to_cursor",
        "run",
        tr("Run to cursor"),
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
        tr("Step back"),
        lambda: _issue_debugger_command("step_back"),
        caption=tr("Back"),
        tester=lambda: _debugger_command_enabled("step_back"),
        default_sequence=select_sequence("<Control-b>", "<Command-b>"),
        group=30,
    )

    get_workbench().add_view(StackView, tr("Stack"), "se")
    get_workbench().add_view(ExceptionView, tr("Exception"), "s")
    get_workbench().bind("DebuggerResponse", _handle_debugger_progress, True)
    get_workbench().bind("ToplevelResponse", _handle_toplevel_response, True)
    get_workbench().bind("debugger_return_response", _handle_debugger_return, True)
    get_workbench().bind("CommandAccepted", _debug_accepted, True)
