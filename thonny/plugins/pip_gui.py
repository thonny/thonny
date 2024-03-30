# -*- coding: utf-8 -*-
import os
import re
import subprocess
import sys
import tkinter as tk
import tkinter.font as tk_font
import urllib.error
import urllib.parse
from abc import ABC, abstractmethod
from logging import exception, getLogger
from os import makedirs
from tkinter import messagebox, ttk
from tkinter.messagebox import showerror
from typing import Dict, List, Optional, Tuple, Union, cast

import thonny
from thonny import get_runner, get_workbench, running, tktextext, ui_utils
from thonny.common import (
    DistInfo,
    InlineCommand,
    normpath_with_actual_case,
    path_startswith,
    running_in_virtual_environment,
)
from thonny.languages import tr
from thonny.misc_utils import construct_cmd_line, levenshtein_distance
from thonny.running import InlineCommandDialog, get_front_interpreter_for_subprocess
from thonny.ui_utils import (
    AutoScrollbar,
    CommonDialog,
    askopenfilename,
    ems_to_pixels,
    get_busy_cursor,
    get_hyperlink_cursor,
    lookup_style_option,
    open_path_in_system_file_manager,
)
from thonny.workdlg import SubprocessDialog

PIP_INSTALLER_URL = "https://bootstrap.pypa.io/get-pip.py"

logger = getLogger(__name__)

_EXTRA_MARKER_RE = re.compile(r"""^.*\bextra\s*==.+$""")


