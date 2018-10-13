# -*- coding: utf-8 -*-

import json
import logging
import os
import re
import subprocess
import sys
import tkinter as tk
import urllib.error
import urllib.parse
import webbrowser
from concurrent.futures.thread import ThreadPoolExecutor
from distutils.version import LooseVersion, StrictVersion
from logging import exception
from os import makedirs
from tkinter import messagebox, ttk
from tkinter.messagebox import showerror
from urllib.request import urlopen, urlretrieve

import thonny
from thonny import get_runner, get_workbench, running, tktextext, ui_utils
from thonny.common import (
    InlineCommand,
    normpath_with_actual_case,
    is_same_path,
    path_startswith,
)
from thonny.ui_utils import (
    AutoScrollbar,
    SubprocessDialog,
    askopenfilename,
    get_busy_cursor,
    lookup_style_option,
    open_path_in_system_file_manager,
    scrollbar_style,
)

PIP_INSTALLER_URL = "https://bootstrap.pypa.io/get-pip.py"


class PipDialog(tk.Toplevel):
    def __init__(self, master):
        self._state = "idle"  # possible values: "listing", "fetching", "idle"
        self._process = None
        self._active_distributions = {}
        self.current_package_data = None

        tk.Toplevel.__init__(self, master)

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.title(self._get_title())

        self._create_widgets(main_frame)

        self.search_box.focus_set()

        self.bind("<Escape>", self._on_close, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._show_instructions()

        self._start_update_list()

    def _create_widgets(self, parent):

        header_frame = ttk.Frame(parent)
        header_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(15, 0))
        header_frame.columnconfigure(0, weight=1)
        header_frame.rowconfigure(1, weight=1)

        name_font = tk.font.nametofont("TkDefaultFont").copy()
        name_font.configure(size=16)
        self.search_box = ttk.Entry(header_frame)
        self.search_box.grid(row=1, column=0, sticky="nsew")
        self.search_box.bind("<Return>", self._on_search, False)

        self.search_button = ttk.Button(
            header_frame,
            text="Find package from PyPI",
            command=self._on_search,
            width=25,
        )
        self.search_button.grid(row=1, column=1, sticky="nse", padx=(10, 0))

        main_pw = tk.PanedWindow(
            parent,
            orient=tk.HORIZONTAL,
            background=lookup_style_option("TPanedWindow", "background"),
            sashwidth=15,
        )
        main_pw.grid(row=2, column=0, sticky="nsew", padx=15, pady=15)
        parent.rowconfigure(2, weight=1)
        parent.columnconfigure(0, weight=1)

        listframe = ttk.Frame(main_pw, relief="flat", borderwidth=1)
        listframe.rowconfigure(0, weight=1)
        listframe.columnconfigure(0, weight=1)

        self.listbox = ui_utils.ThemedListbox(
            listframe,
            activestyle="dotbox",
            width=20,
            height=18,
            selectborderwidth=0,
            relief="flat",
            # highlightthickness=4,
            # highlightbackground="red",
            # highlightcolor="green",
            borderwidth=0,
        )
        self.listbox.insert("end", " <INSTALL>")
        self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select, True)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        list_scrollbar = AutoScrollbar(
            listframe, orient=tk.VERTICAL, style=scrollbar_style("Vertical")
        )
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        list_scrollbar["command"] = self.listbox.yview
        self.listbox["yscrollcommand"] = list_scrollbar.set

        info_frame = ttk.Frame(main_pw)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)

        main_pw.add(listframe)
        main_pw.add(info_frame)

        self.name_label = ttk.Label(info_frame, text="", font=name_font)
        self.name_label.grid(row=0, column=0, sticky="w", padx=5)

        info_text_frame = tktextext.TextFrame(
            info_frame,
            read_only=True,
            horizontal_scrollbar=False,
            background=lookup_style_option("TFrame", "background"),
            vertical_scrollbar_class=AutoScrollbar,
            vertical_scrollbar_style=scrollbar_style("Vertical"),
            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
            width=60,
            height=10,
        )
        info_text_frame.configure(borderwidth=0)
        info_text_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 10))
        self.info_text = info_text_frame.text
        link_color = lookup_style_option("Url.TLabel", "foreground", "red")
        self.info_text.tag_configure("url", foreground=link_color, underline=True)
        self.info_text.tag_bind("url", "<ButtonRelease-1>", self._handle_url_click)
        self.info_text.tag_bind(
            "url", "<Enter>", lambda e: self.info_text.config(cursor="hand2")
        )
        self.info_text.tag_bind(
            "url", "<Leave>", lambda e: self.info_text.config(cursor="")
        )
        self.info_text.tag_configure(
            "install_file", foreground=link_color, underline=True
        )
        self.info_text.tag_bind(
            "install_file", "<ButtonRelease-1>", self._handle_install_file_click
        )
        self.info_text.tag_bind(
            "install_file", "<Enter>", lambda e: self.info_text.config(cursor="hand2")
        )
        self.info_text.tag_bind(
            "install_file", "<Leave>", lambda e: self.info_text.config(cursor="")
        )

        default_font = tk.font.nametofont("TkDefaultFont")
        self.info_text.configure(font=default_font, wrap="word")

        bold_font = default_font.copy()
        # need to explicitly copy size, because Tk 8.6 on certain Ubuntus use bigger font in copies
        bold_font.configure(weight="bold", size=default_font.cget("size"))
        self.info_text.tag_configure("caption", font=bold_font)
        self.info_text.tag_configure("bold", font=bold_font)

        self.command_frame = ttk.Frame(info_frame)
        self.command_frame.grid(row=2, column=0, sticky="w")

        self.install_button = ttk.Button(
            self.command_frame, text=" Upgrade ", command=self._on_click_install
        )

        self.install_button.grid(row=0, column=0, sticky="w", padx=0)

        self.uninstall_button = ttk.Button(
            self.command_frame,
            text="Uninstall",
            command=lambda: self._perform_action("uninstall"),
        )

        self.uninstall_button.grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.advanced_button = ttk.Button(
            self.command_frame,
            text="...",
            width=3,
            command=lambda: self._perform_action("advanced"),
        )

        self.advanced_button.grid(row=0, column=2, sticky="w", padx=(5, 0))

        self.close_button = ttk.Button(info_frame, text="Close", command=self._on_close)
        self.close_button.grid(row=2, column=3, sticky="e")

    def _on_click_install(self):
        self._perform_action("install")

    def _set_state(self, state, force_normal_cursor=False):
        self._state = state
        widgets = [
            self.listbox,
            # self.search_box, # looks funny when disabled
            self.search_button,
            self.install_button,
            self.advanced_button,
            self.uninstall_button,
        ]

        if state == "idle":
            self.config(cursor="")
            for widget in widgets:
                widget["state"] = tk.NORMAL
        else:
            if force_normal_cursor:
                self.config(cursor="")
            else:
                self.config(cursor=get_busy_cursor())

            for widget in widgets:
                widget["state"] = tk.DISABLED

    def _get_state(self):
        return self._state

    def _handle_outdated_or_missing_pip(self, error):
        raise NotImplementedError()

    def _install_pip(self):
        self._clear()
        self.info_text.direct_insert("end", "Installing pip\n\n", ("caption",))
        self.info_text.direct_insert(
            "end",
            "pip, a required module for managing packages is missing or too old.\n\n"
            + "Downloading pip installer (about 1.5 MB), please wait ...\n",
        )
        self.update()
        self.update_idletasks()

        installer_filename, _ = urlretrieve(PIP_INSTALLER_URL)

        self.info_text.direct_insert("end", "Installing pip, please wait ...\n")
        self.update()
        self.update_idletasks()

        proc, _ = self._create_python_process(
            [installer_filename], stderr=subprocess.PIPE
        )
        out, err = proc.communicate()
        os.remove(installer_filename)

        if err != "":
            raise RuntimeError("Error while installing pip:\n" + err)

        self.info_text.direct_insert("end", out + "\n")
        self.update()
        self.update_idletasks()

        # update list
        self._start_update_list()

    def _provide_pip_install_instructions(self, error):
        self._clear()
        self.info_text.direct_insert("end", error)
        self.info_text.direct_insert(
            "end", "You seem to have problems with pip\n\n", ("caption",)
        )
        self.info_text.direct_insert(
            "end",
            "pip, a required module for managing packages is missing or too old for Thonny.\n\n"
            + "If your system package manager doesn't provide recent pip (9.0.0 or later), "
            + "then you can install newest version by downloading ",
        )
        self.info_text.direct_insert("end", PIP_INSTALLER_URL, ("url",))
        self.info_text.direct_insert(
            "end",
            " and running it with "
            + self._get_interpreter()
            + " (probably needs admin privileges).\n\n",
        )

        self.info_text.direct_insert(
            "end", self._instructions_for_command_line_install()
        )
        self._set_state("disabled", True)

    def _instructions_for_command_line_install(self):
        return (
            "Alternatively, if you have an older pip installed, then you can install packages "
            + "on the command line (Tools → Open system shell...)"
        )

    def _start_update_list(self, name_to_show=None):
        raise NotImplementedError()

    def _update_list(self, name_to_show):
        self.listbox.delete(1, "end")
        for name in sorted(self._active_distributions.keys()):
            self.listbox.insert("end", " " + name)

        if name_to_show is None:
            self._show_instructions()
        else:
            self._start_show_package_info(name_to_show)

    def _on_listbox_select(self, event):
        self.listbox.focus_set()
        selection = self.listbox.curselection()
        if len(selection) == 1:
            self.listbox.activate(selection[0])
            if selection[0] == 0:  # special first item
                self._show_instructions()
            else:
                self._start_show_package_info(self.listbox.get(selection[0]).strip())

    def _on_search(self, event=None):
        if self._get_state() != "idle":
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
            self.info_text.direct_insert("end", "Browse the packages\n", ("caption",))
            self.info_text.direct_insert(
                "end",
                "With current interpreter you can only browse the packages here.\n"
                + "Use 'Tools → Open system shell...' for installing, upgrading or uninstalling.\n\n",
            )

            if self._get_target_directory():
                self.info_text.direct_insert(
                    "end", "Packages' directory\n", ("caption",)
                )
                self.info_text.direct_insert(
                    "end", self._get_target_directory(), ("target_directory")
                )
        else:
            self.info_text.direct_insert("end", "Install from PyPI\n", ("caption",))
            self.info_text.direct_insert(
                "end",
                "If you don't know where to get the package from, "
                + "then most likely you'll want to search the Python Package Index. "
                + "Start by entering the name of the package in the search box above and pressing ENTER.\n\n",
            )

            self.info_text.direct_insert(
                "end", "Install from local file\n", ("caption",)
            )
            self.info_text.direct_insert("end", "Click ")
            self.info_text.direct_insert("end", "here", ("install_file",))
            self.info_text.direct_insert(
                "end",
                " to locate and install the package file (usually with .whl, .tar.gz or .zip extension).\n\n",
            )

            self.info_text.direct_insert("end", "Upgrade or uninstall\n", ("caption",))
            self.info_text.direct_insert(
                "end", "Start by selecting the package from the left.\n\n"
            )

            if self._get_target_directory():
                self.info_text.direct_insert("end", "Target:  ", ("caption",))
                if self._targets_virtual_environment():
                    self.info_text.direct_insert(
                        "end", "virtual environment\n", ("caption",)
                    )
                else:
                    self.info_text.direct_insert(
                        "end", "user site packages\n", ("caption",)
                    )

                self.info_text.direct_insert(
                    "end",
                    "This dialog lists all available packages,"
                    + " but allows upgrading and uninstalling only packages from ",
                )
                self.info_text.direct_insert(
                    "end", self._get_target_directory(), ("url")
                )
                self.info_text.direct_insert(
                    "end",
                    ". New packages will be also installed into this directory."
                    + " Other locations must be managed by alternative means.",
                )

        self._select_list_item(0)

    def _start_show_package_info(self, name):
        self.current_package_data = None
        # Fetch info from PyPI
        self._set_state("fetching")
        # Follwing fetches info about latest version.
        # This is OK even when we're looking an installed older version
        # because new version may have more relevant and complete info.
        _start_fetching_package_info(name, None, self._show_package_info)

        self.info_text.direct_delete("1.0", "end")
        self.name_label["text"] = ""
        self.name_label.grid()
        self.command_frame.grid()

        active_dist = self._get_active_dist(name)
        if active_dist is not None:
            self.name_label["text"] = active_dist["project_name"]
            self.info_text.direct_insert("end", "Installed version: ", ("caption",))
            self.info_text.direct_insert("end", active_dist["version"] + "\n")
            self.info_text.direct_insert("end", "Installed to: ", ("caption",))
            self.info_text.direct_insert(
                "end", normpath_with_actual_case(active_dist["location"]), ("url",)
            )
            self.info_text.direct_insert("end", "\n\n")
            self._select_list_item(name)
        else:
            self._select_list_item(0)

        # update gui
        if self._is_read_only_package(name):
            self.install_button.grid_remove()
            self.uninstall_button.grid_remove()
            self.advanced_button.grid_remove()
        else:
            self.install_button.grid(row=0, column=0)
            self.advanced_button.grid(row=0, column=2)

            if active_dist is not None:
                # existing package in target directory
                self.install_button["text"] = "Upgrade"
                self.install_button["state"] = "disabled"
                self.uninstall_button.grid(row=0, column=1)
            else:
                # new package
                self.install_button["text"] = "Install"
                self.uninstall_button.grid_remove()

    def _show_package_info(self, name, data, error_code=None):
        self._set_state("idle")

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
                if not self._get_active_version(name):
                    # new package
                    write("\nPlease check your spelling!" + "\nYou need to enter ")
                    write("exact package name", "bold")
                    write("!")

            else:
                write(
                    "Could not find the package info from PyPI. Error code: "
                    + str(error_code)
                )

            return

        info = data["info"]
        self.name_label["text"] = info[
            "name"
        ]  # search name could have been a bit different
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
        if info.get("requires_dist", None):
            # Available only when release is created by a binary wheel
            # https://github.com/pypa/pypi-legacy/issues/622#issuecomment-305829257
            write_att("Requires", ", ".join(info["requires_dist"]))

        if self._get_active_version(
            name
        ) != latest_stable_version or not self._get_active_version(name):
            self.install_button["state"] = "normal"
        else:
            self.install_button["state"] = "disabled"

    def _is_read_only_package(self, name):
        dist = self._get_active_dist(name)
        if dist is None:
            return False
        else:
            return (
                normpath_with_actual_case(dist["location"])
                != self._get_target_directory()
            )

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
            normalized_items = list(
                map(self._normalize_name, self.listbox.get(0, "end"))
            )
            try:
                index = normalized_items.index(self._normalize_name(name_or_index))
            except Exception:
                exception("Can't find package name from the list: " + name_or_index)
                return

        old_state = self.listbox["state"]
        try:
            self.listbox["state"] = "normal"
            self.listbox.select_clear(0, "end")
            self.listbox.select_set(index)
            self.listbox.activate(index)
            self.listbox.see(index)
        finally:
            self.listbox["state"] = old_state

    def _perform_action(self, action):
        assert self._get_state() == "idle"
        assert self.current_package_data is not None
        data = self.current_package_data
        name = self.current_package_data["info"]["name"]
        install_args = ["install", "--no-cache-dir"]
        if self._use_user_install():
            install_args.append("--user")

        if action == "install":
            if not self._confirm_install(self.current_package_data):
                return

            args = install_args
            if self._get_active_version(name) is not None:
                args.append("--upgrade")

            args.append(name)
        elif action == "uninstall":
            if name in ["pip", "setuptools"] and not messagebox.askyesno(
                "Really uninstall?",
                "Package '{}' is required for installing and uninstalling other packages.\n\n".format(
                    name
                )
                + "Are you sure you want to uninstall it?",
                parent=get_workbench()
            ):
                return
            args = ["uninstall", "-y", name]
        elif action == "advanced":
            details = _ask_installation_details(
                self, data, _get_latest_stable_version(list(data["releases"].keys()))
            )
            if details is None:  # Cancel
                return

            version, package_data, upgrade_deps = details
            if not self._confirm_install(package_data):
                return

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
            self._show_instructions()  # Make the old package go away as fast as possible
        self._start_update_list(None if action == "uninstall" else name)

    def _handle_install_file_click(self, event):
        if self._get_state() != "idle":
            return

        filename = askopenfilename(
            master=self,
            filetypes=[("Package", ".whl .zip .tar.gz"), ("all files", ".*")],
            initialdir=get_workbench().get_cwd(),
        )
        if (
            filename
        ):  # Note that missing filename may be "" or () depending on tkinter version
            self._install_local_file(filename)

    def _handle_target_directory_click(self, event):
        if self._get_target_directory():
            open_path_in_system_file_manager(self._get_target_directory())

    def _install_local_file(self, filename):
        args = ["install"]
        if self._use_user_install():
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
        inst_lines = re.findall(
            "^Installing collected packages:.*?$", out, re.MULTILINE | re.IGNORECASE
        )  # @UndefinedVariable
        if len(inst_lines) == 1:
            # take last element
            elements = re.split(",|:", inst_lines[0])
            name = elements[-1].strip()

        self._start_update_list(name)

    def _handle_url_click(self, event):
        url = _extract_click_text(self.info_text, event, "url")
        if url is not None:
            if url.startswith("http:") or url.startswith("https:"):
                webbrowser.open(url)
            else:
                os.makedirs(url, exist_ok=True)
                open_path_in_system_file_manager(url)

    def _on_close(self, event=None):
        self.destroy()

    def _get_active_version(self, name):
        dist = self._get_active_dist(name)
        if dist is None:
            return None
        else:
            return dist["version"]

    def _get_active_dist(self, name):
        normname = self._normalize_name(name)
        for key in self._active_distributions:

            if self._normalize_name(key) == normname:
                return self._active_distributions[key]

        return None

    def _create_python_process(self, args, stderr):
        raise NotImplementedError()

    def _create_pip_process(self, args, stderr=subprocess.STDOUT):
        if "--disable-pip-version-check" not in args:
            args.append("--disable-pip-version-check")
        return self._create_python_process(["-m", "pip"] + args, stderr=stderr)

    def _get_interpreter(self):
        pass

    def _targets_virtual_environment(self):
        raise NotImplementedError()

    def _use_user_install(self):
        return not self._targets_virtual_environment()

    def _get_target_directory(self):
        raise NotImplementedError()

    def _get_title(self):
        return "Manage packages for " + self._get_interpreter()

    def _confirm_install(self, package_data):
        return True

    def _read_only(self):
        if self._targets_virtual_environment():
            return False
        else:
            # readonly if not in a virtual environment
            # and user site packages is disabled
            import site

            return not site.ENABLE_USER_SITE


