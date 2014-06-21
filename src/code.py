# -*- coding: utf-8 -*-
from __future__ import print_function, division 
"""
EditorNotebook may contain several Editor-s, each Editor contains one CodeView.

It can present program execution information in two ways:
 - coarse: use enter/exit_execution_mode to highlight/un-highlight the main script
 - precise: pass DebuggerResponse-s to handle_vm_message to show program state more precisely

 EditorNotebook passes both kind of requests on to relevant editors.


"""

import os.path
from os.path import dirname, basename, abspath
import ast
import sys
from common import DebuggerResponse
from config import prefs
from misc_utils import eqfn
import ui_utils
import misc_utils
import memory
import logging

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import asksaveasfilename
    from tkinter.filedialog import askopenfilename
    #from tkinter.messagebox import showwarning
    from tkinter.messagebox import showinfo
except ImportError:
    import Tkinter as tk
    import ttk 
    from tkFileDialog import asksaveasfilename
    from tkFileDialog import askopenfilename
    #from tkMessageBox import showwarning
    from tkMessageBox import showinfo
    
import ast_utils
from memory import LocalsFrame
from misc_utils import read_python_file
from codeview import CodeView
from user_logging import log_user_event, SaveEvent, SaveAsEvent,\
    LoadEvent, NewFileEvent

EDITOR_STATE_CHANGE = "<<editor-state-change>>"

editor_book = None

logger = logging.getLogger("thonny.code")
logger.propagate = False
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler(sys.stdout))
debug = logger.debug

class StatementStepper:
    """
    Is responsible for stepping through statements and updating corresponding UI
    both in Editor-s and FunctionDialog-s
    """
    def __init__(self, frame_id, master, code_view):
        self._master = master
        self._code_view = code_view
        self._frame_id = frame_id
        self._expression_view = ExpressionView(code_view)
        self._next_frame_handler = None
    
    def get_frame_id(self):
        return self._frame_id
    
    def handle_vm_message(self, msg):
        #print("SS", msg.state, msg.focus)
        # make sure current next_frame_handler is still relevant
        if self._next_frame_handler != None:
            self._check_clear_next_frame_handler(msg.stack)
        
        # show this frame
        if msg.frame_id == self._frame_id:
            self._code_view.handle_focus_message(msg.focus, msg)
            self._expression_view.handle_vm_message(msg)
        else:
            if self._next_frame_handler == None:
                if msg.code_name == "<module>":
                    self._next_frame_handler = editor_book.get_editor(msg.filename, True)
                    self._next_frame_handler.enter_execution_mode()
                else:
                    # Function call
                    if self._expression_view.winfo_ismapped():
                        call_label = self._expression_view.get_focused_text()
                    else:
                        call_label = "Function call at " + hex(self._frame_id) 
                    self._next_frame_handler = FunctionDialog(self._master, msg, call_label)
                    
            self._next_frame_handler.handle_vm_message(msg)
            
        
    def clear_debug_view(self):
        self._code_view.handle_focus_message(None)
        self._clear_next_frame_handler()
        self._expression_view.clear_debug_view()
    
    def _check_clear_next_frame_handler(self, current_stack):
        
        for frame in current_stack:
            if frame.id == self._next_frame_handler.get_frame_id():
                # it's still relevant
                return
        
        # didn't find that frame id
        self._clear_next_frame_handler()
    
    def _clear_next_frame_handler(self):
        if isinstance(self._next_frame_handler, Editor):
            self._next_frame_handler.exit_execution_mode()
        elif isinstance(self._next_frame_handler, FunctionDialog):
            self._next_frame_handler.destroy()
        else:
            assert self._next_frame_handler == None
            
        self._next_frame_handler = None
    
    def __del__(self):
        self.clear_debug_view()
        self._expression_view.destroy()

class AdvancedStatementStepper(StatementStepper):
    pass
                
