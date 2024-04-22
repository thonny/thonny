# -*- coding: utf-8 -*-
import math
import os
import re
import subprocess
import sys
import tkinter as tk
import tkinter.font as tk_font
import urllib.error
import urllib.parse
from abc import ABC, abstractmethod
from logging import getLogger
from os import makedirs
from tkinter import messagebox, ttk
from tkinter.messagebox import showerror, showwarning
from typing import Dict, List, Optional, Tuple, Union

from packaging.requirements import Requirement
from packaging.utils import NormalizedName, canonicalize_name, canonicalize_version

import thonny
from thonny import get_runner, get_workbench, running, tktextext, ui_utils
from thonny.common import (
    DistInfo,
    InlineCommand,
    export_distributions_info_from_dir,
    export_installed_distributions_info,
    normpath_with_actual_case,
    path_startswith,
    running_in_virtual_environment,
)
from thonny.languages import tr
from thonny.misc_utils import (
    construct_cmd_line,
    download_and_parse_json,
    download_bytes,
    get_menu_char,
)
from thonny.running import BackendProxy, InlineCommandDialog, get_front_interpreter_for_subprocess
from thonny.ui_utils import (
    AutoScrollbar,
    CommonDialog,
    CustomToolbutton,
    askopenfilename,
    create_custom_toolbutton_in_frame,
    ems_to_pixels,
    get_busy_cursor,
    get_hyperlink_cursor,
    lookup_style_option,
    open_path_in_system_file_manager,
)
from thonny.workdlg import SubprocessDialog

logger = getLogger(__name__)

_EXTRA_MARKER_RE = re.compile(r"""^.*\bextra\s*==.+$""")


