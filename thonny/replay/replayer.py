import tkinter as tk
import tkinter.ttk as ttk
from thonny import ui_utils
from thonny.ui_utils import TextWrapper


class ReplayWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.main_pw   = ui_utils.create_PanedWindow(self, orient=tk.HORIZONTAL)
        self.left_pw  = ui_utils.create_PanedWindow(self.main_pw, orient=tk.VERTICAL)
        self.right_frame = ttk.Frame(self.main_pw)
        self.editor_book = EditorNotebook(self.left_pw)
        shell_book = ui_utils.PanelBook(self.main_pw)
        self.shell = ShellFrame(shell_book)
        self.log_frame = LogFrame(self.right_frame)
        self.control_frame = ControlFrame(self.right_frame)
        
        self.main_pw.grid(padx=10, pady=10, sticky=tk.NSEW)
        self.main_pw.add(self.left_pw)
        self.main_pw.add(self.right_frame)
        self.left_pw.add(self.editor_book)
        self.left_pw.add(shell_book)
        shell_book.add(self.shell, text="Shell")
        self.log_frame.grid()
        self.control_frame.grid()
        


class ControlFrame(ttk.Frame):
    pass

class LogFrame(ui_utils.TreeFrame):
    def __init__(self, master):
        ui_utils.TreeFrame.__init__(self, master, ("Event", "Time"))    

class ShellFrame(ttk.Frame, TextWrapper):
    pass

class EditorNotebook(ttk.Notebook):
    pass

if __name__ == "__main__":
    ReplayWindow().mainloop()    