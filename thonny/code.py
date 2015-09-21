# -*- coding: utf-8 -*-
import sys
import os.path
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkMessageBox
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename

from thonny.misc_utils import eqfn, get_res_path
from thonny.codeview import CodeView
from thonny.globals import get_workbench
from thonny import misc_utils
from logging import exception
from thonny.ui_utils import get_current_notebook_tab_widget, select_sequence

_dialog_filetypes = [('all files', '.*'), ('Python files', '.py .pyw'), ('text files', '.txt')]


                
class Editor(ttk.Frame):
    def __init__(self, master, filename=None):
        
        ttk.Frame.__init__(self, master)
        assert isinstance(master, EditorNotebook)
        
        # parent of codeview will be workbench so that it can be maximized
        self._code_view = CodeView(get_workbench(), propose_remove_line_numbers=True, editor=self)
        self._code_view.grid(row=0, column=0, sticky=tk.NSEW, in_=self)
        self._code_view.home_widget = self # don't forget home
        self.maximizable_widget = self._code_view
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._filename = None
        self.file_encoding = None
        
        if filename is not None:
            self._load_file(filename)
            self._code_view.text.edit_modified(False)
        
        self._code_view.text.bind("<<Modified>>", lambda e: master.update_editor_title(self))


    def get_text_widget(self):
        return self._code_view.text
    
    def get_code_view(self):
        # TODO: try to get rid of this
        return self._code_view
    
    def get_filename(self, try_hard=False):
        if self._filename is None and try_hard:
            self.save_file()
            
        return self._filename
            
    def _load_file(self, filename):
        source, self.file_encoding = misc_utils.read_python_file(filename) # TODO: support also text files
        self._filename = filename
        get_workbench().event_generate("Open", editor=self, filename=filename)
        self._code_view.set_content(source)
        self._code_view.focus_set()
        
    def is_modified(self):
        return self._code_view.text.edit_modified()
    
    
    def save_file_enabled(self):
        return self.is_modified() or not self.get_filename()
    
    def save_file(self, ask_filename=False):
        if self._filename is not None and not ask_filename:
            filename = self._filename
            get_workbench().event_generate("Save", editor=self)
        else:
            # http://tkinter.unpythonic.net/wiki/tkFileDialog
            filename = asksaveasfilename (
                filetypes = _dialog_filetypes, 
                defaultextension = ".py",
                initialdir = get_workbench().get_option("run.working_directory")
            )
            if filename == "":
                return None
            
            get_workbench().event_generate("SaveAs", editor=self, filename=filename)
                
        
        content = self._code_view.get_content()
        encoding = self.file_encoding or "UTF-8" 
        f = open(filename, mode="wb", )
        f.write(content.encode(encoding))
        f.close()

        self._filename = filename
        
        self._code_view.text.edit_modified(False)
        return self._filename
    
    def change_font_size(self, delta):
        self._code_view.change_font_size(delta)
    
    def show(self):
        self.master.select(self)
    
    def select_range(self, text_range):
        self._code_view.select_range(text_range)
    
    def focus_set(self):
        self._code_view.focus_set()
    
    def is_focused(self):
        return self.focus_displayof() == self._code_view.text
    