class PipFrame(ttk.Frame, ABC):
    def __init__(self, master, **kw):
        self._state = "inactive"  # possible values: "inactive", "listing", "fetching", "idle"
        self._closed = False
        self._installed_dists: Optional[Dict[NormalizedName, DistInfo]] = None
        self._version_list_cache: Dict[NormalizedName, List[str]] = {}
        self._current_dist_info: Optional[DistInfo] = None
        self._version_button: Optional[CustomToolbutton] = None
        self._action_button: Optional[CustomToolbutton] = None
        self._last_search_results: Optional[Dict[NormalizedName, DistInfo]] = None

        super().__init__(master, **kw)

        self._create_widgets(self)
        self._update_summary()

    def check_load_initial_content(self):
        if self._installed_dists is None:
            self.load_content()

    def load_content(self):
        self._show_instructions()
        self._start_update_list()
        self.search_box.focus_set()

    def _create_widgets(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=self.get_small_padding(),
            pady=ems_to_pixels(0.5),
        )
        header_frame.columnconfigure(0, weight=1)
        header_frame.rowconfigure(1, weight=1)

        self.summary_label = ttk.Label(header_frame, text="")
        self.summary_label.grid(row=1, column=0, sticky="nsw")

        self.search_label = ttk.Label(header_frame, text=tr("Search PyPI") + ": ")
        self.search_label.grid(row=1, column=1, sticky="nsw")

        self.search_box = ttk.Entry(header_frame, width=15)
        self.search_box.grid(row=1, column=2, sticky="nse")
        self.search_box.bind("<Return>", self._on_search, False)
        self.search_box.bind("<KP_Enter>", self._on_search, False)

        # Selecting chars in the search box with mouse didn't make the box active on Linux without following line
        self.search_box.bind("<B1-Motion>", lambda _: self.search_box.focus_set())

        search_button_text = " 🔍"
        self.search_button = CustomToolbutton(
            header_frame,
            text=search_button_text,
            command=self._on_search,
            # width=len(search_button_text) + 2,
        )
        self.search_button.grid(row=1, column=3, sticky="nse", padx=(self.get_small_padding(), 0))

        self.menu_button = CustomToolbutton(
            header_frame,
            text=get_menu_char(),
            command=self._post_general_menu,
            width=1,
        )
        self.menu_button.grid(row=1, column=4, sticky="nse", padx=(self.get_large_padding(), 0))

        main_pw = tk.PanedWindow(
            parent,
            orient=tk.HORIZONTAL,
            background="white",  # lookup_style_option("TPanedWindow", "background"),
            sashwidth=self.get_large_padding(),
        )
        main_pw.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=self.get_pw_padding(),
            pady=(0, self.get_pw_padding()),
        )
        parent.rowconfigure(2, weight=1)
        parent.columnconfigure(0, weight=1)

        listframe = ttk.Frame(main_pw)
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
        self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select, True)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        list_scrollbar = AutoScrollbar(listframe, orient=tk.VERTICAL)
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        list_scrollbar["command"] = self.listbox.yview
        self.listbox["yscrollcommand"] = list_scrollbar.set

        info_text_frame = tktextext.TextFrame(
            main_pw,
            read_only=True,
            horizontal_scrollbar=False,
            # background=lookup_style_option("TFrame", "background"),
            vertical_scrollbar_class=AutoScrollbar,
            padx=ems_to_pixels(0.1),
            pady=0,
            width=70,
            height=5,
        )
        info_text_frame.configure(borderwidth=0)
        info_text_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
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

        default_font = tk_font.nametofont("TkDefaultFont")
        self.info_text.configure(font=default_font, wrap="word")

        title_font = default_font.copy()
        title_font.configure(size=math.ceil(default_font["size"] * 1.5))
        self.info_text.tag_configure(
            "title", font=title_font, spacing1=ems_to_pixels(1.3), spacing3=ems_to_pixels(1)
        )

        bold_font = default_font.copy()
        # need to explicitly copy size, because Tk 8.6 on certain Ubuntus use bigger font in copies
        bold_font.configure(weight="bold", size=default_font.cget("size"))
        self.info_text.tag_configure("caption", font=bold_font)
        self.info_text.tag_configure("bold", font=bold_font)
        self.info_text.tag_configure("right", justify="right")

        # self.info_text.tag_configure()

        main_pw.add(listframe)
        main_pw.add(info_text_frame)

        self._version_menu = tk.Menu(self.info_text, tearoff=False)

    def _post_general_menu(self):
        pass

    def _set_state(self, state, force_normal_cursor=False):
        self._state = state
        self._update_summary()
        # TODO:
        action_buttons = [
            # self.install_button,
            # self.advanced_button,
            # self.uninstall_button,
        ]

        other_widgets = [
            self.listbox,
            # self.search_box, # looks funny when disabled
            self.search_button,
        ]

        if state == "idle" and not self._is_read_only_env():
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

    def _update_summary(self):
        if self._get_state() == "inactive":
            text = ""
        elif self._get_state() == "listing":
            text = tr("Listing installed packages") + "..."
        else:
            text = tr("Installed packages: %d") % len(self._installed_dists)

        self.summary_label.configure(text=text)

    def _start_update_list(self, name_to_show=None):
        raise NotImplementedError()

    def _update_list(self, name_to_show):
        self.listbox.delete(0, "end")
        self.listbox.insert("end", " <" + tr("INSTALL") + ">")
        for name in sorted(self._installed_dists.keys()):
            self.listbox.insert("end", " " + name)

        if name_to_show is None or name_to_show not in self._installed_dists.keys():
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
        self._start_show_package_info(name, self._installed_dists[name].version)

    def _on_search(self, event=None):
        if self._get_state() != "idle":
            # Search box is not made inactive for busy-states
            return "break"

        if self.search_box.get().strip() == "":
            return "break"

        self._start_search(self.search_box.get().strip())
        return "break"

    def _on_install_click(self):
        if self._confirm_install(self._current_dist_info):
            self._install_current()
            self.load_content()

    def _on_uninstall_click(self):
        if self._confirm_uninstall(self._current_dist_info):
            self._uninstall_current()
            self.load_content()

    def _clear(self):
        self._current_dist_info = None
        self._clear_info_text()

    def _clear_info_text(self, start_index: str = "1.0"):
        self._version_button = None
        self._action_button = None
        self.info_text.direct_delete(start_index, "end")

    def _append_info_text(self, text, tags=()):
        self.info_text.direct_insert("end", text, tags)

    def _show_instructions(self):
        self._clear()
        if self._is_read_only_env():
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

    def _get_dist_info(self, name: str, version: str) -> DistInfo:
        installed_dist = self._installed_dists.get(canonicalize_name(name))
        if installed_dist is not None and canonicalize_version(
            installed_dist.version
        ) == canonicalize_version(version):
            return installed_dist

        return download_dist_info_from_pypi(name, version)

    def _get_version_list(self, name: str) -> List[str]:
        norm_name = canonicalize_name(name)
        if norm_name not in self._version_list_cache:
            self._version_list_cache[norm_name] = self._download_version_list(name)

        return self._version_list_cache[norm_name]

    def _download_dist_info(self, name: str, version: str) -> DistInfo:
        return download_dist_info_from_pypi(name, version)

    def _download_version_list(self, name: str) -> List[str]:
        return try_download_version_list_from_pypi(name)

    def _start_show_package_info(self, name, version):
        self._current_dist_info = None
        # Fetch info from PyPI
        self._set_state("fetching")

        self._clear_info_text()

        self._append_info_text(name, tags=("title",))
        self._append_info_text("   ")
        bordercolor = "#aaaaaa"  # TODO

        norm_installed_version = self._get_normalized_installed_version(name)
        norm_new_version = canonicalize_version(version)
        is_installed = norm_new_version == norm_installed_version

        if is_installed:
            version_text = version + " (" + tr("installed") + ")"
            action = self._on_uninstall_click
            action_text = tr("Uninstall")
        else:
            version_text = version
            action = self._on_install_click
            if norm_installed_version is None:
                action_text = tr("Install")
            elif norm_installed_version < norm_new_version:
                action_text = tr("Upgrade to this version")
            else:
                assert norm_installed_version > norm_new_version
                action_text = tr("Downgrade to this version")

        version_button_frame = create_custom_toolbutton_in_frame(
            #  ﹀⌄˅˯  ⌄⌃ ▾▴ ⏷⏶ ▼▲ ▽△ ▿▵  ⬧ ⟠ ↓↑  ˄˅
            self.info_text,
            text=f" {version_text}  ⏷ ",
            command=self._show_version_menu,
            state="disabled",
            background="white",
            borderwidth=1,
            bordercolor=bordercolor,
        )
        self._version_button = version_button_frame.button
        self.info_text.window_create("end", window=version_button_frame)

        if not self._is_read_only_env() and not self._is_read_only_dist(name, version):
            self._append_info_text("  ")
            action_button_frame = create_custom_toolbutton_in_frame(
                self.info_text,
                text=f" {action_text} ",
                command=action,
                state="disabled",
                borderwidth=1,
                bordercolor=bordercolor,
            )
            self._action_button = action_button_frame.button
            self.info_text.window_create("end", window=action_button_frame)

        self._append_info_text("\n")

        if is_installed:
            self._select_list_item(name)
        else:
            logger.info("Selecting '%s' over '%s'", norm_new_version, norm_installed_version)
            self._select_list_item(0)

        # start download and polling
        from concurrent.futures.thread import ThreadPoolExecutor

        executor = ThreadPoolExecutor(max_workers=1)
        dist_info_future = executor.submit(self._get_dist_info, name, version)
        version_list_future = executor.submit(self._get_version_list, name)

        def poll_fetch_complete():
            if dist_info_future.done() and version_list_future.done():
                try:
                    info = dist_info_future.result()
                    versions = version_list_future.result()
                except Exception as e:
                    logger.exception("Error downloading")
                    self._append_info_text(
                        "Could not download package info or list of versions: " + str(e)
                    )
                    self._set_state("idle")
                else:
                    self._complete_show_package_info(name, info, versions)
            else:
                get_workbench().after(200, poll_fetch_complete)

        poll_fetch_complete()

    def _complete_show_package_info(self, name, dist_info: DistInfo, version_list: List[str]):
        self._set_state("idle")
        assert self._version_button is not None
        self._version_button.configure(state="normal")

        if self._action_button is not None:
            self._action_button.configure(state="normal")

        # TODO: if is installed, then do a sanity check to make sure the dists are
        # really related, not simply sharing the name

        self._current_dist_info = dist_info

        def write_att(caption, value, value_tags=()):
            self._append_info_text(caption + ": ", "caption")
            self._append_info_text(value, tags=value_tags)
            self._append_info_text("\n")

        # NB! Json from micropython.org index doesn't have all the same fields as PyPI!
        if dist_info.summary:
            write_att(tr("Summary"), dist_info.summary)
        if dist_info.author:
            write_att(tr("Author"), dist_info.author)
        if dist_info.license:
            write_att(tr("License"), dist_info.license)
        if dist_info.home_page:
            write_att(tr("Homepage"), dist_info.home_page, ("url",))
        # if info.get("bugtrack_url", None):
        #    write_att(tr("Bugtracker"), info["bugtrack_url"], ("url",))
        # if info.get("docs_url", None):
        #    write_att(tr("Documentation"), info["docs_url"], ("url",))
        if dist_info.package_url:
            write_att(tr("PyPI page"), dist_info.package_url, ("url",))
        if dist_info.requires:
            # Available only when release is created by a binary wheel
            # https://github.com/pypa/pypi-legacy/issues/622#issuecomment-305829257
            assert isinstance(dist_info.requires, list)
            assert all(isinstance(item, str) for item in dist_info.requires)

            # See https://www.python.org/dev/peps/pep-0345/#environment-markers.
            # This will filter only the most obvious dependencies marked simply with
            # ``extras == *``.
            # The other, more complex markings, are accepted as they are also
            # more informative (*e.g.*, the desired platform).
            remaining_requires_dist = []  # type: List[str]

            for item in dist_info.requires:
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

    def _show_version_menu(self):
        self._version_menu.delete(0, "end")
        versions = self._get_version_list(self._current_dist_info.name)

        installed_version = self._get_normalized_installed_version(self._current_dist_info.name)
        variable = tk.StringVar(self, value=self._current_dist_info.version)
        installed_version_is_in_list = False

        for version in reversed(versions):
            if canonicalize_version(version) == installed_version:
                installed_version_is_in_list = True

            def show_version(name=self._current_dist_info.name, version=version):
                self._start_show_package_info(name, version)

            label = version
            if canonicalize_version(version) == installed_version:
                label += " (" + tr("Installed") + ")"

            self._version_menu.add_radiobutton(
                label=label,
                command=show_version,
                variable=variable,
                value=version,
            )

        if installed_version and not installed_version_is_in_list:
            showwarning(
                tr("Warning"),
                "Currently installed version not found in the package index\n"
                f"Make sure installed '{self._current_dist_info.name}' is related to "
                f"'{self._current_dist_info.name}' at the index",
                master=self.winfo_toplevel(),
            )

        post_x = self._version_button.winfo_rootx()
        post_y = self._version_button.winfo_rooty() + self._version_button.winfo_height()
        self._version_menu.tk_popup(post_x, post_y)

    @abstractmethod
    def _append_location_to_info_path(self, path):
        raise NotImplementedError()

    def _get_normalized_installed_version(self, name: str) -> Optional[str]:
        info = self._installed_dists.get(canonicalize_name(name))
        if info is None:
            return None
        return canonicalize_version(info.version)

    def _is_read_only_dist(self, name: str, version: str):
        info = self._installed_dists.get(canonicalize_name(name))
        if info is None or canonicalize_version(info.version) != canonicalize_version(version):
            return False

        return self._normalize_target_path(info.installed_location) != self._normalize_target_path(
            self._get_target_directory()
        )

    @abstractmethod
    def _normalize_target_path(self, path: str) -> str:
        raise NotImplementedError()

    def _start_search(self, query, discard_selection=True):
        self._current_dist_info = None
        # Fetch info from PyPI
        self._set_state("fetching")
        self._clear()
        self._append_info_text(tr("Search results") + "\n", tags=("title",))
        self._append_info_text(tr("Searching") + " ...")
        if discard_selection:
            self._select_list_item(0)

        from concurrent.futures.thread import ThreadPoolExecutor

        executor = ThreadPoolExecutor(max_workers=1)
        results_future = executor.submit(self._fetch_search_results, query)

        def poll_fetch_complete():
            if results_future.done():
                try:
                    results = results_future.result()
                except Exception as e:
                    logger.exception("Error when searching packages")
                    self._show_search_results(query, e)
                else:
                    self._show_search_results(query, results)

            else:
                get_workbench().after(200, poll_fetch_complete)

        poll_fetch_complete()

    def _show_search_results(self, query, results: Union[List[DistInfo], Exception]) -> None:
        self._set_state("idle")
        self._clear_info_text("2.0")  # also gets rid ot the newline in the end of the first line
        self._append_info_text("\n")

        if isinstance(results, Exception) or not results:
            if not results:
                self._append_info_text("No results.\n\n")
                return
            else:
                assert isinstance(results, Exception)
                self._append_info_text("Could not fetch search results:\n")
                self._append_info_text(str(results) + "\n\n")
                if isinstance(results, PyPiSearchErrorWithFallback):
                    self._append_info_text("There is an exact match, though:\n\n")
                    results = [results.fallback_result]
                else:
                    self._append_info_text("Try searching for exact package name.\n")
                    return

        assert isinstance(results, list)
        self._last_search_results = {canonicalize_name(r.name): r for r in results}
        for info in results:
            # self._append_info_text("•")
            tags = ("url",)
            if canonicalize_name(info.name) == canonicalize_name(query.lower()):
                tags = tags + ("bold",)

            self._append_info_text(info.name, tags)
            if info.source is not None and self._should_show_search_result_source():
                self._append_info_text(" @ " + info.source)
            self._append_info_text(" - ")
            self.info_text.direct_insert("end", (info.summary or "<No description>").strip() + "\n")
            # self._append_info_text("\n")

    @abstractmethod
    def _should_show_search_result_source(self):
        raise NotImplementedError()

    def _select_list_item(self, name_or_index):
        if isinstance(name_or_index, int):
            index = name_or_index
        else:
            normalized_items = [
                canonicalize_name(name.strip()) for name in self.listbox.get(0, "end")
            ]
            norm_name = canonicalize_name(name_or_index)
            try:
                index = normalized_items.index(norm_name)
            except ValueError:
                logger.exception(
                    "Can't find package name %r from the list %r", name_or_index, normalized_items
                )
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

    def _install_current(self):
        spec = self._current_dist_info.name + "==" + self._current_dist_info.version
        self._run_pip_with_dialog(
            command="install", args=[spec], title=tr("Installing '%s'") % spec
        )

    def _uninstall_current(self):
        spec = self._current_dist_info.name
        self._run_pip_with_dialog(
            command="uninstall", args=[spec], title=tr("Uninstalling '%s'") % spec
        )

    def _install_file(self, filename, is_requirements_file):
        args = []
        if is_requirements_file:
            args.append("-r")
        args.append(filename)

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
                assert self._last_search_results is not None
                dist_info = self._last_search_results[canonicalize_name(url)]
                self._start_show_package_info(dist_info.name, dist_info.version)

    def _get_active_version(self, name):
        dist = self._get_active_dist(name)
        if dist is None:
            return None
        else:
            return dist.version

    def _get_active_dist(self, name):
        normname = canonicalize_name(name)
        for key in self._installed_dists:
            if canonicalize_name(key) == normname:
                return self._installed_dists[key]

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

    def _confirm_install(self, package_data):
        return True

    def _confirm_uninstall(self, info: DistInfo):
        if info.name in ["pip", "setuptools"] and not messagebox.askyesno(
            tr("Really uninstall?"),
            tr("Package '{}' is required for installing and uninstalling other packages.").format(
                info.name
            )
            + "\n\n"
            + tr("Are you sure you want to uninstall it?"),
            master=self,
        ):
            return False

        return True

    def _is_read_only_env(self):
        return self._get_target_directory() is None

    @abstractmethod
    def _fetch_search_results(self, query: str) -> List[DistInfo]: ...

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

    def get_large_padding(self):
        return ems_to_pixels(1.5)

    def get_medium_padding(self):
        return ems_to_pixels(1)

    def get_small_padding(self):
        return ems_to_pixels(0.6)

    def get_pw_padding(self):
        return self.get_medium_padding()


