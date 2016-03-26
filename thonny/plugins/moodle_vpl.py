import tkinter as tk
from tkinter import ttk
from thonny import exersys, misc_utils
import json
import requests
from bs4 import BeautifulSoup
from tkinter.messagebox import showerror
import re
from thonny.globals import get_workbench
import base64

class MoodleVplPlugin(exersys.Plugin):
    def get_id(self):
        return "Moodle VPL"
    
    def open_course(self, course_id=None):
        if course_id is None:
            form = MoodleCourseSelectionForm(tk._default_root)
            return form.course
        else:
            return MoodleVplCourse(course_id)
    
class MoodleVplCourse(exersys.Course):
    def __init__(self, course_url, username, password):
        self._course_url = course_url
        self._course_title = course_url # will be updated later
        self._username = username
        self._password = password
        self._session = requests.Session()
        
        self._login()
        self._load_exercises_and_title()
    
    def _login(self):
        login_url = re.sub("/course/view.php.*$", "/login/index.php", self._course_url)
        data = {'username' : self._username, 'password' : self._password}
        self._session.post(login_url, data=data)
        # TODO: check that login is successful
    
    def get_title(self):
        return self._course_title
    
    def get_id(self):
        return self._course_url
    
    def get_url(self, url):
        return self._session.get(url)
    
    def post_url(self, url, data):
        return self._session.post(url, data)
    
    def _load_exercises_and_title(self):
        self._course_title = None
        self._exercises = []
        
        ex_list_url = self._course_url.replace("/course/view.php",
                                        "/mod/vpl/index.php") + "&sort=name&selection=open"
        
        ex_url_prefix = re.sub("/index.php.*$", "/", ex_list_url)
        
        response = self.get_url(ex_list_url)

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a"):
            href=link.get("href")
            if href and href.startswith("view.php?id="):
                ex = MoodleVplExercise(self, ex_url_prefix + href, link.string)
                self._exercises.append(ex)
            
            if href == self._course_url and link.get("title"):
                self._course_title = link.get("title")
    
    def get_exercises(self):
        return self._exercises

class MoodleVplExercise(exersys.Exercise):
    def __init__(self, course, url, title):
        self._course = course
        self._url = url
        self._title = title
        self._shortdescription = None
        self._description = None
        self._maxfiles = None
        self._requred_files = None
    
    def get_title(self):
        return self._title
    
    def _check_fetch_info(self):
        if self._description is None:
            self._fetch_info()
    
    def _fetch_info(self):
        info_page = self._course.get_url(self._get_ws_url() + "mod_vpl_info");
        info = json.loads(info_page.text)
        self._description = info["intro"]
        self._short_description = info["shortdescription"]
        self._maxfiles = info["maxfiles"]
        self._requred_files = [(entry['name'], entry['data']) for entry in info["reqfiles"]]
            
    
    def _get_ws_url(self):
        ws_url_page_url = self._url.replace("/view.php", "/views/show_webservice.php")
        response = self._course.get_url(ws_url_page_url)
        soup = BeautifulSoup(response.text, "html.parser")
        for div in soup.find_all("div"):
            if div and div.string and  "/mod/vpl/webservice.php" in div.string:
                return div.string
        
        return None
        
    
    def get_description(self):
        self._check_fetch_info()
        return ("<p>" + self._description + "</p>")
    
    def get_latest_feedback(self):
        return "<div style='padding:10px'>" + self._get_latest_feedback_content() + "</div>\n"
    
    def _get_latest_feedback_content(self):
        feedback_page = self._course.get_url(self._get_ws_url() + "mod_vpl_open");
        info = json.loads(feedback_page.text)
        print(info)
        if "exception" in info:
            return ("<p>" + info["exception"] + ": " + info["message"] + "</p>")
        elif info["evaluation"]:
            return self._evaluation_result_to_html(info["evaluation"])
        else:
            return ("<p>" + info["compilation"] + info["evaluation"] 
                    + "\nGrade:" + info["grade"] + "</p>") 
    
    def _evaluation_result_to_html(self, s):
        lines = []
        for line in s.splitlines():
            if line.startswith("-"):
                line = "<div style='padding: 10px 0px 3px 0px; font-weight:bold; font-size:larger'>" + line[1:] + "</div>"
            else:
                line = line + "<br/>"
                
            lines.append(line) 
            
        return "\n".join(lines)
    
    
    def _save_files(self, files):
        post_args = {}
        for i in range(len(files)):
            post_args["files[%d][name]" % i] = files[i]["name"]
            post_args["files[%d][data]" % i] = files[i]["data"]
        
        self._course.post_url(self._get_ws_url() + "mod_vpl_save", post_args)