class BackendPipDialog(PipDialog):
    def __init__(self, master):
        self._backend_proxy = get_runner().get_backend_proxy()
        super().__init__(master)
        assert isinstance(self._backend_proxy, running.CPythonProxy)

        self._last_name_to_show = None

    def _start_update_list(self, name_to_show=None):
        assert self._get_state() in [None, "idle"]
        self._set_state("listing")

        get_workbench().bind(
            "get_active_distributions_response", self._complete_update_list, True
        )
        self._last_name_to_show = name_to_show
        get_runner().send_command(InlineCommand("get_active_distributions"))

    def _complete_update_list(self, msg):
        get_workbench().unbind(
            "get_active_distributions_response", self._complete_update_list
        )
        if "error" in msg:
            self.info_text.direct_delete("1.0", "end")
            self.info_text.direct_insert("1.0", msg["error"])
            self._set_state("idle", True)
            return

        self._active_distributions = msg.distributions
        self._set_state("idle", True)
        self._update_list(self._last_name_to_show)

    def _get_interpreter(self):
        return get_runner().get_executable()

    def _create_python_process(self, args, stderr):
        proc = running.create_backend_python_process(args, stderr=stderr)
        return proc, proc.cmd

    def _confirm_install(self, package_data):
        name = package_data["info"]["name"]

        if name.lower().startswith("thonny"):
            return messagebox.askyesno(
                "Confirmation",
                "Looks like you are installing a Thonny-related package.\n"
                + "If you meant to install a Thonny plugin, then you should\n"
                + "choose 'Tools → Manage plugins...' instead\n"
                + "\n"
                + "Are you sure you want to install '"
                + name
                + "' for the back-end?",
                parent=get_workbench(),
            )
        else:
            return True

    def _handle_outdated_or_missing_pip(self, error):
        if get_runner().using_venv():
            self._install_pip()
        else:
            self._provide_pip_install_instructions(error)

    def _get_target_directory(self):
        if self._targets_virtual_environment():
            return normpath_with_actual_case(self._backend_proxy.get_site_packages())
        else:
            usp = self._backend_proxy.get_user_site_packages()
            os.makedirs(usp, exist_ok=True)
            return normpath_with_actual_case(usp)

    def _targets_virtual_environment(self):
        return get_runner().using_venv()


