# -*- coding: utf-8 -*-
import collections
import logging
import os
import platform
import queue
import re
import signal
import subprocess
import sys
import textwrap
import threading
import time
import tkinter as tk
import tkinter.font
import traceback
import warnings
from tkinter import filedialog, messagebox, ttk
from typing import Callable, List, Optional, Tuple, Union  # @UnusedImport

from _tkinter import TclError

from thonny import get_workbench, misc_utils, tktextext
from thonny.common import TextRange
from thonny.languages import get_button_padding, tr
from thonny.misc_utils import (
    running_on_linux,
    running_on_mac_os,
    running_on_rpi,
    running_on_windows,
)
from thonny.tktextext import TweakableText

PARENS_REGEX = re.compile(r"[\(\)\{\}\[\]]")

logger = logging.getLogger(__name__)


class CommonDialog(tk.Toplevel):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.bind("<FocusIn>", self._unlock_on_focus_in, True)

    def _unlock_on_focus_in(self, event):
        if not self.winfo_ismapped():
            focussed_widget = self.focus_get()
            self.deiconify()
            if focussed_widget:
                focussed_widget.focus_set()

    def get_padding(self):
        return ems_to_pixels(2)

    def get_internal_padding(self):
        return self.get_padding() // 4


class CommonDialogEx(CommonDialog):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)

        # Need to fill the dialog with a frame to gain theme support
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.bind("<Escape>", self.on_close, True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self, event=None):
        self.destroy()


class QueryDialog(CommonDialogEx):
    def __init__(
        self,
        master,
        title: str,
        prompt: str,
        initial_value: str = "",
        options: List[str] = [],
        entry_width: Optional[int] = None,
    ):
        super().__init__(master)
        self.var = tk.StringVar(value=initial_value)
        self.result = None

        margin = self.get_padding()
        spacing = margin // 2

        self.title(title)
        self.prompt_label = ttk.Label(self.main_frame, text=prompt)
        self.prompt_label.grid(row=1, column=1, columnspan=2, padx=margin, pady=(margin, spacing))

        if options:
            self.entry_widget = ttk.Combobox(
                self.main_frame, textvariable=self.var, values=options, height=15, width=entry_width
            )
        else:
            self.entry_widget = ttk.Entry(self.main_frame, textvariable=self.var, width=entry_width)

        self.entry_widget.bind("<Return>", self.on_ok, True)
        self.entry_widget.bind("<KP_Enter>", self.on_ok, True)

        self.entry_widget.grid(
            row=3, column=1, columnspan=2, sticky="we", padx=margin, pady=(0, margin)
        )

        self.ok_button = ttk.Button(
            self.main_frame, text=tr("OK"), command=self.on_ok, default="active"
        )
        self.ok_button.grid(row=5, column=1, padx=(margin, spacing), pady=(0, margin), sticky="e")
        self.cancel_button = ttk.Button(self.main_frame, text=tr("Cancel"), command=self.on_cancel)
        self.cancel_button.grid(row=5, column=2, padx=(0, margin), pady=(0, margin), sticky="e")

        self.main_frame.columnconfigure(1, weight=1)

        self.entry_widget.focus_set()

    def on_ok(self, event=None):
        self.result = self.var.get()
        self.destroy()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()

    def get_result(self) -> Optional[str]:
        return self.result


def ask_string(
    title: str,
    prompt: str,
    initial_value: str = "",
    options: List[str] = [],
    entry_width: Optional[int] = None,
    master=None,
):
    dlg = QueryDialog(
        master, title, prompt, initial_value=initial_value, options=options, entry_width=entry_width
    )
    show_dialog(dlg, master)
    return dlg.get_result()


class CustomMenubar(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master, style="CustomMenubar.TFrame")
        self._menus = []
        self._opened_menu = None

        ttk.Style().map(
            "CustomMenubarLabel.TLabel",
            background=[
                ("!active", lookup_style_option("Menubar", "background", "gray")),
                ("active", lookup_style_option("Menubar", "activebackground", "LightYellow")),
            ],
            foreground=[
                ("!active", lookup_style_option("Menubar", "foreground", "black")),
                ("active", lookup_style_option("Menubar", "activeforeground", "black")),
            ],
        )

    def add_cascade(self, label, menu):
        label_widget = ttk.Label(
            self,
            style="CustomMenubarLabel.TLabel",
            text=label,
            padding=[6, 3, 6, 2],
            font="TkDefaultFont",
        )

        if len(self._menus) == 0:
            padx = (6, 0)
        else:
            padx = 0

        label_widget.grid(row=0, column=len(self._menus), padx=padx)

        def enter(event):
            label_widget.state(("active",))

            # Don't know how to open this menu when another menu is open
            # another tk_popup just doesn't work unless old menu is closed by click or Esc
            # https://stackoverflow.com/questions/38081470/is-there-a-way-to-know-if-tkinter-optionmenu-dropdown-is-active
            # unpost doesn't work in Win and Mac: https://www.tcl.tk/man/tcl8.5/TkCmd/menu.htm#M62
            # print("ENTER", menu, self._opened_menu)
            if self._opened_menu is not None:
                self._opened_menu.unpost()
                click(event)

        def leave(event):
            label_widget.state(("!active",))

        def click(event):
            try:
                # print("Before")
                self._opened_menu = menu
                menu.tk_popup(
                    label_widget.winfo_rootx(),
                    label_widget.winfo_rooty() + label_widget.winfo_height(),
                )
            finally:
                # print("After")
                self._opened_menu = None

        label_widget.bind("<Enter>", enter, True)
        label_widget.bind("<Leave>", leave, True)
        label_widget.bind("<1>", click, True)
        self._menus.append(menu)


