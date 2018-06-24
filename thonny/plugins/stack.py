import tkinter as tk
from tkinter import ttk 
from thonny import get_workbench, ui_utils

class StackView(ui_utils.TreeFrame):
    def __init__(self, master):
        super().__init__(master, ("function", "location"))

        self.tree.column('function', width=120, anchor=tk.W, stretch=False)
        self.tree.column('location', width=450, anchor=tk.W, stretch=True)
        
        self.tree.heading('function', text='Function', anchor=tk.W) 
        self.tree.heading('location', text='Location', anchor=tk.W)
        
        get_workbench().bind("DebuggerProgress", self._update_stack, True)
        get_workbench().bind("ToplevelResult", lambda e=None: self._clear_tree(), True)
    
    def _update_stack(self, msg):
        self._clear_tree()
        for frame in msg.stack:
            if hasattr(frame, "lineno"):
                lineno = frame.lineno
            else:
                lineno = frame.last_event_focus.lineno
                
            node_id = self.tree.insert("", "end")
            self.tree.set(node_id, "function", frame.code_name)
            self.tree.set(node_id, "location", 
                          "%s, line %s" % (frame.filename, lineno))

def load_plugin():
    get_workbench().add_view(StackView, "Stack", "s")