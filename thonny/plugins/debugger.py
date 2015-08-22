# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from thonny.common import DebuggerResponse, DebuggerCommand
from thonny.memory import VariablesFrame
from logging import debug
from thonny import ast_utils, memory, misc_utils, ui_utils
from thonny.misc_utils import shorten_repr
import ast
from thonny.codeview import CodeView
from tkinter.messagebox import showinfo
from thonny.code import Editor
 
class Debugger:
    
    
    def __init__(self, workbench):
        self._workbench = workbench
        
        workbench.add_command("debug", "run", "Debug current script",
            self._cmd_debug_current_script,
            default_sequence="<Control-F5>")
        workbench.add_command("step_over", "run", "Step over",
            self._cmd_step_over,
            default_sequence="<F8>")
        workbench.add_command("step_into", "run", "Step into",
            self._cmd_step_into,
            default_sequence="<Control-F8>")
        
        
        self._bottom_frame_visualizer = None
        
        workbench.bind("DebuggerProgress", self._update_focus)
    
    def _cmd_debug_current_script(self):
        editor = self._workbench.get_current_editor()
        if not editor:
            return 
        
        self._filename = editor.get_filename()
        self._text = editor.get_text_widget() 

    def _cmd_step_into(self):
        pass
    
    def _cmd_step_over(self):
        pass


    def _update_focus(self, event):
        pass
    
    
    def enter_execution_mode(self, main_filename):
        assert not self.is_in_execution_mode() 
        
        # save all editors which have a filename
        for editor in self.winfo_children():
            if editor.get_filename():
                editor._cmd_save_file()
        
        # highlight and remember the main editor
        self._main_editor = self.get_editor(main_filename, True)
        self._main_editor.enter_execution_mode()
    
    def exit_execution_mode(self):
        assert self.is_in_execution_mode()
        
        for editor in self.winfo_children():
            editor.exit_execution_mode()
            
        self._main_editor = None
    
    def is_in_execution_mode(self):
        return self._main_editor is not None
            


class FrameVisualizer:
    """
    Is responsible for stepping through statements and updating corresponding UI
    in Editor-s, FunctionCallDialog-s, ModuleDialog-s and shell
    """
    def __init__(self, master, workbench, frame_id, line_offset=0, col_offset=0):
        self._text = master.text
        self._frame_id = frame_id
        self._expression_view = ExpressionView(master, workbench)
        self._next_frame_visualizer = None
        
    
    def update(self, msg):
        #print("SS", msg.state, msg.focus)
        # make sure current next_frame_handler is still relevant
        if self._next_frame_visualizer is not None:
            self._check_clear_next_frame_visualizer(msg.stack)
        
        # show this frame
        if msg.frame_id == self._frame_id:
            self._code_view.handle_focus_message(msg.focus, msg)
            self._expression_view.handle_vm_message(msg)
        else:
            if self._next_frame_visualizer is None:
                if msg.code_name == "<module>":
                    self._next_frame_visualizer = self.master.get_editor(msg.filename, True)
                    self._next_frame_visualizer.enter_execution_mode()
                else:
                    # Function call
                    if self._expression_view.winfo_ismapped():
                        call_label = self._expression_view.get_focused_text()
                    else:
                        call_label = "Function call at " + hex(self._frame_id) 
                    self._next_frame_visualizer = FunctionCallDialog(self._master, msg, call_label)
                    
            self._next_frame_visualizer.handle_vm_message(msg)
            
        
    def clear_debug_view(self):
        self._code_view.handle_focus_message(None)
        self._clear_next_frame_visualizer()
        self._expression_view.clear_debug_view()
    
    def _check_clear_next_frame_visualizer(self, current_stack):
        
        for frame in current_stack:
            if frame.id == self._next_frame_visualizer.get_frame_id():
                # it's still relevant
                return
        
        # didn't find that frame id
        self._clear_next_frame_visualizer()
    
    def _clear_next_frame_visualizer(self):
        if isinstance(self._next_frame_visualizer, Editor):
            self._next_frame_visualizer.exit_execution_mode()
        elif isinstance(self._next_frame_visualizer, FunctionCallDialog):
            self._next_frame_visualizer.destroy()
        else:
            assert self._next_frame_visualizer is None
            
        self._next_frame_visualizer = None
    
    def __del__(self):
        self.clear_debug_view()
        self._expression_view.destroy()


    # TODO:
    def _text_handle_focus_message(self, text_range, msg=None):
        
        if text_range is None:
            self.clear_tags(['before', 'after', 'exception'])
            
        elif "statement" in msg.state or "suite" in msg.state:
            self.clear_tags(['before', 'after', 'exception'])
            self.text.tag_configure('before', background="#F8FC9A", borderwidth=1, relief=tk.SOLID)
             
            if msg.state.startswith("before"):
                tag = "before"
            elif msg.state.startswith("after"):
                tag = "after"
            else:
                tag = "exception"
            
            # TODO: duplicated in main
            # better just skip those events
            if (msg.state in ("before_statement", "before_statement_again")
                or (self._workbench.get_option("debugging.detailed_steps")
                    and msg.state in ("after_statement",
                                      "after_suite",
                                      "before_suite"))):
                self.tag_range(text_range, tag, True)
            
        
        else:
            # if expression is in focus, statement will be shown without border
            self.text.tag_configure('before', background="#F8FC9A", borderwidth=0, relief=tk.SOLID)
            


    def _text_enter_execution_mode(self):
        self.read_only = True
        self.text.configure(insertwidth=0)
        self.text.configure(background="LightYellow")

    def _textexit_execution_mode(self):
        self.read_only = False
        self.text.configure(insertwidth=2)
        self.text.configure(background="White", insertwidth=2, insertbackground="Black")