class PipDialog(CommonDialog, ABC):
    def __init__(self, master):
        self._state = "idle"  # possible values: "listing", "fetching", "idle"
        self._process = None
        self._closed = False
        self._active_distributions = {}
        self.current_package_data = None

        super().__init__(master)

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=self.get_medium_padding())
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.title(self._get_title())

        self._create_widgets(main_frame)

        self.search_box.focus_set()

        self.bind("<Escape>", self._on_close, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._show_instructions()

        self._start_update_list()

    def get_search_button_text(self):
        return tr("Search on PyPI")

    def get_install_button_text(self):
        return tr("Install")

    def get_upgrade_button_text(self):
        return tr("Upgrade")

    def get_uninstall_button_text(self):
        return tr("Uninstall")

    def _create_widgets(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=self.get_medium_padding(),
            pady=(self.get_medium_padding(), 0),
        )
        header_frame.columnconfigure(0, weight=1)
        header_frame.rowconfigure(1, weight=1)

        default_font = tk_font.nametofont("TkDefaultFont")
        name_font = default_font.copy()
        name_font.configure(size=default_font["size"] * 2)
        self.search_box = ttk.Entry(header_frame)
        self.search_box.grid(row=1, column=0, sticky="nsew")
        self.search_box.bind("<Return>", self._on_search, False)
        self.search_box.bind("<KP_Enter>", self._on_search, False)

        # Selecting chars in the search box with mouse didn't make the box active on Linux without following line
        self.search_box.bind("<B1-Motion>", lambda _: self.search_box.focus_set())

        self.search_button = ttk.Button(
            header_frame,
            text=self.get_search_button_text(),
            command=self._on_search,
            width=len(self.get_search_button_text()) + 2,
        )
        self.search_button.grid(row=1, column=1, sticky="nse", padx=(self.get_small_padding(), 0))

        main_pw = tk.PanedWindow(
            parent,
            orient=tk.HORIZONTAL,
            background=lookup_style_option("TPanedWindow", "background"),
            sashwidth=self.get_large_padding(),
        )
        main_pw.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=self.get_medium_padding(),
            pady=(self.get_medium_padding(), self.get_medium_padding()),
        )
        parent.rowconfigure(2, weight=1)
        parent.columnconfigure(0, weight=1)

        listframe = ttk.Frame(main_pw, relief="flat", borderwidth=1)
        listframe.rowconfigure(0, weight=1)
        listframe.columnconfigure(0, weight=1)

        self.listbox = ui_utils.ThemedListbox(
            listframe,
            activestyle="dotbox",
            width=20,
            height=23,
            selectborderwidth=0,
            relief="flat",
            # highlightthickness=4,
            # highlightbackground="red",
            # highlightcolor="green",
            borderwidth=0,
        )
        self.listbox.insert("end", " <" + tr("INSTALL") + ">")
        self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select, True)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        list_scrollbar = AutoScrollbar(listframe, orient=tk.VERTICAL)
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        list_scrollbar["command"] = self.listbox.yview
        self.listbox["yscrollcommand"] = list_scrollbar.set

        info_frame = ttk.Frame(main_pw)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)

        main_pw.add(listframe)
        main_pw.add(info_frame)

        self.title_label = ttk.Label(info_frame, text="", font=name_font)
        self.title_label.grid(
            row=0, column=0, sticky="w", padx=0, pady=(0, self.get_large_padding())
        )

        info_text_frame = tktextext.TextFrame(
            info_frame,
            read_only=True,
            horizontal_scrollbar=False,
            background=lookup_style_option("TFrame", "background"),
            vertical_scrollbar_class=AutoScrollbar,
            padx=ems_to_pixels(0.1),
            pady=0,
            width=70,
            height=10,
        )
        info_text_frame.configure(borderwidth=0)
        info_text_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 10))
        self.info_text = info_text_frame.text
        link_color = lookup_style_option("Url.TLabel", "foreground", "red")
        self.info_text.tag_configure("url", foreground=link_color, underline=True)
        self.info_text.tag_bind("url", "<ButtonRelease-1>", self._handle_url_click)
        self.info_text.tag_bind(
            "url", "<Enter>", lambda e: self.info_text.config(cursor=get_hyperlink_cursor())
        )
        self.info_text.tag_bind("url", "<Leave>", lambda e: self.info_text.config(cursor=""))
        self.info_text.tag_configure("install_reqs", foreground=link_color, underline=True)
        self.info_text.tag_bind(
            "install_reqs", "<ButtonRelease-1>", self._handle_install_requirements_click
        )
        self.info_text.tag_bind(
            "install_reqs",
            "<Enter>",
            lambda e: self.info_text.config(cursor=get_hyperlink_cursor()),
        )
        self.info_text.tag_bind(
            "install_reqs", "<Leave>", lambda e: self.info_text.config(cursor="")
        )
        self.info_text.tag_configure("install_file", foreground=link_color, underline=True)
        self.info_text.tag_bind(
            "install_file", "<ButtonRelease-1>", self._handle_install_file_click
        )
        self.info_text.tag_bind(
            "install_file",
            "<Enter>",
            lambda e: self.info_text.config(cursor=get_hyperlink_cursor()),
        )
        self.info_text.tag_bind(
            "install_file", "<Leave>", lambda e: self.info_text.config(cursor="")
        )

        self.info_text.configure(font=default_font, wrap="word")

        bold_font = default_font.copy()
        # need to explicitly copy size, because Tk 8.6 on certain Ubuntus use bigger font in copies
        bold_font.configure(weight="bold", size=default_font.cget("size"))
        self.info_text.tag_configure("caption", font=bold_font)
        self.info_text.tag_configure("bold", font=bold_font)
        self.info_text.tag_configure("right", justify="right")

        self.command_frame = ttk.Frame(info_frame)
        self.command_frame.grid(row=2, column=0, sticky="w")

        self.install_button = ttk.Button(
            self.command_frame,
            text=" " + self.get_upgrade_button_text() + " ",
            command=self._on_install_click,
            width=20,
        )

        self.install_button.grid(row=0, column=0, sticky="w", padx=0)

        self.uninstall_button = ttk.Button(
            self.command_frame,
            text=self.get_uninstall_button_text(),
            command=self._on_uninstall_click,
            width=20,
        )

        self.uninstall_button.grid(row=0, column=1, sticky="w", padx=(self.get_small_padding(), 0))

        self.advanced_button = ttk.Button(
            self.command_frame,
            text="...",
            width=3,
            command=lambda: self._perform_pip_action("advanced"),
        )

        self.advanced_button.grid(row=0, column=2, sticky="w", padx=(self.get_small_padding(), 0))

        self.close_button = ttk.Button(info_frame, text=tr("Close"), command=self._on_close)
        self.close_button.grid(row=2, column=3, sticky="e")

    def _set_state(self, state, force_normal_cursor=False):
        self._state = state
        action_buttons = [
            self.install_button,
            self.advanced_button,
            self.uninstall_button,
        ]

        other_widgets = [
            self.listbox,
            # self.search_box, # looks funny when disabled
            self.search_button,
        ]

        if state == "idle" and not self._is_read_only():
            for widget in action_buttons:
                widget["state"] = tk.NORMAL
        else:
            for widget in action_buttons:
                widget["state"] = tk.DISABLED

        if state == "idle":
            for widget in other_widgets:
                widget["state"] = tk.NORMAL
        else:
            self.config(cursor=get_busy_cursor())
            for widget in other_widgets:
                widget["state"] = tk.DISABLED

        if state == "idle" or force_normal_cursor:
            self.config(cursor="")
        else:
            self.config(cursor=get_busy_cursor())

    def _get_state(self):
        return self._state

    def _start_update_list(self, name_to_show=None):
        raise NotImplementedError()

    def _update_list(self, name_to_show):
        self.listbox.delete(1, "end")
        for name in sorted(self._active_distributions.keys()):
            self.listbox.insert("end", " " + name)

        if name_to_show is None or name_to_show not in self._active_distributions.keys():
            self._show_instructions()
        else:
            self._on_listbox_select_package(name_to_show)

    def _on_listbox_select(self, event):
        self.listbox.focus_set()
        selection = self.listbox.curselection()
        if len(selection) == 1:
            self.listbox.activate(selection[0])
            if selection[0] == 0:  # special first item
                self._show_instructions()
            else:
                self._on_listbox_select_package(self.listbox.get(selection[0]).strip())

    def _on_listbox_select_package(self, name):
        self._start_show_package_info(name)

    def _on_search(self, event=None):
        if self._get_state() != "idle":
            # Search box is not made inactive for busy-states
            return

        if self.search_box.get().strip() == "":
            return

        self._start_search(self.search_box.get().strip())

    def _on_install_click(self):
        self._perform_pip_action("install")

    def _on_uninstall_click(self):
        self._perform_pip_action("uninstall")

    def _clear(self):
        self.current_package_data = None
        self.title_label.grid_remove()
        self.command_frame.grid_remove()
        self._clear_info_text()

    def _clear_info_text(self):
        self.info_text.direct_delete("1.0", "end")

    def _append_info_text(self, text, tags=()):
        self.info_text.direct_insert("end", text, tags)

    def _show_instructions(self):
        self._clear()
        if self._is_read_only():
            self._show_read_only_instructions()
        else:
            self._show_instructions_about_installing_from_pypi()
            if self._installer_runs_locally():
                self._show_instructions_about_installing_from_requirements_file()
                self._show_instructions_about_installing_from_local_file()
            self._show_instructions_about_existing_packages()

            if self._get_target_directory():
                self._show_instructions_about_target()

            self._show_extra_instructions()

        self._select_list_item(0)

    def _show_extra_instructions(self):
        pass

    def _show_read_only_instructions(self):
        pass

    def _show_instructions_about_installing_from_pypi(self):
        self._append_info_text(tr("Install from PyPI") + "\n", ("caption",))
        self.info_text.direct_insert(
            "end",
            tr(
                "If you don't know where to get the package from, "
                + "then most likely you'll want to search the Python Package Index. "
                + "Start by entering the name of the package in the search box above and pressing ENTER."
            )
            + "\n\n",
        )

    def _show_instructions_about_installing_from_requirements_file(self):
        self.info_text.direct_insert(
            "end", tr("Install from requirements file") + "\n", ("caption",)
        )
        self._append_info_text(tr("Click" + " "))
        self._append_info_text(tr("here"), ("install_reqs",))
        self.info_text.direct_insert(
            "end",
            " "
            + tr("to locate requirements.txt file and install the packages specified in it.")
            + "\n\n",
        )

    def _show_instructions_about_installing_from_local_file(self):
        self._append_info_text(tr("Install from local file") + "\n", ("caption",))
        self._append_info_text(tr("Click") + " ")
        self._append_info_text(tr("here"), ("install_file",))
        self.info_text.direct_insert(
            "end",
            " "
            + tr(
                "to locate and install the package file (usually with .whl, .tar.gz or .zip extension)."
            )
            + "\n\n",
        )

    def _show_instructions_about_existing_packages(self):
        self._append_info_text(tr("Upgrade or uninstall") + "\n", ("caption",))
        self.info_text.direct_insert(
            "end", tr("Start by selecting the package from the left.") + "\n\n"
        )

    def _show_instructions_about_target(self):
        self._append_info_text(tr("Target") + "\n", ("caption",))
        self._append_location_to_info_path(self._get_target_directory())

    def _download_package_info(self, name: str, version_str: Optional[str]) -> Dict:
        return get_package_info_from_pypi(name, version_str)

    def _start_show_package_info(self, name):
        self.current_package_data = None
        # Fetch info from PyPI
        self._set_state("fetching")

        self._clear_info_text()
        self.title_label["text"] = ""
        self.title_label.grid()
        self.command_frame.grid()
        self.uninstall_button["text"] = self.get_uninstall_button_text()

        active_dist = self._get_active_dist(name)
        if active_dist is not None:
            self.title_label["text"] = active_dist.project_name
            self._append_info_text(tr("Installed version:") + " ", ("caption",))
            self._append_info_text(active_dist.version + "\n")
            self._append_info_text(tr("Installed to:") + " ", ("caption",))
            self._append_location_to_info_path(active_dist.location)
            self._append_info_text("\n\n")
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
                self.install_button["text"] = self.get_upgrade_button_text()
                self.install_button["state"] = "disabled"
                self.uninstall_button.grid(row=0, column=1)
            else:
                # new package
                self.install_button["text"] = self.get_install_button_text()
                self.uninstall_button.grid_remove()

        # start download and polling
        from concurrent.futures.thread import ThreadPoolExecutor

        executor = ThreadPoolExecutor(max_workers=1)
        download_future = executor.submit(self._download_package_info, name, None)

        def poll_fetch_complete():
            if download_future.done():
                try:
                    data = download_future.result()
                    if "info" in data and "name" not in data["info"]:
                        # this is the case of micropython.org/pi
                        data["info"]["name"] = name
                    self._show_package_info(name, data)
                except urllib.error.HTTPError as e:
                    self._show_package_info(
                        name, {"info": {"name": name}, "error": str(e), "releases": {}}, e.code
                    )
                except Exception as e:
                    self._show_package_info(
                        name, {"info": {"name": name}, "error": str(e), "releases": {}}, e
                    )
            else:
                get_workbench().after(200, poll_fetch_complete)

        poll_fetch_complete()

    @abstractmethod
    def _append_location_to_info_path(self, path):
        raise NotImplementedError()

    def _show_package_info(self, name, data, error_code=None):
        self._set_state("idle")

        self.current_package_data = data

        def write(s, tag=None):
            if tag is None:
                tags = ()
            else:
                tags = (tag,)
            self._append_info_text(s, tags)

        def write_att(caption, value, value_tag=None):
            write(caption + ": ", "caption")
            write(value, value_tag)
            write("\n")

        if error_code is not None:
            if error_code == 404:
                write(tr("Could not find the package from PyPI."))
                if not self._get_active_version(name):
                    # new package
                    write("\n" + tr("Please check your spelling!"))

            else:
                write(
                    tr("Could not find the package info from PyPI.")
                    + " "
                    + tr("Error code:")
                    + " "
                    + str(error_code)
                )
                logger.exception("Coult not fetch package info for %r", name)

            return

        info = data["info"]
        # NB! Json from micropython.org index doesn't have all the same fields as PyPI!
        self.title_label["text"] = info["name"]  # search name could have been a bit different
        latest_stable_version = _get_latest_stable_version(data["releases"].keys())
        if latest_stable_version is not None:
            write_att(tr("Latest stable version"), latest_stable_version)
        else:
            write_att(tr("Latest version"), info["version"])
        if "summary" in info:
            write_att(tr("Summary"), info["summary"])
        if "author" in info:
            write_att(tr("Author"), info["author"])
        if "license" in info:
            write_att(tr("License"), info["license"])
        if "home_page" in info:
            write_att(tr("Homepage"), info["home_page"], "url")
        if info.get("bugtrack_url", None):
            write_att(tr("Bugtracker"), info["bugtrack_url"], "url")
        if info.get("docs_url", None):
            write_att(tr("Documentation"), info["docs_url"], "url")
        if info.get("package_url", None):
            write_att(tr("PyPI page"), info["package_url"], "url")
        if info.get("requires_dist", None):
            # Available only when release is created by a binary wheel
            # https://github.com/pypa/pypi-legacy/issues/622#issuecomment-305829257
            requires_dist = info["requires_dist"]
            assert isinstance(requires_dist, list)
            assert all(isinstance(item, str) for item in requires_dist)

            # See https://www.python.org/dev/peps/pep-0345/#environment-markers.
            # This will filter only the most obvious dependencies marked simply with
            # ``extras == *``.
            # The other, more complex markings, are accepted as they are also
            # more informative (*e.g.*, the desired platform).
            remaining_requires_dist = []  # type: List[str]

            for item in requires_dist:
                if ";" not in item:
                    remaining_requires_dist.append(item)
                    continue

                _, marker_text = item.split(";", 1)

                # Check if the environment marker matches ``extra == '*'.
                #
                # This is easier implemented with ``packaging.markers``, but we want to
                # avoid introducing a new dependency as Thonny is included in
                # distributions which might lack a package for it.
                #
                # Please see
                # https://packaging.pypa.io/en/latest/_modules/packaging/markers.html#Marker
                # for the parsing rules.

                # Match extra == quoted string
                is_extra = _EXTRA_MARKER_RE.match(marker_text) is not None

                if is_extra:
                    continue

                remaining_requires_dist.append(item)

            write_att(tr("Requires"), ", ".join(remaining_requires_dist))

        if self._get_active_version(name) != latest_stable_version or not self._get_active_version(
            name
        ):
            self.install_button["state"] = "normal"
        else:
            self.install_button["state"] = "disabled"

    def _is_read_only_package(self, name):
        dist = self._get_active_dist(name)
        if dist is None:
            return False
        else:
            return self._normalize_target_path(dist.location) != self._get_target_directory()

    @abstractmethod
    def _normalize_target_path(self, path: str) -> str:
        raise NotImplementedError()

    def _start_search(self, query, discard_selection=True):
        self.current_package_data = None
        # Fetch info from PyPI
        self._set_state("fetching")
        self._clear()
        self.title_label.grid()
        self.title_label["text"] = tr("Search results")
        self.info_text.direct_insert("1.0", tr("Searching") + " ...")
        if discard_selection:
            self._select_list_item(0)

        from concurrent.futures.thread import ThreadPoolExecutor

        executor = ThreadPoolExecutor(max_workers=1)
        results_future = executor.submit(self._fetch_search_results, query)

        def poll_fetch_complete():
            if results_future.done():
                try:
                    results = results_future.result()
                except OSError as e:
                    self._show_search_results(query, str(e))
                else:
                    self._show_search_results(query, results)

            else:
                get_workbench().after(200, poll_fetch_complete)

        poll_fetch_complete()

    def _show_search_results(self, query, results: Union[List[Dict], str]) -> None:
        self._set_state("idle")
        self._clear_info_text()

        if isinstance(results, str) or not results:
            if not results:
                self._append_info_text("No results.\n\n")
            else:
                self._append_info_text("Could not fetch search results:\n")
                self._append_info_text(results + "\n\n")

            self._append_info_text("Try opening the package directly:\n")
            self._append_info_text(query, ("url",))
            return

        for item in results:
            # self._append_info_text("•")
            tags = ("url",)
            if item["name"].lower() == query.lower():
                tags = tags + ("bold",)

            self._append_info_text(item["name"], tags)
            if item.get("source"):
                self._append_info_text(" @ " + item["source"])
            self._append_info_text("\n")
            self.info_text.direct_insert(
                "end", (item.get("description") or "<No description>").strip() + "\n"
            )
            self._append_info_text("\n")

    def _select_list_item(self, name_or_index):
        if isinstance(name_or_index, int):
            index = name_or_index
        else:
            normalized_items = list(map(normalize_package_name, self.listbox.get(0, "end")))
            try:
                index = normalized_items.index(normalize_package_name(name_or_index))
            except Exception:
                exception(tr("Can't find package name from the list:") + " " + name_or_index)
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

    def _perform_pip_action(self, action: str) -> None:
        if self._perform_pip_action_without_refresh(action):
            if action == "uninstall":
                self._show_instructions()  # Make the old package go away as fast as possible
            self._start_update_list(
                None if action == "uninstall" else self.current_package_data["info"]["name"]
            )

            if self._has_remote_target():
                get_workbench().event_generate("RemoteFilesChanged")

    def _perform_pip_action_without_refresh(self, action: str) -> bool:
        """Returns whether the action was at least started and some packages might have been
        modified.
        """
        assert self._get_state() == "idle"
        assert self.current_package_data is not None
        data = self.current_package_data
        name = self.current_package_data["info"]["name"]

        install_args = ["--progress-bar", "off"]

        if action == "install":
            command = "install"
            title = tr("Installing '%s'") % name
            if not self._confirm_install(self.current_package_data):
                return False

            args = install_args
            if self._get_active_version(name) is not None:
                title = tr("Upgrading '%s'") % name
                args.append("--upgrade")

            args.append(name)

        elif action == "uninstall":
            command = "uninstall"
            title = tr("Uninstalling '%s'") % name
            if name in ["pip", "setuptools"] and not messagebox.askyesno(
                tr("Really uninstall?"),
                tr(
                    "Package '{}' is required for installing and uninstalling other packages."
                ).format(name)
                + "\n\n"
                + tr("Are you sure you want to uninstall it?"),
                master=self,
            ):
                return False
            args = ["--yes", name]
        elif action == "advanced":
            raise NotImplementedError()
        else:
            raise RuntimeError("Unknown action")

        self._run_pip_with_dialog(command, args, title=title)
        return True

    def _handle_install_file_click(self, event):
        if self._get_state() != "idle":
            return

        filename = askopenfilename(
            master=self,
            filetypes=[(tr("Package"), ".whl .zip .gz"), (tr("all files"), ".*")],
            initialdir=get_workbench().get_local_cwd(),
            parent=self.winfo_toplevel(),
        )
        if filename:  # Note that missing filename may be "" or () depending on tkinter version
            self._install_file(filename, False)

    def _handle_install_requirements_click(self, event):
        if self._get_state() != "idle":
            return

        filename = askopenfilename(
            master=self,
            filetypes=[("requirements", ".txt"), (tr("all files"), ".*")],
            initialdir=get_workbench().get_local_cwd(),
            parent=self.winfo_toplevel(),
        )
        if filename:  # Note that missing filename may be "" or () depending on tkinter version
            self._install_file(filename, True)

    def _handle_target_directory_click(self, event):
        if self._get_target_directory():
            open_path_in_system_file_manager(self._get_target_directory())

    def _install_file(self, filename, is_requirements_file):
        args = self._get_install_file_args(filename, is_requirements_file)

        returncode, out, err = self._run_pip_with_dialog(
            command="install", args=args, title=tr("Installing '%s'") % os.path.basename(filename)
        )

        # Try to find out the name of the package we're installing
        name = None

        # output should include a line like this:
        # Installing collected packages: pytz, six, python-dateutil, numpy, pandas
        inst_lines = re.findall(
            "^Installing collected packages:.*?$", out, re.MULTILINE | re.IGNORECASE
        )  # @UndefinedVariable
        if len(inst_lines) == 1:
            # take last element
            elements = re.split("[,:]", inst_lines[0])
            name = elements[-1].strip()

        self._start_update_list(name)

    def _get_install_file_args(self, filename, is_requirements_file):
        args = []
        if is_requirements_file:
            args.append("-r")
        args.append(filename)

        return args

    def _handle_url_click(self, event):
        url = _extract_click_text(self.info_text, event, "url")
        if url is not None:
            if url.startswith("http:") or url.startswith("https:"):
                import webbrowser

                webbrowser.open(url)
            elif os.path.sep in url:
                os.makedirs(url, exist_ok=True)
                open_path_in_system_file_manager(url)
            else:
                self._start_show_package_info(url)

    def _on_close(self, event=None):
        self._closed = True
        self.destroy()

    def _get_active_version(self, name):
        dist = self._get_active_dist(name)
        if dist is None:
            return None
        else:
            return dist.version

    def _get_active_dist(self, name):
        normname = normalize_package_name(name)
        for key in self._active_distributions:
            if normalize_package_name(key) == normname:
                return self._active_distributions[key]

        return None

    def _run_pip_with_dialog(
        self, command: str, args: List[str], title: str
    ) -> Tuple[int, str, str]:
        raise NotImplementedError()

    def _get_interpreter_description(self):
        raise NotImplementedError()

    def _has_remote_target(self):
        raise NotImplementedError()

    def _installer_runs_locally(self):
        raise NotImplementedError()

    def _get_target_directory(self):
        raise NotImplementedError()

    def _get_title(self):
        return tr("Manage packages for %s") % self._get_interpreter_description()

    def _confirm_install(self, package_data):
        return True

    def _is_read_only(self):
        return self._get_target_directory() is None

    @abstractmethod
    def _fetch_search_results(self, query: str) -> List[Dict[str, str]]: ...

    def _advertise_pipkin(self):
        self._append_info_text("\n\n")
        self._append_info_text("Under the hood " + "\n", ("caption", "right"))
        self._append_info_text(
            "This dialog uses `pipkin`, a new command line tool for managing "
            "MicroPython and CircuitPython packages. ",
            ("right",),
        )
        self._append_info_text("See ", ("right",))
        self._append_info_text("https://pypi.org/project/pipkin/", ("url", "right"))
        self._append_info_text(" for more info. \n", ("right",))


