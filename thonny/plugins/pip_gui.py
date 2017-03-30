# -*- coding: utf-8 -*-

import webbrowser

import tkinter as tk
from tkinter import ttk, messagebox

from thonny import misc_utils, tktextext, ui_utils
from thonny.globals import get_workbench, get_runner
import subprocess
import collections
import threading
from urllib.request import urlopen
import urllib.error
from concurrent.futures.thread import ThreadPoolExecutor
import os
import json
from distutils.version import LooseVersion, StrictVersion
import logging
import re

LINK_COLOR="#3A66DD"

class PipDialog(tk.Toplevel):
    def __init__(self, master):
        self._state = None # possible values: "listing", "fetching", "idle"
        self._process = None
        self._installed_versions = {}
        self.current_package_data = None
        
        tk.Toplevel.__init__(self, master)
        
        
        width = 700
        height = 350
        self.geometry("%dx%d+%d+%d" % (width, height,
            master.winfo_rootx() + master.winfo_width() // 2 - width//2,
            master.winfo_rooty() + master.winfo_height() // 2 - height//2))

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.title("Manage packages for C:\\Users\\Aivar\\.thonny\\BundledPython36\\python.exe")
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        #self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(master)
        self.grab_set() # to make it active
        #self.grab_release() # to allow eg. copy something from the editor 
        
        self._create_widgets(main_frame)
        
        self.search_box.focus_set()
        
        self.bind('<Escape>', self._on_close, True) 
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        #self.listbox.selection_set(0)
        self._show_instructions()
        self._start_update_list()
    
    
    def _create_widgets(self, parent):
        
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15,0))
        header_frame.columnconfigure(0, weight=1)
        header_frame.rowconfigure(0, weight=1)
        
        name_font = tk.font.nametofont("TkDefaultFont").copy()
        name_font.configure(size=16)
        self.search_box = ttk.Entry(header_frame, background=ui_utils.CALM_WHITE)
        self.search_box.grid(row=0, column=0, sticky="nsew")
        self.search_box.bind("<Return>", self._on_search, False)
        
        self.search_button = ttk.Button(header_frame, text="Search", command=self._on_search)
        self.search_button.grid(row=0, column=1, sticky="nse", padx=(10,0))
        
        
        main_pw = tk.PanedWindow(parent, orient=tk.HORIZONTAL,
                                 background=ui_utils.get_button_face_color(),
                                 sashwidth=10)
        main_pw.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)
        
        listframe = ttk.Frame(main_pw, relief="groove", borderwidth=1)
        listframe.rowconfigure(0, weight=1)
        listframe.columnconfigure(0, weight=1)
        
        self.listbox = tk.Listbox(listframe, activestyle="dotbox", width=20,
                                  background=ui_utils.CALM_WHITE,
                                  selectborderwidth=0, relief="flat",
                                  highlightthickness=0, borderwidth=0)
        self.listbox.insert("end", " <INSTALL>")
        self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select, True)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        list_scrollbar = ttk.Scrollbar(listframe, orient=tk.VERTICAL)
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        list_scrollbar['command'] = self.listbox.yview
        self.listbox["yscrollcommand"] = list_scrollbar.set
        
        info_frame = ttk.Frame(main_pw)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)
        
        main_pw.add(listframe)
        main_pw.add(info_frame)
        
        self.name_label = ttk.Label(info_frame, text="", font=name_font)
        self.name_label.grid(row=0, column=0, sticky="w", padx=5)
        

        
        info_text_frame = tktextext.TextFrame(info_frame, read_only=True,
                                              horizontal_scrollbar=False)
        info_text_frame.configure(borderwidth=1)
        info_text_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0,20))
        self.info_text = info_text_frame.text
        self.info_text.tag_configure("url", foreground=LINK_COLOR, underline=True)
        self.info_text.tag_bind("url", "<ButtonRelease-1>", self._handle_url_click)
        self.info_text.tag_bind("url", "<Enter>", lambda e: self.info_text.config(cursor="hand2"))
        self.info_text.tag_bind("url", "<Leave>", lambda e: self.info_text.config(cursor=""))
        
        self.info_text.configure(background=ui_utils.get_button_face_color(),
                                 font=tk.font.nametofont("TkDefaultFont"),
                                 wrap="word")
        bold_font = tk.font.nametofont("TkDefaultFont").copy()
        bold_font.configure(weight="bold")
        self.info_text.tag_configure("caption", font=bold_font)
        
        
        self.command_frame = ttk.Frame(info_frame)
        self.command_frame.grid(row=2, column=0, sticky="w")
        
        self.install_button = ttk.Button(self.command_frame, text=" Upgrade ",
                                         command=lambda: self._perform_action("install"))
        self.install_button.grid(row=0, column=0, sticky="w", padx=0)
        
        self.uninstall_button = ttk.Button(self.command_frame, text="Uninstall",
                                           command=lambda: self._perform_action("uninstall"))
        self.uninstall_button.grid(row=0, column=1, sticky="w", padx=(5,0))
        
        """
        link_font = tk.font.nametofont("TkDefaultFont").copy()
        link_font["underline"] = 1
        self.advanced_link = ttk.Label(self.command_frame, text="Advanced ...",
                                       cursor="hand2",
                                       foreground=LINK_COLOR, font=link_font)
        #                              
        """
        self.advanced_button = ttk.Button(self.command_frame, text="...", width=3,
                                          command=lambda: self._perform_action("advanced"))
        self.advanced_button.grid(row=0, column=2, sticky="w", padx=(5,0))
        
        self.close_button = ttk.Button(info_frame, text="Close", command=self._on_close)
        self.close_button.grid(row=2, column=3, sticky="e")
        

    def _set_state(self, state):
        self._state = state
        widgets = [self.listbox, 
                           # self.search_box, # looks funny when disabled 
                           self.search_button,
                           self.install_button, self.advanced_button, self.uninstall_button]
        if state == "idle":
            self.config(cursor="")
            for widget in widgets:
                widget["state"] = tk.NORMAL
        else:
            self.config(cursor="wait")
            for widget in widgets:
                widget["state"] = tk.DISABLED
    
    def _get_state(self):
        return self._state
    
    def _start_update_list(self, name_to_show=None):
        assert self._get_state() in [None, "idle"]
        self._set_state("listing")
        self._process, _ = _create_pip_process(["list", "--format", "json"])
        
        def poll_completion():
            if self._process == None:
                return
            else:
                returncode = self._process.poll()
                if returncode is None:
                    # not done yet
                    self.after(200, poll_completion)
                else:
                    self._set_state("idle")
                    if returncode == 0:
                        raw_data = self._process.stdout.read()
                        self._update_list(json.loads(raw_data))
                        if name_to_show is None:
                            self._show_instructions()
                        else:
                            self._start_show_package_info(name_to_show)
                    else:   
                        messagebox.showerror("pip list error", self._process.stdout.read())
                    
                    self._process = None
        
        poll_completion()
                    
        
    def _update_list(self, data):
        self.listbox.delete(1, "end")
        self._installed_versions = {entry["name"] : entry["version"] for entry in data}
        for name in sorted(self._installed_versions.keys(), key=str.lower):
            self.listbox.insert("end", " " + name)
        
        
    
    def _on_listbox_select(self, event):
        selection = self.listbox.curselection()
        if len(selection) == 1:
            if selection[0] == 0: # special first item
                self._show_instructions()
            else:
                self._start_show_package_info(self.listbox.get(selection[0]).strip())
    
    def _on_search(self, event=None):
        if not self._get_state() == "idle":
            # Search box is not made inactive for busy-states
            return
        
        self._start_show_package_info(self.search_box.get())
    
    def _show_instructions(self):
        self.current_package_data = None
        self.name_label.grid_remove()
        self.command_frame.grid_remove()
        self.info_text.direct_delete("1.0", "end")
        self.info_text.direct_insert("end", "Installing a package\n", ("caption",))
        self.info_text.direct_insert("end", "Start by entering the name of the package in the search box above and pressing ENTER.\n\n")
        self.info_text.direct_insert("end", "Upgrading or uninstalling a package\n", ("caption",))
        self.info_text.direct_insert("end", 'Start by selecting the package from the left.\n\n')
        self._select_list_item(0)
    
    def _start_show_package_info(self, name):
        self.current_package_data = None
        self.info_text.direct_delete("1.0", "end")
        self.name_label["text"] = ""
        self.name_label.grid()
        self.command_frame.grid()
        
        installed_version = self._get_installed_version(name) 
        if installed_version is not None:
            self.name_label["text"] = name
            self.info_text.direct_insert("end", "Installed version: ", ('caption',))
            self.info_text.direct_insert("end", installed_version + "\n")
        
        
        # Fetch info from PyPI  
        self._set_state("fetching")
        # Follwing url fetches info about latest version.
        # This is OK even when we're looking an installed older version
        # because new version may have more relevant and complete info.
        url = "https://pypi.python.org/pypi/{}/json".format(name)
        url_future = _fetch_url_future(url)
            
        def poll_fetch_complete():
            if url_future.done():
                self._set_state("idle")
                try:
                    _, bin_data = url_future.result()
                    raw_data = bin_data.decode("UTF-8")
                    # TODO: check for 404
                    self._show_package_info(json.loads(raw_data))
                except urllib.error.HTTPError as e:
                    self._show_package_info(None, e.code)
                        
            else:
                self.after(200, poll_fetch_complete)
        
        poll_fetch_complete()

    def _show_package_info(self, data, error_code=None):
        self.current_package_data = data
        def write(s, tag=None):
            if tag is None:
                tags = ()
            else:
                tags = (tag,)
            self.info_text.direct_insert("end", s, tags)
        
        def write_att(caption, value, value_tag=None):
            write(caption + ": ", "caption")
            write(value, value_tag)
            write("\n")
            
        if error_code is not None:
            if error_code == 404:
                write("Could not find the package. Please check spelling!")
            else:
                write("Could not find the package info. Error code: " + str(error_code))
            return
        
        info = data["info"]
        self.name_label["text"] = info["name"] # search name could have been a bit different
        latest_stable_version = _get_latest_stable_version(data["releases"].keys())
        if latest_stable_version is not None:
            write_att("Latest stable version", latest_stable_version)
        write_att("Summary", info["summary"])
        write_att("Author", info["author"])
        write_att("Homepage", info["home_page"], "url")
        if info.get("bugtrack_url", None):
            write_att("Bugtracker", info["bugtrack_url"], "url")
        if info.get("docs_url", None):
            write_att("Documentation", info["docs_url"], "url")
        if info.get("package_url", None):
            write_att("PyPI page", info["package_url"], "url")
        
        if self._get_installed_version(info["name"]) is not None:
            self.install_button["text"] = "Upgrade"
            self.uninstall_button.grid(row=0, column=1)
            
            self._select_list_item(info["name"])
            if self._get_installed_version(info["name"]) == latest_stable_version:
                self.install_button["state"] = "disabled"
            else: 
                self.install_button["state"] = "normal"
        else:
            self.install_button["text"] = "Install"
            self.uninstall_button.grid_forget()
            self._select_list_item(0)
            
    
    def _normalize_name(self, name):
        # looks like (in some cases?) pip list gives the name as it was used during install
        # ie. the list may contain lowercase entry, when actual metadata has uppercase name 
        # Example: when you "pip install cx-freeze", then "pip list"
        # really returns "cx-freeze" although correct name is "cx_Freeze"
        return name.lower().replace("-", "_").strip()
    
    def _select_list_item(self, name_or_index):
        if isinstance(name_or_index, int):
            index = name_or_index
        else:
            normalized_items = list(map(self._normalize_name, self.listbox.get(0, "end")))
            index = normalized_items.index(self._normalize_name(name_or_index))
        
        self.listbox.select_clear(0, "end")
        self.listbox.select_set(index)
        self.listbox.see(index)
        
        
    
    def _perform_action(self, action):
        assert self._get_state() == "idle"
        assert self.current_package_data is not None
        data = self.current_package_data
        name = self.current_package_data["info"]["name"]
        install_args = ["install", "--no-cache-dir"] 
        
        if action == "install":
            args = install_args
            if self._get_installed_version(name) is not None:
                args.append("--upgrade")
            args.append(name)
        elif action == "uninstall":
            if (name in ["pip", "setuptools"]
                and not messagebox.askyesno("Really uninstall?",
                    "Package '{}' is required for installing and uninstalling other packages.\n\n".format(name)
                    + "Are you sure you want to uninstall it?")):
                return
            args = ["uninstall", "-y", name]
        elif action == "advanced":
            details = _ask_installation_details(self, data, 
                        _get_latest_stable_version(list(data["releases"].keys())))
            if details is None: # Cancel
                return
            
            version, upgrade_deps = details
            args = install_args
            if upgrade_deps:
                args.append("--upgrade")
            args.append(name + "==" + version)
            
        else:
            raise RuntimeError("Unknown action")
        
        proc, cmd = _create_pip_process(args)
        # following call blocks
        title = subprocess.list2cmdline(cmd)
        
        _show_subprocess_dialog(self, proc, title)
        if action == "uninstall":
            self._show_instructions() # Make the old package go away as fast as possible
        self._start_update_list(None if action == "uninstall" else name)
        
        
    
    def _handle_url_click(self, event):
        # http://stackoverflow.com/a/33957256/261181
        try:
            index = self.info_text.index("@%s,%s" % (event.x, event.y))
            tag_indices = list(self.info_text.tag_ranges('url'))
            for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
                # check if the tag matches the mouse click index
                if self.info_text.compare(start, '<=', index) and self.info_text.compare(index, '<', end):
                    url = self.info_text.get(start, end)
                    webbrowser.open(url)
        except:
            logging.exception("URL clicking")
    
    def _on_close(self, event=None):
        self.destroy()
        
    def _get_installed_version(self, name):
        for list_name in self._installed_versions:
            if self._normalize_name(name) == self._normalize_name(list_name):
                return self._installed_versions[list_name]
        
        return None

