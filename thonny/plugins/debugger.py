# -*- coding: utf-8 -*-

"""
Adds debugging commands and features. 
"""

import tkinter as tk
from tkinter import ttk
from thonny.common import DebuggerCommand
from thonny.memory import VariablesFrame
from thonny import ast_utils, memory, misc_utils, ui_utils
from thonny.misc_utils import shorten_repr
import ast
from thonny.codeview import CodeView, get_syntax_options_for_tag
from tkinter.messagebox import showinfo, showerror
from thonny import get_workbench, get_runner
from thonny.ui_utils import select_sequence
import tokenize
import logging

class Debugger:
    def __init__(self):
        
        self._init_commands()
        
        self._main_frame_visualizer = None
        self._last_progress_message = None
        
        get_workbench().bind("DebuggerProgress", self._handle_debugger_progress, True)
        get_workbench().bind("ToplevelResult", self._handle_toplevel_result, True)
    
    def _init_commands(self):
        get_workbench().add_command("debug", "run", "Debug current script",
            self._cmd_debug_current_script,
            caption="Debug",
            tester=self._cmd_debug_current_script_enabled,
            default_sequence="<Control-F5>",
            group=10,
            image="debug-current-script",
            include_in_toolbar=True)
        
        get_workbench().add_command("step_over", "run", "Step over",
            self._cmd_step_over,
            caption="Over",
            tester=self._cmd_stepping_commands_enabled,
            default_sequence="<F6>",
            group=30,
            image="step-over",
            include_in_toolbar=True)

        get_workbench().add_command("step_back", "run", "Step back",
            self._cmd_step_back,
            caption="Back",
            tester=self._cmd_stepping_commands_enabled,
            default_sequence="<F9>",
            group=30)

        get_workbench().add_command("step_into", "run", "Step into",
            self._cmd_step_into,
            caption="Into",
            tester=self._cmd_stepping_commands_enabled,
            default_sequence="<F7>",
            group=30,
            image="step-into",
            include_in_toolbar=True)
        
        get_workbench().add_command("step_out", "run", "Step out",
            self._cmd_step_out,
            caption="Out",
            tester=self._cmd_stepping_commands_enabled,
            default_sequence="<F8>",
            group=30,
            image="step-out",
            include_in_toolbar=True)
        
        get_workbench().add_command("run_to_cursor", "run", "Run to cursor",
            self._cmd_run_to_cursor,
            tester=self._cmd_run_to_cursor_enabled,
            default_sequence=select_sequence("<Control-F8>", "<Control-F8>"),
            group=30,
            image="run-to-cursor",
            include_in_toolbar=False)

    
    def _cmd_debug_current_script(self):
        get_runner().execute_current("Debug")

    def _cmd_debug_current_script_enabled(self):
        return (get_workbench().get_editor_notebook().get_current_editor() is not None
                and get_runner().get_state() == "waiting_toplevel_command"
                and "debug" in get_runner().supported_features())

    def _check_issue_debugger_command(self, command, **kwargs):
        cmd = DebuggerCommand(command=command, **kwargs)
        self._last_debugger_command = cmd

        if get_workbench().get_option("general.debug_mode"):
            print("LAST DEBUGGER COMMAND:", cmd.command, cmd)

        state = get_runner().get_state() 
        if (state == "waiting_debugger_command"):
            logging.debug("_check_issue_debugger_command: %s", cmd)
            
            # tell VM the state we are seeing
            cmd.setdefault (
                frame_id=self._last_progress_message.stack[-1].id,
                state=self._last_progress_message.stack[-1].last_event,
                focus=self._last_progress_message.stack[-1].last_event_focus
            )
            
            get_runner().send_command(cmd)
        else:
            logging.debug("Bad state for sending debugger command " + str(command))


    def _cmd_stepping_commands_enabled(self):
        return get_runner().get_state() == "waiting_debugger_command"
    
    def _cmd_step_into(self):
        self._check_issue_debugger_command("step")
    
    def _cmd_step_over(self):
        # Step over should stop when new statement or expression is selected.
        # At the same time, I need to get value from after_expression event.
        # Therefore I ask backend to stop first after the focus
        # and later I ask it to run to the beginning of new statement/expression.
        
        self._check_issue_debugger_command("exec")

    def _cmd_step_back(self):
        self._check_issue_debugger_command("back")
        
    def _cmd_step_out(self):
        self._check_issue_debugger_command("out")

    def _cmd_run_to_cursor(self):
        visualizer = self._get_topmost_selected_visualizer()
        if visualizer:
            assert isinstance(visualizer._text_frame, CodeView)
            code_view = visualizer._text_frame
            selection = code_view.get_selected_range()
            
            target_lineno = visualizer._firstlineno-1 + selection.lineno
            self._check_issue_debugger_command("line",
                                               target_filename=visualizer._filename, 
                                               target_lineno=target_lineno,
                                               )

    def _cmd_run_to_cursor_enabled(self):
        return (self._cmd_stepping_commands_enabled()
                and self._get_topmost_selected_visualizer() is not None
                )

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
        

    def _handle_debugger_progress(self, msg):
        self._last_progress_message = msg
        
        main_frame_id = msg.stack[0].id
        
        # clear obsolete main frame visualizer
        if (self._main_frame_visualizer 
            and self._main_frame_visualizer.get_frame_id() != main_frame_id):
            self._main_frame_visualizer.close()
            self._main_frame_visualizer = None
            
        if not self._main_frame_visualizer:
            self._main_frame_visualizer = MainFrameVisualizer(msg.stack[0])
            
        self._main_frame_visualizer.update_this_and_next_frames(msg)
        
        if msg.exception:
            showerror("Exception",
                      msg.exception_lower_stack_description.lstrip() + 
                      msg.exception["type_name"] 
                      + ": " + msg.exception_msg)
    
    def _should_skip_event(self, msg):
        return False
        frame_info = msg.stack[-1]
        event = frame_info.last_event
        tags = frame_info.last_event_args["node_tags"]
        time = msg.time
        
        if event == "after_statement" and time != "past":
            return True
        
        # TODO: consult also configuration
        if "call_function" in tags and time != "past":
            return True
        else:
            return False
    
    def _handle_toplevel_result(self, msg):
        if self._main_frame_visualizer is not None:
            self._main_frame_visualizer.close()
            self._main_frame_visualizer = None    