class BackendPipDialog(PipDialog):
    def __init__(self, master):
        self._backend_proxy = get_runner().get_backend_proxy()
        super().__init__(master)

        self._last_name_to_show = None

    def _has_remote_target(self):
        return get_runner().get_backend_proxy().supports_remote_files()

    def _start_update_list(self, name_to_show=None):
        assert self._get_state() in [None, "idle"]
        self._set_state("listing")

        get_workbench().bind("get_active_distributions_response", self._complete_update_list, True)
        self._last_name_to_show = name_to_show
        logger.debug("Sending get_active_distributions")
        get_runner().send_command(InlineCommand("get_active_distributions"))

    def _complete_update_list(self, msg):
        if self._closed:
            return

        get_workbench().unbind("get_active_distributions_response", self._complete_update_list)
        if "error" in msg:
            self._clear_info_text()
            self.info_text.direct_insert("1.0", msg["error"])
            self._set_state("idle", True)
            return

        self._active_distributions = msg.distributions
        self._set_state("idle", True)
        self._update_list(self._last_name_to_show)

    def _confirm_install(self, package_data):
        for question in self._backend_proxy.get_package_installation_confirmations(package_data):
            if not messagebox.askyesno(
                tr("Confirmation"),
                question,
                master=self,
            ):
                return False
        return True

    def _run_pip_with_dialog(
        self, command: str, args: List[str], title: str
    ) -> Tuple[int, str, str]:
        if command == "install":
            back_cmd = InlineCommand("install_distributions", args=args)
        elif command == "uninstall":
            back_cmd = InlineCommand("uninstall_distributions", args=args)
        else:
            raise AssertionError(f"Unexpected command {command}")

        dlg = InlineCommandDialog(
            self,
            back_cmd,
            title=command,
            instructions=title,
            autostart=True,
            output_prelude=f"{command} {construct_cmd_line(args)}\n",
        )
        ui_utils.show_dialog(dlg)

        return dlg.returncode, dlg.stdout, dlg.stderr

    def _get_interpreter_description(self):
        return self._backend_proxy.get_full_label()

    def _installer_runs_locally(self):
        return self._backend_proxy.can_install_packages_from_files()

    def _get_target_directory(self):
        return self._backend_proxy.get_packages_target_dir_with_comment()[0]

    def _normalize_target_path(self, path: str) -> str:
        return self._backend_proxy.normalize_target_path(path)

    def _append_location_to_info_path(self, path):
        if self._backend_proxy.uses_local_filesystem():
            tags = ("url",)
        else:
            tags = ()
        self.info_text.direct_insert("end", self._normalize_target_path(path), tags)

    def _show_extra_instructions(self):
        from thonny.plugins.micropython.mp_front import MicroPythonProxy

        if isinstance(self._backend_proxy, MicroPythonProxy):
            self._advertise_pipkin()

    def _show_read_only_instructions(self):
        path, comment = self._backend_proxy.get_packages_target_dir_with_comment()
        assert path is None

        self._append_info_text(tr("Installation is not possible") + "\n", ("caption",))
        self.info_text.direct_insert(
            "end",
            comment + "\n\n",
        )

    def _fetch_search_results(self, query: str) -> List[Dict[str, str]]:
        return self._backend_proxy.search_packages(query)

    def _download_package_info(self, name: str, version_str: Optional[str]) -> Dict:
        return self._backend_proxy.get_package_info_from_index(name, version_str)

    def get_search_button_text(self):
        return self._backend_proxy.get_search_button_text()


