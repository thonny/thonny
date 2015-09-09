# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from thonny.common import DebuggerCommand, \
    parse_shell_command, ToplevelCommand, unquote_path, CommandSyntaxError
from thonny.memory import VariablesFrame
from logging import debug
from thonny import ast_utils, memory, misc_utils, ui_utils
from thonny.misc_utils import shorten_repr
import ast
from thonny.codeview import CodeView
from tkinter.messagebox import showinfo
from thonny.globals import get_workbench, get_runner
import shlex
 
class Debugger:
    def __init__(self):
        get_workbench().add_command("debug", "run", "Debug current script",
            self._cmd_debug_current_script,
            default_sequence="<Control-F5>")
        get_workbench().add_command("step_over", "run", "Step over",
            self._cmd_step_over,
            default_sequence="<F8>")
        get_workbench().add_command("step_into", "run", "Step into",
            self._cmd_step_into,
            default_sequence="<Control-F8>")
        
        
        self._main_frame_visualizer = None
        self._last_progress_message_handled = None
        
        self._runner = get_workbench().get_runner()
        
        get_workbench().bind("DebuggerProgress", self._handle_debugger_progress, True)
        get_workbench().bind("ToplevelResult", self._handle_toplevel_result, True)
        
        get_workbench().get_view("ShellView").add_command("Debug", self._handle_debug_from_shell)
    
    def _cmd_debug_current_script(self):
        get_runner().execute_current("Debug")


    def _check_issue_debugger_command(self, cmd, automatic=False):
        if self._runner.get_state() == "waiting_debug_command":
            self._issue_debugger_command(cmd, automatic)
            # TODO: notify memory panes and editors? Make them inactive?
    
    def _issue_debugger_command(self, cmd, automatic=False):
        debug("_issue cmd: %s, auto: %s", cmd, automatic)
        
        # tell VM the state we are seeing
        cmd.setdefault (
            frame_id=self._last_progress_message_handled.stack[-1].id,
            state=self._last_progress_message_handled.stack[-1].last_event,
            focus=self._last_progress_message_handled.stack[-1].last_event_focus
        )
        
        get_runner().send_command(cmd)


    def _cmd_step_into_enabled(self):
        return self._runner.get_state() == "waiting_debug_command"
    
    def _cmd_step_into(self):
        self._check_issue_debugger_command(DebuggerCommand("step_into"))
    
    def _cmd_step_over_enabled(self):
        return self._cmd_step_into_enabled()
    
    def _cmd_step_over(self):
        self._check_issue_debugger_command(DebuggerCommand("step_over"))

    def _handle_debug_from_shell(self, cmd_line):
        command, args = parse_shell_command(cmd_line)
        
        if len(args) >= 1:
            get_workbench().get_editor_notebook().save_all_named_editors()
            get_runner().send_command(ToplevelCommand(command=command,
                               filename=unquote_path(args[0]),
                               args=args[1:]))
        else:
            raise CommandSyntaxError("Command '%s' takes at least one argument", command)


    def _handle_debugger_progress(self, msg):
        
        # TODO: if exception then show message
        
        """
        if (hasattr(msg, "tags") 
            and "call_function" in msg.tags
            and not self.get_option("debugging.expand_call_functions")):
            # skip some events
            
            self._check_issue_debugger_command(DebuggerCommand(command="step"), automatic=True)
        
            if (msg.state in ("after_statement")
                and not self.get_option("debugging.detailed_steps")
                or self.continue_with_step_over(self.last_manual_debugger_command_sent, msg)):
                
                self._check_issue_debugger_command(DebuggerCommand(command="step"), automatic=True)
        """
                
        
        self._last_progress_message_handled = msg
        
        main_frame_id = msg.stack[0].id
        
        # clear obsolete main frame visualizer
        if (self._main_frame_visualizer 
            and self._main_frame_visualizer.get_frame_id() != main_frame_id):
            self._main_frame_visualizer.close()
            self._main_frame_visualizer = None
            
        if not self._main_frame_visualizer:
            self._main_frame_visualizer = MainFrameVisualizer(msg.stack[0])
            
        self._main_frame_visualizer.update_this_and_next_frames(msg) 
    
    
    def _handle_toplevel_result(self, msg):
        if self._main_frame_visualizer is not None:
            self._main_frame_visualizer.close()
            self._main_frame_visualizer = None    