class Editor(ttk.Frame):
    """
    Text editor and visual part of module stepper
    """
    def __init__(self, master, filename=None):
        ttk.Frame.__init__(self, master)
        
        assert isinstance(master, EditorNotebook)
        
        self._code_view = CodeView(self)
        self._code_view.grid(sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._stepper = None
        
        self._filename = None
        self.file_encoding = None
        
        if filename != None:
            self._load_file(filename)
            self._code_view.text.edit_modified(False)
            
        self._code_view.text.bind("<<Modified>>", lambda _: self.event_generate(EDITOR_STATE_CHANGE), "+")
            

    def get_filename(self, try_hard=False):
        if self._filename == None and try_hard:
            self.cmd_save_file()
            
        return self._filename
            
    def _load_file(self, filename):
        source, self.file_encoding = read_python_file(filename) # TODO: support also text files
        self._filename = filename
        log_user_event(LoadEvent(self._code_view, filename))
        self._code_view.set_content(source)
        
    def is_modified(self):
        return self._code_view.text.edit_modified()
    
    
    def cmd_save_file_enabled(self):
        return self.is_modified()
    
    def cmd_select_all(self):
        self._code_view.select_all();
    
    def cmd_save_file(self):
        if self._filename != None:
            filename = self._filename
            log_user_event(SaveEvent(self._code_view))
        else:
            filename = asksaveasfilename()
            if filename == "":
                return None
            log_user_event(SaveAsEvent(self._code_view, filename))
                
        
        encoding = self.file_encoding or "UTF-8" 
        
        f = open(filename, mode="wb", )
        content = self._code_view.get_content()
        f.write(content.encode(encoding))
        f.close()
    
        self._filename = filename
        
        self._code_view.text.edit_modified(False)
        self.event_generate(EDITOR_STATE_CHANGE)
        
        return self._filename
    
    def change_font_size(self, delta):
        self._code_view.change_font_size(delta)
    
    def show(self):
        editor_book.select(self)
    
    def handle_vm_message(self, msg):
        assert isinstance(msg, DebuggerResponse)
        
        if self.is_modified():
            raise RuntimeError ("Can't show debug info in modified editor")
        
        """
        # actually this check is not sound, as this_frame.source is not guaranteed 
        # to be saved at code compilation time 
        if frame.source != self._code_view.get_content():
            print("Editor content>" + self._code_view.get_content() + "<")
            print("frame.source>" + frame.source + "<")
            raise RuntimeError ("Editor content doesn't match module source. Did you change it after starting the program?")
        """
        
        if self._stepper == None:
            if prefs["advanced_debugging"]:
                self._stepper = AdvancedStatementStepper(msg.frame_id, self, self._code_view)
            else:
                self._stepper = StatementStepper(msg.frame_id, self, self._code_view)
        
        self._stepper.handle_vm_message(msg)
    
    def select_range(self, text_range):
        self._code_view.select_range(text_range)
    
    def enter_execution_mode(self):
        self._code_view.enter_execution_mode()
    
    
    def clear_debug_view(self):
        if self._stepper != None:
            self._stepper.clear_debug_view()
    
    def exit_execution_mode(self):
        self.clear_debug_view()
        self._code_view.exit_execution_mode()
        self._stepper = None
    
    def get_frame_id(self):
        if self._stepper == None:
            return None
        else:
            return self._stepper.frame_id
    

class EditorNotebook(ttk.Notebook):
    """
    Manages opened files / modules
    """
    def __init__(self, master):
        ttk.Notebook.__init__(self, master, padding=0)
        self.enable_traversal()
        self.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.bind_all(EDITOR_STATE_CHANGE, self._on_editor_state_changed)
        
        self._main_editor = None # references the editor of main file during execution
        
        # TODO: temporary
        sfuffdir = os.path.normpath(os.path.join(dirname(abspath(__file__)), "..", "stuff"))
        self._open_file(os.path.join(sfuffdir, "euler1.py"))
        self._open_file(os.path.join(sfuffdir, "pere_sissetulek.py"))
        self._open_file(os.path.join(sfuffdir, "kuupaev.py"))
        #self._open_file(os.path.join(sfuffdir, "aliasing.py"))
        self._open_file(os.path.join(sfuffdir, "kahest_suurim.py"))
        self.show_file(os.path.join(sfuffdir, "kahest_suurim.py"))
        self.show_file(os.path.join(sfuffdir, "multilevel.py"))
        #self._open_file(progdir + "/../atidb.py")
        
        global editor_book
        editor_book = self
        
        
    def cmd_new_file(self):
        new_editor = Editor(self)
        log_user_event(NewFileEvent(new_editor._code_view))
        self.add(new_editor, text=self._generate_editor_title(None))
        self.select(new_editor)
    
    def cmd_open_file(self):
        filename = askopenfilename()
        if filename != "":
            self.show_file(filename)
    
    def cmd_close_file(self):
        # TODO: ask in case file is modified
        self.forget(self.select());
    
    def get_current_editor(self):
        for child in self.winfo_children():
            if str(child) == str(self.select()):
                return child
            
        return None
    
    """
    def save_all_named_editors(self):
        for editor in self.winfo_children():
            if editor.get_filename():
                editor.cmd_save_file()
    """
    
    def enter_execution_mode(self, main_filename):
        assert not self.is_in_execution_mode() 
        
        # save all editors which have a filename
        for editor in self.winfo_children():
            if editor.get_filename():
                editor.cmd_save_file()
        
        # highlight and remember the main editor
        self._main_editor = self.get_editor(main_filename, True)
        self._main_editor.enter_execution_mode()
    
    def exit_execution_mode(self):
        assert self.is_in_execution_mode()
        
        for editor in self.winfo_children():
            editor.exit_execution_mode()
            
        self._main_editor = None
    
    def is_in_execution_mode(self):
        return self._main_editor != None
            
    def handle_vm_message(self, msg):
        
        if self.is_in_execution_mode() and isinstance(msg, DebuggerResponse):
            debug("EditorNotebook.handle_vm_message: %s", (msg.state, msg.focus))
            if prefs["advanced_debugging"]:
                # only one editor shows debug view
                for editor in self.winfo_children():
                    if eqfn(editor.get_filename(), msg.filename):
                        editor.handle_vm_message(msg)
                    else:
                        editor.clear_debug_view()
            else:
                # editor of main file will take care of forwarding the msg
                self._main_editor.handle_vm_message(msg)
                
        else:
            pass # don't care about other events
    
    def show_file(self, filename, text_range=None):
        editor = self.get_editor(filename, True)
        self.select(editor)
        
        assert editor != None
        
        if text_range != None:
            editor.select_range(text_range)
            
        return editor
    
    def change_font_size(self, delta):
        pass
    
    def _on_editor_state_changed(self, event):
        assert isinstance(event.widget, Editor) 
        editor = event.widget
        self.tab(editor, text=self._generate_editor_title(editor.get_filename(), editor.is_modified()))
    
     
    def _generate_editor_title(self, filename, is_modified=False):
        if filename == None:
            result = "<untitled>"
        else:
            result = basename(filename)
        
        if is_modified:
            result += " *"
        
        return result
    
    
    def _on_tab_changed(self, event):
        "TODO:"
        
    def _open_file(self, filename):
        editor = Editor(self, filename)
        self.add(editor, text=self._generate_editor_title(filename))
              
        return editor
        
    def get_editor(self, filename, open_when_necessary=False):
        for child in self.winfo_children():
            child_filename = child.get_filename(False)
            if child_filename and eqfn(child.get_filename(), filename):
                return child
        
        if open_when_necessary:
            return self._open_file(filename)
        else:
            return None
    

class ExpressionView(tk.Text):
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
                         font=ui_utils.EDITOR_FONT)
        self._codeview = codeview
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
            if self._main_range == None or msg.focus.not_smaller_eq_in(self._main_range):
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
                if (prefs["values_in_heap"]
                    and not (msg.value.is_function and prefs["friendly_values"])):
                    value_str = id_str
                elif prefs["friendly_values"]:
                    value_str = msg.value.friendly_repr
                else:
                    value_str = msg.value.short_repr
                
                #print("ins", start_mark, value_str)
                self.insert(start_mark, value_str, ('value', 'after', id_str))
                #self.insert(start_mark, value_str) # TODO:
                self._update_size()
                
            else:
                debug("EV: got exc: %s", msg)
                "TODO: make it red"
                
        elif (msg.state == "before_statement_again"
              and self._main_range != None # TODO: shouldn't need this 
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
        assert self._main_range != None
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
    
         
    
class FunctionDialog(tk.Toplevel):
    def __init__(self, master, msg, title):
        tk.Toplevel.__init__(self, master)
        self._frame_id = msg.frame_id
        self.title(title)
        self.transient(master)
        if ui_utils.running_on_windows():
            self.wm_attributes('-toolwindow', 1)
        
        
        # TODO: take size from prefs
        self.geometry("{}x{}+{}+{}".format(master.winfo_width(),
                                           master.winfo_height(),
                                           master.winfo_toplevel().winfo_rootx(),
                                           master.winfo_toplevel().winfo_rooty()))
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._init_layout_widgets(master, msg)
        self._load_function(msg)
        self._stepper = StatementStepper(msg.frame_id, self, self._code_view)
        self._code_view.text.focus()
    
    def get_frame_id(self):
        return self._frame_id
    
    def _init_layout_widgets(self, master, msg):
        self.main_frame= ttk.Frame(self) # just a backgroud behind padding of main_pw, without this OS X leaves white border
        self.main_frame.grid(sticky=tk.NSEW)        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.main_pw = ui_utils.create_PanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.main_pw.grid(sticky=tk.NSEW, padx=10, pady=10)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        
        self._code_book = ui_utils.PanelBook(self.main_pw)
        self._code_view = CodeView(self._code_book, first_line_no=msg.firstlineno)
        self._code_book.add(self._code_view)
        self._code_view.enter_execution_mode()
        
        #self._code_book.rowconfigure(1, weight=1)
        #self._code_book.columnconfigure(0, weight=1)
        
        
        self._locals_book = ui_utils.PanelBook(self.main_pw)
        self._locals_frame = LocalsFrame(self._locals_book)
        self._locals_book.add(self._locals_frame, text="Local variables")
        
        
        self.main_pw.add(self._code_book, minsize=150)
        self.main_pw.add(self._locals_book, minsize=150)
    
    def _load_function(self, msg):
        self._code_view.set_content(msg.source)
        if hasattr(msg, "function"):
            function_label = msg.function.short_repr
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

    