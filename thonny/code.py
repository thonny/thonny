# -*- coding: utf-8 -*-
import sys
import os.path
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename

from thonny.misc_utils import eqfn
from thonny.codeview import CodeView
from thonny import get_workbench, ui_utils
from logging import exception
from thonny.ui_utils import select_sequence
from thonny.tktextext import rebind_control_a
import tokenize
from tkinter.messagebox import askyesno
import traceback

_dialog_filetypes = [('Python files', '.py .pyw'), ('text files', '.txt'), ('all files', '.*')]


                
class Editor(ttk.Frame):
    def __init__(self, master, filename=None):
        
        ttk.Frame.__init__(self, master)
        assert isinstance(master, EditorNotebook)
        
        # parent of codeview will be workbench so that it can be maximized
        self._code_view = CodeView(get_workbench(),
                                   propose_remove_line_numbers=True,
                                   font="EditorFont")
        get_workbench().event_generate("EditorTextCreated", editor=self, text_widget=self.get_text_widget())
        
        self._code_view.grid(row=0, column=0, sticky=tk.NSEW, in_=self)
        self._code_view.home_widget = self # don't forget home
        self.maximizable_widget = self._code_view
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._filename = None
        
        if filename is not None:
            self._load_file(filename)
            self._code_view.text.edit_modified(False)
        
        self._code_view.text.bind("<<Modified>>", self._on_text_modified, True)
        self._code_view.text.bind("<<TextChange>>", self._on_text_change, True)
        self._code_view.text.bind("<Control-Tab>", self._control_tab, True)
        
        get_workbench().bind("DebuggerProgress", self._listen_debugger_progress, True)
        get_workbench().bind("ToplevelResult", self._listen_for_toplevel_result, True)
        
        self.update_appearance()


    def get_text_widget(self):
        return self._code_view.text
    
    def get_code_view(self):
        # TODO: try to get rid of this
        return self._code_view
    
    def get_filename(self, try_hard=False):
        if self._filename is None and try_hard:
            self.save_file()
            
        return self._filename
    
    def get_long_description(self):
        
        if self._filename is None:
            result = "<untitled>"
        else:
            result = self._filename
        
        try:
            index = self._code_view.text.index("insert")
            if index and "." in index:
                line, col = index.split(".")
                result += "  @  {} : {}".format(line, int(col)+1)
        except:
            exception("Finding cursor location")
        
        return result
    
    def _load_file(self, filename):
        with tokenize.open(filename) as fp: # TODO: support also text files
            source = fp.read() 
            
        self._filename = filename
        get_workbench().event_generate("Open", editor=self, filename=filename)
        self._code_view.set_content(source)
        self._code_view.focus_set()
        self.master.remember_recent_file(filename)
        
    def is_modified(self):
        return self._code_view.text.edit_modified()
    
    
    def save_file_enabled(self):
        return self.is_modified() or not self.get_filename()
    
    def save_file(self, ask_filename=False):
        if self._filename is not None and not ask_filename:
            filename = self._filename
            get_workbench().event_generate("Save", editor=self, filename=filename)
        else:
            # http://tkinter.unpythonic.net/wiki/tkFileDialog
            filename = asksaveasfilename (
                filetypes = _dialog_filetypes, 
                defaultextension = ".py",
                initialdir = get_workbench().get_cwd()
            )
            if filename in ["", (), None]: # Different tkinter versions may return different values
                return None
            
            # Seems that in some Python versions defaultextension 
            # acts funny
            if filename.lower().endswith(".py.py"):
                filename = filename[:-3]
            
            get_workbench().event_generate("SaveAs", editor=self, filename=filename)
                
        
        content = self._code_view.get_content()
        encoding = "UTF-8" # TODO: check for marker in the head of the code
        try: 
            f = open(filename, mode="wb", )
            f.write(content.encode(encoding))
            f.flush()
            os.fsync(f) # Force writes on disk, see https://learn.adafruit.com/adafruit-circuit-playground-express/creating-and-editing-code#1-use-an-editor-that-writes-out-the-file-completely-when-you-save-it
            f.close()
        except PermissionError:
            if askyesno("Permission Error",
                     "Looks like this file or folder is not writable.\n\n"
                     + "Do you want to save under another folder and/or filename?"):
                return self.save_file(True)
            else:
                return None
            

        self._filename = filename
        self.master.remember_recent_file(filename)
        
        self._code_view.text.edit_modified(False)

        return self._filename
    
    def show(self):
        self.master.select(self)
    
    def update_appearance(self):
        self._code_view.set_line_numbers(
            get_workbench().get_option("view.show_line_numbers")
            or get_workbench().get_mode() == "simple")
        self._code_view.set_line_length_margin(get_workbench().get_option("view.recommended_line_length"))
        self._code_view.text.event_generate("<<UpdateAppearance>>")
    
    def _listen_debugger_progress(self, event):
        # Go read-only
        # TODO: check whether this module is active?
        self._code_view.text.set_read_only(True)
    
    def _listen_for_toplevel_result(self, event):
        self._code_view.text.set_read_only(False)
    
    def _control_tab(self, event):
        if event.state & 1: # shift was pressed
            direction = -1
        else:
            direction = 1
        self.master.select_next_prev_editor(direction)
        return "break"
    
    def _shift_control_tab(self, event):
        self.master.select_next_prev_editor(-1)
        return "break"
    
    def select_range(self, text_range):
        self._code_view.select_range(text_range)
    
    def focus_set(self):
        self._code_view.focus_set()
    
    def is_focused(self):
        return self.focus_displayof() == self._code_view.text

    def _on_text_modified(self, event):
        try:
            self.master.update_editor_title(self)
        except:
            traceback.print_exc()

    def _on_text_change(self, event):
        self.master.update_editor_title(self)
        
    def destroy(self):
        get_workbench().unbind("DebuggerProgress", self._listen_debugger_progress)
        get_workbench().unbind("ToplevelResult", self._listen_for_toplevel_result)
        ttk.Frame.destroy(self)
    