class SubprocessDialog(tk.Toplevel):
    """Shows incrementally the output of given subprocess.
    Allows cancelling"""
    
    def __init__(self, master, proc, title):
        self._proc = proc
        self.stdout = ""
        self.stderr = ""
        self.returncode = None
        self.cancelled = False
        
        tk.Toplevel.__init__(self, master)
        
        
        width = 400
        height = 250
        self.geometry("%dx%d+%d+%d" % (width, height,
            master.winfo_rootx() + master.winfo_width() // 2 - width//2,
            master.winfo_rooty() + master.winfo_height() // 2 - height//2))

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame = ttk.Frame(self) # To get styled background
        main_frame.grid()

        text_font=tk.font.nametofont("TkFixedFont").copy()
        text_font["size"] = int(text_font["size"] * 0.7)
        text_frame = tktextext.TextFrame(main_frame, read_only=True, horizontal_scrollbar=False,
                                         background=ui_utils.get_button_face_color(),
                                         font=text_font,
                                         wrap="word")
        text_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=15, pady=15)
        self.text = text_frame.text
        
        self.button = ttk.Button(main_frame, text="Cancel", command=self._close)
        self.button.grid(row=1, column=0, pady=(0,15))
        
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        

        self.title(title)
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        #self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(master)
        self.grab_set() # to make it active and modal
        self.text.focus_set()
        
        
        self.bind('<Escape>', self._close_if_done, True) # escape-close only if process has completed 
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._start_listening()
    
    def _start_listening(self):
        event_queue = collections.deque()
        
        def listen_stream(stream_name):
            stream = getattr(self._proc, stream_name)
            while True:
                data = stream.readline()
                if data == '':
                    break
                else:
                    event_queue.append((stream_name, data))
                    setattr(self, stream_name, getattr(self, stream_name) + data)
            
            self.returncode = self._proc.wait()
        
        threading.Thread(target=listen_stream, args=["stdout"]).start()
        if self._proc.stderr is not None:
            threading.Thread(target=listen_stream, args=["stderr"]).start()
        
        def poll_output_events():
            while len(event_queue) > 0:
                stream_name, data = event_queue.popleft()
                self.text.direct_insert("end", data, tags=(stream_name, ))
                self.text.see("end")
            
            if self._proc.poll() == None:
                self.after(200, poll_output_events)
            else:
                self.button["text"] = "OK"
                self.button.focus_set()
                if self.returncode == 0:
                    self._close()
        
        poll_output_events()
        
    
    def _close_if_done(self, event):
        if self._proc.poll() is not None:
            self._close(event)        

    def _close(self, event=None):
        if (self._proc.poll() is None
            and not messagebox.askyesno("Cancel the process?",
                "The process is still running.\nAre you sure you want to cancel?")):
            self._proc.kill()
            self.cancelled = True
            return
        else:
            self.destroy()
        
class DetailsDialog(tk.Toplevel):
    def __init__(self, master, package_metadata, selected_version):
        tk.Toplevel.__init__(self, master)
        self.result = None
        
        self.title("Advanced install / upgrade / downgrade")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame = ttk.Frame(self) # To get styled background
        main_frame.grid()
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        version_label = ttk.Label(main_frame, text="Desired version")
        version_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(15,0), sticky="w")
        
        def version_sort_key(s):
            # Trying to massage understandable versions into valid StrictVersions
            if s.replace(".", "").isnumeric(): # stable release
                s2 = s + "b999" # make it latest beta version
            elif "rc" in s:
                s2 = s.replace("rc", "b8")
            else:
                s2 = s
            try:
                return StrictVersion(s2)
            except:
                # use only numbers
                nums = re.findall(r"\d+", s)
                while len(nums) < 2:
                    nums.append("0")
                return StrictVersion(".".join(nums[:3]))
        
        version_strings = list(package_metadata["releases"].keys())
        version_strings.sort(key=version_sort_key, reverse=True)
        self.version_combo = ttk.Combobox(main_frame, values=version_strings,
                              exportselection=False)
        try:
            self.version_combo.current(version_strings.index(selected_version))
        except:
            pass
        
        self.version_combo.state(['!disabled', 'readonly'])
        self.version_combo.grid(row=1, column=0, columnspan=2, pady=(0,15),
                                padx=20, sticky="ew")
        
        
        self.update_deps_var = tk.IntVar()
        self.update_deps_var.set(0)
        self.update_deps_cb = ttk.Checkbutton(main_frame, text="Upgrade dependencies",
                                              variable=self.update_deps_var)
        self.update_deps_cb.grid(row=2, column=0, columnspan=2, padx=20, sticky="w")
        
        self.ok_button = ttk.Button(main_frame, text="Install", command=self._ok)
        self.ok_button.grid(row=3, column=0, pady=15, padx=(20, 0), sticky="se")
        self.cancel_button = ttk.Button(main_frame, text="Cancel", command=self._cancel)
        self.cancel_button.grid(row=3, column=1, pady=15, padx=(5,20), sticky="se")
        
        

        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        #self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(master)
        self.grab_set() # to make it active and modal
        self.version_combo.focus_set()
        
        
        self.bind('<Escape>', self._cancel, True)  
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        
        # Position
        self.update_idletasks()
        self.geometry("+%d+%d" % (
            master.winfo_rootx() + master.winfo_width() // 2 - self.winfo_width()//2,
            master.winfo_rooty() + master.winfo_height() // 2 - self.winfo_height()//2))
        
    
    def _ok(self, event=None):
        self.result = self.version_combo.get(), bool(self.update_deps_var.get())
        self.destroy()
    
    def _cancel(self, event=None):
        self.result = None
        self.destroy()
        
def _fetch_url_future(url, timeout=10):
    def load_url():
        with urlopen(url, timeout=timeout) as conn:
            return (conn, conn.read())
            
    executor = ThreadPoolExecutor(max_workers=1)
    return executor.submit(load_url)


def _create_pip_process(args):
    encoding = "UTF-8"
    env = {}
    for name in os.environ:
        if ("python" not in name.lower() and name not in ["TK_LIBRARY", "TCL_LIBRARY"]): # skip python vars
            env[name] = os.environ[name]
            
    env["PYTHONIOENCODING"] = encoding
    env["PYTHONUNBUFFERED"] = "1"
                
    interpreter = get_runner().get_interpreter_command()
    cmd = [interpreter, "-m", "pip"] + args
    
    return (subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            env=env, universal_newlines=True, encoding=encoding),
            cmd)

def _get_latest_stable_version(version_strings):
    versions = []
    for s in version_strings:
        if s.replace(".", "").isnumeric(): # Assuming stable versions have only dots and numbers
            versions.append(LooseVersion(s)) # LooseVersion __str__ doesn't change the version string
    
    if len(versions) == 0:
        return None
        
    return str(sorted(versions)[-1])


def _show_subprocess_dialog(master, proc, title):
    dlg = SubprocessDialog(master, proc, title)
    dlg.wait_window()


def _ask_installation_details(master, data, selected_version):
    dlg = DetailsDialog(master, data, selected_version)
    dlg.wait_window()
    return dlg.result

def load_plugin():
    def open_pip_gui(*args):
        pg = PipDialog(get_workbench())
        pg.wait_window()

        
    get_workbench().add_command("pipgui", "tools", "Manage packages...", open_pip_gui,
                                group=80)


    