class FrameVisualizer:
    """
    Is responsible for stepping through statements and updating corresponding UI
    in Editor-s, FunctionCallDialog-s, ModuleDialog-s
    """
    def __init__(self, text_wrapper, frame_info):
        self._text_wrapper = text_wrapper
        self._text = text_wrapper.text
        self._frame_id = frame_info.id
        self._expression_view = ExpressionBox(text_wrapper)
        self._next_frame_visualizer = None
        
        self._text.tag_configure('focus', background="#F8FC9A", borderwidth=1, relief=tk.SOLID)
        #self._text.tag_configure('before', background="#F8FC9A") TODO: ???
        #self._text.tag_configure('after', background="#D7EDD3")
        #self._text.tag_configure('exception', background="#FFBFD6")
        self._text.configure(insertwidth=0, background="LightYellow")
        self._text_wrapper.read_only = True
    
    def close(self):
        if self._next_frame_visualizer:
            self._next_frame_visualizer.close()
            self._next_frame_visualizer = None
            
            
        self._text.wrapper.read_only = False
        
        # TODO: better remember previous insertwidth and insertbackground
        self._text.configure(background="White", insertwidth=2, insertbackground="Black")
    
    def get_frame_id(self):
        return self._frame_id
    
    def update_this_and_next_frames(self, msg):
        """Must not be used on obsolete frame"""
        
        #info("State: %s, focus: %s", msg.state, msg.focus)
        
        frame_info, next_frame_info = self._find_this_and_next_frame(msg.stack)
        self._update_this_frame(msg, frame_info)
        
        # clear obsolete next frame visualizer
        if (self._next_frame_visualizer 
            and (not next_frame_info or 
                 self._next_frame_visualizer.get_frame_id() != next_frame_info)):
            self._next_frame_visualizer.close()
            self._next_frame_visualizer = None
            
        if next_frame_info and not self._next_frame_visualizer:
            self._next_frame_visualizer = self._create_next_frame_visualizer(next_frame_info)
            
        if self._next_frame_visualizer:
            self._next_frame_visualizer.update_this_and_next_frames(msg)
        
            
    def _update_this_frame(self, msg, frame_info):
        self._frame_info = frame_info
        self._text.tag_remove("focus", "0.0", "end")
            
        """             
        if msg.state.startswith("before"):
            tag = "before"
        elif msg.state.startswith("after"):
            tag = "after"
        else:
            tag = "exception"
        """
        
        
        # TODO: if focus is in expression, then find and highlight closest
        # statement
        self._tag_range(frame_info.last_event_focus, "focus", True)
        
        # TODO: use different color if focus is not topmost
        
        # TODO: update expression box

    def _find_this_and_next_frame(self, stack):
        for i in range(len(stack)):
            if stack[i].id == self._frame_id:
                if i == len(stack)-1: # last frame
                    return stack[i], None
                else:
                    return stack[i], stack[i+1]
                    
        else:
            raise AssertionError("Frame doesn't exist anymore")
        
    
    def _tag_range(self, text_range, tag, see=False):
        first_line, first_col, last_line = self._get_text_range_block(text_range)
        
        for lineno in range(first_line, last_line+1):
            self._text.tag_add(tag,
                              "%d.%d" % (lineno, first_col),
                              "%d.0" % (lineno+1))
            
        self._text.update_idletasks()
        self._text.see("%d.0" % (first_line))
        #print("SEEING: " + "%d.0" % (first_line))
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
            return ModuleLoadDialog(self._text_wrapper, next_frame_info)
        else:
            dialog = FunctionCallDialog(self._text_wrapper, next_frame_info)
            
            if self._expression_view.winfo_ismapped():
                dialog.title(self._expression_view.get_focused_text())
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
    def __init__(self, text_wrapper, frame_id):
        self._dialog = FunctionCallDialog(text_wrapper)
        FrameVisualizer.__init__(self, self._dialog.get_code_view(), frame_id)
        
    def close(self):
        super().close()
        self._dialog.destroy()

