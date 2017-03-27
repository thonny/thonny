# -*- coding: utf-8 -*-

import datetime
import webbrowser
import platform

import tkinter as tk
from tkinter import ttk
import tkinter.font as font

from thonny import misc_utils, tktextext
from thonny.misc_utils import get_python_version_string
from thonny.globals import get_workbench
import subprocess
import collections
import threading
from urllib.request import urlopen
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor

class PipDialog(tk.Toplevel):
    def __init__(self, master):
        self._state = None # possible values: "listing", "fetching", "idle"
        
        tk.Toplevel.__init__(self, master)
        
        
        width = 600
        height = 400
        self.geometry("%dx%d+%d+%d" % (width, height,
            master.winfo_rootx() + master.winfo_width() // 2 - width//2,
            master.winfo_rooty() + master.winfo_height() // 2 - height//2))

        main_frame = tk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.title("Manage packages for C:\\Users\\Aivar\\.thonny\\BundledPython36\\python.exe")
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        #self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(master)
        self.grab_set() # to make it active
        self.grab_release() # to allow eg. copy something from the editor 
        self.protocol("WM_DELETE_WINDOW", self._ok)
        
        self._create_widgets(main_frame)
        
        self.search_box.focus_set()
        
        self.bind('<Return>', self._ok, True) 
        self.bind('<Escape>', self._ok, True) 
    
    def _set_state(self, state):
        self._state = state
        # TODO: update widget availability
    
    def _get_state(self):
        return self._state
    
    def _update_list(self):
        assert self._get_state() in [None, "idle"]
        self.set_state("listing")
        
        
    
    def _create_widgets(self, parent):
        
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15,0))
        header_frame.columnconfigure(0, weight=1)
        header_frame.rowconfigure(0, weight=1)
        
        name_font = tk.font.nametofont("TkDefaultFont").copy()
        #name_font.configure(size=16)
        self.search_box = ttk.Entry(header_frame, font=name_font)
        self.search_box.grid(row=0, column=0, sticky="nsew")
        
        self.search_button = ttk.Button(header_frame, text="Search")
        self.search_button.grid(row=0, column=1, sticky="nse", padx=(10,0))
        
        
        main_pw = ttk.Panedwindow(parent, orient=tk.HORIZONTAL)
        main_pw.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)
        
        listframe = ttk.Frame(main_pw)
        main_pw.add(listframe, weight=1)
        
        self.list = tk.StringVar(value=("<install new package>", "jedi", "matplotlib", "pip"))
        print(self.list)
        self.listbox = tk.Listbox(listframe, listvariable=self.list)
        self.listbox.grid(row=0, column=0, sticky="nsew") 
        listframe.rowconfigure(0, weight=1)
        listframe.columnconfigure(0, weight=1)
        
        infoframe = tk.Frame(main_pw)
        infoframe.columnconfigure(0, weight=1)
        infoframe.rowconfigure(1, weight=1)
        main_pw.add(infoframe, weight=3)
        
        info_text_frame = tktextext.TextFrame(infoframe,
                                              horizontal_scrollbar=False)
        self.info_text = info_text_frame.text
        self.info_text.configure(background="SystemButtonFace",
                                 font=tk.font.nametofont("TkDefaultFont"),
                                 wrap="word")
        self.info_text.insert("1.0", """Version: 0.10.0
Summary: An autocompletion tool for Python that can be used for text editors.
Home-page: https://github.com/davidhalter/jedi
Author: David Halter
Author-email: davidhalter88@gmail.com
License: MIT
Location: c:\python36-32\lib\site-packages
Requires:""")
        info_text_frame.configure(borderwidth=1)
        info_text_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=20)
        
        
        command_frame = ttk.Frame(infoframe)
        command_frame.grid(row=2, column=0, sticky="w")
        
        install_button = ttk.Button(command_frame, text="  Upgrade  (2.0.7 → 2.1.0)  ")
        install_button.grid(row=0, column=0, sticky="w")
        
        upgrade_button = ttk.Button(command_frame, text="Upgrade")
        #upgrade_button.grid(row=0, column=1, sticky="w")
        
        uninstall_button = ttk.Button(command_frame, text="Uninstall")
        #uninstall_button.grid(row=0, column=2, sticky="w")
    
        close_button = ttk.Button(infoframe, text="Close")
        close_button.grid(row=2, column=3, sticky="e")
        
        self._load_package_info("thonny", "2.0.7")
    
    
    def _load_package_info(self, name, version):
        url = "https://pypi.python.org/pypi/{}/{}/json".format(name, version)
        fut = _fetch_url_future(url)
        self._check_update_info(fut)
        
    
    def _check_update_info(self, fut):
        if fut.done():
            data = fut.result().decode("UTF-8")
            self.info_text.insert("end", "\n" + data)
        else:
            self.after(200, self._check_update_info, fut)
            
        
    
    def _ok(self, event=None):
        self.destroy()


def _fetch_url_future(url, timeout=10):
    def load_url():
        with urlopen(url, timeout=timeout) as conn:
            return conn.read()
            
    executor = ThreadPoolExecutor(max_workers=1)
    return executor.submit(load_url)


def _execute_system_command_and_wait(cmd):
    encoding = "UTF-8"
    env = {"PYTHONIOENCODING" : encoding,
           "PYTHONUNBUFFERED" : "1"}
    
    try:
        output = subprocess.check_output(cmd, "ls non_existent_file; exit 0",
                            stderr=subprocess.STDOUT, env=env,
                            universal_newlines=True, encoding=encoding)
        return (0, output)
    except subprocess.CalledProcessError as e:
        return (e.returncode, e.output)
    

def _direct_system_command_to_queue(cmd, event_queue):
    encoding = "UTF-8"
    env = {"PYTHONIOENCODING" : encoding,
           "PYTHONUNBUFFERED" : "1"}
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                            universal_newlines=True, encoding=encoding)
    
    proc.events = collections.deque()
    
    def listen_stream(stream_name):
        stream = getattr(proc.stdout, stream_name)
        while True:
            data = stream.readline()
            if data == '':
                break
            else:
                event_queue.append((stream_name, data))
        
        returncode = proc.wait()
        event_queue.append(("returncode", returncode))
    
    threading.Thread(target=listen_stream, args=["stdout"]).start()
    threading.Thread(target=listen_stream, args=["stderr"]).start()
    
    return proc 
    
    
    


def load_plugin():
    def open_pip_gui(*args):
        pg = PipDialog(get_workbench())
        pg.wait_window()

        
    get_workbench().add_command("pipgui", "tools", "Manage packages...", open_pip_gui,
                                group=80)


    