class AutomaticPanedWindow(tk.PanedWindow):
    """
    Enables inserting panes according to their position_key-s.
    Automatically adds/removes itself to/from its master AutomaticPanedWindow.
    Fixes some style glitches.
    """

    def __init__(self, master, position_key=None, preferred_size_in_pw=None, **kwargs):
        tk.PanedWindow.__init__(self, master, border=0, **kwargs)
        self._pane_minsize = 100
        self.position_key = position_key
        self._restoring_pane_sizes = False

        self._last_window_size = (0, 0)
        self._full_size_not_final = True
        self._configure_binding = self.bind("<Configure>", self._on_window_resize, True)
        self._update_appearance_binding = self.bind(
            "<<ThemeChanged>>", self._update_appearance, True
        )
        self.bind("<B1-Motion>", self._on_mouse_dragged, True)
        self._update_appearance()

        # should be in the end, so that it can be detected when
        # constructor hasn't completed yet
        self.preferred_size_in_pw = preferred_size_in_pw

    def insert(self, pos, child, **kw):
        kw.setdefault("minsize", self._pane_minsize)

        if pos == "auto":
            # According to documentation I should use self.panes()
            # but this doesn't return expected widgets
            for sibling in sorted(
                self.pane_widgets(),
                key=lambda p: p.position_key if hasattr(p, "position_key") else 0,
            ):
                if (
                    not hasattr(sibling, "position_key")
                    or sibling.position_key == None
                    or sibling.position_key > child.position_key
                ):
                    pos = sibling
                    break
            else:
                pos = "end"

        if isinstance(pos, tk.Widget):
            kw["before"] = pos

        self.add(child, **kw)

    def add(self, child, **kw):
        kw.setdefault("minsize", self._pane_minsize)

        tk.PanedWindow.add(self, child, **kw)
        self._update_visibility()
        self._check_restore_preferred_sizes()

    def remove(self, child):
        tk.PanedWindow.remove(self, child)
        self._update_visibility()
        self._check_restore_preferred_sizes()

    def forget(self, child):
        tk.PanedWindow.forget(self, child)
        self._update_visibility()
        self._check_restore_preferred_sizes()

    def destroy(self):
        self.unbind("<Configure>", self._configure_binding)
        self.unbind("<<ThemeChanged>>", self._update_appearance_binding)
        tk.PanedWindow.destroy(self)

    def is_visible(self):
        if not isinstance(self.master, AutomaticPanedWindow):
            return self.winfo_ismapped()
        else:
            return self in self.master.pane_widgets()

    def pane_widgets(self):
        result = []
        for pane in self.panes():
            # pane is not the widget but some kind of reference object
            assert not isinstance(pane, tk.Widget)
            result.append(self.nametowidget(str(pane)))
        return result

    def _on_window_resize(self, event):
        if event.width < 10 or event.height < 10:
            return
        window = self.winfo_toplevel()
        window_size = (window.winfo_width(), window.winfo_height())
        initializing = hasattr(window, "initializing") and window.initializing

        if (
            not initializing
            and not self._restoring_pane_sizes
            and (window_size != self._last_window_size or self._full_size_not_final)
        ):
            self._check_restore_preferred_sizes()
            self._last_window_size = window_size

    def _on_mouse_dragged(self, event):
        if event.widget == self and not self._restoring_pane_sizes:
            self._update_preferred_sizes()

    def _update_preferred_sizes(self):
        for pane in self.pane_widgets():
            if getattr(pane, "preferred_size_in_pw", None) is not None:
                if self.cget("orient") == "horizontal":
                    current_size = pane.winfo_width()
                else:
                    current_size = pane.winfo_height()

                if current_size > 20:
                    pane.preferred_size_in_pw = current_size

                    # paneconfig width/height effectively puts
                    # unexplainable maxsize to some panes
                    # if self.cget("orient") == "horizontal":
                    #    self.paneconfig(pane, width=current_size)
                    # else:
                    #    self.paneconfig(pane, height=current_size)
                    #
            # else:
            #    self.paneconfig(pane, width=1000, height=1000)

    def _check_restore_preferred_sizes(self):
        window = self.winfo_toplevel()
        if getattr(window, "initializing", False):
            return

        try:
            self._restoring_pane_sizes = True
            self._restore_preferred_sizes()
        finally:
            self._restoring_pane_sizes = False

    def _restore_preferred_sizes(self):
        total_preferred_size = 0
        panes_without_preferred_size = []

        panes = self.pane_widgets()
        for pane in panes:
            if not hasattr(pane, "preferred_size_in_pw"):
                # child isn't fully constructed yet
                return

            if pane.preferred_size_in_pw is None:
                panes_without_preferred_size.append(pane)
                # self.paneconfig(pane, width=1000, height=1000)
            else:
                total_preferred_size += pane.preferred_size_in_pw

                # Without updating pane width/height attribute
                # the preferred size may lose effect when squeezing
                # non-preferred panes too small. Also zooming/unzooming
                # changes the supposedly fixed panes ...
                #
                # but
                # paneconfig width/height effectively puts
                # unexplainable maxsize to some panes
                # if self.cget("orient") == "horizontal":
                #    self.paneconfig(pane, width=pane.preferred_size_in_pw)
                # else:
                #    self.paneconfig(pane, height=pane.preferred_size_in_pw)

        assert len(panes_without_preferred_size) <= 1

        size = self._get_size()
        if size is None:
            return

        leftover_size = self._get_size() - total_preferred_size
        used_size = 0
        for i, pane in enumerate(panes[:-1]):
            used_size += pane.preferred_size_in_pw or leftover_size
            self._place_sash(i, used_size)
            used_size += int(str(self.cget("sashwidth")))

    def _get_size(self):
        if self.cget("orient") == tk.HORIZONTAL:
            result = self.winfo_width()
        else:
            result = self.winfo_height()

        if result < 20:
            # Not ready yet
            return None
        else:
            return result

    def _place_sash(self, i, distance):
        if self.cget("orient") == tk.HORIZONTAL:
            self.sash_place(i, distance, 0)
        else:
            self.sash_place(i, 0, distance)

    def _update_visibility(self):
        if not isinstance(self.master, AutomaticPanedWindow):
            return

        if len(self.panes()) == 0 and self.is_visible():
            self.master.forget(self)

        if len(self.panes()) > 0 and not self.is_visible():
            self.master.insert("auto", self)

    def _update_appearance(self, event=None):
        self.configure(sashwidth=lookup_style_option("Sash", "sashthickness", ems_to_pixels(0.6)))
        self.configure(background=lookup_style_option("TPanedWindow", "background"))