class FrameVisualizer:
    """
    Is responsible for stepping through statements and updating corresponding UI
    in Editor-s, FunctionCallDialog-s, ModuleDialog-s
    """
    def __init__(self, text_frame, frame_info):
        self._text_frame = text_frame
        self._text = text_frame.text
        self._frame_id = frame_info.id
        self._filename = frame_info.filename
        self._firstlineno = frame_info.firstlineno
        self._source = frame_info.source
        self._expression_box = ExpressionBox(text_frame)
        self._next_frame_visualizer = None
        self._text.set_read_only(True)
    
    def close(self):
        if self._next_frame_visualizer:
            self._next_frame_visualizer.close()
            self._next_frame_visualizer = None
            
        self._text.set_read_only(False)
        self._remove_focus_tags()
        self._expression_box.clear_debug_view()
    
    def get_frame_id(self):
        return self._frame_id
    
    def update_this_and_next_frames(self, msg):
        """Must not be used on obsolete frame"""
        
        #debug("State: %s, focus: %s", msg.state, msg.focus)
        
        frame_info, next_frame_info = self._find_this_and_next_frame(msg.stack)
        self._update_this_frame(msg, frame_info)
        
        # clear obsolete next frame visualizer
        if (self._next_frame_visualizer 
            and (not next_frame_info or 
                 self._next_frame_visualizer.get_frame_id() != next_frame_info.id)):
            self._next_frame_visualizer.close()
            self._next_frame_visualizer = None
            
        if next_frame_info and not self._next_frame_visualizer:
            self._next_frame_visualizer = self._create_next_frame_visualizer(next_frame_info)
            
        if self._next_frame_visualizer:
            self._next_frame_visualizer.update_this_and_next_frames(msg)
        
    
    def _remove_focus_tags(self):
        for name in ["exception_focus", "active_focus", 
                     "completed_focus", "suspended_focus"]:
            self._text.tag_remove(name, "0.0", "end")
     
    def _update_this_frame(self, msg, frame_info):
        self._frame_info = frame_info
        
        if "statement" in frame_info.last_event:
            if msg.exception is not None:
                stmt_tag = "exception_focus"
            elif frame_info.last_event.startswith("before"):
                stmt_tag = "active_focus"
            else:
                stmt_tag = "completed_focus"
        else:
            assert "expression" in frame_info.last_event
            stmt_tag = "suspended_focus"
            
        self._remove_focus_tags()
        self._tag_range(frame_info.current_statement, stmt_tag)
        
        self._expression_box.update_expression(msg, frame_info)

    def _find_this_and_next_frame(self, stack):
        for i in range(len(stack)):
            if stack[i].id == self._frame_id:
                if i == len(stack)-1: # last frame
                    return stack[i], None
                else:
                    return stack[i], stack[i+1]
                    
        else:
            raise AssertionError("Frame doesn't exist anymore")
        
    
    def _tag_range(self, text_range, tag):
        first_line, first_col, last_line = self._get_text_range_block(text_range)
        
        for lineno in range(first_line, last_line+1):
            self._text.tag_add(tag,
                              "%d.%d" % (lineno, first_col),
                              "%d.0" % (lineno+1))
            
        self._text.update_idletasks()
        self._text.see("%d.0" % (first_line))

        if last_line - first_line < 3:
            # if it's safe to assume that whole code fits into screen
            # then scroll it down a bit so that expression view doesn't hide behind
            # lower edge of the editor
            self._text.update_idletasks()
            self._text.see("%d.0" % (first_line+3))
            
    def _get_text_range_block(self, text_range):
        first_line = text_range.lineno - self._frame_info.firstlineno + 1
        last_line = text_range.end_lineno - self._frame_info.firstlineno + 1
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
     


