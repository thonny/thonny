# -*- coding: utf-8 -*-

import webbrowser

import tkinter as tk
from tkinter import ttk, messagebox

from thonny import misc_utils, tktextext, ui_utils, THONNY_USER_BASE
from thonny.globals import get_workbench, get_runner
import subprocess
from urllib.request import urlopen, urlretrieve
import urllib.error
import urllib.parse
from concurrent.futures.thread import ThreadPoolExecutor
import os
import json
from distutils.version import LooseVersion, StrictVersion
import logging
import re
from tkinter.filedialog import askopenfilename
from logging import exception
from thonny.ui_utils import SubprocessDialog, AutoScrollbar, get_busy_cursor
from thonny.misc_utils import running_on_windows
import sys

LINK_COLOR="#3A66DD"
PIP_INSTALLER_URL="https://bootstrap.pypa.io/get-pip.py"

class PipDialog(tk.Toplevel):
    def __init__(self, master, only_user=False):
        self._state = None # possible values: "listing", "fetching", "idle"
        self._process = None
        self._installed_versions = {}
        self._only_user = only_user
        self.current_package_data = None
        
        tk.Toplevel.__init__(self, master)
        
        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.title(self._get_title())
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        self.transient(master)
        self.grab_set() # to make it active
        #self.grab_release() # to allow eg. copy something from the editor 
        
        self._create_widgets(main_frame)
        
        self.search_box.focus_set()
        
        self.bind('<Escape>', self._on_close, True) 
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._show_instructions()
        ui_utils.center_window(self, master)
        
        self._start_update_list()
    
    
    def _create_widgets(self, parent):
        
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(15,0))
        header_frame.columnconfigure(0, weight=1)
        header_frame.rowconfigure(1, weight=1)
        
        name_font = tk.font.nametofont("TkDefaultFont").copy()
        name_font.configure(size=16)
        self.search_box = ttk.Entry(header_frame, background=ui_utils.CALM_WHITE)
        self.search_box.grid(row=1, column=0, sticky="nsew")
        self.search_box.bind("<Return>", self._on_search, False)
        
        self.search_button = ttk.Button(header_frame, text="Search", command=self._on_search)
        self.search_button.grid(row=1, column=1, sticky="nse", padx=(10,0))
        
        
        main_pw = tk.PanedWindow(parent, orient=tk.HORIZONTAL,
                                 background=ui_utils.get_main_background(),
                                 sashwidth=10)
        main_pw.grid(row=2, column=0, sticky="nsew", padx=15, pady=15)
        parent.rowconfigure(2, weight=1)
        parent.columnconfigure(0, weight=1)
        
        listframe = ttk.Frame(main_pw, relief="groove", borderwidth=1)
        listframe.rowconfigure(0, weight=1)
        listframe.columnconfigure(0, weight=1)
        
        self.listbox = tk.Listbox(listframe, activestyle="dotbox", 
                                  width=20, height=10,
                                  background=ui_utils.CALM_WHITE,
                                  selectborderwidth=0, relief="flat",
                                  highlightthickness=0, borderwidth=0)
        self.listbox.insert("end", " <INSTALL>")
        self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select, True)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        list_scrollbar = AutoScrollbar(listframe, orient=tk.VERTICAL)
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
                                              horizontal_scrollbar=False,
                                              vertical_scrollbar_class=AutoScrollbar,
                                              width=60, height=10)
        info_text_frame.configure(borderwidth=1)
        info_text_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0,20))
        self.info_text = info_text_frame.text
        self.info_text.tag_configure("url", foreground=LINK_COLOR, underline=True)
        self.info_text.tag_bind("url", "<ButtonRelease-1>", self._handle_url_click)
        self.info_text.tag_bind("url", "<Enter>", lambda e: self.info_text.config(cursor="hand2"))
        self.info_text.tag_bind("url", "<Leave>", lambda e: self.info_text.config(cursor=""))
        self.info_text.tag_configure("install_file", foreground=LINK_COLOR, underline=True)
        self.info_text.tag_bind("install_file", "<ButtonRelease-1>", self._handle_install_file_click)
        self.info_text.tag_bind("install_file", "<Enter>", lambda e: self.info_text.config(cursor="hand2"))
        self.info_text.tag_bind("install_file", "<Leave>", lambda e: self.info_text.config(cursor=""))
        
        default_font = tk.font.nametofont("TkDefaultFont")
        self.info_text.configure(background=ui_utils.get_main_background(),
                                 font=default_font,
                                 wrap="word")

        bold_font = default_font.copy()
        # need to explicitly copy size, because Tk 8.6 on certain Ubuntus use bigger font in copies
        bold_font.configure(weight="bold", size=default_font.cget("size"))
        self.info_text.tag_configure("caption", font=bold_font)
        self.info_text.tag_configure("bold", font=bold_font)
        
        
        self.command_frame = ttk.Frame(info_frame)
        self.command_frame.grid(row=2, column=0, sticky="w")
        
        self.install_button = ttk.Button(self.command_frame, text=" Upgrade ",
                                         command=self._on_click_install)
        
        if not self._read_only():
            self.install_button.grid(row=0, column=0, sticky="w", padx=0)
        
        self.uninstall_button = ttk.Button(self.command_frame, text="Uninstall",
                                           command=lambda: self._perform_action("uninstall"))
        
        if not self._read_only():
            self.uninstall_button.grid(row=0, column=1, sticky="w", padx=(5,0))
        
        self.advanced_button = ttk.Button(self.command_frame, text="...", width=3,
                                          command=lambda: self._perform_action("advanced"))
        
        if not self._read_only():
            self.advanced_button.grid(row=0, column=2, sticky="w", padx=(5,0))
        
        self.close_button = ttk.Button(info_frame, text="Close", command=self._on_close)
        self.close_button.grid(row=2, column=3, sticky="e")
    
    def _on_click_install(self):
        name = self.current_package_data["info"]["name"]
        if self._confirm_install(name):
            self._perform_action("install")

    def _set_state(self, state, normal_cursor=False):
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
            self.config(cursor=get_busy_cursor())
            for widget in widgets:
                widget["state"] = tk.DISABLED
        
        if normal_cursor:
            self.config(cursor="")
    
    def _get_state(self):
        return self._state
    
    def _handle_outdated_or_missing_pip(self):
        raise NotImplementedError()
        
    def _install_pip(self):
        self._clear()
        self.info_text.direct_insert("end", "Installing pip\n\n", ("caption", ))
        self.info_text.direct_insert("end", "pip, a required module for managing packages is missing or too old.\n\n"
                                + "Downloading pip installer (about 1.5 MB), please wait ...\n")
        self.update()
        self.update_idletasks()
        
        installer_filename, _ = urlretrieve(PIP_INSTALLER_URL)
        
        self.info_text.direct_insert("end", "Installing pip, please wait ...\n")
        self.update()
        self.update_idletasks()
        
        proc, _ = self._create_backend_process([installer_filename], stderr=subprocess.PIPE)
        out, err = proc.communicate()
        os.remove(installer_filename)
        
        if err != "":
            raise RuntimeError("Error while installing pip:\n" + err)
        
        self.info_text.direct_insert("end", out  + "\n")
        self.update()
        self.update_idletasks()
        
        # update list
        self._start_update_list()
        
        
    def _provide_pip_install_instructions(self):
        self._clear()
        self.info_text.direct_insert("end", "Outdated or missing pip\n\n", ("caption", ))
        self.info_text.direct_insert("end", "pip, a required module for managing packages is missing or too old for Thonny.\n\n"
                                + "If your system package manager doesn't provide recent pip (9.0.0 or later), "
                                + "then you can install newest version by downloading ")
        self.info_text.direct_insert("end", PIP_INSTALLER_URL, ("url",))
        self.info_text.direct_insert("end", " and running it with " 
                                     + self._get_interpreter()
                                     + " (probably needs admin privileges).\n\n")
        
        self.info_text.direct_insert("end", self._instructions_for_command_line_install())
        self._set_state("disabled", True)
    
    def _instructions_for_command_line_install(self):
        return ("Alternatively, if you have an older pip installed, then you can install packages "
                                     + "on the command line (Tools → Open system shell...)")
    
    def _start_update_list(self, name_to_show=None):
        assert self._get_state() in [None, "idle"]
        self._set_state("listing")
        args = ["list"]
        if self._only_user:
            args.append("--user")
        args.extend(["--pre", "--format", "json"])
        self._process, _ = self._create_pip_process(args)
        
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
                        error = self._process.stdout.read()
                        if ("no module named pip" in error.lower() # pip not installed
                            or "no such option" in error.lower()): # too old pip
                            self._handle_outdated_or_missing_pip()
                            return
                        else:
                            messagebox.showerror("pip list error", error)
                    
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
        
        if self.search_box.get().strip() == "":
            return
        
        self._start_show_package_info(self.search_box.get().strip())
    
    def _clear(self):
        self.current_package_data = None
        self.name_label.grid_remove()
        self.command_frame.grid_remove()
        self.info_text.direct_delete("1.0", "end")
    
    def _show_instructions(self):
        self._clear()
        if self._read_only():
            self.info_text.direct_insert("end", "With current interpreter you can only browse the packages here.\n"
                                       + "Use 'Tools → Open system shell...' for installing, upgrading or uninstalling.")
        else:            
            self.info_text.direct_insert("end", "Install from PyPI\n", ("caption",))
            self.info_text.direct_insert("end", "If you don't know where to get the package from, "
                                         + "then most likely you'll want to search the Python Package Index. "
                                         + "Start by entering the name of the package in the search box above and pressing ENTER.\n\n")
            
            self.info_text.direct_insert("end", "Install from local file\n", ("caption",))
            self.info_text.direct_insert("end", "Click ")
            self.info_text.direct_insert("end", "here", ("install_file",))
            self.info_text.direct_insert("end", " to locate and install the package file (usually with .whl, .tar.gz or .zip extension).\n\n")
            
            self.info_text.direct_insert("end", "Upgrade or uninstall\n", ("caption",))
            self.info_text.direct_insert("end", 'Start by selecting the package from the left.')
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
        url = "https://pypi.python.org/pypi/{}/json".format(urllib.parse.quote(name))
        url_future = _fetch_url_future(url)
            
        def poll_fetch_complete():
            if url_future.done():
                self._set_state("idle")
                try:
                    _, bin_data = url_future.result()
                    raw_data = bin_data.decode("UTF-8")
                    self._show_package_info(name, json.loads(raw_data))
                except urllib.error.HTTPError as e:
                    self._show_package_info(name, self._generate_minimal_data(name), e.code)
                        
            else:
                self.after(200, poll_fetch_complete)
        
        poll_fetch_complete()
    
    def _generate_minimal_data(self, name):
        return {
            "info" : {'name' : name},
            "releases" : {}
            }

    def _show_package_info(self, name, data, error_code=None):
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
                write("Could not find the package from PyPI.")
                if not self._get_installed_version(name):
                    # new package
                    write("\nPlease check your spelling!"
                          + "\nYou need to enter ")
                    write("exact package name", "bold")
                    write("!")
                    
            else:
                write("Could not find the package info from PyPI. Error code: " + str(error_code))
            return
        
        info = data["info"]
        self.name_label["text"] = info["name"] # search name could have been a bit different
        latest_stable_version = _get_latest_stable_version(data["releases"].keys())
        if latest_stable_version is not None:
            write_att("Latest stable version", latest_stable_version)
        else:
            write_att("Latest version", data["info"]["version"])
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
            if not self._read_only():
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
        
        # https://www.python.org/dev/peps/pep-0503/#id4
        return re.sub(r"[-_.]+", "-", name).lower().strip()
    
    def _select_list_item(self, name_or_index):
        if isinstance(name_or_index, int):
            index = name_or_index
        else:
            normalized_items = list(map(self._normalize_name, self.listbox.get(0, "end")))
            try:
                index = normalized_items.index(self._normalize_name(name_or_index))
            except:
                exception("Can't find package name from the list: " + name_or_index)
                return
        
        self.listbox.select_clear(0, "end")
        self.listbox.select_set(index)
        self.listbox.see(index)
        
        
    
    def _perform_action(self, action):
        assert self._get_state() == "idle"
        assert self.current_package_data is not None
        data = self.current_package_data
        name = self.current_package_data["info"]["name"]
        install_args = ["install", "--no-cache-dir"] 
        if self._only_user:
            install_args.append("--user")
        
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
        
        proc, cmd = self._create_pip_process(args)
        title = subprocess.list2cmdline(cmd)
        
        # following call blocks
        _show_subprocess_dialog(self, proc, title)
        if action == "uninstall":
            self._show_instructions() # Make the old package go away as fast as possible
        self._start_update_list(None if action == "uninstall" else name)
        
        
    
    def _handle_install_file_click(self, event):
        if self._get_state() != "idle":
            return 
        
        filename = askopenfilename (
            filetypes = [('Package', '.whl .zip .tar.gz'), ('all files', '.*')], 
            initialdir = get_workbench().get_option("run.working_directory")
        )
        if filename: # Note that missing filename may be "" or () depending on tkinter version
            self._install_local_file(filename)
    
    def _install_local_file(self, filename):
        args = ["install"]
        if self._only_user:
            args.append("--user")
        args.append(filename)
        
        proc, cmd = self._create_pip_process(args)
        # following call blocks
        title = subprocess.list2cmdline(cmd)
        
        _, out, _ = _show_subprocess_dialog(self, proc, title)
        
        # Try to find out the name of the package we're installing
        name = None
        
        # output should include a line like this:
        # Installing collected packages: pytz, six, python-dateutil, numpy, pandas
        inst_lines = re.findall("^Installing collected packages:.*?$", out,
                                     re.MULTILINE | re.IGNORECASE)  # @UndefinedVariable
        if len(inst_lines) == 1:
            # take last element
            elements = re.split(",|:", inst_lines[0])
            name = elements[-1].strip()
        
        self._start_update_list(name)
    
    def _handle_url_click(self, event):
        url = _extract_click_text(self.info_text, event, "url")
        if url is not None:
            webbrowser.open(url)
    
    def _on_close(self, event=None):
        self.destroy()
        
    def _get_installed_version(self, name):
        for list_name in self._installed_versions:
            if self._normalize_name(name) == self._normalize_name(list_name):
                return self._installed_versions[list_name]
        
        return None

    def _prepare_env_for_pip_process(self, encoding):
        env = {}
        for name in os.environ:
            if ("python" not in name.lower() and name not in ["TK_LIBRARY", "TCL_LIBRARY"]): # skip python vars
                env[name] = os.environ[name]
                
        env["PYTHONIOENCODING"] = encoding
        env["PYTHONUNBUFFERED"] = "1"
        
        return env

    def _create_backend_process(self, args, stderr=subprocess.STDOUT):
        encoding = "UTF-8"
        
                    
        cmd = [self._get_interpreter()] + args
        
        startupinfo = None
        creationflags = 0
        if running_on_windows():
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        return (subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=stderr,
                                env=self._prepare_env_for_pip_process(encoding),
                                universal_newlines=True,
                                creationflags=creationflags,
                                startupinfo=startupinfo),
                cmd)

    def _create_pip_process(self, args):
        return self._create_backend_process(["-m", "pip"] + args)
    
    def _get_interpreter(self):
        pass
    
    def _get_title(self):
        return "Manage packages for " + self._get_interpreter()
    
    def _confirm_install(self, name):
        return True
    
    def _read_only(self):
        return False