class EditorNotebook(ttk.Notebook):
    """
    Manages opened files / modules
    """
    def __init__(self, master):
        _check_create_ButtonNotebook_style()
        ttk.Notebook.__init__(self, master, padding=0, style="ButtonNotebook")
        
        get_workbench().add_option("file.reopen_files", False)
        
        self._init_commands()
        self.enable_traversal()
        
        # open files from last session
        """ TODO: they should go only to recent files
        for filename in prefs["open_files"].split(";"):
            if os.path.exists(filename):
                self._open_file(filename)
        """
        self._load_startup_files()
    
    def _list_recent_files(self):
        get_workbench().add_option("file.recent_files", [])
         
        # TODO:
        
    
    def _init_commands(self):    
        # TODO: do these commands have to be in EditorNotebook ??
        # Create a module level function install_editor_notebook ??
        # Maybe add them separately, when notebook has been installed ??
        
        
        get_workbench().add_command("new_file", "file", "New", 
            self._cmd_new_file,
            default_sequence=select_sequence("<Control-n>", "<Command-n>"),
            group=10,
            image_filename=get_res_path("file.new_file.gif"),
            include_in_toolbar=True)
        
        get_workbench().add_command("open_file", "file", "Open...", 
            self._cmd_open_file,
            default_sequence=select_sequence("<Control-o>", "<Command-o>"),
            group=10,
            image_filename=get_res_path("file.open_file.gif"),
            include_in_toolbar=True)
        
        get_workbench().add_command("close_file", "file", "Close", 
            self._cmd_close_file,
            default_sequence=select_sequence("<Control-w>", "<Command-w>"),
            tester=lambda: self.get_current_editor() is not None,
            group=10)
        
        get_workbench().add_command("save_file", "file", "Save", 
            self._cmd_save_file,
            default_sequence=select_sequence("<Control-s>", "<Command-s>"),
            tester=self._cmd_save_file_enabled,
            group=10,
            image_filename=get_res_path("file.save_file.gif"),
            include_in_toolbar=True)
        
        get_workbench().add_command("save_file_as", "file", "Save as...",
            self._cmd_save_file_as,
            default_sequence=select_sequence("<Control-Shift-S>", "<Command-Shift-S>"),
            tester=lambda: self.get_current_editor() is not None,
            group=10)
        
        get_workbench().add_command("toggle_comment", "edit", "Toggle comment",
            self._cmd_toggle_selection_comment,
            default_sequence=select_sequence("<Control-Key-3>", "<Command-Key-3>"),
            tester=None, # TODO: not read-only
            group=50)
        
        get_workbench().add_command("comment_selection", "edit", "Comment out",
            self._cmd_comment_selection,
            default_sequence="<Alt-Key-3>",
            tester=None, # TODO: not read-only
            group=50)
        
        get_workbench().add_command("uncomment_selection", "edit", "Uncomment",
            self._cmd_uncomment_selection,
            default_sequence="<Alt-Key-4>",
            tester=None, # TODO: not read-only
            group=50)

        get_workbench()
    
    
    def _load_startup_files(self):
        
        filenames = sys.argv[1:]
        
        if get_workbench().get_option("file.reopen_files"):
            for filename in get_workbench().get_option("file.open_files"): 
                if filename not in filenames:
                    filenames.append(filename) 
            
        for filename in filenames:
            if os.path.exists(filename):
                self.show_file(filename)
        
        if len(filenames) == 0:
            self._cmd_new_file()
        
        self._remember_open_files()
    
    def save_all_named_editors(self):
        for editor in self.winfo_children():
            if editor.get_filename():
                editor.save_file()
    
    def _remember_open_files(self):
        open_files = [editor.get_filename() 
                      for editor in self.winfo_children() 
                      if editor.get_filename()]
        
        get_workbench().set_option("file.open_files", open_files)
    
    def _cmd_new_file(self):
        new_editor = Editor(self)
        get_workbench().event_generate("NewFile", editor=new_editor)
        self.add(new_editor, text=self._generate_editor_title(None))
        self.select(new_editor)
        new_editor.focus_set()
    
    def _cmd_open_file(self):
        filename = askopenfilename (
            filetypes = _dialog_filetypes, 
            initialdir = get_workbench().get_option("run.working_directory")
        )
        if filename != "":
            #self.close_single_untitled_unmodified_editor()
            self.show_file(filename)
            self._remember_open_files()
    
    def _cmd_close_file(self):
        current_editor = self.get_current_editor()
        if current_editor:
            if not self.check_allow_closing(current_editor):
                return
            self.forget(current_editor)
            current_editor.destroy()
            self._remember_open_files()
    
    def _cmd_save_file(self):
        if self.get_current_editor():
            self.get_current_editor().save_file()
        
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
    
    def _cmd_toggle_selection_comment(self):
        if self.get_current_editor() is not None: 
            self.get_current_editor().get_code_view().toggle_selection_comment()
            
    def _cmd_comment_selection(self):
        if self.get_current_editor() is not None: 
            self.get_current_editor().get_code_view().comment_selection()
    
    def _cmd_uncomment_selection(self):
        if self.get_current_editor() is not None: 
            self.get_current_editor().get_code_view().uncomment_selection()
    
    def close_single_untitled_unmodified_editor(self):
        editors = self.winfo_children()
        if (len(editors) == 1 
            and not editors[0].is_modified()
            and not editors[0].get_filename()):
            self._cmd_close_file()
        
    def get_current_editor(self):
        return get_current_notebook_tab_widget(self)
    
    def show_file(self, filename, text_range=None):
        #self.close_single_untitled_unmodified_editor()
        editor = self.get_editor(filename, True)
        assert editor is not None
        
        self.select(editor)
        editor.focus_set()
        
        if text_range is not None:
            editor.select_range(text_range)
            
        return editor
    
    def change_font_size(self, delta):
        pass
    
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
    
    
    def focus_set(self):
        editor = self.get_current_editor()
        if editor: 
            editor.focus_set()
        else:
            super().focus_set()

    def current_editor_is_focused(self):
        editor = self.get_current_editor()
        return editor.is_focused()

    
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
            
        confirm = tkMessageBox.askyesnocancel(
                  title="Save On Close",
                  message=message,
                  default=tkMessageBox.YES,
                  master=self)
        
        if confirm:
            for editor in modified_editors:
                if editor.get_filename(True):
                    editor._cmd_save_file()
                else:
                    return False
            return True
        
        elif confirm is None:
            return False
        else:
            return True
        