class ClosableNotebook(ttk.Notebook):
    def __init__(self, master, style="ButtonNotebook.TNotebook", **kw):
        super().__init__(master, style=style, **kw)

        self.tab_menu = self.create_tab_menu()
        self._popup_index = None
        self.pressed_index = None

        self.bind("<ButtonPress-1>", self._letf_btn_press, True)
        self.bind("<ButtonRelease-1>", self._left_btn_release, True)
        if running_on_mac_os():
            self.bind("<ButtonPress-2>", self._right_btn_press, True)
            self.bind("<Control-Button-1>", self._right_btn_press, True)
        else:
            self.bind("<ButtonPress-3>", self._right_btn_press, True)

        # self._check_update_style()

    def create_tab_menu(self):
        menu = tk.Menu(self.winfo_toplevel(), tearoff=False, **get_style_configuration("Menu"))
        menu.add_command(label=tr("Close"), command=self._close_tab_from_menu)
        menu.add_command(label=tr("Close others"), command=self._close_other_tabs)
        menu.add_command(label=tr("Close all"), command=self.close_tabs)
        return menu

    def _letf_btn_press(self, event):
        try:
            elem = self.identify(event.x, event.y)
            index = self.index("@%d,%d" % (event.x, event.y))

            if "closebutton" in elem:
                self.state(["pressed"])
                self.pressed_index = index
        except Exception:
            # may fail, if clicked outside of tab
            return

    def _left_btn_release(self, event):
        if not self.instate(["pressed"]):
            return

        try:
            elem = self.identify(event.x, event.y)
            index = self.index("@%d,%d" % (event.x, event.y))
        except Exception:
            # may fail, when mouse is dragged
            return
        else:
            if "closebutton" in elem and self.pressed_index == index:
                self.close_tab(index)

            self.state(["!pressed"])
        finally:
            self.pressed_index = None

    def _right_btn_press(self, event):
        try:
            index = self.index("@%d,%d" % (event.x, event.y))
            self._popup_index = index
            self.tab_menu.tk_popup(*self.winfo_toplevel().winfo_pointerxy())
        except Exception:
            logging.exception("Opening tab menu")

    def _close_tab_from_menu(self):
        self.close_tab(self._popup_index)

    def _close_other_tabs(self):
        self.close_tabs(self._popup_index)

    def close_tabs(self, except_index=None):
        for tab_index in reversed(range(len(self.winfo_children()))):
            if except_index is not None and tab_index == except_index:
                continue
            else:
                self.close_tab(tab_index)

    def close_tab(self, index):
        child = self.get_child_by_index(index)
        if hasattr(child, "close"):
            child.close()
        else:
            self.forget(index)
            child.destroy()

    def get_child_by_index(self, index):
        tab_id = self.tabs()[index]
        if tab_id:
            return self.nametowidget(tab_id)
        else:
            return None

    def get_current_child(self):
        child_id = self.select()
        if child_id:
            return self.nametowidget(child_id)
        else:
            return None

    def focus_set(self):
        editor = self.get_current_child()
        if editor:
            editor.focus_set()
        else:
            super().focus_set()

    def _check_update_style(self):
        style = ttk.Style()
        if "closebutton" in style.element_names():
            # It's done already
            return

        # respect if required images have been defined already
        if "img_close" not in self.image_names():
            img_dir = os.path.join(os.path.dirname(__file__), "res")
            ClosableNotebook._close_img = tk.PhotoImage(
                "img_tab_close", file=os.path.join(img_dir, "tab_close.gif")
            )
            ClosableNotebook._close_active_img = tk.PhotoImage(
                "img_tab_close_active", file=os.path.join(img_dir, "tab_close_active.gif")
            )

        style.element_create(
            "closebutton",
            "image",
            "img_tab_close",
            ("active", "pressed", "!disabled", "img_tab_close_active"),
            ("active", "!disabled", "img_tab_close_active"),
            border=8,
            sticky="",
        )

        style.layout(
            "ButtonNotebook.TNotebook.Tab",
            [
                (
                    "Notebook.tab",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Notebook.padding",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Notebook.focus",
                                            {
                                                "side": "top",
                                                "sticky": "nswe",
                                                "children": [
                                                    (
                                                        "Notebook.label",
                                                        {"side": "left", "sticky": ""},
                                                    ),
                                                    (
                                                        "Notebook.closebutton",
                                                        {"side": "left", "sticky": ""},
                                                    ),
                                                ],
                                            },
                                        )
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )

    def _check_remove_padding(self, kw):
        # Windows themes produce 1-pixel padding to the bottom of the pane
        # Don't know how to get rid of it using themes
        if "padding" not in kw and ttk.Style().theme_use().lower() in (
            "windows",
            "xpnative",
            "vista",
        ):
            kw["padding"] = (0, 0, 0, -1)

    def add(self, child, **kw):
        self._check_remove_padding(kw)
        super().add(child, **kw)

    def insert(self, pos, child, **kw):
        self._check_remove_padding(kw)
        super().insert(pos, child, **kw)


class AutomaticNotebook(ClosableNotebook):
    """
    Enables inserting views according to their position keys.
    Remember its own position key. Automatically updates its visibility.
    """

    def __init__(self, master, position_key, preferred_size_in_pw=None):
        if get_workbench().in_simple_mode():
            style = "TNotebook"
        else:
            style = "ButtonNotebook.TNotebook"
        super().__init__(master, style=style, padding=0)
        self.position_key = position_key

        # should be in the end, so that it can be detected when
        # constructor hasn't completed yet
        self.preferred_size_in_pw = preferred_size_in_pw

    def add(self, child, **kw):
        super().add(child, **kw)
        self._update_visibility()

    def insert(self, pos, child, **kw):
        if pos == "auto":
            for sibling in map(self.nametowidget, self.tabs()):
                if (
                    not hasattr(sibling, "position_key")
                    or sibling.position_key == None
                    or sibling.position_key > child.position_key
                ):
                    pos = sibling
                    break
            else:
                pos = "end"

        super().insert(pos, child, **kw)
        self._update_visibility()

    def hide(self, tab_id):
        super().hide(tab_id)
        self._update_visibility()

    def forget(self, tab_id):
        if tab_id in self.tabs() or tab_id in self.winfo_children():
            super().forget(tab_id)
        self._update_visibility()

    def is_visible(self):
        return self in self.master.pane_widgets()

    def get_visible_child(self):
        for child in self.winfo_children():
            if str(child) == str(self.select()):
                return child

        return None

    def _update_visibility(self):
        if not isinstance(self.master, AutomaticPanedWindow):
            return
        if len(self.tabs()) == 0 and self.is_visible():
            self.master.remove(self)

        if len(self.tabs()) > 0 and not self.is_visible():
            self.master.insert("auto", self)


class TreeFrame(ttk.Frame):
    def __init__(
        self,
        master,
        columns,
        displaycolumns="#all",
        show_scrollbar=True,
        show_statusbar=False,
        borderwidth=0,
        relief="flat",
        **tree_kw
    ):
        ttk.Frame.__init__(self, master, borderwidth=borderwidth, relief=relief)
        # http://wiki.tcl.tk/44444#pagetoc50f90d9a
        self.vert_scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, style=scrollbar_style("Vertical")
        )
        if show_scrollbar:
            self.vert_scrollbar.grid(
                row=0, column=1, sticky=tk.NSEW, rowspan=2 if show_statusbar else 1
            )

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            displaycolumns=displaycolumns,
            yscrollcommand=self.vert_scrollbar.set,
            **tree_kw
        )
        self.tree["show"] = "headings"
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.vert_scrollbar["command"] = self.tree.yview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_select, "+")
        self.tree.bind("<Double-Button-1>", self.on_double_click, "+")

        self.error_label = ttk.Label(self.tree)

        if show_statusbar:
            self.statusbar = ttk.Frame(self)
            self.statusbar.grid(row=1, column=0, sticky="nswe")
        else:
            self.statusbar = None

    def _clear_tree(self):
        for child_id in self.tree.get_children():
            self.tree.delete(child_id)

    def clear(self):
        self._clear_tree()

    def on_select(self, event):
        pass

    def on_double_click(self, event):
        pass

    def show_error(self, error_text):
        self.error_label.configure(text=error_text)
        self.error_label.grid()

    def clear_error(self):
        self.error_label.grid_remove()


def scrollbar_style(orientation):
    # In mac ttk.Scrollbar uses native rendering unless style attribute is set
    # see http://wiki.tcl.tk/44444#pagetoc50f90d9a
    # Native rendering doesn't look good in dark themes
    if running_on_mac_os() and get_workbench().uses_dark_ui_theme():
        return orientation + ".TScrollbar"
    else:
        return None


def sequence_to_accelerator(sequence):
    """Translates Tk event sequence to customary shortcut string
    for showing in the menu"""

    if not sequence:
        return ""

    if not sequence.startswith("<"):
        return sequence

    accelerator = (
        sequence.strip("<>").replace("Key-", "").replace("KeyPress-", "").replace("Control", "Ctrl")
    )

    # Tweaking individual parts
    parts = accelerator.split("-")
    # tkinter shows shift with capital letter, but in shortcuts it's customary to include it explicitly
    if len(parts[-1]) == 1 and parts[-1].isupper() and not "Shift" in parts:
        parts.insert(-1, "Shift")

    # even when shift is not required, it's customary to show shortcut with capital letter
    if len(parts[-1]) == 1:
        parts[-1] = parts[-1].upper()

    accelerator = "+".join(parts)

    # Post processing
    accelerator = (
        accelerator.replace("Minus", "-")
        .replace("minus", "-")
        .replace("Plus", "+")
        .replace("plus", "+")
    )

    return accelerator


def get_zoomed(toplevel):
    if "-zoomed" in toplevel.wm_attributes():  # Linux
        return bool(toplevel.wm_attributes("-zoomed"))
    else:  # Win/Mac
        return toplevel.wm_state() == "zoomed"


def set_zoomed(toplevel, value):
    if "-zoomed" in toplevel.wm_attributes():  # Linux
        toplevel.wm_attributes("-zoomed", str(int(value)))
    else:  # Win/Mac
        if value:
            toplevel.wm_state("zoomed")
        else:
            toplevel.wm_state("normal")