class BackendPipFrame(PipFrame):
    def __init__(self, master):
        self._last_name_to_show = None
        super().__init__(master)

        get_workbench().bind("ToplevelResponse", self.on_toplevel_response, True)

        if self._get_proxy():
            self.load_content()

    def on_toplevel_response(self, event=None):
        if self._state == "inactive":
            self.load_content()

    def _get_proxy(self) -> Optional[running.BackendProxy]:
        runner = get_runner()
        if runner is None:
            return None
        return runner.get_backend_proxy()

    def _has_remote_target(self):
        return self._get_proxy().supports_remote_files()

    def _start_update_list(self, name_to_show=None):
        assert self._get_state() in [None, "idle", "inactive"]
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

        self._installed_dists = {canonicalize_name(d.name): d for d in msg.distributions}
        self._set_state("idle", True)
        self._update_list(self._last_name_to_show)

    def _confirm_install(self, package_data):
        for question in self._get_proxy().get_package_installation_confirmations(package_data):
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
        return self._get_proxy().get_full_label()

    def _installer_runs_locally(self):
        return self._get_proxy().can_install_packages_from_files()

    def _get_target_directory(self):
        return self._get_proxy().get_packages_target_dir_with_comment()[0]

    def _normalize_target_path(self, path: str) -> str:
        return self._get_proxy().normalize_target_path(path)

    def _append_location_to_info_path(self, path):
        if self._get_proxy().uses_local_filesystem():
            tags = ("url",)
        else:
            tags = ()
        self.info_text.direct_insert("end", self._normalize_target_path(path), tags)

    def _show_extra_instructions(self):
        from thonny.plugins.micropython.mp_front import MicroPythonProxy

        if isinstance(self._get_proxy(), MicroPythonProxy):
            self._advertise_pipkin()

    def _show_read_only_instructions(self):
        path, comment = self._get_proxy().get_packages_target_dir_with_comment()
        assert path is None

        self._append_info_text(tr("Installation is not possible") + "\n", ("caption",))
        self.info_text.direct_insert(
            "end",
            comment + "\n\n",
        )

    def _fetch_search_results(self, query: str) -> List[DistInfo]:
        return self._get_proxy().search_packages(query)

    def _download_dist_info(self, name: str, version: str) -> DistInfo:
        return self._get_proxy().get_package_info_from_index(name, version)

    def _download_version_list(self, name: str) -> List[str]:
        return self._get_proxy().get_version_list_from_index(name)

    def _should_show_search_result_source(self):
        from thonny.plugins.micropython.mp_front import MicroPythonProxy

        return isinstance(self._get_proxy(), MicroPythonProxy)

    def get_pw_padding(self):
        return 0