class MainFrameVisualizer(FrameVisualizer):
    """
    Takes care of stepping in the main module
    """
    def __init__(self, frame_info):
        editor = get_workbench().get_editor_notebook().show_file(frame_info.filename)
        FrameVisualizer.__init__(self, editor.get_code_view(), frame_info)
        

class CallFrameVisualizer(FrameVisualizer):
    def __init__(self, text_frame, frame_id):
        self._dialog = FunctionCallDialog(text_frame)
        FrameVisualizer.__init__(self, self._dialog.get_code_view(), frame_id)
        
    def close(self):
        super().close()
        self._dialog.destroy()

class ExpressionBox(tk.Text):
    def __init__(self, codeview):
        
        opts = dict(height=1,
                     width=1,
                     relief=tk.RAISED,
                     background="#DCEDF2",
                     borderwidth=1,
                     highlightthickness=0,
                     padx=7,
                     pady=7,
                     wrap=tk.NONE,
                     font="EditorFont")
        
        opts.update(get_syntax_options_for_tag("expression_box"))
        
        tk.Text.__init__(self, codeview.winfo_toplevel(), **opts)
        self._codeview = codeview
        
        self._last_focus = None
        self._last_root_expression = None
        
        self.tag_configure("value", get_syntax_options_for_tag("value"))
        self.tag_configure('before', get_syntax_options_for_tag("active_focus"))
        self.tag_configure('after', get_syntax_options_for_tag("completed_focus"))
        self.tag_configure('exception', get_syntax_options_for_tag("exception_focus"))
        self.tag_raise("exception", "before")
        self.tag_raise("exception", "after")
        
        
    def update_expression(self, msg, frame_info):
        focus = frame_info.last_event_focus
        event = frame_info.last_event
        
        if frame_info.current_root_expression is not None:
            self._load_expression(frame_info.filename, frame_info.current_root_expression)
            
            for subrange, value in frame_info.current_evaluations:
                self._replace(subrange, value)
            
            if "expression" in event:
                # Event may be also after_statement_again
                self._highlight_range(focus, event, msg.exception)
                
            self._update_position(frame_info.current_root_expression)
            self._update_size()
            
        else:
            # hide and clear on non-expression events
            self.clear_debug_view()

        self._last_focus = focus
        self._last_root_expression = frame_info.current_root_expression
        
        
    def get_focused_text(self):
        if self._last_focus: 
            start_mark = self._get_mark_name(self._last_focus.lineno, self._last_focus.col_offset)
            end_mark = self._get_mark_name(self._last_focus.end_lineno, self._last_focus.end_col_offset)
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
        
        id_str = memory.format_object_id(value["id"])
        if get_workbench().in_heap_mode():
            value_str = id_str
        else:
            value_str = shorten_repr(value["repr"], 100)
        
        object_tag = "object_" + str(value["id"])
        self.insert(start_mark, value_str, ('value', object_tag))
        if misc_utils.running_on_mac_os():
            sequence = "<Command-Button-1>"
        else:
            sequence = "<Control-Button-1>"
        self.tag_bind(object_tag, sequence,
                      lambda _: get_workbench().event_generate("ObjectSelect", object_id=value["id"]))
        
        #print("AFTER 9", repr(self.get("1.0", "end")))
    
    def _load_expression(self, filename, text_range):
        with tokenize.open(filename) as fp:
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
                    #print("Creating mark", start_mark, index1)
                    self.mark_gravity(start_mark, tk.LEFT)
                
                end_mark = self._get_mark_name(node.end_lineno, node.end_col_offset) 
                if not end_mark in self.mark_names():
                    self.mark_set(end_mark, index2)
                    #print("Creating mark", end_mark, index2)
                    self.mark_gravity(end_mark, tk.RIGHT)
                
                    
    def _get_mark_name(self, lineno, col_offset):
        return str(lineno) + "_" + str(col_offset)
    
    def _get_tag_name(self, node_or_text_range):
        return (str(node_or_text_range.lineno)
                + "_" + str(node_or_text_range.col_offset)
                + "_" + str(node_or_text_range.end_lineno)
                + "_" + str(node_or_text_range.end_col_offset))
    
    def _highlight_range(self, text_range, state, exception):
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
        end_index = self._get_mark_name(text_range.end_lineno, text_range.end_col_offset) 
        self.tag_add(tag, start_index, end_index)
        
        if exception:
            self.tag_add("exception", start_index, end_index)
            
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
    