class BackendPipDialog(PipDialog):
    def _get_interpreter(self):
        return get_runner().get_interpreter_command()

    def _confirm_install(self, name):
        if name.lower().startswith("thonny"):
            return messagebox.askyesno("Confirmation", 
                                     "Looks like you are installing a Thonny-related package.\n"
                                   + "If you meant to install a Thonny plugin, then you should\n"
                                   + "close this dialog and choose 'Tools → Manage plugins...'\n"
                                   + "\n"
                                   + "Are you sure you want to install '" + name + "' here?")
        else:
            return True

    def _handle_outdated_or_missing_pip(self):
        if get_runner().using_venv():
            self._install_pip()
        else:
            self._provide_pip_install_instructions()
        
    def _read_only(self):
        return not get_runner().using_venv()

class PluginsPipDialog(PipDialog):
    def __init__(self, master):
        PipDialog.__init__(self, master, only_user=True)
    
    def _get_interpreter(self):
        return sys.executable.replace("thonny.exe", "python.exe")
    
    def _prepare_env_for_pip_process(self, encoding):
        env = PipDialog._prepare_env_for_pip_process(self, encoding)
        env["PYTHONUSERBASE"] = THONNY_USER_BASE
        return env
        
        
    def _create_widgets(self, parent):
        bg = "#ffff99"
        banner = tk.Label(parent, background=bg)
        banner.grid(row=0, column=0, sticky="nsew")
        
        banner_text = tk.Label(banner, text="NB! This dialog is for managing Thonny plug-ins and their dependencies.\n"
                                + "If you want to install packages for your own programs then close this and choose 'Tools → Manage packages...'\n"
                                + "\n"
                                + "This dialog installs packages into " + THONNY_USER_BASE + "\n"
                                + "\n"
                                + "NB! You need to restart Thonny after installing / upgrading / uninstalling a plug-in.",
                                background=bg, justify="left")
        banner_text.grid(pady=10, padx=10)
        
        PipDialog._create_widgets(self, parent)
    
    def _get_title(self):
        return "Thonny plug-ins"

    def _handle_outdated_or_missing_pip(self):
        return self._provide_pip_install_instructions()
    
    def _instructions_for_command_line_install(self):
        # System shell is not suitable without correct PYTHONUSERBASE 
        return ""
        