def _check_create_ButtonNotebook_style():
    """Taken from http://svn.python.org/projects/python/trunk/Demo/tkinter/ttk/notebook_closebtn.py"""
    style = ttk.Style()
    if "closebutton" in style.element_names():
        # It's done already
        return

    get_workbench().get_image('tab_close.gif', "img_close")
    get_workbench().get_image('tab_close_active.gif', "img_close_active")
    
    style.element_create("closebutton", "image", "img_close",
        ("active", "pressed", "!disabled", "img_close_active"),
        ("active", "!disabled", "img_close_active"), border=8, sticky='')

    style.layout("ButtonNotebook", [("Notebook.client", {"sticky": "nswe"})])

    style.layout("ButtonNotebook.Tab", [
        ("ButtonNotebook.tab", {"sticky": "nswe", "children":
            [("ButtonNotebook.padding", {"side": "top", "sticky": "nswe",
                                         "children":
                [("ButtonNotebook.focus", {"side": "top", "sticky": "nswe",
                                           "children":
                    [("ButtonNotebook.label", {"side": "left", "sticky": ''}),
                     ("ButtonNotebook.closebutton", {"side": "left", "sticky": ''})
                     ]
                })]
            })]
        })]
    )

    def btn_press(event):
        try:
            x, y, widget = event.x, event.y, event.widget
            elem = widget.identify(x, y)
            index = widget.index("@%d,%d" % (x, y))
        
            if "closebutton" in elem:
                widget.state(['pressed'])
                widget.pressed_index = index
        except:
            # may fail, if clicked outside of tab
            pass
    
    def btn_release(event):
        x, y, widget = event.x, event.y, event.widget
    
        if not widget.instate(['pressed']):
            return
    
        try:
            elem =  widget.identify(x, y)
            index = widget.index("@%d,%d" % (x, y))
        
            if "closebutton" in elem and widget.pressed_index == index:
                if isinstance(widget, EditorNotebook):
                    widget._cmd_close_file()
                else:
                    widget.forget(index)
                    widget.event_generate("<<NotebookClosedTab>>")
        
            widget.state(["!pressed"])
            widget.pressed_index = None
        except:
            # may fail, when mouse is dragged
            exception("Closing tab")
    
    get_workbench().bind_class("TNotebook", "<ButtonPress-1>", btn_press, True)
    get_workbench().bind_class("TNotebook", "<ButtonRelease-1>", btn_release, True)
    