class EnhancedTextWithLogging(tktextext.EnhancedText):
    def __init__(self, master=None, style="Text", tag_current_line=False, cnf={}, **kw):
        super().__init__(
            master=master, style=style, tag_current_line=tag_current_line, cnf=cnf, **kw
        )

        self._last_event_changed_line_count = False

    def direct_insert(self, index, chars, tags=None, **kw):
        # try removing line numbers
        # TODO: shouldn't it take place only on paste?
        # TODO: does it occur when opening a file with line numbers in it?
        # if self._propose_remove_line_numbers and isinstance(chars, str):
        #    chars = try_remove_linenumbers(chars, self)

        concrete_index = self.index(index)
        line_before = self.get(concrete_index + " linestart", concrete_index + " lineend")
        self._last_event_changed_line_count = "\n" in chars
        result = tktextext.EnhancedText.direct_insert(self, index, chars, tags=tags, **kw)
        line_after = self.get(concrete_index + " linestart", concrete_index + " lineend")
        trivial_for_coloring, trivial_for_parens = self._is_trivial_edit(
            chars, line_before, line_after
        )
        get_workbench().event_generate(
            "TextInsert",
            index=concrete_index,
            text=chars,
            tags=tags,
            text_widget=self,
            trivial_for_coloring=trivial_for_coloring,
            trivial_for_parens=trivial_for_parens,
        )
        return result

    def direct_delete(self, index1, index2=None, **kw):
        try:
            # index1 may be eg "sel.first" and it doesn't make sense *after* deletion
            concrete_index1 = self.index(index1)
            if index2 is not None:
                concrete_index2 = self.index(index2)
            else:
                concrete_index2 = None

            chars = self.get(index1, index2)
            self._last_event_changed_line_count = "\n" in chars
            line_before = self.get(
                concrete_index1 + " linestart",
                (concrete_index1 if concrete_index2 is None else concrete_index2) + " lineend",
            )
            return tktextext.EnhancedText.direct_delete(self, index1, index2=index2, **kw)
        finally:
            line_after = self.get(
                concrete_index1 + " linestart",
                (concrete_index1 if concrete_index2 is None else concrete_index2) + " lineend",
            )
            trivial_for_coloring, trivial_for_parens = self._is_trivial_edit(
                chars, line_before, line_after
            )
            get_workbench().event_generate(
                "TextDelete",
                index1=concrete_index1,
                index2=concrete_index2,
                text_widget=self,
                trivial_for_coloring=trivial_for_coloring,
                trivial_for_parens=trivial_for_parens,
            )

    def _is_trivial_edit(self, chars, line_before, line_after):
        # line is taken after edit for insertion and before edit for deletion
        if not chars.strip():
            # linebreaks, including with automatic indent
            # check it doesn't break a triple-quote
            trivial_for_coloring = line_before.count("'''") == line_after.count(
                "'''"
            ) and line_before.count('"""') == line_after.count('"""')
            trivial_for_parens = trivial_for_coloring
        elif len(chars) > 1:
            # paste, cut, load or something like this
            trivial_for_coloring = False
            trivial_for_parens = False
        elif chars == "#":
            trivial_for_coloring = "''''" not in line_before and '"""' not in line_before
            trivial_for_parens = trivial_for_coloring and not re.search(PARENS_REGEX, line_before)
        elif chars in "()[]{}":
            trivial_for_coloring = line_before.count("'''") == line_after.count(
                "'''"
            ) and line_before.count('"""') == line_after.count('"""')
            trivial_for_parens = False
        elif chars == "'":
            trivial_for_coloring = "'''" not in line_before and "'''" not in line_after
            trivial_for_parens = False  # can put parens into open string
        elif chars == '"':
            trivial_for_coloring = '"""' not in line_before and '"""' not in line_after
            trivial_for_parens = False  # can put parens into open string
        elif chars == "\\":
            # can shorten closing quote
            trivial_for_coloring = '"""' not in line_before and '"""' not in line_after
            trivial_for_parens = False
        else:
            trivial_for_coloring = line_before.count("'''") == line_after.count(
                "'''"
            ) and line_before.count('"""') == line_after.count('"""')
            trivial_for_parens = trivial_for_coloring

        return trivial_for_coloring, trivial_for_parens


class SafeScrollbar(ttk.Scrollbar):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)

    def set(self, first, last):
        try:
            ttk.Scrollbar.set(self, first, last)
        except Exception:
            traceback.print_exc()


class AutoScrollbar(SafeScrollbar):
    # http://effbot.org/zone/tkinter-autoscrollbar.htm
    # a vert_scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.

    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)

    def set(self, first, last):
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.grid_remove()
        elif float(first) > 0.001 or float(last) < 0.009:
            # with >0 and <1 it occasionally made scrollbar wobble back and forth
            self.grid()
        ttk.Scrollbar.set(self, first, last)

    def pack(self, **kw):
        raise tk.TclError("cannot use pack with this widget")

    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")


def update_entry_text(entry, text):
    original_state = entry.cget("state")
    entry.config(state="normal")
    entry.delete(0, "end")
    entry.insert(0, text)
    entry.config(state=original_state)


class VerticallyScrollableFrame(ttk.Frame):
    # http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        # set up scrolling with canvas
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.interior = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tk.NW)
        self.bind("<Configure>", self._configure_interior, "+")
        self.bind("<Expose>", self._expose, "+")

    def _expose(self, event):
        self.update_idletasks()
        self.update_scrollbars()

    def _configure_interior(self, event):
        self.update_scrollbars()

    def update_scrollbars(self):
        # update the scrollbars to match the size of the inner frame
        size = (self.canvas.winfo_width(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if (
            self.interior.winfo_reqwidth() != self.canvas.winfo_width()
            and self.canvas.winfo_width() > 10
        ):
            # update the interior's width to fit canvas
            # print("CAWI", self.canvas.winfo_width())
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())


class ScrollableFrame(ttk.Frame):
    # http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        # set up scrolling with canvas
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        hscrollbar.grid(row=1, column=0, sticky=tk.NSEW)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.interior = ttk.Frame(self.canvas)
        self.interior.columnconfigure(0, weight=1)
        self.interior.rowconfigure(0, weight=1)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tk.NW)
        self.bind("<Configure>", self._configure_interior, "+")
        self.bind("<Expose>", self._expose, "+")

    def _expose(self, event):
        self.update_idletasks()
        self._configure_interior(event)

    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.canvas.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)


class ThemedListbox(tk.Listbox):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)

        self._ui_theme_change_binding = self.bind(
            "<<ThemeChanged>>", self._reload_theme_options, True
        )
        self._reload_theme_options()

    def _reload_theme_options(self, event=None):
        style = ttk.Style()

        states = []
        if self["state"] == "disabled":
            states.append("disabled")

        # Following crashes when a combobox is focused
        # if self.focus_get() == self:
        #    states.append("focus")
        opts = {}
        for key in [
            "background",
            "foreground",
            "highlightthickness",
            "highlightcolor",
            "highlightbackground",
        ]:
            value = style.lookup(self.get_style_name(), key, states)
            if value:
                opts[key] = value

        self.configure(opts)

    def get_style_name(self):
        return "Listbox"

    def destroy(self):
        self.unbind("<<ThemeChanged>>", self._ui_theme_change_binding)
        super().destroy()


class ToolTip:
    """Taken from http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml"""

    def __init__(self, widget, options):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.options = options

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + self.widget.winfo_height() + 2
        self.tipwindow = tw = tk.Toplevel(self.widget)
        if running_on_mac_os():
            try:
                # Must be the first thing to do after creating window
                # https://wiki.tcl-lang.org/page/MacWindowStyle
                tw.tk.call(
                    "::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "noActivates"
                )
                if get_tk_version_info() >= (8, 6, 10) and running_on_mac_os():
                    tw.wm_overrideredirect(1)
            except tk.TclError:
                pass
        else:
            tw.wm_overrideredirect(1)

        tw.wm_geometry("+%d+%d" % (x, y))

        if running_on_mac_os():
            # TODO: maybe it's because of Tk 8.5, not because of Mac
            tw.wm_transient(self.widget)

        label = tk.Label(tw, text=self.text, **self.options)
        label.pack()
        # get_workbench().bind("WindowFocusOut", self.hidetip, True)

    def hidetip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

        # get_workbench().unbind("WindowFocusOut", self.hidetip)


def create_tooltip(widget, text, **kw):
    options = get_style_configuration("Tooltip").copy()
    options.setdefault("background", "#ffffe0")
    options.setdefault("foreground", "#000000")
    options.setdefault("relief", "solid")
    options.setdefault("borderwidth", 1)
    options.setdefault("padx", 1)
    options.setdefault("pady", 0)
    options.update(kw)

    toolTip = ToolTip(widget, options)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)