class PluginsPipDialog(PipDialog):
    def __init__(self, master):
        PipDialog.__init__(self, master)

        # make sure directory exists, so user can put her plug-ins there
        d = self._get_target_directory()
        makedirs(d, exist_ok=True)

    def _start_update_list(self, name_to_show=None):
        assert self._get_state() in [None, "idle"]
        import pkg_resources

        pkg_resources._initialize_master_working_set()

        self._active_distributions = {
            dist.key: {
                "project_name": dist.project_name,
                "key": dist.key,
                "location": dist.location,
                "version": dist.version,
            }
            for dist in pkg_resources.working_set  # pylint: disable=not-an-iterable
        }

        self._update_list(name_to_show)

    def _conflicts_with_thonny_version(self, req_strings):
        import pkg_resources

        try:
            conflicts = []
            for req_string in req_strings:
                req = pkg_resources.Requirement.parse(req_string)
                if req.project_name == "thonny" and thonny.get_version() not in req:
                    conflicts.append(req_string)

            return conflicts
        except Exception:
            logging.exception("Problem computing conflicts")
            return None

    def _get_interpreter(self):
        return sys.executable.replace("thonny.exe", "python.exe")

    def _targets_virtual_environment(self):
        # https://stackoverflow.com/a/42580137/261181
        return (
            hasattr(sys, "base_prefix")
            and sys.base_prefix != sys.prefix
            or hasattr(sys, "real_prefix")
            and getattr(sys, "real_prefix") != sys.prefix
        )

    def _create_python_process(self, args, stderr):
        proc = running.create_frontend_python_process(args, stderr=stderr)
        return proc, proc.cmd

    def _confirm_install(self, package_data):
        name = package_data["info"]["name"]
        reqs = package_data["info"].get("requires_dist", None)
        
        other_version_text = (
            "NB! There may be another version available "
            + "which is compatible with current Thonny version. "
            + "Click on '...' button to choose the version to install."
        )
        
        if name.lower().startswith("thonny-") and not reqs:
            showerror(
                "Thonny plugin without requirements",
                "Looks like you are trying to install an outdated Thonny\n"
                + "plug-in (it doesn't specify required Thonny version).\n\n"
                + "If you still want it, then please install it from the command line."
                + "\n\n" + other_version_text,
                parent=get_workbench(),
            )
            return False
        elif reqs:
            conflicts = self._conflicts_with_thonny_version(reqs)
            if conflicts:
                showerror(
                    "Unsuitable requirements",
                    "This package requires different Thonny version:\n\n  "
                    + "\n  ".join(conflicts)
                    + "\n\nIf you still want it, then please install it from the command line."
                    + "\n\n" + other_version_text,
                    parent=get_workbench(),
                )
                return False

        return True

    def _get_target_directory(self):
        if self._use_user_install():
            import site

            assert hasattr(site, "getusersitepackages")
            os.makedirs(site.getusersitepackages(), exist_ok=True)
            return normpath_with_actual_case(site.getusersitepackages())
        else:
            for d in sys.path:
                if ("site-packages" in d or "dist-packages" in d) and path_startswith(
                    d, sys.prefix
                ):
                    return normpath_with_actual_case(d)
            return None

    def _create_widgets(self, parent):
        bg = "#ffff99"
        banner = tk.Label(parent, background=bg)
        banner.grid(row=0, column=0, sticky="nsew")

        banner_msg = (
            "This dialog is for managing Thonny plug-ins and their dependencies.\n"
            + "If you want to install packages for your own programs then choose 'Tools → Manage packages...'\n"
        )

        runner = get_runner()
        if (
            runner is not None
            and runner.get_executable() is not None
            and is_same_path(self._get_interpreter(), get_runner().get_executable())
        ):
            banner_msg += "(In this case Thonny's back-end uses same interpreter, so both dialogs manage same packages.)\n"

        banner_msg += (
            "\n"
            + "NB! You need to restart Thonny after installing / upgrading / uninstalling a plug-in."
        )

        banner_text = tk.Label(banner, text=banner_msg, background=bg, justify="left")
        banner_text.grid(pady=10, padx=10)

        PipDialog._create_widgets(self, parent)

    def _get_title(self):
        return "Thonny plug-ins"

    def _handle_outdated_or_missing_pip(self, error):
        return self._provide_pip_install_instructions(error)


