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
        return "Open a course ..."
    
    def open_course(self, course_id=None):
        """If course_id is None, prompt user about details and return new course object."""

class Course:
    def get_plugin(self):
        """Return the plugin associated with this course"""
    
    def get_id(self):
        """Return the id of this course (eg. url or path)"""
    
    def get_title(self):
        """Return title to be shown in the course combo (without plugin_id and course_id)"""
    
    def get_exercises(self):
        """Return list of exercise objects"""
        
    def _get_descriptor(self):
        return self.get_plugin().get_id() + ": " + self.get_title() + " @ " + self.get_id()
        
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
        
        self._current_course = None
    
    def _init_widgets(self):
        padx = 15
        pady = 15
        
        self._course_title_var = create_string_var("")
        self._course_combo = ttk.Combobox(self,
                              exportselection=False,
                              state='readonly',
                              textvariable=self._course_title_var,
                              values=[],
                              postcommand=self._reload_courses_info)
        self._course_combo.bind("<<ComboboxSelected>>", self._on_course_combo_select, True)
        self._course_combo.grid(column=1, row=1, sticky=tk.NSEW, padx=padx, pady=pady)
        
        self._exercise_title_var = create_string_var("")
        self._exercise_title_combo = ttk.Combobox(self,
                              exportselection=False,
                              state='readonly',
                              textvariable=self._exercise_title_var,
                              values=["<select exercise>", "1. Nädalapalk"])
        
        self._exercise_title_combo.grid(column=1, row=2, sticky=tk.NSEW, padx=padx, pady=(0,pady))
        
        self._task_frame = tkinterhtml.HtmlFrame(self, borderwidth=1, relief=tk.FLAT,
                                                 horizontal_scrollbar="auto")
        self._task_frame.grid(column=1, row=3, sticky=tk.NSEW, padx=padx, pady=(0, pady))
        
        self._submit_button = ttk.Button(self, text='Submit `npalk.py`', command=self._on_submit)
        self._submit_button.grid(column=1, row=4, sticky=tk.NSEW, padx=padx, pady=(0, pady))
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
        
        self._reset()
    
    def _reset(self):
        self._course_title_var.set("Select a course ...")
        self._exercise_title_var.set("")
        self._task_frame.set_content("<p></p>")
    
    def _get_known_courses(self):
        """Returns dictionary where key is course title and value is pair of plugin_id and course_id"""
        return get_workbench().get_option("exersys.known_courses")
    
    def _reload_courses_info(self, event=None):
        values = []
        
        for descriptor in self._get_known_courses():
            values.append(descriptor)
        
        # add links for opening new courses
        for plugin_id in _plugins:
            plugin = _plugins[plugin_id]
            prompt = "%s: <%s>" % (plugin_id, plugin.get_open_course_prompt())
            values.append(prompt)
        
        self._course_combo["values"] = values
    
    def _on_course_combo_select(self, event=None):
        selected_item = self._course_combo.get()
         
        plugin_id, course_text = selected_item.split(": ", maxsplit=1)
        plugin = _plugins[plugin_id]
        
        if course_text.endswith(">"):
            course_id = None
        else:
            _, course_id = course_text.split(" @ ")
            
        course = plugin.open_course(course_id)
        
        if course:
            self._load_course(course)
        else:
            self._reset()
    
    def _get_plugin_for_opening_link(self, link_text):
        assert link_text.endswith(">")
        plugin_id, _ = link_text.split(":", maxsplit=1)
        return _plugins[plugin_id]
    
    def _get_course_by_descriptor(self, descriptor):
        plugin_id, _, course_id = self._parse_course_descriptor(descriptor)
        return _plugins[plugin_id].open_course(course_id)
    
    def _parse_course_descriptor(self, descriptor):
        """Course descriptor consists of plugin id, course title and course id, for example:
        Moodle: Basics of Programming @ https://moodle.ut.ee/course/view.php?id=500
        returns ("Moodle", "Basics of Programming", "https://moodle.ut.ee/course/view.php?id=500")
        """
        plugin_id, course = descriptor.split(": ", maxsplit=1)
        course_title, course_id = course.split(" @ ", maxsplit=1)
        return plugin_id, course_title, course_id
            
    
    def _on_exercise_combo_change(self):
        exercise = self._get_selected_exercise()
        self._load_exercise(exercise)
    
    def _load_course(self, course):
        self._course_combo["text"] = course._get_descriptor()
    
    def _get_selected_exercise(self):
        course = self._get_selected_course()
        for ex in course.get_exercises():
            if ex.get_title() == self._exercise_title_var.get():
                return ex
        
        raise RuntimeError("Can't find selected exercise")
    
    def _on_submit(self):
        print("Submit")
        
    def _load_exercise(self, exercise):
        self._exercise_title_var.set(exercise.get_title())
        self._task_frame.set_content(exercise.get_description())

def init_exercise_system():    
    get_workbench().add_option("exersys.known_courses", [])
    get_workbench().add_view(ExerciseView, "Exercise", "ne")