class NoteBox(CommonDialog):
    def __init__(self, master=None, max_default_width=300, **kw):
        super().__init__(master=master, highlightthickness=0, **kw)

        self._max_default_width = max_default_width

        self.wm_overrideredirect(True)
        if running_on_mac_os():
            # TODO: maybe it's because of Tk 8.5, not because of Mac
            self.wm_transient(master)
        try:
            # For Mac OS
            self.tk.call(
                "::tk::unsupported::MacWindowStyle", "style", self._w, "help", "noActivates"
            )
        except tk.TclError:
            pass

        self._current_chars = ""
        self._click_bindings = {}

        self.padx = 5
        self.pady = 5
        self.text = TweakableText(
            self,
            background="#ffffe0",
            borderwidth=1,
            relief="solid",
            undo=False,
            read_only=True,
            font="TkDefaultFont",
            highlightthickness=0,
            padx=self.padx,
            pady=self.pady,
            wrap="word",
        )

        self.text.grid(row=0, column=0, sticky="nsew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.text.bind("<Escape>", self.close, True)

        # tk._default_root.bind_all("<1>", self._close_maybe, True)
        # tk._default_root.bind_all("<Key>", self.close, True)

        self.withdraw()

    def clear(self):
        for tag in self._click_bindings:
            self.text.tag_unbind(tag, "<1>", self._click_bindings[tag])
            self.text.tag_remove(tag, "1.0", "end")

        self.text.direct_delete("1.0", "end")
        self._current_chars = ""
        self._click_bindings.clear()

    def set_content(self, *items):
        self.clear()

        for item in items:
            if isinstance(item, str):
                self.text.direct_insert("1.0", item)
                self._current_chars = item
            else:
                assert isinstance(item, (list, tuple))
                chars, *props = item
                if len(props) > 0 and callable(props[-1]):
                    tags = tuple(props[:-1])
                    click_handler = props[-1]
                else:
                    tags = tuple(props)
                    click_handler = None

                self.append_text(chars, tags, click_handler)

            self.text.see("1.0")

    def append_text(self, chars, tags=(), click_handler=None):
        tags = tuple(tags)

        if click_handler is not None:
            click_tag = "click_%d" % len(self._click_bindings)
            tags = tags + (click_tag,)
            binding = self.text.tag_bind(click_tag, "<1>", click_handler, True)
            self._click_bindings[click_tag] = binding

        self.text.direct_insert("end", chars, tags)
        self._current_chars += chars

    def place(self, target, focus=None):

        # Compute the area that will be described by this Note
        focus_x = target.winfo_rootx()
        focus_y = target.winfo_rooty()
        focus_height = target.winfo_height()

        if isinstance(focus, TextRange):
            assert isinstance(target, tk.Text)
            topleft = target.bbox("%d.%d" % (focus.lineno, focus.col_offset))
            if focus.end_col_offset == 0:
                botright = target.bbox(
                    "%d.%d lineend" % (focus.end_lineno - 1, focus.end_lineno - 1)
                )
            else:
                botright = target.bbox("%d.%d" % (focus.end_lineno, focus.end_col_offset))

            if topleft and botright:
                focus_x += topleft[0]
                focus_y += topleft[1]
                focus_height = botright[1] - topleft[1] + botright[3]

        elif isinstance(focus, (list, tuple)):
            focus_x += focus[0]
            focus_y += focus[1]
            focus_height = focus[3]

        elif focus is None:
            pass

        else:
            raise TypeError("Unsupported focus")

        # Compute dimensions of the note
        font = self.text["font"]
        if isinstance(font, str):
            font = tk.font.nametofont(font)

        lines = self._current_chars.splitlines()
        max_line_width = 0
        for line in lines:
            max_line_width = max(max_line_width, font.measure(line))

        width = min(max_line_width, self._max_default_width) + self.padx * 2 + 2
        self.wm_geometry("%dx%d+%d+%d" % (width, 100, focus_x, focus_y + focus_height))

        self.update_idletasks()
        line_count = int(float(self.text.index("end")))
        line_height = font.metrics()["linespace"]

        self.wm_geometry(
            "%dx%d+%d+%d" % (width, line_count * line_height, focus_x, focus_y + focus_height)
        )

        # TODO: detect the situation when note doesn't fit under
        # the focus box and should be placed above

        self.deiconify()

    def show_note(self, *content_items: Union[str, List], target=None, focus=None) -> None:

        self.set_content(*content_items)
        self.place(target, focus)

    def _close_maybe(self, event):
        if event.widget not in [self, self.text]:
            self.close(event)

    def close(self, event=None):
        self.withdraw()


def get_widget_offset_from_toplevel(widget):
    x = 0
    y = 0
    toplevel = widget.winfo_toplevel()
    while widget != toplevel:
        x += widget.winfo_x()
        y += widget.winfo_y()
        widget = widget.master
    return x, y


class EnhancedVar(tk.Variable):
    def __init__(self, master=None, value=None, name=None, modification_listener=None):
        if master is not None and not isinstance(master, (tk.Widget, tk.Wm)):
            raise TypeError("First positional argument 'master' must be None, Widget or Wm")

        super().__init__(master=master, value=value, name=name)
        self.modified = False
        self.modification_listener = modification_listener
        if sys.version_info < (3, 6):
            self.trace("w", self._on_write)
        else:
            self.trace_add("write", self._on_write)

    def _on_write(self, *args):
        self.modified = True
        if self.modification_listener:
            try:
                self.modification_listener()
            except Exception:
                # Otherwise whole process will be brought down
                # because for some reason Tk tries to call non-existing method
                # on variable
                get_workbench().report_exception()


class EnhancedStringVar(EnhancedVar, tk.StringVar):
    pass


class EnhancedIntVar(EnhancedVar, tk.IntVar):
    pass


class EnhancedBooleanVar(EnhancedVar, tk.BooleanVar):
    pass


class EnhancedDoubleVar(EnhancedVar, tk.DoubleVar):
    pass


def create_string_var(value, modification_listener=None) -> EnhancedStringVar:
    """Creates a tk.StringVar with "modified" attribute
    showing whether the variable has been modified after creation"""
    return EnhancedStringVar(None, value, None, modification_listener)


def create_int_var(value, modification_listener=None) -> EnhancedIntVar:
    """See create_string_var"""
    return EnhancedIntVar(None, value, None, modification_listener)


def create_double_var(value, modification_listener=None) -> EnhancedDoubleVar:
    """See create_string_var"""
    return EnhancedDoubleVar(None, value, None, modification_listener)


def create_boolean_var(value, modification_listener=None) -> EnhancedBooleanVar:
    """See create_string_var"""
    return EnhancedBooleanVar(None, value, None, modification_listener)


def shift_is_pressed(event_state):
    # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html
    # http://stackoverflow.com/q/32426250/261181
    return event_state & 0x0001


def caps_lock_is_on(event_state):
    # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html
    # http://stackoverflow.com/q/32426250/261181
    return event_state & 0x0002


def control_is_pressed(event_state):
    # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html
    # http://stackoverflow.com/q/32426250/261181
    return event_state & 0x0004


def sequence_to_event_state_and_keycode(sequence: str) -> Optional[Tuple[int, int]]:
    # remember handlers for certain shortcuts which require
    # different treatment on non-latin keyboards
    if sequence[0] != "<":
        return None

    parts = sequence.strip("<").strip(">").split("-")
    # support only latin letters for now
    if parts[-1].lower() not in list("abcdefghijklmnopqrstuvwxyz"):
        return None

    letter = parts.pop(-1)
    if "Key" in parts:
        parts.remove("Key")
    if "key" in parts:
        parts.remove("key")

    modifiers = {part.lower() for part in parts}

    if letter.isupper():
        modifiers.add("shift")

    if modifiers not in [{"control"}, {"control", "shift"}]:
        # don't support others for now
        return None

    event_state = 0
    # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html
    # https://stackoverflow.com/questions/32426250/python-documentation-and-or-lack-thereof-e-g-keyboard-event-state
    for modifier in modifiers:
        if modifier == "shift":
            event_state |= 0x0001
        elif modifier == "control":
            event_state |= 0x0004
        else:
            # unsupported modifier
            return None

    # for latin letters keycode is same as its ascii code
    return (event_state, ord(letter.upper()))


def select_sequence(win_version, mac_version, linux_version=None):
    if running_on_windows():
        return win_version
    elif running_on_mac_os():
        return mac_version
    elif running_on_linux() and linux_version:
        return linux_version
    else:
        return win_version


def try_remove_linenumbers(text, master):
    try:
        if has_line_numbers(text) and messagebox.askyesno(
            title="Remove linenumbers",
            message="Do you want to remove linenumbers from pasted text?",
            default=messagebox.YES,
            master=master,
        ):
            return remove_line_numbers(text)
        else:
            return text
    except Exception:
        traceback.print_exc()
        return text


def has_line_numbers(text):
    lines = text.splitlines()
    return len(lines) > 2 and all([len(split_after_line_number(line)) == 2 for line in lines])


def split_after_line_number(s):
    parts = re.split(r"(^\s*\d+\.?)", s)
    if len(parts) == 1:
        return parts
    else:
        assert len(parts) == 3 and parts[0] == ""
        return parts[1:]


def remove_line_numbers(s):
    cleaned_lines = []
    for line in s.splitlines():
        parts = split_after_line_number(line)
        if len(parts) != 2:
            return s
        else:
            cleaned_lines.append(parts[1])

    return textwrap.dedent(("\n".join(cleaned_lines)) + "\n")


def center_window(win, master=None):
    # for backward compat
    return assign_geometry(win, master)


def assign_geometry(win, master=None, min_left=0, min_top=0):
    if master is None:
        master = tk._default_root

    size = get_workbench().get_option(get_size_option_name(win))
    if size:
        width, height = size
        saved_size = True
    else:
        fallback_width = 600
        fallback_height = 400
        # need to wait until size is computed
        # (unfortunately this causes dialog to jump)
        if getattr(master, "initializing", False):
            # can't get reliable positions when main window is not in mainloop yet
            width = fallback_width
            height = fallback_height
        else:
            if not running_on_linux():
                # better to avoid in Linux because it causes ugly jump
                win.update_idletasks()
            # looks like it doesn't take window border into account
            width = win.winfo_width()
            height = win.winfo_height()

            if width < 10:
                # ie. size measurement is not correct
                width = fallback_width
                height = fallback_height

        saved_size = False

    left = master.winfo_rootx() + master.winfo_width() // 2 - width // 2
    top = master.winfo_rooty() + master.winfo_height() // 2 - height // 2

    left = max(left, min_left)
    top = max(top, min_top)

    if saved_size:
        win.geometry("%dx%d+%d+%d" % (width, height, left, top))
    else:
        win.geometry("+%d+%d" % (left, top))


class WaitingDialog(CommonDialog):
    def __init__(self, master, async_result, description, title="Please wait!", timeout=None):
        self._async_result = async_result
        super().__init__(master)
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        self.title(title)
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        # self.protocol("WM_DELETE_WINDOW", self._close)
        self.desc_label = ttk.Label(self, text=description, wraplength=300)
        self.desc_label.grid(padx=20, pady=20)

        self.update_idletasks()

        self.timeout = timeout
        self.start_time = time.time()
        self.after(500, self._poll)

    def _poll(self):
        if self._async_result.ready():
            self._close()
        elif self.timeout and time.time() - self.start_time > self.timeout:
            raise TimeoutError()
        else:
            self.after(500, self._poll)
            self.desc_label["text"] = self.desc_label["text"] + "."

    def _close(self):
        self.destroy()


def run_with_waiting_dialog(master, action, args=(), description="Working"):
    # http://stackoverflow.com/a/14299004/261181
    from multiprocessing.pool import ThreadPool

    pool = ThreadPool(processes=1)

    async_result = pool.apply_async(action, args)
    dlg = WaitingDialog(master, async_result, description=description)
    show_dialog(dlg, master)

    return async_result.get()


class FileCopyDialog(CommonDialog):
    def __init__(self, master, source, destination, description=None, fsync=True):
        self._source = source
        self._destination = destination
        self._old_bytes_copied = 0
        self._bytes_copied = 0
        self._fsync = fsync
        self._done = False
        self._cancelled = False
        self._closed = False

        super().__init__(master)

        main_frame = ttk.Frame(self)  # To get styled background
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.title(tr("Copying"))

        if description is None:
            description = tr("Copying\n  %s\nto\n  %s") % (source, destination)

        label = ttk.Label(main_frame, text=description)
        label.grid(row=0, column=0, columnspan=2, sticky="nw", padx=15, pady=15)

        self._bar = ttk.Progressbar(main_frame, maximum=os.path.getsize(source), length=200)
        self._bar.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=0)

        self._cancel_button = ttk.Button(main_frame, text=tr("Cancel"), command=self._cancel)
        self._cancel_button.grid(row=2, column=1, sticky="ne", padx=15, pady=15)
        self._bar.focus_set()

        main_frame.columnconfigure(0, weight=1)

        self._update_progress()

        self.bind("<Escape>", self._cancel, True)  # escape-close only if process has completed
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self._start()

    def _start(self):
        def work():
            self._copy_progess = 0

            with open(self._source, "rb") as fsrc:
                with open(self._destination, "wb") as fdst:
                    while True:
                        buf = fsrc.read(16 * 1024)
                        if not buf:
                            break

                        fdst.write(buf)
                        fdst.flush()
                        if self._fsync:
                            os.fsync(fdst)
                        self._bytes_copied += len(buf)

            self._done = True

        threading.Thread(target=work, daemon=True).start()

    def _update_progress(self):
        if self._done:
            if not self._closed:
                self._close()
            return

        self._bar.step(self._bytes_copied - self._old_bytes_copied)
        self._old_bytes_copied = self._bytes_copied

        self.after(100, self._update_progress)

    def _close(self):
        self.destroy()
        self._closed = True

    def _cancel(self, event=None):
        self._cancelled = True
        self._close()


