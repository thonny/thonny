"""
from rope.base.project import Project
from rope.refactor.rename import Rename
import rope.base.libutils
import tkinter as tk
from tkinter import ttk
import os.path

#arguments: 1) full path to the file, 2) new name to be applied to the identifier, 3) Rope offset (position) of the renamed identifier in the current file
#returns a list of Rope change objects applying to this rename refactor
#throws an exception if anything goes wrong, needs to be handled by callers!
def get_list_of_rename_changes(full_path, new_variable_name, offset):
    filearr = os.path.split(full_path)
    project_path = filearr[0]
    module_name = filearr[1]
    project = Project(project_path, ropefolder=None)
    module = rope.base.libutils.path_to_resource(project, full_path)
    changes = Rename(project, module, offset).get_changes(new_variable_name)
    return (project, changes)
    
#performs the changes 
#arguments: 1) Rope project, 2) Rope changes object
def perform_changes(project, changes):
    project.do(changes)
    project.close()

#cancels the changes, cleans up the project
def cancel_changes(project):
    project.close()

#utility method for convering a Text index to a Rope offset
def calculate_offset(text):
    contents = text.get(1.0, 'end').split('\n')
    insert_index = text.index('insert')
    linearr = insert_index.split('.')
    line_no = int(linearr[0])
    char_no = int(linearr[1])

    totalchars = char_no
    for line in range(line_no - 1):
        totalchars += len(contents[line]) + 1

    return totalchars

#inspired by http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
#creates a window asking for a new identifier name, can later be accessed via the refactor_new_variable_name variable
class RenameWindow(tk.Toplevel):
    def __init__(self, master, title = None):
        tk.Toplevel.__init__(self, master)
        self.refactor_new_variable_name = None

        self.transient(master)

        self.title('Rename')

        self.parent = master
        self.result = None
    
        ttk.Label(self, text="New name:").grid(row=0, columnspan=2)
        self.new_name_entry = ttk.Entry(self)
        self.new_name_entry.grid(row=1, columnspan=2)
        self.new_name_entry.focus_force();

        self.ok_button = ttk.Button(self, text="OK", command=self.ok, default=tk.ACTIVE)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.cancel)
        self.ok_button.grid(row=2, column=0, sticky=tk.W + tk.E, padx=5)
        self.cancel_button.grid(row=2, column=1, sticky=tk.W + tk.E, padx=5)

        self.bind("<Return>", self.ok, True)
        self.bind("<Escape>", self.cancel, True)

        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (master.winfo_rootx()+50,
                                  master.winfo_rooty()+50))
        self.resizable(width=False, height=False)

        self.wait_window(self)
    
    #user clicked cancel - destroy the object, return the focus to master    
    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()

    #user clicked ok - set the variable name, destroy the object, return the focus to parent
    def ok(self, event=None):
        self.withdraw()
        self.update_idletasks()
        self.refactor_new_variable_name = self.new_name_entry.get()
        self.cancel()


class RefactorRenameStartEvent(thonny.user_logging.UserEvent): #user initiated the refactoring process
    def __init__(self, editor):
        self.editor_id = id(editor)

class RefactorRenameCancelEvent(thonny.user_logging.UserEvent): #user manually cancelled the refactoring process
    def __init__(self, editor):
        self.editor_id = id(editor)

class RefactorRenameFailedEvent(thonny.user_logging.UserEvent): #refactoring process failed due to an error
    def __init__(self, editor):
        self.editor_id = id(editor)

class RefactorRenameCompleteEvent(thonny.user_logging.UserEvent): #refactoring process was successfully completed
    def __init__(self, description, offset, affected_files):
        self.description = description
        self.offset = offset
        self.affected_files = affected_files

def _cmd_refactor_rename(self):
    self.log_user_event(thonny.refactor.RefactorRenameStartEvent(self.editor_notebook.get_current_editor()))
    if not self.editor_notebook.get_current_editor():
        self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_notebook.get_current_editor()))
        errorMessage = tkMessageBox.showerror(
                       title="Rename failed",
                       message="Rename operation failed (no active editor tabs?).", #TODO - more informative text needed
                       master=self)
        return

    #create a list of active but unsaved/modified editors)
    unsaved_editors = [x for x in self.editor_notebook.winfo_children() if type(x) == Editor and x._cmd_save_file_enabled()]

    if len(unsaved_editors) != 0:
        #confirm with the user that all open editors need to be saved first
        confirm = tkMessageBox.askyesno(
                  title="Save Files Before Rename",
                  message="All modified files need to be saved before refactoring. Do you want to continue?",
                  default=tkMessageBox.YES,
                  master=self)

        if not confirm:
            self.log_user_event(thonny.refactor.RefactorRenameCancelEvent(self.editor_notebook.get_current_editor()))
            return #if user doesn't want it, return

        for editor in unsaved_editors:                     
            if not editor.get_filename():
                self.editor_notebook.select(editor) #in the case of editors with no filename, show it, so user knows which one they're saving
            editor._cmd_save_file()
            if editor._cmd_save_file_enabled(): #just a sanity check - if after saving a file still needs saving, something is wrong
                self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_notebook.get_current_editor()))
                errorMessage = tkMessageBox.showerror(
                               title="Rename failed",
                               message="Rename operation failed (saving file failed).", #TODO - more informative text needed
                               master=self)
                return

    filename = self.editor_notebook.get_current_editor().get_filename()

    if filename == None: #another sanity check - the current editor should have an associated filename by this point 
        self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_notebook.get_current_editor()))
        errorMessage = tkMessageBox.showerror(
                       title="Rename failed",
                       message="Rename operation failed (no filename associated with current module).", #TODO - more informative text needed
                       master=self)
        return

    identifier = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE) #regex to compare valid python identifiers against

    while True: #ask for new variable name until a valid one is entered
        renameWindow = thonny.refactor.RenameWindow(self)
        newname = renameWindow.refactor_new_variable_name
        if newname == None:
            self.log_user_event(thonny.refactor.RefactorRenameCancelEvent(self.editor_notebook.get_current_editor()))
            return #user canceled, return

        if re.match(identifier, newname):
            break #valid identifier entered, continue

        errorMessage = tkMessageBox.showerror(
                       title="Incorrect identifier",
                       message="Incorrect Python identifier, please re-enter.",
                       master=self)

    try: 
        #calculate the offset for rope
        offset = thonny.refactor.calculate_offset(self.editor_notebook.get_current_editor()._code_view.text)
        #get the project handle and list of changes
        project, changes = thonny.refactor.get_list_of_rename_changes(filename, newname, offset)
        #if len(changes.changes == 0): raise Exception

    except Exception:
        try: #rope needs the cursor to be AFTER the first character of the variable being refactored
             #so the reason for failure might be that the user had the cursor before the variable name
            offset = offset + 1
            project, changes = thonny.refactor.get_list_of_rename_changes(filename, newname, offset)
            #if len(changes.changes == 0): raise Exception

        except Exception: #couple of different reasons why this could happen, let's list them all in the error message
            self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_notebook.get_current_editor()))
            message = 'Rename operation failed. A few possible reasons: \n'
            message += '1) Not a valid Python identifier selected \n'
            message += '2) The current file or any other files in the same directory or in any of its subdirectores contain incorrect syntax. Make sure the current project is in its own separate folder.'
            errorMessage = tkMessageBox.showerror(
                           title="Rename failed",
                           message=message, #TODO - maybe also print stack trace for more info?
                           master=self)               
            return

    description = changes.description #needed for logging

    #sanity check
    if len(changes.changes) == 0:
        self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_notebook.get_current_editor()))
        errorMessage = tkMessageBox.showerror(
                           title="Rename failed",
                           message="Rename operation failed - no identifiers affected by change.", #TODO - more informative text needed
                           master=self)               
        return

    affected_files = [] #needed for logging
    #show the preview window to user
    messageText = 'Confirm the changes. The following files will be modified:\n'
    for change in changes.changes:
        affected_files.append(change.resource._path)
        messageText += '\n ' + change.resource._path

    messageText += '\n\n NB! This action cannot be undone.'

    confirm = tkMessageBox.askyesno(
              title="Confirm changes",
              message=messageText,
              default=tkMessageBox.YES,
              master=self)
    
    #confirm with user to finalize the changes
    if not confirm:
        self.log_user_event(thonny.refactor.RefactorRenameCancelEvent(self.editor_notebook.get_current_editor()))
        thonny.refactor.cancel_changes(project)
        return

    try:
        thonny.refactor.perform_changes(project, changes)
    except Exception:
            self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_notebook.get_current_editor()))
            errorMessage = tkMessageBox.showerror(
                           title="Rename failed",
                           message="Rename operation failed (Rope error).", #TODO - more informative text needed
                           master=self)     
            thonny.refactor.cancel_changes(project)
            return            

    #everything went fine, let's load all the active tabs again and set their content
    for editor in self.editor_notebook.winfo_children():
        try: 
            filename = editor.get_filename()
            source, self.file_encoding = misc_utils.read_python_file(filename)
            editor._code_view.set_content(source)
            self.editor_notebook.tab(editor, text=self.editor_notebook._generate_editor_title(filename))
        except Exception:
            try: #it is possible that a file (module) itself was renamed - Rope allows it. so let's see if a file exists with the new name. 
                filename = filename.replace(os.path.split(filename)[1], newname + '.py')
                source, self.file_encoding = misc_utils.read_python_file(filename)
                editor._code_view.set_content(source)
                self.editor_notebook.tab(editor, text=self.editor_notebook._generate_editor_title(filename))
            except Exception: #something went wrong with reloading the file, let's close this tab to avoid consistency problems
                self.editor_notebook.forget(editor)
                editor.destroy()

    self.log_user_event(thonny.refactor.RefactorRenameCompleteEvent(description, offset, affected_files))
    current_browser_node_path = self.file_browser.get_selected_path()
    self.file_browser.refresh_tree()
    if current_browser_node_path is not None:
        self.file_browser.open_path_in_browser(current_browser_node_path)

def _cmd_refactor_rename_enabled(self):
    return self.editor_notebook.get_current_editor() is not None

def _load_plugin_(workbench):
    get_workbench().add_command("refactor_rename", "edit", "Rename identifier", ...)
"""