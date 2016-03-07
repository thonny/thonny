import tkinter as tk
from tkinter import ttk
from thonny import exersys, misc_utils
import urllib.request
from bs4 import BeautifulSoup

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
    def __init__(self, url):
        self._url = url
        self._load_exercises()
    
    def _load_exercises(self):
        ex_list_url = self._url.replace("/course/view.php",
                                        "/mod/vpl/index.php") + "&sort=name"
        with urllib.request.urlopen(ex_list_url, timeout=10) as handle:
            ex_list_source = handle.read().decode("UTF-8")
        soup = BeautifulSoup(ex_list_source, "html.parser")
        for link in soup.find_all("a"):
            href=link.get("href")
            if href and href.startswith("view.php?id="):
                print(href, link.string)


class MoodleCourseSelectionForm(tk.Toplevel):
    def __init__(self, master, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf=cnf, **kw)
        
        self.geometry("+%d+%d" % (master.winfo_rootx() + master.winfo_width() // 2 - 50,
                                  master.winfo_rooty() + master.winfo_height() // 2 - 150))
        self.title("Open Moodle VPL course")
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._ok)
        
        
        
        ttk.Label(self, text="Course URL").grid(row=0, column=0, sticky=tk.W, padx=(20, 10), pady=(20, 2))
        self._url_entry = ttk.Entry(self, width=60)
        self._url_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=(10, 20), pady=(20, 2))
        
        ttk.Label(self, text="Username").grid(row=1, column=0, sticky=tk.W, padx=(20, 10), pady=2)
        self._username_entry = ttk.Entry(self, width=10)
        self._username_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=(10, 20), pady=2)
        
        ttk.Label(self, text="Password").grid(row=2, column=0, sticky=tk.W, padx=(20, 10), pady=2)
        self._password_entry = ttk.Entry(self, show="●", width=10)
        self._password_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=(10, 20), pady=2)
        
        ok_button = ttk.Button(self, text="OK", command=self._ok, default="active")
        ok_button.grid(row=3, column=1, sticky=tk.E, padx=5, pady=(10, 20))
        
        cancel_button = ttk.Button(self, text="Cancel", command=self._cancel)
        cancel_button.grid(row=3, column=2, sticky=tk.E, padx=5, pady=(10, 20))

        self.bind('<Return>', self._ok, True) 
        self.bind('<Escape>', self._cancel, True) 
        
        self._url_entry.focus_set()
        
        self.columnconfigure(0, weight=1)
        
        self.wait_window()
        
    def _ok(self, event=None):
        # TODO: login and create course
        self.destroy()
        
    def _cancel(self, event=None):
        self.course = None
        self.destroy()
    
def _create_request(url, session_cookie, data=None):
    req = urllib.request.Request(url, data=data)
    req.add_header('Accept', "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    req.add_header("Accept-Language", "et,et-EE;q=0.8,en-US;q=0.5,en;q=0.3")
    req.add_header("User-Agent", 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0')
    if session_cookie is not None:
        req.add_header("Cookie", session_cookie)
    if data is not None:
        req.add_header('Content-Type', "application/x-www-form-urlencoded;charset=utf-8")
    return req


def load_plugin():
    exersys.add_plugin(MoodleVplPlugin())

if __name__ == "__main__":
    MoodleVplCourse("https://moodle.ut.ee/course/view.php?id=500")