class FrameDialog(tk.Toplevel, FrameVisualizer):
    def __init__(self, master, frame_info):
        tk.Toplevel.__init__(self, master)
        
        self.transient(master)
        if misc_utils.running_on_windows():
            self.wm_attributes('-toolwindow', 1)
        
        
        # TODO: take size from prefs
        editor_notebook = get_workbench().get_editor_notebook()
        if master.winfo_toplevel() == get_workbench():
            position_reference = editor_notebook
        else:
            # align to previous frame
            position_reference = master.winfo_toplevel()
            
        self.geometry("{}x{}+{}+{}".format(editor_notebook.winfo_width(),
                                           editor_notebook.winfo_height()-20,
                                           position_reference.winfo_rootx(),
                                           position_reference.winfo_rooty()))
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._init_layout_widgets(master, frame_info)
        FrameVisualizer.__init__(self, self._text_frame, frame_info)
        
        self._load_code(frame_info)
        self._text_frame.text.focus()
    
    def _init_layout_widgets(self, master, frame_info):
        self.main_frame= ttk.Frame(self) # just a backgroud behind padding of main_pw, without this OS X leaves white border
        self.main_frame.grid(sticky=tk.NSEW)        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.main_pw = ui_utils.AutomaticPanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.main_pw.grid(sticky=tk.NSEW, padx=10, pady=10)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        self._code_book = ttk.Notebook(self.main_pw)
        self._text_frame = CodeView(self._code_book, 
                                      first_line_number=frame_info.firstlineno,
                                      font="EditorFont")
        self._code_book.add(self._text_frame, text="Source")
        self.main_pw.add(self._code_book, minsize=100)
        
    
    def _load_code(self, frame_info):
        self._text_frame.set_content(frame_info.source)
    
    def _update_this_frame(self, msg, frame_info):
        FrameVisualizer._update_this_frame(self, msg, frame_info)
    
    def _on_close(self):
        showinfo("Can't close yet", 'Use "Stop" command if you want to cancel debugging')
    
    
    def close(self):
        FrameVisualizer.close(self)
        self.destroy()

class FunctionCallDialog(FrameDialog):
    def __init__(self, master, frame_info):
        FrameDialog.__init__(self, master, frame_info)
    
    def _init_layout_widgets(self, master, frame_info):
        FrameDialog._init_layout_widgets(self, master, frame_info)
        self._locals_book = ttk.Notebook(self.main_pw)
        self._locals_frame = VariablesFrame(self._locals_book)
        self._locals_book.add(self._locals_frame, text="Local variables")
        self.main_pw.add(self._locals_book, minsize=100)

    def _load_code(self, frame_info):
        FrameDialog._load_code(self, frame_info)
        
        if hasattr(frame_info, "function"):
            function_label = frame_info.function["repr"]
        else:
            function_label = frame_info.code_name
        
        # change tab label
        self._code_book.tab(self._text_frame, text=function_label)
    
    def _update_this_frame(self, msg, frame_info):
        FrameDialog._update_this_frame(self, msg, frame_info)
        self._locals_frame.update_variables(frame_info.locals)

        
class ModuleLoadDialog(FrameDialog):
    def __init__(self, text_frame, frame_info):
        FrameDialog.__init__(self, text_frame)
    
    
    
def load_plugin():
    Debugger()
    
