import tkinter as tk
from tkinter import ttk
from thonny.globals import get_workbench
import tkinterhtml
from thonny.ui_utils import create_string_var

_plugins = {}

def add_plugin(plugin):
    _plugins[plugin.get_id()] = plugin

def refresh_ui():
    """Notifies ExerciseView about updates (submission complete etc.)"""
    # TODO:

class Plugin:
    def get_id(self):
        """return string for identifying the plugin"""
        return type(self).__name__
    
    def get_open_course_prompt(self):
        """Don't put <> here"""
        return "Open a %s course ..." % self.get_id()
    
    def open_course(self, course_id=None):
        """If course_id is None, prompt user about details and return new course object."""

class Course:
    def get_id(self):
        """Return the id of this course (eg. url or path)"""
    
    def get_title(self):
        """Return title to be shown in the course combo (without plugin_id and course_id)"""
    
    def get_exercises(self):
        """Return list of exercise objects"""
        
class Exercise:
    def get_title(self):
        """Return title to be shown in the exercise combo"""
    
    def get_description(self):
        """Return html description of the exercise"""
    
    def get_required_files(self):
        """Return list of required file names"""
        return []
    
    def get_max_number_of_files(self):
        """Return how many files can be submitted"""
        return 1
    
    def accept_submission(self, file_names, feedback_reporting_function):
        """Start checking procedure and return.
        Call refresh_ui when checking is complete."""
    
    def cancel_submission(self):
        """Try to cancel ongoing submission.
        Call refresh_ui when submission is cancelled."""
    
    def get_latest_feedback(self):
        """Return latest feedback as html string or None"""
        return None
    
    def get_state(self):
        '''Return "checking", "cancelling" or "ready"'''

class ExerciseView(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, background="white", **kw)
        self._init_widgets()
        self._exercises_by_title = {}
        
        self._plugins_by_prompt = {}
    
    def _init_widgets(self):
        padx = 15
        pady = 15
        
        self._course_combo_var = create_string_var("")
        self._course_combo = ttk.Combobox(self,
                              exportselection=False,
                              state='readonly',
                              textvariable=self._course_combo_var,
                              values=[],
                              postcommand=self._reload_courses_info)
        self._course_combo.bind("<<ComboboxSelected>>", self._on_course_combo_select, True)
        self._course_combo.grid(column=1, row=1, sticky=tk.NSEW, padx=padx, pady=pady)
        
        self._exercise_title_var = create_string_var("")
        self._exercise_combo = ttk.Combobox(self,
                              exportselection=False,
                              state='readonly',
                              textvariable=self._exercise_title_var,
                              values=["<select exercise>", "1. Nädalapalk"])
        self._exercise_combo.bind("<<ComboboxSelected>>", self._on_exercise_combo_select, True)
        self._exercise_combo.grid(column=1, row=2, sticky=tk.NSEW, padx=padx, pady=(0,pady))
        
        self._task_frame = tkinterhtml.HtmlFrame(self, borderwidth=1, relief=tk.FLAT,
                                                 horizontal_scrollbar="auto")
        self._task_frame.grid(column=1, row=3, sticky=tk.NSEW, padx=padx, pady=(0, pady))
        
        self._submit_button = ttk.Button(self, text='Submit `npalk.py`', command=self._on_submit)
        self._submit_button.grid(column=1, row=4, sticky=tk.NSEW, padx=padx, pady=(0, pady))
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
        
        self._reset_course()
    
    def _reset_course(self):
        self._course_combo_var.set("Select a course ...")
        self._exercise_title_var.set("")
        self._task_frame.set_content("<p>&nbsp;</p>")
        self._exercises_by_title = {}
    
    def _get_known_courses(self):
        """Returns dictionary where key is course title and value is pair of plugin_id and course_id"""
        return get_workbench().get_option("exersys.known_courses")
    
    def _reload_courses_info(self, event=None):
        values = []
        
        for course_title in self._get_known_courses():
            values.append(course_title)
        
        # links for opening new courses
        for plugin_id in _plugins:
            plugin = _plugins[plugin_id]
            prompt = "<%s>" % plugin.get_open_course_prompt()
            values.append(prompt)
            self._plugins_by_prompt[prompt] = plugin
        
        self._course_combo["values"] = values
    
    def _on_course_combo_select(self, event=None):
        selected_item = self._course_combo.get()
        
        if selected_item.startswith("<"):
            plugin = self._plugins_by_prompt[selected_item]
            course_id = None
        else:
            course_id, plugin_id = self._get_known_courses()[selected_item]
            plugin = _plugins[plugin_id]
        
        course = plugin.open_course(course_id)
        
        if course:
            self._load_course(course)
        else:
            self._reset_course()
    
    def _on_exercise_combo_select(self, event=None):
        print("EXSELECT")
        title = self._exercise_title_var.get()
        exercise = self._exercises_by_title[title]
        self._load_exercise(exercise)
    
    def _load_course(self, course):
        self._course_combo_var.set(course.get_title())
        
        exercise_titles = []
        for exercise in course.get_exercises():
            exercise_titles.append(exercise.get_title())
            self._exercises_by_title[exercise.get_title()] = exercise
            
        self._exercise_combo['values'] = exercise_titles
        
        if len(exercise_titles) > 0:
            self._exercise_combo.current(0)
            self._on_exercise_combo_select()
    
    def _load_exercise(self, exercise):
        self._exercise_title_var.set(exercise.get_title())
        self._task_frame.set_content(exercise.get_description())

    def _on_submit(self):
        print("Submit")
        
def init_exercise_system():    
    get_workbench().add_option("exersys.known_courses", [])
    get_workbench().add_view(ExerciseView, "Exercise", "ne")