class DetailsDialog(tk.Toplevel):
    def __init__(self, master, package_metadata, selected_version):
        tk.Toplevel.__init__(self, master)
        self.result = None
        self._closed = False
        self._version_data = None
        self._package_name = package_metadata["info"]["name"]
        self.title("Advanced install / upgrade / downgrade")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame = ttk.Frame(self)  # To get styled background
        main_frame.grid(sticky="nsew")
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        version_label = ttk.Label(main_frame, text="Desired version")
        version_label.grid(
            row=0, column=0, columnspan=2, padx=20, pady=(15, 0), sticky="w"
        )

        def version_sort_key(s):
            # Trying to massage understandable versions into valid StrictVersions
            if s.replace(".", "").isnumeric():  # stable release
                s2 = s + "b999"  # make it latest beta version
            elif "rc" in s:
                s2 = s.replace("rc", "b8")
            else:
                s2 = s
            try:
                return StrictVersion(s2)
            except Exception:
                # use only numbers
                nums = re.findall(r"\d+", s)
                while len(nums) < 2:
                    nums.append("0")
                return StrictVersion(".".join(nums[:3]))

        version_strings = list(package_metadata["releases"].keys())
        version_strings.sort(key=version_sort_key, reverse=True)
        self.version_var = ui_utils.create_string_var(
            selected_version, self._start_fetching_version_info
        )
        self.version_combo = ttk.Combobox(
            main_frame,
            textvariable=self.version_var,
            values=version_strings,
            exportselection=False,
        )

        self.version_combo.state(["!disabled", "readonly"])
        self.version_combo.grid(
            row=1, column=0, columnspan=2, pady=(0, 15), padx=20, sticky="ew"
        )

        self.requires_label = ttk.Label(main_frame, text="")
        self.requires_label.grid(
            row=2, column=0, columnspan=2, pady=(0, 15), padx=20, sticky="ew"
        )

        self.update_deps_var = tk.IntVar()
        self.update_deps_var.set(0)
        self.update_deps_cb = ttk.Checkbutton(
            main_frame, text="Upgrade dependencies", variable=self.update_deps_var
        )
        self.update_deps_cb.grid(row=3, column=0, columnspan=2, padx=20, sticky="w")

        self.ok_button = ttk.Button(main_frame, text="Install", command=self._ok)
        self.ok_button.grid(row=4, column=0, pady=15, padx=(20, 0), sticky="se")
        self.cancel_button = ttk.Button(main_frame, text="Cancel", command=self._cancel)
        self.cancel_button.grid(row=4, column=1, pady=15, padx=(5, 20), sticky="se")

        # self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.version_combo.focus_set()

        self.bind("<Escape>", self._cancel, True)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        if self.version_var.get().strip():
            self._start_fetching_version_info()

    def _set_state(self, state):
        self._state = state
        widgets = [
            self.version_combo,
            # self.search_box, # looks funny when disabled
            self.ok_button,
            self.update_deps_cb,
        ]

        if state == "idle":
            self.config(cursor="")
            for widget in widgets:
                if widget == self.version_combo:
                    widget.state(["!disabled", "readonly"])
                else:
                    widget["state"] = tk.NORMAL
        else:
            self.config(cursor=get_busy_cursor())
            for widget in widgets:
                widget["state"] = tk.DISABLED

        if self.version_var.get().strip() == "" or not self._version_data:
            self.ok_button["state"] = tk.DISABLED

    def _start_fetching_version_info(self):
        self._set_state("busy")
        _start_fetching_package_info(
            self._package_name, self.version_var.get(), self._show_version_info
        )

    def _show_version_info(self, name, info, error_code=None):
        if self._closed:
            return

        self._version_data = info
        if (
            not error_code
            and "requires_dist" in info["info"]
            and isinstance(info["info"]["requires_dist"], list)
        ):
            reqs = "Requires:\n  * " + "\n  * ".join(info["info"]["requires_dist"])
        elif error_code:
            reqs = "Error code: " + str(error_code)
            if "error" in info:
                reqs += "\nError: " + info["error"]
        else:
            reqs = ""

        self.requires_label.configure(text=reqs)
        self._set_state("idle")

    def _ok(self, event=None):
        self.result = (
            self.version_var.get(),
            self._version_data,
            bool(self.update_deps_var.get()),
        )
        self._closed = True
        self.destroy()

    def _cancel(self, event=None):
        self.result = None
        self._closed = True
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
        if s.replace(
            ".", ""
        ).isnumeric():  # Assuming stable versions have only dots and numbers
            versions.append(
                LooseVersion(s)
            )  # LooseVersion __str__ doesn't change the version string

    if len(versions) == 0:
        return None

    return str(sorted(versions)[-1])