class ChoiceDialog(CommonDialogEx):
    def __init__(
        self,
        master=None,
        title="Choose one",
        question: str = "Choose one:",
        choices=[],
        initial_choice_index=None,
    ) -> None:
        super().__init__(master=master)

        self.title(title)
        self.resizable(False, False)

        self.main_frame.columnconfigure(0, weight=1)

        row = 0
        question_label = ttk.Label(self.main_frame, text=question)
        question_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=20)
        row += 1

        self.var = tk.StringVar("")
        if initial_choice_index is not None:
            self.var.set(choices[initial_choice_index])
        for choice in choices:
            rb = ttk.Radiobutton(self.main_frame, text=choice, variable=self.var, value=choice)
            rb.grid(row=row, column=0, columnspan=2, sticky="w", padx=20)
            row += 1

        ok_button = ttk.Button(self.main_frame, text=tr("OK"), command=self._ok, default="active")
        ok_button.grid(row=row, column=0, sticky="e", pady=20)

        cancel_button = ttk.Button(self.main_frame, text=tr("Cancel"), command=self._cancel)
        cancel_button.grid(row=row, column=1, sticky="e", padx=20, pady=20)

        self.bind("<Escape>", self._cancel, True)
        self.bind("<Return>", self._ok, True)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _ok(self):
        self.result = self.var.get()
        if not self.result:
            self.result = None

        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class LongTextDialog(CommonDialog):
    def __init__(self, title, text_content, parent=None):
        if parent is None:
            parent = tk._default_root

        super().__init__(master=parent)
        self.title(title)

        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        default_font = tk.font.nametofont("TkDefaultFont")
        self._text = tktextext.TextFrame(
            main_frame,
            read_only=True,
            wrap="none",
            font=default_font,
            width=80,
            height=10,
            relief="sunken",
            borderwidth=1,
        )
        self._text.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
        self._text.text.direct_insert("1.0", text_content)
        self._text.text.see("1.0")

        copy_button = ttk.Button(
            main_frame, command=self._copy, text=tr("Copy to clipboard"), width=20
        )
        copy_button.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 20))

        close_button = ttk.Button(
            main_frame, command=self._close, text=tr("Close"), default="active"
        )
        close_button.grid(row=2, column=1, sticky="w", padx=20, pady=(0, 20))
        close_button.focus_set()

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Escape>", self._close, True)

    def _copy(self, event=None):
        self.clipboard_clear()
        self.clipboard_append(self._text.text.get("1.0", "end"))

    def _close(self, event=None):
        self.destroy()


