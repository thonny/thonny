import tkinter as tk
from tkinter import ttk
from thonny.globals import get_workbench
import tkinterhtml
from thonny.ui_utils import create_string_var

ABOUT_EXERCISE_VIEW = "About exercise view"

_plugins = []

def add_plugin(plugin):
    global _plugins
    _plugins.append(plugin)

def refresh_ui():
    """Notifies ExerciseView about updates (submission complete etc.)"""
    # TODO:

class Plugin:
    def get_open_course_prompt(self):
        """Don't put <> here"""
        return "open example course"
    
    def open_course(self, course_id=None):
        """If course_id is None, prompt user about details and return new course object."""

class Course:
    def get_title(self):
        """Return title to be shown in the course combo"""
    
    def get_exercises(self):
        """Return list of exercise objects"""

class Exercise:
    def get_title(self):
        """Return title to be shown in the exercise combo"""
    
    def get_description(self):
        """Return html description of the exercise"""
    
    def get_required_files(self):
        """Return list of required file names"""
    
    def get_max_number_of_files(self):
        """Return how many files can be submitted"""
    
    def accept_submission(self, file_names, feedback_reporting_function):
        """Start checking procedure and return.
        Call refresh_ui when checking is complete."""
    
    def cancel_submission(self):
        """Try to cancel ongoing submission.
        Call refresh_ui when submission is cancelled."""
    
    def get_latest_feedback(self):
        """Return latest feedback as html string or None"""
    
    def get_state(self):
        '''Return "checking", "cancelling" or "ready"'''

class ExerciseView(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, background="white", **kw)
        self._init_widgets()
    
    def _init_widgets(self):
        padx = 15
        pady = 15
        
        course_combo_values = [ABOUT_EXERCISE_VIEW] + self._get_known_courses()
        for plugin in _plugins:      
            course_combo_values.append("<%s>" % plugin.get_open_course_prompt())
            
        self._course_variable = create_string_var("", self._on_course_change)
        self._course_combo = ttk.Combobox(self,
                              exportselection=False,
                              state='readonly',
                              textvariable=self._course_variable,
                              values=course_combo_values)
        
        self._course_combo.grid(column=1, row=1, sticky=tk.NSEW, padx=padx, pady=pady)
        
        self._exercise_variable = create_string_var("", self._on_exercise_change)
        self._exercise_title_combo = ttk.Combobox(self,
                              exportselection=False,
                              state='readonly',
                              textvariable=self._exercise_variable,
                              values=["<select exercise>", "1. Nädalapalk"])
        
        self._exercise_title_combo.grid(column=1, row=2, sticky=tk.NSEW, padx=padx, pady=(0,pady))
        
        self._task_frame = tkinterhtml.HtmlFrame(self, borderwidth=1, relief=tk.FLAT,
                                                 horizontal_scrollbar="auto")
        self._task_frame.grid(column=1, row=3, sticky=tk.NSEW, padx=padx, pady=(0, pady))
        self._task_frame.set_content("<html><body></body></html>")
        
        self._task_frame.set_content("""
<h1>Ülesanne. Nädalapalk</h1>
<p class="Textbody"><span lang="EN-US">Kui inimene töötab nädalas 40 tundi või vähem, siis nende tundide eest saab ta palga vastavalt oma tavalisele tunnitasule. Kui inimene töötab rohkem kui 40 tundi, siis ületundide eest on tunnitasu 50% kõrgem.<o:p></o:p></span></p>
<p class="Standard"><span lang="EN-US">Koostage programm, mis küsib kasutajalt töötundide arvu nädalas ja tavalise tunnitasu (<b>küsige just sellises järjekorras, esimese asjana - töötundide arvu ja teise asjana - tunnitasu</b>) ning väljastab vastava nädalapalga arvestades ka ületundidega, kui neid on.<o:p></o:p></span></p>
<p class="Standard">Nt. kui töötundide arv nädalas on 30 ja tunnitasuks on 10, siis nädalapalgaks on 300 eurot (arvutamise käik: 30*10). Kui töötundide arvuks on 60 ja tunnitasuks on 8, siis nädalapalgaks on 560 eurot (arvutamise käik: 40*8+(60-40)*(8*1.5)=320+20*12=320+240=560).</p>
<p> </p>
<p><span style="line-height: 1.4;">Lahenduse (st </span><em style="line-height: 1.4;">.py</em><span style="line-height: 1.4;"> laiendiga faili) üleslaadimiseks vali ülaltpoolt link "Esitamine". Kõige lihtsam on lohistada fail hiirega üleslaadimise kastikesse. Vajutades nuppu "Esita", salvestatakse lahendus Moodle'isse. Järgneval lehel tuleks vajutada nuppu "Jätka", mis paneb ühe spetsiaalse skripti esitatud lahendust kontrollima. Kontrolli tulemused peaksid ilmuma mõne sekundi jooksul (pealkirjaga "Kommentaarid").</span></p>
<p><span style="line-height: 1.4;">Kui ilmub veateade pealkirjaga "Kommentaar ... VIGA", siis viitab see tõenäoliselt mingile veale sinu programmis (kui arvad, et su programm on õige ja viga on kontrollijas, siis kirjuta aadressil <a target="_blank" href="mailto:prog@ut.ee">prog@ut.ee</a></span><a target="_blank" href="mailto:marina.lepp@ut.ee" style="line-height: 1.4;"></a><span style="line-height: 1.4;">).</span></p>
<p>Kui programm töötab õigesti, siis kommentaariks peab tulema OK.</p>
<p><span style="line-height: 1.4;">Samale ülesandele saab lahendust esita</span><span style="font-size: small;">da </span><span style="line-height: 1.4;">palju kordi</span><span style="font-size: small;">.</span></p>
<p>Kui ülesande esitamisel tekib tehnilisi tõrkeid, siis kirjuta aadressil <a target="_blank" href="mailto:prog@ut.ee">prog@ut.ee</a><a target="_blank" href="mailto:marina.lepp@ut.ee"><br /></a></p>        
        """)
        
        self._submit_button = ttk.Button(self, text='Submit `npalk.py`', command=self._on_submit)
        self._submit_button.grid(column=1, row=4, sticky=tk.NSEW, padx=padx, pady=(0, pady))
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
        
    def _get_known_courses(self):
        return ["Programmeerimise alused",
                "Programmeerimisest maalähedaselt"]
    
    def _on_submit(self):
        print("Submit")
        
    def _on_course_change(self):
        print(self._course_variable.get())

    def _on_exercise_change(self):
        print(self._exercise_variable.get())

def init_exercise_system():    
    get_workbench().add_view(ExerciseView, "Exercise", "ne")