def _show_subprocess_dialog(master, proc, title):
    dlg = SubprocessDialog(master, proc, title)
    ui_utils.show_dialog(dlg, master)
    return dlg.returncode, dlg.stdout, dlg.stderr


def _ask_installation_details(master, data, selected_version):
    dlg = DetailsDialog(master, data, selected_version)
    ui_utils.show_dialog(dlg, master)
    return dlg.result


def _start_fetching_package_info(name, version_str, completion_handler):
    # Fetch info from PyPI
    if version_str is None:
        url = "https://pypi.org/pypi/{}/json".format(urllib.parse.quote(name))
    else:
        url = "https://pypi.org/pypi/{}/{}/json".format(
            urllib.parse.quote(name), urllib.parse.quote(version_str)
        )

    url_future = _fetch_url_future(url)

    def poll_fetch_complete():
        if url_future.done():
            try:
                _, bin_data = url_future.result()
                raw_data = bin_data.decode("UTF-8")
                completion_handler(name, json.loads(raw_data))
            except urllib.error.HTTPError as e:
                completion_handler(
                    name,
                    {"info": {"name": name}, "error": str(e), "releases": {}},
                    e.code,
                )
        else:
            tk._default_root.after(200, poll_fetch_complete)

    poll_fetch_complete()


def _extract_click_text(widget, event, tag):
    # http://stackoverflow.com/a/33957256/261181
    try:
        index = widget.index("@%s,%s" % (event.x, event.y))
        tag_indices = list(widget.tag_ranges(tag))
        for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
            # check if the tag matches the mouse click index
            if widget.compare(start, "<=", index) and widget.compare(index, "<", end):
                return widget.get(start, end)
    except Exception:
        logging.exception("extracting click text")

    return None


def load_plugin() -> None:
    def open_backend_pip_gui(*args):
        pg = BackendPipDialog(get_workbench())
        ui_utils.show_dialog(pg)

    def open_backend_pip_gui_enabled():
        return "pip_gui" in get_runner().supported_features()

    def open_frontend_pip_gui(*args):
        pg = PluginsPipDialog(get_workbench())
        ui_utils.show_dialog(pg)

    get_workbench().add_command(
        "backendpipgui",
        "tools",
        "Manage packages...",
        open_backend_pip_gui,
        tester=open_backend_pip_gui_enabled,
        group=80,
    )
    get_workbench().add_command(
        "pluginspipgui", "tools", "Manage plug-ins...", open_frontend_pip_gui, group=180
    )