class MoodleCourseSelectionForm(tk.Toplevel):
    def __init__(self, master, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf=cnf, **kw)
        
        self.geometry("+%d+%d" % (max(50, master.winfo_rootx() + master.winfo_width() // 2 - 200),
                                  max(50, master.winfo_rooty() + master.winfo_height() // 2 - 250)))
        self.title("Open Moodle VPL course")
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        
        
        
        ttk.Label(self, text="Course URL").grid(row=0, column=0, sticky=tk.W, padx=(20, 10), pady=(20, 3))
        self._url_entry = ttk.Entry(self, width=45)
        self._url_entry.grid(row=0, column=1, columnspan=3, sticky=tk.EW, padx=(10, 20), pady=(20, 3))
        
        ttk.Label(self, text="Username").grid(row=1, column=0, sticky=tk.W, padx=(20, 10), pady=3)
        self._username_entry = ttk.Entry(self, width=15)
        self._username_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=(10, 20), pady=3)
        
        ttk.Label(self, text="Password").grid(row=2, column=0, sticky=tk.W, padx=(20, 10), pady=3)
        self._password_entry = ttk.Entry(self, show="●", width=15)
        self._password_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=(10, 20), pady=3)
        
        ok_button = ttk.Button(self, text="OK", command=self._ok, default="active")
        ok_button.grid(row=3, column=2, sticky=tk.E, padx=5, pady=(10, 20))
        
        cancel_button = ttk.Button(self, text="Cancel", command=self._cancel)
        cancel_button.grid(row=3, column=3, sticky=tk.E, padx=(5,20), pady=(10, 20))

        self.bind('<Return>', self._ok, True) 
        self.bind('<Escape>', self._cancel, True) 
        
        self._url_entry.insert(0, get_workbench().get_option("moodlevpl.last_course_url"))
        self._username_entry.insert(0, get_workbench().get_option("moodlevpl.saved_username"))
        self._password_entry.insert(0, _get_saved_password())
        self._url_entry.focus_set()
        
        self.columnconfigure(1, weight=1)
        
        self.wait_window()
        
    def _ok(self, event=None):
        
        url = self._url_entry.get()
        username = self._username_entry.get()
        password = self._password_entry.get()
        
        if (not url.strip().startswith("http://")
            and not url.strip().startswith("https://")):
            showerror("Problem", "URL should start with http:// or https://")
            self._url_entry.focus_set()
            return
        
        if username.strip() == "":
            showerror("Problem", "Please enter user name")
            self._username_entry.focus_set()
            return
            
        
        if password.strip() == "":
            showerror("Problem", "Please enter password")
            self._password_entry.focus_set()
            return
        
        self.course = MoodleVplCourse(url, username, password)
        self.destroy()
        
    def _cancel(self, event=None):
        self.course = None
        self.destroy()


def _save_password(password):
    # TODO: save to separate conf file so that user can post his normal conf file if needed for debugging   
    get_workbench().set_option("moodlevpl.saved_password",
                               base64.b64encode(password.encode("UTF-8")).decode("ASCII"))

def _get_saved_password():
    return base64.b64decode(get_workbench().get_option("moodlevpl.saved_password")
                            .encode("ASCII")).decode("UTF-8")



def load_plugin():
    get_workbench().add_option("moodlevpl.saved_username", "")
    get_workbench().add_option("moodlevpl.saved_password", "")
    get_workbench().add_option("moodlevpl.last_course_url", "")
    exersys.add_plugin(MoodleVplPlugin())