class EditorNotebook(ui_utils.ClosableNotebook):
    """
    Manages opened files / modules
    """
    def __init__(self, master):
        super().__init__(master, padding=0)
        
        get_workbench().set_default("file.reopen_all_files", False)
        get_workbench().set_default("file.open_files", [])
        get_workbench().set_default("file.current_file", None)
        get_workbench().set_default("file.recent_files", [])
        get_workbench().set_default("view.highlight_current_line", False)
        get_workbench().set_default("view.show_line_numbers", False)
        get_workbench().set_default("view.recommended_line_length", 0)
        
        self._init_commands()
        self.enable_traversal()
        
        # open files from last session
        """ TODO: they should go only to recent files
        for filename in prefs["open_files"].split(";"):
            if os.path.exists(filename):
                self._open_file(filename)
        """
        
        self.update_appearance()
    
    def _list_recent_files(self):
        pass
        # TODO:
        
    
    def _init_commands(self):    
        # TODO: do these commands have to be in EditorNotebook ??
        # Create a module level function install_editor_notebook ??
        # Maybe add them separately, when notebook has been installed ??
        
        
        get_workbench().add_command("new_file", "file", "New", 
            self._cmd_new_file,
            caption="New",
            default_sequence=select_sequence("<Control-n>", "<Command-n>"),
            group=10,
            image="new-file",
            include_in_toolbar=True)
        
        get_workbench().add_command("open_file", "file", "Open...", 
            self._cmd_open_file,
            caption="Load",
            default_sequence=select_sequence("<Control-o>", "<Command-o>"),
            group=10,
            image="open-file",
            include_in_toolbar=True)
        
        # http://stackoverflow.com/questions/22907200/remap-default-keybinding-in-tkinter
        get_workbench().bind_class("Text", "<Control-o>", self._control_o)
        rebind_control_a(get_workbench())
        
        get_workbench().add_command("close_file", "file", "Close", 
            self._cmd_close_file,
            default_sequence=select_sequence("<Control-w>", "<Command-w>"),
            tester=lambda: self.get_current_editor() is not None,
            group=10)
        
        get_workbench().add_command("close_files", "file", "Close all", 
            self.close_tabs,
            tester=lambda: self.get_current_editor() is not None,
            group=10)
        
        get_workbench().add_command("save_file", "file", "Save", 
            self._cmd_save_file,
            caption="Save",
            default_sequence=select_sequence("<Control-s>", "<Command-s>"),
            tester=self._cmd_save_file_enabled,
            group=10,
            image="save-file",
            include_in_toolbar=True)
        
        get_workbench().add_command("save_file_as", "file", "Save as...",
            self._cmd_save_file_as,
            default_sequence=select_sequence("<Control-Shift-S>", "<Command-Shift-S>"),
            tester=lambda: self.get_current_editor() is not None,
            group=10)
        

        get_workbench().createcommand("::tk::mac::OpenDocument", self._mac_open_document)
    
    
    def load_startup_files(self):
        """If no filename was sent from command line
        then load previous files (if setting allows)"""  
        
        cmd_line_filenames = [name for name in sys.argv[1:] if os.path.exists(name)]
        
        
        if len(cmd_line_filenames) > 0:
            filenames = cmd_line_filenames
        elif get_workbench().get_option("file.reopen_all_files"):
            filenames = get_workbench().get_option("file.open_files")
        elif get_workbench().get_option("file.current_file"):
            filenames = [get_workbench().get_option("file.current_file")]
        else:
            filenames = []
            
        if len(filenames) > 0:
            for filename in filenames:
                if os.path.exists(filename):
                    self.show_file(filename)
            
            cur_file = get_workbench().get_option("file.current_file")
            # choose correct active file
            if len(cmd_line_filenames) > 0:
                self.show_file(cmd_line_filenames[0])
            elif cur_file and os.path.exists(cur_file):
                self.show_file(cur_file)
            else:
                self._cmd_new_file()
        else:
            self._cmd_new_file()
            
        
        self._remember_open_files()
    
    def save_all_named_editors(self):
        all_saved = True
        for editor in self.winfo_children():
            if editor.get_filename() and editor.is_modified():
                success = editor.save_file()
                all_saved = all_saved and success
        
        return all_saved
    
    def remember_recent_file(self, filename):
        recents = get_workbench().get_option("file.recent_files")
        if filename in recents:
            recents.remove(filename)
        recents.insert(0, filename)
        existing_recents = [name for name in recents if os.path.exists(name)]
        get_workbench().set_option("file.recent_files", existing_recents[:10])
            
    def _remember_open_files(self):
        if (self.get_current_editor() is not None 
            and self.get_current_editor().get_filename() is not None):
            get_workbench().set_option("file.current_file", 
                                       self.get_current_editor().get_filename())
            
        open_files = [editor.get_filename() 
                          for editor in self.winfo_children() 
                          if editor.get_filename()]
        
        get_workbench().set_option("file.open_files", open_files)
        
        if len(open_files) == 0:
            get_workbench().set_option("file.current_file", None)
    
    def _cmd_new_file(self):
        new_editor = Editor(self)
        get_workbench().event_generate("NewFile", editor=new_editor)
        self.add(new_editor, text=self._generate_editor_title(None))
        self.select(new_editor)
        new_editor.focus_set()
    
    def _cmd_open_file(self):
        filename = askopenfilename (
            filetypes = _dialog_filetypes, 
            initialdir = get_workbench().get_cwd()
        )
        if filename: # Note that missing filename may be "" or () depending on tkinter version
            #self.close_single_untitled_unmodified_editor()
            self.show_file(filename)
            self._remember_open_files()
    
    def _control_o(self, event):
        # http://stackoverflow.com/questions/22907200/remap-default-keybinding-in-tkinter
        self._cmd_open_file()
        return "break"
    
    def _close_files(self, except_index=None):
        
        for tab_index in reversed(range(len(self.winfo_children()))):
            if except_index is not None and tab_index == except_index:
                continue
            else:
                editor = self.get_child_by_index(tab_index)
                if self.check_allow_closing(editor):
                    self.forget(editor)
                    editor.destroy()
                
        self._remember_open_files()
        
    
    def _cmd_close_file(self):
        self.close_tab(self.index(self.select()))
    
    def close_tab(self, index):
        editor = self.get_child_by_index(index)
            
        if editor:
            if not self.check_allow_closing(editor):
                return
            self.forget(editor)
            editor.destroy()
            self._remember_open_files()
    
    def _cmd_save_file(self):
        if self.get_current_editor():
            self.get_current_editor().save_file()
            self.update_editor_title(self.get_current_editor())
        
        self._remember_open_files()
    
    def _cmd_save_file_enabled(self):
        return (self.get_current_editor() 
            and self.get_current_editor().save_file_enabled())
    
    def _cmd_save_file_as(self):
        if self.get_current_editor():
            self.get_current_editor().save_file(ask_filename=True)
            self.update_editor_title(self.get_current_editor())
            
        self._remember_open_files()
    
    def _cmd_save_file_as_enabled(self):
        return self.get_current_editor() is not None
    
    def close_single_untitled_unmodified_editor(self):
        editors = self.winfo_children()
        if (len(editors) == 1 
            and not editors[0].is_modified()
            and not editors[0].get_filename()):
            self._cmd_close_file()
    
    def _mac_open_document(self, *args):
        for arg in args:
            if isinstance(arg, str) and os.path.exists(arg):
                self.show_file(arg)
        get_workbench().become_topmost_window()
        
    def get_current_editor(self):
        return self.get_current_child()
    
    def select_next_prev_editor(self, direction):
        cur_index = self.index(self.select())
        next_index = (cur_index + direction) % len(self.tabs())
        self.select(self.get_child_by_index(next_index))
    
    def show_file(self, filename, text_range=None):
        #self.close_single_untitled_unmodified_editor()
        editor = self.get_editor(filename, True)
        assert editor is not None
        
        self.select(editor)
        editor.focus_set()
        
        if text_range is not None:
            editor.select_range(text_range)
            
        return editor
    
    def update_appearance(self):
        for editor in self.winfo_children():
            editor.update_appearance()
    
    def update_editor_title(self, editor):
        self.tab(editor,
            text=self._generate_editor_title(editor.get_filename(), editor.is_modified()))
    
     
    def _generate_editor_title(self, filename, is_modified=False):
        if filename is None:
            result = "<untitled>"
        else:
            result = os.path.basename(filename)
        
        if is_modified:
            result += " *"
        
        return result
    
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
    
    
    def check_allow_closing(self, editor=None):
        if not editor:
            modified_editors = [e for e in self.winfo_children() if e.is_modified()]
        else:
            if not editor.is_modified():
                return True
            else:
                modified_editors = [editor]
        if len(modified_editors) == 0:
            return True
        
        message = "Do you want to save files before closing?"
        if editor:
            message = "Do you want to save file before closing?"
            
        confirm = messagebox.askyesnocancel(
                  title="Save On Close",
                  message=message,
                  default=messagebox.YES,
                  master=self)
        
        if confirm:
            for editor in modified_editors:
                if editor.get_filename(True):
                    editor.save_file()
                else:
                    return False
            return True
        
        elif confirm is None:
            return False
        else:
            return True
        