class ExpressionBox(tk.Text):
    def __init__(self, codeview):
        tk.Text.__init__(self, codeview.text,
                         height=1,
                         width=1,
                         relief=tk.RAISED,
                         background="#DCEDF2",
                         borderwidth=1,
                         highlightthickness=0,
                         padx=7,
                         pady=7,
                         wrap=tk.NONE,
                         font=get_workbench().get_font("EditorFont"))
        self._codeview = codeview
        
        self._main_range = None
        self._last_focus = None
        
        self.tag_config("value", foreground="Blue")
        self.tag_configure('before', background="#F8FC9A", borderwidth=1, relief=tk.SOLID)
        self.tag_configure('after', background="#D7EDD3", borderwidth=1, relief=tk.FLAT)
        self.tag_configure('exception', background="#FFBFD6", borderwidth=1, relief=tk.SOLID)
        
        
    def handle_vm_message(self, msg):
        debug("ExpressionBox.handle_vm_message %s", (msg.state, msg.focus))
        
        if msg.state in ("before_expression", "before_expression_again"):
            # (re)load stuff
            if self._main_range is None or msg.focus.not_smaller_eq_in(self._main_range):
                self._load_expression(msg.filename, msg.focus)
                self._update_position(msg.focus)
                self._update_size()
                
            self._highlight_range(msg.focus, msg.state)
            
        
        elif msg.state == "after_expression":
            debug("EV: after_expression %s", msg)
            
            self.tag_configure('after', background="#BBEDB2", borderwidth=1, relief=tk.FLAT)
            start_mark = self._get_mark_name(msg.focus.lineno, msg.focus.col_offset)
            end_mark = self._get_mark_name(msg.focus.end_lineno, msg.focus.end_col_offset)
            
            if hasattr(msg, "value"):
                debug("EV: replacing expression with value")
                #print("del", start_mark, end_mark)
                self.delete(start_mark, end_mark)
                
                id_str = memory.format_object_id(msg.value.id)
                if get_workbench().in_heap_mode():
                    value_str = id_str
                else:
                    value_str = shorten_repr(msg.value.repr, 100)
                
                #print("ins", start_mark, value_str)
                object_tag = "object_" + str(msg.value.id)
                self.insert(start_mark, value_str, ('value', 'after', object_tag))
                if misc_utils.running_on_mac_os():
                    sequence = "<Command-Button-1>"
                else:
                    sequence = "<Control-Button-1>"
                self.tag_bind(object_tag, sequence,
                              lambda _: get_workbench().event_generate("ObjectSelect", object_id=msg.value.id))
                    
                self._update_size()
                
            else:
                debug("EV: got exc: %s", msg)
                "TODO: make it red"
                
        elif (msg.state == "before_statement_again"
              and self._main_range is not None # TODO: shouldn't need this 
              and self._main_range.is_smaller_eq_in(msg.focus)):
            # we're at final stage of executing parent statement 
            # (eg. assignment after the LHS has been evaluated)
            # don't close yet
            self.tag_configure('after', background="#DCEDF2", borderwidth=1, relief=tk.FLAT)   
        else:
            # hide and clear on non-expression events
            self.clear_debug_view()

        if hasattr(msg, "focus"):
            self._last_focus = msg.focus
        
        
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
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", "end")
            
        for mark in self.mark_names():
            self.mark_unset(mark)
            
    
    def _load_expression(self, filename, text_range):
        whole_source, _ = misc_utils.read_python_file(filename)
        root = ast_utils.parse_source(whole_source, filename)
        self._main_range = text_range
        assert self._main_range is not None
        main_node = ast_utils.find_expression(root, text_range)
        
        source = ast_utils.extract_text_range(whole_source, text_range)
        debug("EV.load_exp: %s", (text_range, main_node, source))
        
        self.delete("1.0", "end")
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
                    self.mark_gravity(start_mark, tk.LEFT)
                
                end_mark = self._get_mark_name(node.end_lineno, node.end_col_offset) 
                if not end_mark in self.mark_names():
                    self.mark_set(end_mark, index2)
                    self.mark_gravity(end_mark, tk.RIGHT)
                    
    def _get_mark_name(self, lineno, col_offset):
        return str(lineno) + "_" + str(col_offset)
    
    def _get_tag_name(self, node_or_text_range):
        return (str(node_or_text_range.lineno)
                + "_" + str(node_or_text_range.col_offset)
                + "_" + str(node_or_text_range.end_lineno)
                + "_" + str(node_or_text_range.end_col_offset))
    
    def _highlight_range(self, text_range, state):
        debug("EV._highlight_range: %s", text_range)
        self.tag_remove("after", "1.0", "end")
        self.tag_remove("before", "1.0", "end")
        self.tag_remove("exception", "1.0", "end")
        
        if state.startswith("after"):
            tag = "after"
        elif state.startswith("before"):
            tag = "before"
        else:
            tag = "exception"
            
        self.tag_add(tag,
                     self._get_mark_name(text_range.lineno, text_range.col_offset),
                     self._get_mark_name(text_range.end_lineno, text_range.end_col_offset))
        
    def _update_position(self, text_range):
        bbox = self._codeview.get_char_bbox(text_range.lineno, text_range.col_offset)
        if isinstance(bbox, tuple):
            x = bbox[0] + 6
            y = bbox[1] - 6
        else:
            x = 30
            y = 30
        self.place(x=x, y=y, anchor=tk.NW)
    
    def _update_size(self):
        content = self.get("1.0", tk.END)
        lines = content.splitlines()
        self["height"] = len(lines)
        self["width"] = max(map(len, lines))
    