class PluginsPipFrame(PipFrame):
    def __init__(self, master):
        super().__init__(master)
        # make sure directory exists, so user can put her plug-ins there
        d = self._get_target_directory()
        makedirs(d, exist_ok=True)

    def _has_remote_target(self):
        return False

    def _installer_runs_locally(self):
        return True

    def _start_update_list(self, name_to_show=None):
        assert self._get_state() in [None, "idle", "inactive"]
        self._set_state("listing")

        self._installed_dists = export_installed_distributions_info_as_dict()
        logger.info("Got %d installed dists", len(self._installed_dists))
        self._set_state("idle", True)

        self._update_list(name_to_show)
        logger.info("After update list")

    def _conflicts_with_thonny_version(self, req_strings):
        try:
            conflicts = []
            for req_string in req_strings:
                req = Requirement(req_string)
                if req.name == "thonny" and thonny.get_version() not in req:
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

    def _fetch_search_results(self, query: str) -> List[DistInfo]:
        return perform_pypi_search(query)

    def _should_show_search_result_source(self):
        return False


class PluginsPipDialog(CommonDialog):
    def __init__(self, master):
        super().__init__(master)

        banner = ttk.Frame(self, style="Tip.TFrame")
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

        banner.grid(row=0, column=0)

        self.pip_frame = PluginsPipFrame(self)
        self.pip_frame.grid(row=1, sticky=tk.NSEW, ipadx=self.get_medium_padding())
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=2, sticky="nsew", ipadx=self.get_medium_padding())
        bottom_frame.columnconfigure(0, weight=1)

        self.close_button = ttk.Button(bottom_frame, text=tr("Close"), command=self._on_close)
        self.close_button.grid(sticky="e")

        self.title(tr("Thonny plug-ins"))

        self.bind("<Escape>", self._on_close, True)
        self.bind("<Map>", self._on_show, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_show(self, event):
        self.update()
        self.pip_frame.check_load_initial_content()

    def _on_close(self, event=None):
        self._closed = True
        self.destroy()


class PackagesView(BackendPipFrame):
    pass


class StubsPipFrame(PipFrame):
    def __init__(self, master, proxy_class: type[BackendProxy], **kw):
        self.proxy_class = proxy_class
        super().__init__(master, **kw)
        self.load_content()

    def _has_remote_target(self):
        return False

    def _installer_runs_locally(self):
        return True

    def _start_update_list(self, name_to_show=None):
        assert self._get_state() in [None, "idle", "inactive"]
        self._set_state("listing")

        self._installed_dists = {
            canonicalize_name(d.name): d
            for d in export_distributions_info_from_dir(self._get_target_directory())
        }
        self._set_state("idle", True)

        self._update_list(name_to_show)

    def _get_interpreter_description(self):
        return self.proxy_class.backend_description

    def _get_target_directory(self):
        return self.proxy_class.get_stubs_location()

    def _normalize_target_path(self, path: str) -> str:
        return normpath_with_actual_case(path)

    def _run_pip_with_dialog(self, command: str, args: Dict, title: str) -> Tuple[int, str, str]:
        cmd = ["-m", "pipkin", "--dir", self._get_target_directory(), command]
        if command == "uninstall":
            cmd += ["--yes"]
        cmd += args

        proc = running.create_frontend_python_process(
            cmd,
            stderr=subprocess.STDOUT,
            environment_extras={"PYTHONPATH": thonny.get_vendored_libs_dir()},
        )
        dlg = SubprocessDialog(
            self, proc, title="pipkin " + command, long_description=title, autostart=True
        )
        ui_utils.show_dialog(dlg)
        return dlg.returncode, dlg.stdout, dlg.stderr

    def _append_location_to_info_path(self, path):
        self.info_text.direct_insert("end", self._normalize_target_path(path), ("url",))

    def _fetch_search_results(self, query: str) -> List[DistInfo]:
        return self.proxy_class.search_packages(query)

    def _download_dist_info(self, name: str, version: str) -> DistInfo:
        return self.proxy_class.get_package_info_from_index(name, version)

    def _should_show_search_result_source(self):
        return True


def perform_pypi_search(query: str) -> List[DistInfo]:
    try:
        return _perform_plain_pypi_search(query)
    except Exception as e:
        logger.exception("Could not search PyPI for %r", query)
        # Let's try a fallback by treating the query as package name
        name = canonicalize_name(query.strip().replace(" ", ""))
        logger.info("Probing for package named %r", name)
        try:
            dist_info = download_dist_info_from_pypi(name, None)
        except Exception:
            logger.exception("No luck with %r", name)
            raise e from None
        else:
            raise PyPiSearchErrorWithFallback(str(e), dist_info) from e


def _perform_plain_pypi_search(query: str) -> List[DistInfo]:
    import urllib.parse

    logger.info("Performing PyPI search for %r", query)

    url = "https://pypi.org/search/?q={}".format(urllib.parse.quote(query))
    data = download_bytes(url)

    results = _extract_pypi_search_results(data.decode("utf-8"))
    logger.info("Got %r PyPI matches", len(results))
    return [
        DistInfo(name=r["name"], version=r["version"], summary=r.get("description"), source="PyPI")
        for r in results
    ]


def download_dist_info_from_pypi(name: str, version: Optional[str]) -> DistInfo:
    # versioned data does not have releases, so need to make 2 downloads
    info = download_dist_data_from_pypi(name, version)["info"]

    return DistInfo(
        name=info["name"],
        version=info["version"],
        summary=info["summary"] or None,
        license=info["license"] or None,
        author=info["author"] or None,
        classifiers=info["classifiers"] or None,
        home_page=info["home_page"] or info["project_url"],
        package_url=info["package_url"],
        requires=info["requires_dist"],
        source="PyPI",
        installed_location=None,
    )


def try_download_version_list_from_pypi(name: str) -> List[str]:
    try:
        releases = download_dist_data_from_pypi(name, None)["releases"]
        return list(releases.keys())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # package is not at PyPI
            return []
        else:
            raise


def download_dist_data_from_pypi(name: str, version: Optional[str]) -> Dict:
    if version is None:
        url = "https://pypi.org/pypi/{}/json".format(urllib.parse.quote(name))
    else:
        url = "https://pypi.org/pypi/{}/{}/json".format(
            urllib.parse.quote(name), urllib.parse.quote(version)
        )

    logger.info("Downloading package info (%r, %r) from %s", name, version, url)

    return download_and_parse_json(url)


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
                if tag_class in (
                    "package-snippet__name",
                    "package-snippet__description",
                    "package-snippet__version",
                ):
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

    results = PypiSearchResultsParser(html_data).results
    if not results:
        # this may mean either no matches or changed structure of PyPI search page
        # Let's probe for known marker of no matches
        if not "There were no results for" in html_data:
            raise RuntimeError("Unexpected structure of PyPI search results")

    return results


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


def export_installed_distributions_info_as_dict() -> Dict[NormalizedName, DistInfo]:
    return {canonicalize_name(d.name): d for d in export_installed_distributions_info()}


class PyPiSearchErrorWithFallback(RuntimeError):
    def __init__(self, message, fallback_result: DistInfo):
        super().__init__(message)
        self.fallback_result = fallback_result


def load_plugin() -> None:
    def open_backend_pip_gui(*args):
        get_workbench().show_view("PackagesView")

    def open_plugins_pip_gui(*args):
        pg = PluginsPipDialog(get_workbench())
        ui_utils.show_dialog(pg)

    get_workbench().add_view(PackagesView, tr("Packages"), "s")

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