def ask_one_from_choices(
    master=None,
    title="Choose one",
    question: str = "Choose one:",
    choices=[],
    initial_choice_index=None,
):
    dlg = ChoiceDialog(master, title, question, choices, initial_choice_index)
    show_dialog(dlg, master)
    return dlg.result


def get_busy_cursor():
    if running_on_windows():
        return "wait"
    elif running_on_mac_os():
        return "spinning"
    else:
        return "watch"


def get_tk_version_str():
    return tk._default_root.tk.call("info", "patchlevel")


def get_tk_version_info():
    result = []
    for part in get_tk_version_str().split("."):
        try:
            result.append(int(part))
        except Exception:
            result.append(0)
    return tuple(result)


def get_style_configuration(style_name, default={}):
    style = ttk.Style()
    # NB! style.configure seems to reuse the returned dict
    # Don't change it without copying first
    result = style.configure(style_name)
    if result is None:
        return default
    else:
        return result


def lookup_style_option(style_name, option_name, default=None):
    style = ttk.Style()
    setting = style.lookup(style_name, option_name)
    if setting in [None, ""]:
        return default
    elif setting == "True":
        return True
    elif setting == "False":
        return False
    else:
        return setting


def scale(value):
    return get_workbench().scale(value)


def open_path_in_system_file_manager(path):
    if running_on_mac_os():
        # http://stackoverflow.com/a/3520693/261181
        # -R doesn't allow showing hidden folders
        subprocess.Popen(["open", path])
    elif running_on_linux():
        subprocess.Popen(["xdg-open", path])
    else:
        assert running_on_windows()
        subprocess.Popen(["explorer", path])


def _get_dialog_provider():
    if platform.system() != "Linux" or get_workbench().get_option("file.avoid_zenity"):
        return filedialog

    import shutil

    if shutil.which("zenity"):
        return _ZenityDialogProvider

    # fallback
    return filedialog


