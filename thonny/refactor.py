from rope.base.project import Project
from rope.refactor.rename import Rename
import rope.base.libutils
import tkinter as tk
from tkinter import ttk
import os.path
import thonny.user_logging

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
    def __init__(self, parent, title = None):
        tk.Toplevel.__init__(self, parent)
        self.refactor_new_variable_name = None

        self.transient(parent)

        self.title('Rename')

        self.parent = parent
        self.result = None
    
        ttk.Label(self, text="New name:").grid(row=0, columnspan=2)
        self.new_name_entry = ttk.Entry(self)
        self.new_name_entry.grid(row=1, columnspan=2)
        self.new_name_entry.focus_force();

        self.ok_button = ttk.Button(self, text="OK", command=self.ok, default=tk.ACTIVE)
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.cancel)
        self.ok_button.grid(row=2, column=0, sticky=tk.W + tk.E, padx=5)
        self.cancel_button.grid(row=2, column=1, sticky=tk.W + tk.E, padx=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.resizable(width=False, height=False)

        self.wait_window(self)
    
    #user clicked cancel - destroy the object, return the focus to parent    
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