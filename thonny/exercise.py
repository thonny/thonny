import tkinter as tk
from tkinter import ttk
from thonny.globals import get_workbench
import tkinterhtml

ABOUT_EXERCISE_VIEW = "About exercise view"

_plugins = []

def add_plugin(plugin):
    global _plugins
    _plugins.append(plugin)

class ExerciseView(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, background="white", **kw)
        self._init_widgets()
    
    def _init_widgets(self):
        padx = 15
        pady = 15
        
        course_combo_values = [ABOUT_EXERCISE_VIEW] + self._get_known_courses()
        for plugin in _plugins:      
            course_combo_values.append("<open %s>" % plugin.get_kind())
            
        self._course_combo = ttk.Combobox(self,
                              exportselection=False,
                              state='readonly',
                              #textvariable=self._interpreter_variable,
                              values=course_combo_values)
        
        self._course_combo.grid(column=1, row=1, sticky=tk.NSEW, padx=padx, pady=pady)
        
        self._exercise_title_combo = ttk.Combobox(self,
                              exportselection=False,
                              state='readonly',
                              #textvariable=self._interpreter_variable,
                              values=["<select exercise>"])
        
        self._exercise_title_combo.grid(column=1, row=2, sticky=tk.NSEW, padx=padx, pady=(0,pady))
        
        self._task_frame = tkinterhtml.HtmlFrame(self, borderwidth=1, relief=tk.FLAT,
                                                 horizontal_scrollbar="auto")
        self._task_frame.grid(column=1, row=3, sticky=tk.NSEW, padx=padx, pady=(0, pady))
        self._task_frame.set_content("<html><body></body></html>")
        
        self._submit_button = ttk.Button(self, text="Submit kala.py", command=self._on_submit)
        self._submit_button.grid(column=1, row=4, sticky=tk.NSEW, padx=padx, pady=(0, pady))
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
        
    def _get_known_courses(self):
        return ["Programmeerimise alused",
                "Programmeerimisest maalähedaselt"]
    
    def _on_submit(self):
        print("Submit")

def init_exercise_system():    
    get_workbench().add_view(ExerciseView, "Exercise", "ne")