def asksaveasfilename(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/getSaveFile.htm
    _check_dialog_parent(options)
    return _get_dialog_provider().asksaveasfilename(**options)


def askopenfilename(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/getOpenFile.htm
    _check_dialog_parent(options)
    return _get_dialog_provider().askopenfilename(**options)


def askopenfilenames(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/getOpenFile.htm
    _check_dialog_parent(options)
    return _get_dialog_provider().askopenfilenames(**options)


def askdirectory(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/chooseDirectory.htm
    _check_dialog_parent(options)
    return _get_dialog_provider().askdirectory(**options)


def _check_dialog_parent(options):
    if options.get("parent") and options.get("master"):
        parent = options["parent"].winfo_toplevel()
        master = options["master"].winfo_toplevel()
        if parent is not master:
            logger.warning(
                "Dialog with different parent/master toplevels:\n%s",
                "".join(traceback.format_stack()),
            )
    elif options.get("parent"):
        parent = options["parent"].winfo_toplevel()
        master = options["parent"].winfo_toplevel()
    elif options.get("master"):
        parent = options["master"].winfo_toplevel()
        master = options["master"].winfo_toplevel()
    else:
        logger.warning("Dialog without parent:\n%s", "".join(traceback.format_stack()))
        parent = tk._default_root
        master = tk._default_root

    options["parent"] = parent
    options["master"] = master

    if running_on_mac_os():
        # used to require master/parent (https://bugs.python.org/issue34927)
        # but this is deprecated in Catalina (https://github.com/thonny/thonny/issues/840)
        # TODO: Consider removing this when upgrading from Tk 8.6.8
        del options["master"]
        del options["parent"]


class _ZenityDialogProvider:
    # https://www.writebash.com/bash-gui/zenity-create-file-selection-dialog-224.html
    # http://linux.byexamples.com/archives/259/a-complete-zenity-dialog-examples-1/
    # http://linux.byexamples.com/archives/265/a-complete-zenity-dialog-examples-2/

    # another possibility is to use PyGobject: https://github.com/poulp/zenipy

    @classmethod
    def askopenfilename(cls, **options):
        args = cls._convert_common_options("Open file", **options)
        return cls._call(args)

    @classmethod
    def askopenfilenames(cls, **options):
        args = cls._convert_common_options("Open files", **options)
        return cls._call(args + ["--multiple"]).split("|")

    @classmethod
    def asksaveasfilename(cls, **options):
        args = cls._convert_common_options("Save as", **options)
        args.append("--save")
        if options.get("confirmoverwrite", True):
            args.append("--confirm-overwrite")

        filename = cls._call(args)
        if not filename:
            return None

        if "defaultextension" in options and "." not in os.path.basename(filename):
            filename += options["defaultextension"]

        return filename

    @classmethod
    def askdirectory(cls, **options):
        args = cls._convert_common_options("Select directory", **options)
        args.append("--directory")
        return cls._call(args)

    @classmethod
    def _convert_common_options(cls, default_title, **options):
        args = ["--file-selection", "--title=%s" % options.get("title", default_title)]

        filename = _options_to_zenity_filename(options)
        if filename:
            args.append("--filename=%s" % filename)

        parent = options.get("parent", options.get("master", None))
        if parent is not None:
            args.append("--modal")
            args.append("--attach=%s" % hex(parent.winfo_id()))

        for desc, pattern in options.get("filetypes", ()):
            # zenity requires star before extension
            pattern = pattern.replace(" .", " *.")
            if pattern.startswith("."):
                pattern = "*" + pattern

            if pattern == "*.*":
                # ".*" was provided to make the pattern safe for Tk dialog
                # not required with Zenity
                pattern = "*"

            args.append("--file-filter=%s | %s" % (desc, pattern))

        return args

    @classmethod
    def _call(cls, args):
        args = ["zenity", "--name=Thonny", "--class=Thonny"] + args
        result = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            # TODO: log problems
            print(result.stderr, file=sys.stderr)
            # could check stderr, but it may contain irrelevant warnings
            return None


def _options_to_zenity_filename(options):
    if options.get("initialdir"):
        if options.get("initialfile"):
            return os.path.join(options["initialdir"], options["initialfile"])
        else:
            return options["initialdir"] + os.path.sep

    return None


def register_latin_shortcut(
    registry, sequence: str, handler: Callable, tester: Optional[Callable]
) -> None:
    res = sequence_to_event_state_and_keycode(sequence)
    if res is not None:
        if res not in registry:
            registry[res] = []
        registry[res].append((handler, tester))


def handle_mistreated_latin_shortcuts(registry, event):
    # tries to handle Ctrl+LatinLetter shortcuts
    # given from non-Latin keyboards
    # See: https://bitbucket.org/plas/thonny/issues/422/edit-keyboard-shortcuts-ctrl-c-ctrl-v-etc

    # only consider events with Control held
    if not event.state & 0x04:
        return

    if running_on_mac_os():
        return

    # consider only part of the state,
    # because at least on Windows, Ctrl-shortcuts' state
    # has something extra
    simplified_state = 0x04
    if shift_is_pressed(event.state):
        simplified_state |= 0x01

    # print(simplified_state, event.keycode)
    if (simplified_state, event.keycode) in registry:
        if event.keycode != ord(event.char) and event.keysym in (None, "??"):
            # keycode and char doesn't match,
            # this means non-latin keyboard
            for handler, tester in registry[(simplified_state, event.keycode)]:
                if tester is None or tester():
                    handler()


def show_dialog(dlg, master=None, geometry=True, min_left=0, min_top=0):
    if getattr(dlg, "closed", False):
        return

    if master is None:
        master = getattr(dlg, "parent", None) or getattr(dlg, "master", None) or tk._default_root

    master = master.winfo_toplevel()

    get_workbench().event_generate("WindowFocusOut")
    # following order seems to give most smooth appearance
    focused_widget = master.focus_get()
    dlg.transient(master.winfo_toplevel())

    if geometry:
        # dlg.withdraw() # unfortunately inhibits size calculations in assign_geometry
        if isinstance(geometry, str):
            dlg.geometry(geometry)
        else:
            assign_geometry(dlg, master, min_left, min_top)
        # dlg.wm_deiconify()

    dlg.lift()
    dlg.focus_set()

    try:
        dlg.grab_set()
    except TclError as e:
        print("Can't grab:", e, file=sys.stderr)

    master.winfo_toplevel().wait_window(dlg)
    dlg.grab_release()
    master.winfo_toplevel().lift()
    master.winfo_toplevel().focus_force()
    master.winfo_toplevel().grab_set()
    if running_on_mac_os():
        master.winfo_toplevel().grab_release()

    if focused_widget is not None:
        try:
            focused_widget.focus_force()
        except TclError:
            pass


def popen_with_ui_thread_callback(*Popen_args, on_completion, poll_delay=0.1, **Popen_kwargs):
    if "encoding" not in Popen_kwargs:
        if "env" not in Popen_kwargs:
            Popen_kwargs["env"] = os.environ.copy()
        Popen_kwargs["env"]["PYTHONIOENCODING"] = "utf-8"
        if sys.version_info >= (3, 6):
            Popen_kwargs["encoding"] = "utf-8"

    proc = subprocess.Popen(*Popen_args, **Popen_kwargs)

    # Need to read in thread in order to avoid blocking because
    # of full pipe buffer (see https://bugs.python.org/issue1256)
    out_lines = []
    err_lines = []

    def read_stream(stream, target_list):
        while True:
            line = stream.readline()
            if line:
                target_list.append(line)
            else:
                break

    t_out = threading.Thread(target=read_stream, daemon=True, args=(proc.stdout, out_lines))
    t_err = threading.Thread(target=read_stream, daemon=True, args=(proc.stderr, err_lines))
    t_out.start()
    t_err.start()

    def poll():
        if proc.poll() is not None:
            t_out.join(3)
            t_err.join(3)
            on_completion(proc, out_lines, err_lines)
            return

        tk._default_root.after(int(poll_delay * 1000), poll)

    poll()
    return proc


class MenuEx(tk.Menu):
    def __init__(self, target):
        self._testers = {}
        super().__init__(
            target, tearoff=False, postcommand=self.on_post, **get_style_configuration("Menu")
        )

    def on_post(self, *args):
        self.update_item_availability()

    def update_item_availability(self):
        for i in range(self.index("end") + 1):
            item_data = self.entryconfigure(i)
            if "label" in item_data:
                tester = self._testers.get(item_data["label"])
                if tester and not tester():
                    self.entryconfigure(i, state=tk.DISABLED)
                else:
                    self.entryconfigure(i, state=tk.NORMAL)

    def add(self, itemType, cnf={}, **kw):
        cnf = cnf or kw
        tester = cnf.get("tester")
        if "tester" in cnf:
            del cnf["tester"]

        super().add(itemType, cnf)

        itemdata = self.entryconfigure(self.index("end"))
        labeldata = itemdata.get("label")
        if labeldata:
            self._testers[labeldata] = tester


class TextMenu(MenuEx):
    def __init__(self, target):
        self.text = target
        MenuEx.__init__(self, target)
        self.add_basic_items()
        self.add_extra_items()

    def add_basic_items(self):
        self.add_command(label=tr("Cut"), command=self.on_cut, tester=self.can_cut)
        self.add_command(label=tr("Copy"), command=self.on_copy, tester=self.can_copy)
        self.add_command(label=tr("Paste"), command=self.on_paste, tester=self.can_paste)

    def add_extra_items(self):
        self.add_separator()
        self.add_command(label=tr("Select All"), command=self.on_select_all)

    def on_cut(self):
        self.text.event_generate("<<Cut>>")

    def on_copy(self):
        self.text.event_generate("<<Copy>>")

    def on_paste(self):
        self.text.event_generate("<<Paste>>")

    def on_select_all(self):
        self.text.event_generate("<<SelectAll>>")

    def can_cut(self):
        return self.get_selected_text() and not self.selection_is_read_only()

    def can_copy(self):
        return self.get_selected_text()

    def can_paste(self):
        return not self.selection_is_read_only()

    def get_selected_text(self):
        try:
            return self.text.get("sel.first", "sel.last")
        except TclError:
            return ""

    def selection_is_read_only(self):
        if hasattr(self.text, "is_read_only"):
            return self.text.is_read_only()

        return False


def create_url_label(master, url, text=None):
    import webbrowser

    return create_action_label(master, text or url, lambda _: webbrowser.open(url))


def create_action_label(master, text, click_handler, **kw):
    url_font = tkinter.font.nametofont("TkDefaultFont").copy()
    url_font.configure(underline=1)
    url_label = ttk.Label(
        master, text=text, style="Url.TLabel", cursor="hand2", font=url_font, **kw
    )
    url_label.bind("<Button-1>", click_handler)
    return url_label


def get_size_option_name(window):
    return "layout." + type(window).__name__ + "_size"


def get_default_theme():
    if running_on_windows():
        return "Windows"
    elif running_on_rpi():
        return "Raspberry Pi"
    else:
        return "Enhanced Clam"


def get_default_basic_theme():
    if running_on_windows():
        return "xpnative"
    else:
        return "clam"


EM_WIDTH = None


def ems_to_pixels(x):
    global EM_WIDTH
    if EM_WIDTH is None:
        EM_WIDTH = tkinter.font.nametofont("TkDefaultFont").measure("m")
    return int(EM_WIDTH * x)


_btn_padding = None


def set_text_if_different(widget, text) -> bool:
    if widget["text"] != text:
        widget["text"] = text
        return True
    else:
        return False


def tr_btn(s):
    """Translates button caption, adds padding to make sure text fits"""
    global _btn_padding
    if _btn_padding is None:
        _btn_padding = get_button_padding()

    return _btn_padding + tr(s) + _btn_padding


def add_messagebox_parent_checker():
    def wrap_with_parent_checker(original):
        def wrapper(*args, **options):
            _check_dialog_parent(options)
            return original(*args, **options)

        return wrapper

    from tkinter import messagebox

    for name in [
        "showinfo",
        "showwarning",
        "showerror",
        "askquestion",
        "askokcancel",
        "askyesno",
        "askyesnocancel",
        "askretrycancel",
    ]:
        fun = getattr(messagebox, name)
        setattr(messagebox, name, wrap_with_parent_checker(fun))


if __name__ == "__main__":
    root = tk.Tk()