class PluginsPipDialog(PipDialog):
    def __init__(self, master):
        PipDialog.__init__(self, master)

        # make sure directory exists, so user can put her plug-ins there
        d = self._get_target_directory()
        makedirs(d, exist_ok=True)

    def _has_remote_target(self):
        return False

    def _installer_runs_locally(self):
        return True

    def _start_update_list(self, name_to_show=None):
        assert self._get_state() in [None, "idle"]
        import pkg_resources

        pkg_resources._initialize_master_working_set()

        self._active_distributions = {
            dist.key: DistInfo(
                project_name=dist.project_name,
                key=dist.key,
                location=dist.location,
                version=dist.version,
            )
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
            logger.exception("Problem computing conflicts")
            return None

    def _get_interpreter_description(self):
        return get_front_interpreter_for_subprocess(sys.executable)

    def _confirm_install(self, package_data):
        if not self._looks_like_plug_in(package_data) and not messagebox.askyesno(
            tr("Confirmation"),
            tr(
                "This doesn't look like Thonny plug-in.\n\n"
                "If you want to install it for your programs, then use\n"
                "'Tools => Manage packages' instead.\n\n"
                "Are you sure you want to install it as Thonny plug-in?"
            ),
            master=self,
        ):
            return False

        name = package_data["info"]["name"]
        reqs = package_data["info"].get("requires_dist", None)

        other_version_text = tr(
            "NB! There may be another version available "
            + "which is compatible with current Thonny version. "
            + "Click on '...' button to choose the version to install."
        )

        if name.lower().startswith("thonny-") and not reqs:
            showerror(
                tr("Thonny plugin without requirements"),
                (
                    "Looks like you are trying to install an outdated Thonny\n"
                    + "plug-in (it doesn't specify required Thonny version\n"
                    + "or hasn't uploaded a whl file before other files).\n\n"
                    + "If you still want it, then please install it from the command line."
                )
                + "\n\n"
                + other_version_text,
                master=self,
            )
            return False
        elif reqs:
            conflicts = self._conflicts_with_thonny_version(reqs)
            if conflicts:
                showerror(
                    tr("Unsuitable requirements"),
                    tr("This package requires different Thonny version:")
                    + "\n\n  "
                    + "\n  ".join(conflicts)
                    + "\n\n"
                    + tr("If you still want it, then please install it from the command line.")
                    + "\n\n"
                    + other_version_text,
                    master=self,
                )
                return False

        return True

    def _looks_like_plug_in(self, package_data):
        name = package_data["name"].lower()
        if "thonny" in name:
            return True
        if name in ["birdseye"]:
            return True

        return False

    def _get_target_directory(self):
        if running_in_virtual_environment():
            for d in sys.path:
                if ("site-packages" in d or "dist-packages" in d) and path_startswith(
                    d, sys.prefix
                ):
                    return normpath_with_actual_case(d)
            return None
        else:
            target = thonny.get_sys_path_directory_containg_plugins()
            os.makedirs(target, exist_ok=True)
            return normpath_with_actual_case(target)

    def _normalize_target_path(self, path: str) -> str:
        return normpath_with_actual_case(path)

    def _create_widgets(self, parent):
        banner = ttk.Frame(parent, style="Tip.TFrame")
        banner.grid(row=0, column=0, sticky="nsew")

        banner_msg = (
            tr(
                "This dialog is for managing Thonny plug-ins and their dependencies.\n"
                + "If you want to install packages for your own programs then choose 'Tools → Manage packages...'"
            )
            + "\n"
        )

        banner_msg += "\n" + tr(
            "NB! You need to restart Thonny after installing / upgrading / uninstalling a plug-in."
        )

        banner_text = ttk.Label(banner, text=banner_msg, style="Tip.TLabel", justify="left")
        banner_text.grid(pady=self.get_medium_padding(), padx=self.get_medium_padding())

        PipDialog._create_widgets(self, parent)

    def _get_title(self):
        return tr("Thonny plug-ins")

    def _run_pip_with_dialog(self, command: str, args: Dict, title: str) -> Tuple[int, str, str]:
        cmd = ["-m", "pip", "--disable-pip-version-check", "--no-color", command]
        if command == "install":
            cmd += [
                "--no-warn-script-location",
            ]
        cmd += args

        proc = running.create_frontend_python_process(
            cmd,
            stderr=subprocess.STDOUT,
            environment_extras={"PYTHONUSERBASE": thonny.get_user_base_directory_for_plugins()},
        )
        dlg = SubprocessDialog(
            self, proc, title="pip " + command, long_description=title, autostart=True
        )
        ui_utils.show_dialog(dlg)
        return dlg.returncode, dlg.stdout, dlg.stderr

    def _append_location_to_info_path(self, path):
        self.info_text.direct_insert("end", self._normalize_target_path(path), ("url",))

    def _fetch_search_results(self, query: str) -> List[Dict[str, str]]:
        return perform_pypi_search(query)


def _fetch_url_future(url, fallback_url=None, timeout=10):
    from urllib.request import urlopen

    def load_url():
        try:
            with urlopen(url, timeout=timeout) as conn:
                return (conn, conn.read())
        except urllib.error.HTTPError as e:
            if e.code == 404 and fallback_url is not None:
                with urlopen(fallback_url, timeout=timeout) as conn:
                    return (conn, conn.read())
            else:
                raise

    from concurrent.futures.thread import ThreadPoolExecutor

    executor = ThreadPoolExecutor(max_workers=1)
    return executor.submit(load_url)


def _get_latest_stable_version(version_strings):
    from distutils.version import LooseVersion

    versions = []
    for s in version_strings:
        if s.replace(".", "").isnumeric():  # Assuming stable versions have only dots and numbers
            versions.append(
                LooseVersion(s)
            )  # LooseVersion __str__ doesn't change the version string

    if len(versions) == 0:
        return None

    return str(sorted(versions)[-1])


def normalize_package_name(name):
    # looks like (in some cases?) pip list gives the name as it was used during install
    # ie. the list may contain lowercase entry, when actual metadata has uppercase name
    # Example: when you "pip install cx-freeze", then "pip list"
    # really returns "cx-freeze" although correct name is "cx_Freeze"

    # https://www.python.org/dev/peps/pep-0503/#id4
    return re.sub(r"[-_.]+", "-", name).lower().strip()


def perform_pypi_search(query: str, source: Optional[str] = None) -> List[Dict[str, str]]:
    import urllib.parse
    from urllib.request import urlopen

    logger.info("Performing PyPI search for %r", query)

    url = "https://pypi.org/search/?q={}".format(urllib.parse.quote(query))
    with urlopen(url, timeout=10) as fp:
        data = fp.read()

    results = _extract_pypi_search_results(data.decode("utf-8"))

    for result in results:
        if source:
            result["source"] = source
        result["distance"] = levenshtein_distance(query, result["name"])

    logger.info("Got %r matches")
    return results


def get_package_info_from_pypi(name: str, version_str: Optional[str]) -> Dict:
    import json
    from urllib.request import urlopen

    if version_str is None:
        url = "https://pypi.org/pypi/{}/json".format(urllib.parse.quote(name))
    else:
        url = "https://pypi.org/pypi/{}/{}/json".format(
            urllib.parse.quote(name), urllib.parse.quote(version_str)
        )

    logger.info("Downloading package info from %s", url)
    with urlopen(url) as fp:
        return json.load(fp)


def _extract_pypi_search_results(html_data: str) -> List[Dict[str, str]]:
    from html.parser import HTMLParser

    def get_class(attrs):
        for name, value in attrs:
            if name == "class":
                return value

        return None

    class_prefix = "package-snippet__"

    class PypiSearchResultsParser(HTMLParser):
        def __init__(self, data):
            HTMLParser.__init__(self)
            self.results = []
            self.active_class = None
            self.feed(data)

        def handle_starttag(self, tag, attrs):
            if tag == "a" and get_class(attrs) == "package-snippet":
                self.results.append({})

            if tag in ("span", "p"):
                tag_class = get_class(attrs)
                if tag_class in ("package-snippet__name", "package-snippet__description"):
                    self.active_class = tag_class
                else:
                    self.active_class = None
            else:
                self.active_class = None

        def handle_data(self, data):
            if self.active_class is not None:
                att_name = self.active_class[len(class_prefix) :]
                self.results[-1][att_name] = data

        def handle_endtag(self, tag):
            self.active_class = None

    return PypiSearchResultsParser(html_data).results


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
        logger.exception("extracting click text")

    return None


def load_plugin() -> None:
    def open_backend_pip_gui(*args):
        if not get_runner().is_waiting_toplevel_command():
            showerror(
                tr("Not available"),
                tr("You need to stop your program before launching the package manager."),
                master=get_workbench(),
            )
            return

        pg = BackendPipDialog(get_workbench())
        ui_utils.show_dialog(pg)

    def open_plugins_pip_gui(*args):
        pg = PluginsPipDialog(get_workbench())
        ui_utils.show_dialog(pg)

    get_workbench().add_command(
        "backendpipgui",
        "tools",
        tr("Manage packages..."),
        open_backend_pip_gui,
        group=80,
    )
    get_workbench().add_command(
        "pluginspipgui", "tools", tr("Manage plug-ins..."), open_plugins_pip_gui, group=180
    )