class FrameDialog(tk.Toplevel, FrameVisualizer):
    def __init__(self, text_wrapper, frame_info):
        tk.Toplevel.__init__(self, text_wrapper)
        FrameVisualizer.__init__(self, text_wrapper, frame_info)
        
        self.transient(text_wrapper)
        if misc_utils.running_on_windows():
            self.wm_attributes('-toolwindow', 1)
        
        
        # TODO: take size from prefs
        self.geometry("{}x{}+{}+{}".format(text_wrapper.winfo_width(),
                                           text_wrapper.winfo_height(),
                                           text_wrapper.winfo_toplevel().winfo_rootx(),
                                           text_wrapper.winfo_toplevel().winfo_rooty()))
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._init_layout_widgets(text_wrapper, frame_info)
        self._load_function(frame_info)
        self._text_wrapper.text.focus()
    
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
        self._text_wrapper = CodeView(self._code_book, first_line_no=frame_info.firstlineno)
        self._code_book.add(self._text_wrapper, text="Source")
        self._text_wrapper.enter_execution_mode()
        self.main_pw.add(self._code_book, minsize=130)
        
    
    def _load_code(self, frame_info):
        self._text_wrapper.set_content(frame_info.source)
    
    def _update_this_frame(self, msg, frame_info):
        FrameVisualizer._update_this_frame(self, msg, frame_info)
        self._locals_frame.update_variables(None)
    
    def _on_close(self):
        showinfo("Can't close yet", "Step until the end of this code to close it")
    
    
    def close(self):
        FrameVisualizer.close(self)
        self.destroy()

class FunctionCallDialog(FrameDialog):
    def __init__(self, text_wrapper, frame_info):
        FrameDialog.__init__(self, text_wrapper)
    
    def _init_layout_widgets(self, master, frame_info):
        FrameDialog._init_layout_widgets(self, master, frame_info)
        self._locals_book = ttk.Notebook(self.main_pw)
        self._locals_frame = VariablesFrame(self._locals_book)
        self._locals_book.add(self._locals_frame, text="Local variables")
        self.main_pw.add(self._locals_book, minsize=75)

    def _load_code(self, frame_info):
        FrameDialog._load_code(self, frame_info)
        
        if hasattr(frame_info, "function"):
            function_label = frame_info.function.repr
        else:
            function_label = frame_info.code_name
        
        # change tab label
        self._code_book.tab(self._text_wrapper, text=function_label)
        
        
class ModuleLoadDialog(FrameDialog):
    def __init__(self, text_wrapper, frame_info):
        FrameDialog.__init__(self, text_wrapper)
    
    
    
def load_plugin():
    Debugger()
    
        