class DetailsDialog(tk.Toplevel):
    def __init__(self, master, package_metadata, selected_version):
        tk.Toplevel.__init__(self, master)
        self.result = None
        
        self.title("Advanced install / upgrade / downgrade")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame = ttk.Frame(self) # To get styled background
        main_frame.grid(sticky="nsew")
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
        
        ui_utils.center_window(self, master)
        
    
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
    return dlg.returncode, dlg.stdout, dlg.stderr


def _ask_installation_details(master, data, selected_version):
    dlg = DetailsDialog(master, data, selected_version)
    dlg.wait_window()
    return dlg.result


def _extract_click_text(widget, event, tag):
    # http://stackoverflow.com/a/33957256/261181
    try:
        index = widget.index("@%s,%s" % (event.x, event.y))
        tag_indices = list(widget.tag_ranges(tag))
        for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
            # check if the tag matches the mouse click index
            if widget.compare(start, '<=', index) and widget.compare(index, '<', end):
                return widget.get(start, end)
    except:
        logging.exception("extracting click text")
        return None


def load_plugin():
    def open_backend_pip_gui(*args):
        pg = BackendPipDialog(get_workbench())
        pg.wait_window()
    
    def open_backend_pip_gui_enabled():
        return "pip_gui" in get_runner().supported_features()

    def open_frontend_pip_gui(*args):
        pg = PluginsPipDialog(get_workbench())
        pg.wait_window()

    get_workbench().add_command("backendpipgui", "tools", "Manage packages...", open_backend_pip_gui,
                                tester=open_backend_pip_gui_enabled,
                                group=80)
    get_workbench().add_command("pluginspipgui", "tools", "Manage plug-ins...", open_frontend_pip_gui,
                                group=180)


    