class ScriptFrameVisualizer:
    pass

class ShellFrameVisualizer:
    pass

class ExpressionView(tk.Text):
    def __init__(self, codeview, workbench):
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
                         font=workbench.get_font("EditorFont"))
        self._codeview = codeview
        self._workbench = workbench
        self._main_range = None
        self._last_focus = None
        
        self.tag_config("value", foreground="Blue")
        self.tag_configure('before', background="#F8FC9A", borderwidth=1, relief=tk.SOLID)
        self.tag_configure('after', background="#D7EDD3", borderwidth=1, relief=tk.FLAT)
        self.tag_configure('exception', background="#FFBFD6", borderwidth=1, relief=tk.SOLID)
        
        
    def handle_vm_message(self, msg):
        debug("ExpressionView.handle_vm_message %s", (msg.state, msg.focus))
        
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
                if self._workbench.get_option("view.values_in_heap"):
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
                              lambda _: self._workbench.event_generate("ObjectSelect", object_id=msg.value.id))
                    
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
    

class ModuleLoadDialog(tk.Toplevel):
    pass         
    
class FunctionCallDialog(tk.Toplevel, FrameVisualizer):
    def __init__(self, master, msg, title):
        tk.Toplevel.__init__(self, master)
        self._frame_id = msg.frame_id
        self.title(title)
        self.transient(master)
        if misc_utils.running_on_windows():
            self.wm_attributes('-toolwindow', 1)
        
        
        # TODO: take size from prefs
        self.geometry("{}x{}+{}+{}".format(master.winfo_width(),
                                           master.winfo_height(),
                                           master.winfo_toplevel().winfo_rootx(),
                                           master.winfo_toplevel().winfo_rooty()))
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._init_layout_widgets(master, msg)
        self._load_function(msg)
        FrameVisualizer.__init__(self, msg.frame_id, master, self._workbench, self._code_view)
        self._code_view.text.focus()
    
    def get_frame_id(self):
        return self._frame_id
    
    def _init_layout_widgets(self, master, msg):
        self.main_frame= ttk.Frame(self) # just a backgroud behind padding of main_pw, without this OS X leaves white border
        self.main_frame.grid(sticky=tk.NSEW)        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.main_pw = ui_utils.AutomaticPanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.main_pw.grid(sticky=tk.NSEW, padx=10, pady=10)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        self._code_book = ttk.Notebook(self.main_pw)
        self._code_view = CodeView(self._code_book, first_line_no=msg.firstlineno)
        self._code_book.add(self._code_view)
        self._code_view.enter_execution_mode()
        
        #self._code_book.rowconfigure(1, weight=1)
        #self._code_book.columnconfigure(0, weight=1)
        
        
        self._locals_book = ttk.Notebook(self.main_pw)
        self._locals_frame = LocalsFrame(self._locals_book)
        self._locals_book.add(self._locals_frame, text="Local variables")
        
        
        self.main_pw.add(self._code_book, minsize=130)
        self.main_pw.add(self._locals_book, minsize=75)
    
    def _load_function(self, msg):
        self._code_view.set_content(msg.source)
        if hasattr(msg, "function"):
            function_label = msg.function.repr
        else:
            function_label = msg.code_name
             
        self._code_book.tab(self._code_view, text=function_label)
        #self._locals_frame.handle_vm_message(msg)
    
    def handle_vm_message(self, msg):
        self._stepper.handle_vm_message(msg)
        
        if hasattr(msg, "stack"):
            frame = list(filter(lambda f: f.id == self._frame_id, msg.stack))[0]
            self._locals_frame.update_variables(frame.locals)
        else:
            self._locals_frame.update_variables(None)
                
    
    def _on_close(self):
        showinfo("Can't close yet", "Step until the end of this function to close it")

    
class LocalsFrame(VariablesFrame):   
    def handle_vm_message(self, event):
        pass
    
def load_plugin(workbench):
    Debugger(workbench)
    
        