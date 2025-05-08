# -*- coding: utf-8 -*-
import os
import platform
import re
import subprocess
import sys
import textwrap
import threading
import time
import tkinter as tk
import tkinter.font
import traceback
from dataclasses import dataclass
from logging import getLogger
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union  # @UnusedImport

from _tkinter import TclError

from thonny import get_workbench, misc_utils, tktextext
from thonny.common import TextRange, normpath_with_actual_case
from thonny.custom_notebook import CustomNotebook, CustomNotebookPage
from thonny.languages import get_button_padding, tr
from thonny.misc_utils import running_on_linux, running_on_mac_os, running_on_windows
from thonny.tktextext import TweakableText

PARENS_REGEX = re.compile(r"[\(\)\{\}\[\]]")

logger = getLogger(__name__)


# Using tk.Frame instead of ttk.Frame, because Aqua theme doesn't allow changing Frame background
class CustomToolbutton(tk.Frame):
    def __init__(
        self,
        master,
        command: Callable = None,
        style: Optional[str] = None,
        image=None,
        state="normal",
        text=None,
        compound=None,
        width=None,
        pad=None,
        font=None,
        background=None,
        foreground=None,
        borderwidth=0,
    ):
        if isinstance(image, (list, tuple)):
            self.normal_image = image[0]
            self.disabled_image = image[-1]
        else:
            self.normal_image = image
            self.disabled_image = image

        self.state = state
        self.style = style
        self.background = background
        self.foreground = foreground
        self.prepare_style_options()

        if state == "disabled":
            self.current_image = self.disabled_image
        else:
            self.current_image = self.normal_image

        super().__init__(
            master, background=self.normal_background, borderwidth=borderwidth, relief="solid"
        )
        kw = {}
        if font is not None:
            kw["font"] = font

        self.label = tk.Label(
            self,
            image=self.current_image,
            text=text,
            compound=compound,
            width=None if width is None else ems_to_pixels(width - 1),
            background=self.normal_background,
            foreground=self.normal_foreground,
            **kw,
        )

        # TODO: introduce padx and pady arguments
        if isinstance(pad, int):
            padx = pad
            pady = pad
        elif isinstance(pad, (tuple, list)):
            assert len(pad) == 2
            # TODO: how to use it?
            padx = pad
            pady = 0
        else:
            padx = None
            pady = None

        if text and not image:
            # text only button content needs adjustment
            pady = pady or 0
            pady = (pady, pady + ems_to_pixels(0.23))

        self.label.grid(row=0, column=0, padx=padx, pady=pady, sticky="nsew")
        self.command = command
        self.bind("<1>", self.on_click, True)
        self.label.bind("<1>", self.on_click, True)
        self.bind("<Enter>", self.on_enter, True)
        self.bind("<Leave>", self.on_leave, True)

        self._on_theme_changed_binding = self.bind("<<ThemeChanged>>", self.on_theme_changed, True)

    def cget(self, key: str) -> Any:
        if key in ["text", "image"]:
            return self.label.cget(key)
        else:
            return super().cget(key)

    def on_click(self, event):
        if self.state == "normal":
            self.command()

    def on_enter(self, event):
        if self.state == "normal":
            super().configure(background=self.hover_background)
            self.label.configure(background=self.hover_background)

    def on_leave(self, event):
        super().configure(background=self.normal_background)
        self.label.configure(background=self.normal_background)

    def configure(self, cnf={}, state=None, image=None, command=None, background=None, **kw):
        if command:
            self.command = command

        if "state" in cnf and not state:
            state = cnf.get("state")
        elif not state:
            state = "normal"

        self.state = state
        if image:
            self.current_image = image
        elif self.state == "disabled":
            self.current_image = self.disabled_image
        else:
            self.current_image = self.normal_image

        super().configure(background=background)
        # tkinter.Frame should be always state=normal as it won't display the image if "disabled"
        # at least on mac with Tk 8.6.13
        self.label.configure(
            cnf, image=self.current_image, state="normal", background=background, **kw
        )

    def on_theme_changed(self, event):
        self.prepare_style_options()
        self.configure(background=self.normal_background, foreground=self.normal_foreground)

    def prepare_style_options(self):
        style_conf = get_style_configuration("CustomToolbutton")
        if self.style:
            style_conf |= get_style_configuration(self.style)
        self.normal_background = self.background or style_conf["background"]
        self.normal_foreground = self.foreground or style_conf["foreground"]
        self.hover_background = style_conf["activebackground"]

    def destroy(self):
        if not get_workbench().is_closing():
            try:
                self.unbind("<<ThemeChanged>>", self._on_theme_changed_binding)
            except Exception:
                pass
        super().destroy()


class CommonDialog(tk.Toplevel):
    def __init__(self, master=None, skip_tk_dialog_attributes=False, **kw):
        assert master
        super().__init__(master=master, class_="Thonny", **kw)
        self.withdraw()  # remain invisible until size calculations are done

        # Opening a dialog and minimizing everything with Win-D in Windows makes the main
        # window and dialog stuck. This is a work-around.
        self.bind("<FocusIn>", self._unlock_on_focus_in, True)

        if not skip_tk_dialog_attributes:
            # https://bugs.python.org/issue43655
            if self._windowingsystem == "aqua":
                self.tk.call(
                    "::tk::unsupported::MacWindowStyle", "style", self, "moveableModal", "closeBox"
                )
            elif self._windowingsystem == "x11":
                self.wm_attributes("-type", "dialog")

        self.resizable(True, True)
        self.parent = master

    def _unlock_on_focus_in(self, event):
        if not self.winfo_ismapped():
            focussed_widget = self.focus_get()
            self.deiconify()
            if focussed_widget:
                focussed_widget.focus_set()

    def get_large_padding(self):
        return ems_to_pixels(1.5)

    def get_medium_padding(self):
        return ems_to_pixels(1)

    def get_small_padding(self):
        return ems_to_pixels(0.6)

    def set_initial_focus(self, node=None) -> bool:
        if node is None:
            node = self

        if isinstance(
            node,
            (
                ttk.Entry,
                ttk.Combobox,
                ttk.Treeview,
                tk.Text,
                ttk.Notebook,
                CustomNotebook,
                ttk.Button,
                tk.Listbox,
            ),
        ):
            node.focus_set()
            return True

        else:
            for child in node.winfo_children():
                if self.set_initial_focus(child):
                    return True

        return False


class CommonDialogEx(CommonDialog):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Need to fill the dialog with a frame to gain theme support
        self.main_frame = ttk.Frame(self)

        # ipady doesn't work right, at least on Linux (it only applies to the first gridded child)
        # therefore only providing common padding for left and right edges
        self.main_frame.grid(row=0, column=0, sticky="nsew", ipadx=self.get_large_padding())
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

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

        margin = self.get_large_padding()
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


class WorkbenchPanedWindow(tk.PanedWindow):
    def __init__(
        self,
        master: tk.Widget,
        orient: Literal["horizontal", "vertical"],
        size_config_key: Optional[str] = None,
    ):
        self.size_config_key = size_config_key
        super().__init__(master, orient=orient)
        self._update_appearance_binding = self.bind(
            "<<ThemeChanged>>", self._update_appearance, True
        )
        self._update_appearance()

    def all_children_hidden(self):
        for child in self.panes():
            if not self.panecget(child, "hide"):
                return False

        return True

    def update_visibility(self):
        if isinstance(self.master, tk.PanedWindow):
            should_be_hidden = self.all_children_hidden()
            if self.winfo_ismapped() and should_be_hidden and self.size_config_key is not None:
                if self.cget("orient") == "vertical":
                    value = self.winfo_width()
                else:
                    value = self.winfo_height()

                get_workbench().set_option(self.size_config_key, value)

            self.master.paneconfig(self, hide=should_be_hidden)

    def _update_appearance(self, event=None):
        self.configure(sashwidth=lookup_style_option("Sash", "sashthickness", ems_to_pixels(0.6)))
        self.configure(background=lookup_style_option(".", "background"))

    def destroy(self):
        self.unbind("<<ThemeChanged>>", self._update_appearance_binding)
        super().destroy()

    def has_several_visible_panes(self):
        count = 0
        for child in self.winfo_children():
            if child.winfo_ismapped():
                count += 1

        return count > 1


class ViewNotebook(CustomNotebook):
    """
    Enables inserting views according to their position keys.
    Remember its own position key. Automatically updates its visibility.
    """

    def __init__(self, master, location_in_workbench, position_key):
        self.location_in_workbench = location_in_workbench
        if get_workbench().in_simple_mode():
            closable = False
        else:
            closable = True
        super().__init__(master, closable=closable)
        self.position_key = position_key

    def forget(self, child: tk.Widget) -> None:
        if (
            isinstance(self.master, WorkbenchPanedWindow)
            and self.master.has_several_visible_panes()
        ):
            close_height = self.winfo_height()
            get_workbench().set_option(
                f"layout.{self.location_in_workbench}_nb_height", close_height
            )

        super().forget(child)

    def after_insert(
        self,
        pos: Union[int, Literal["end"]],
        page: CustomNotebookPage,
        old_notebook: Optional[CustomNotebook],
    ) -> None:
        super().after_insert(pos, page, old_notebook)
        self._update_visibility()
        if old_notebook is None:
            get_workbench().event_generate("NotebookPageOpened", page=page)
        else:
            get_workbench().event_generate(
                "NotebookPageMoved", page=page, new_notebook=self, old_notebook=old_notebook
            )

    def after_forget(
        self, pos: int, page: CustomNotebookPage, new_notebook: Optional[CustomNotebook]
    ):
        # see the comment at after_add_or_insert
        super().after_forget(pos, page, new_notebook)
        self._update_visibility()
        if new_notebook is None:
            get_workbench().event_generate("NotebookPageClosed", page=page)
        # if there is new_notebook, then Workbench gets its Moved event from it

    def _is_visible(self):
        return self.winfo_ismapped()

    def _update_visibility(self):
        if isinstance(self.master, WorkbenchPanedWindow):
            if len(self.tabs()) == 0 and self._is_visible():
                self.master.paneconfig(self, hide=True)

            if len(self.tabs()) > 0 and not self._is_visible():
                self.master.paneconfig(self, hide=False)

            self.master.update_visibility()

    def allows_dragging_to_another_notebook(self) -> bool:
        return True


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
        consider_heading_stripe=True,
        **tree_kw,
    ):
        ttk.Frame.__init__(self, master, borderwidth=borderwidth, relief=relief)
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        if show_scrollbar:
            self.vert_scrollbar.grid(
                row=0, column=1, sticky=tk.NSEW, rowspan=2 if show_statusbar else 1
            )
            scrollbar_stripe = check_create_aqua_scrollbar_stripe(self)
            if scrollbar_stripe is not None:
                scrollbar_stripe.grid(
                    row=0, column=1, sticky="nse", rowspan=2 if show_statusbar else 1
                )
                scrollbar_stripe.tkraise()

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            displaycolumns=displaycolumns,
            yscrollcommand=self.vert_scrollbar.set,
            **tree_kw,
        )
        self.tree["show"] = "headings"
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        if consider_heading_stripe:
            heading_stripe = check_create_heading_stripe(self)
            if heading_stripe is not None:
                heading_stripe.grid(row=0, column=0, sticky="new")
                heading_stripe.tkraise()
        self.vert_scrollbar["command"] = self.tree.yview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_select, "+")
        self.tree.bind("<Double-Button-1>", self.on_double_click, "+")
        self.tree.bind("<Button-3>", self.on_secondary_click, True)
        if misc_utils.running_on_mac_os():
            self.tree.bind("<2>", self.on_secondary_click, True)
            self.tree.bind("<Control-1>", self.on_secondary_click, True)

        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(command=self.on_copy, label="Copy")

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

    def on_secondary_click(self, event):
        self.tree.identify_row(event.y)
        self.context_menu.post(event.x_root, event.y_root)

    def on_copy(self):
        texts = []
        for item in self.tree.selection():
            text = self.tree.item(item, option="text")
            values = map(str, self.tree.item(item, option="values"))
            combined = text + "\t" + "\t".join(values)
            texts.append(combined.strip("\t"))
        self.clipboard_clear()
        self.clipboard_append(os.linesep.join(texts))

    def on_select(self, event):
        pass

    def on_double_click(self, event):
        pass

    def show_error(self, error_text):
        self.error_label.configure(text=error_text)
        self.error_label.grid()

    def clear_error(self):
        self.error_label.grid_remove()


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
        .replace("space", "Space")
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
    def __init__(
        self,
        master,
        indent_width: int,
        tab_width: int,
        style="Text",
        tag_current_line=False,
        cnf={},
        **kw,
    ):
        super().__init__(
            master=master,
            indent_width=indent_width,
            tab_width=tab_width,
            style=style,
            tag_current_line=tag_current_line,
            cnf=cnf,
            **kw,
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
        if not self._suppress_events:
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
                concrete_index2 = self.index(index1 + " +1c")

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
            if not self._suppress_events:
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
        self.hide_count = 0
        self.gridded = False
        super().__init__(master=master, **kw)

    def set(self, first, last):
        if float(first) <= 0.0 and float(last) >= 1.0:
            # Need to accept 1 automatic hide, otherwise even narrow files
            # get horizontal scrollbar
            if self.gridded and self.hide_count < 2:
                self.grid_remove()
        elif float(first) > 0.001 or float(last) < 0.999:
            # with >0 and <1 it occasionally made scrollbar wobble back and forth
            if not self.gridded:
                self.grid()
        ttk.Scrollbar.set(self, first, last)

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        self.gridded = True

    def grid_configure(self, *args, **kwargs):
        super().grid_configure(*args, **kwargs)
        self.gridded = True

    def grid_remove(self):
        super().grid_remove()
        self.gridded = False
        self.hide_count += 1

    def grid_forget(self):
        super().grid_forget()
        self.gridded = False
        self.hide_count += 1

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
        self.widget: tk.Widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.options = options
        self.focus_out_bind_ref = None

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return

        # x = self.widget.winfo_pointerx() + ems_to_pixels(0)
        # y = self.widget.winfo_pointery() + ems_to_pixels(0.8)
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx()
        y = y + self.widget.winfo_rooty() + self.widget.winfo_height() + ems_to_pixels(0.2)
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
        self.focus_out_bind_ref = self.widget.winfo_toplevel().bind(
            "<FocusOut>", self.hidetip, True
        )

    def hidetip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if self.tipwindow:
            self.widget.unbind("<FocusOut>", self.focus_out_bind_ref)
        if tw:
            tw.destroy()


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

    widget.bind("<Enter>", enter, True)
    widget.bind("<Leave>", leave, True)


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


class HeadingStripe(tk.Frame):
    def __init__(self, master, height, background):
        super().__init__(master, height=height, background=background)
        self._on_theme_changed_binding = self.bind("<<ThemeChanged>>", self.on_theme_changed, True)

    def on_theme_changed(self, event=None):
        opts = get_style_configuration("Heading")
        px_to_hide = opts.get("topmost_pixels_to_hide", 0)
        if isinstance(px_to_hide, list):
            # don't know why it happens sometimes
            assert len(px_to_hide) == 1
            px_to_hide = px_to_hide[0]
        background = opts.get("background")
        self.configure(height=px_to_hide, background=background)

    def destroy(self):
        self.unbind(self._on_theme_changed_binding)
        super().destroy()


class ScrollbarStripe(tk.Frame):
    def __init__(self, master, stripe_width):
        # Want to cover a gray stripe on the right edge of the scrollbar.

        super().__init__(master, width=stripe_width, background=self.get_background())
        self._on_theme_changed_binding = self.bind("<<ThemeChanged>>", self.on_theme_changed, True)

    def get_background(self):
        # Not sure if it is good idea to use fixed colors, but no named (light-dark aware) color matches.
        # Best dynamic alternative is probably systemTextBackgroundColor
        if os_is_in_dark_mode():
            return "#2d2e31"
        else:
            return "#fafafa"

    def on_theme_changed(self, event=None):
        px_to_hide = lookup_style_option("Vertical.TScrollbar", "rightmost_pixels_to_hide", 0)
        if px_to_hide == 0:
            self.grid_remove()
        else:
            self.grid()
            self.configure(background=self.get_background())

    def destroy(self):
        self.unbind(self._on_theme_changed_binding)
        super().destroy()


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


def shift_is_pressed(event: tk.Event) -> bool:
    # https://tkdocs.com/shipman/event-handlers.html
    # http://stackoverflow.com/q/32426250/261181
    return event.state & 0x0001


def caps_lock_is_on(event: tk.Event) -> bool:
    # https://tkdocs.com/shipman/event-handlers.html
    # http://stackoverflow.com/q/32426250/261181
    return event.state & 0x0002


def control_is_pressed(event: tk.Event) -> bool:
    # https://tkdocs.com/shipman/event-handlers.html
    # http://stackoverflow.com/q/32426250/261181
    return event.state & 0x0004


def alt_is_pressed_without_char(event: tk.Event) -> bool:
    # https://tkdocs.com/shipman/event-handlers.html
    # http://stackoverflow.com/q/32426250/261181
    # https://bugs.python.org/msg268429
    if event.char:
        return False

    if running_on_windows():
        return event.state & 0x20000
    elif running_on_mac_os():
        # combinations always produce a char or are consumed by the OS
        return False
    else:
        return event.state & 0x0010


def command_is_pressed(event: tk.Event) -> bool:
    # https://tkdocs.com/shipman/event-handlers.html
    # http://stackoverflow.com/q/32426250/261181
    if not running_on_mac_os():
        return False
    return event.state & 0x0008


def get_hyperlink_cursor() -> str:
    if running_on_mac_os():
        return "pointinghand"
    else:
        return "hand2"


def get_beam_cursor() -> str:
    if running_on_mac_os() or running_on_windows():
        return "ibeam"
    else:
        return "xterm"


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
    # https://tkdocs.com/shipman/event-handlers.html
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


# Place a toplevel window at the center of parent or screen
# It is a Python implementation of ::tk::PlaceWindow.
# Copied and adapted from tkinter.simpledialog of Python 3.10.2
def _place_window(w, parent=None, width=None, height=None):
    w.wm_withdraw()  # Remain invisible while we figure out the geometry
    w.update_idletasks()  # Actualize geometry information

    minwidth = width or w.winfo_reqwidth()
    minheight = height or w.winfo_reqheight()
    maxwidth = w.winfo_vrootwidth()
    maxheight = w.winfo_vrootheight()
    if parent is not None and parent.winfo_ismapped():
        logger.info(
            f"Parent y: {parent.winfo_y()}, rooty: {parent.winfo_rooty()}, vrooty: {parent.winfo_vrooty()}"
        )
        x = parent.winfo_rootx() + (parent.winfo_width() - minwidth) // 2
        y = parent.winfo_y() + (parent.winfo_height() - minheight) // 2
        vrootx = w.winfo_vrootx()
        vrooty = w.winfo_vrooty()
        x = min(x, vrootx + maxwidth - minwidth)
        x = max(x, vrootx)
        y = min(y, vrooty + maxheight - minheight)
        # don't allow the dialog go higher than parent. This way the title bar remains visible.
        y = max(y, vrooty, parent.winfo_y())
        if w._windowingsystem == "aqua":
            # Avoid the native menu bar which sits on top of everything.
            y = max(y, ems_to_pixels(2))

        if y + minheight > maxheight:
            logger.debug("Aligning top with parent (%s vs %s)", y + minheight, maxheight)
            y = parent.winfo_y()
    else:
        x = (w.winfo_screenwidth() - minwidth) // 2
        y = (w.winfo_screenheight() - minheight) // 2

    w.wm_maxsize(maxwidth, maxheight)
    if width and height:
        geometry = "%dx%d+%d+%d" % (width, height, x, y)
    else:
        geometry = "+%d+%d" % (x, y)

    logger.info(f"Placing {w} with geometry {geometry}")
    w.wm_geometry(geometry)
    w.wm_deiconify()  # Become visible at the desired location


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
        self.result = None
        super().__init__(master=master)

        self.title(title)
        self.resizable(False, False)

        self.main_frame.columnconfigure(0, weight=1)

        row = 0
        question_label = ttk.Label(self.main_frame, text=question)
        question_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=20)
        row += 1

        self.var = tk.StringVar(value="")
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
    if platform.system() == "Linux" and get_workbench().get_option("file.use_zenity"):
        return _ZenityDialogProvider

    # fallback
    return filedialog


def try_restore_focus_after_file_dialog(dialog_parent):
    if dialog_parent is None:
        return

    logger.info("Restoring focus to %s", dialog_parent)
    old_focused_widget = dialog_parent.winfo_toplevel().focus_get()

    dialog_parent.winfo_toplevel().lift()
    dialog_parent.winfo_toplevel().focus_force()
    dialog_parent.winfo_toplevel().grab_set()
    if running_on_mac_os():
        dialog_parent.winfo_toplevel().grab_release()

    if old_focused_widget is not None:
        try:
            old_focused_widget.focus_force()
        except TclError:
            logger.warning("Could not restore focus to %r", old_focused_widget)


def asksaveasfilename(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/getOpenFile.htm
    parent = _check_dialog_parent(options)
    try:
        result = _get_dialog_provider().asksaveasfilename(**options)
        # Different tkinter versions may return different values
        if result in ["", (), None]:
            return None

        if running_on_windows():
            # may have /-s instead of \-s and wrong case
            return os.path.join(
                normpath_with_actual_case(os.path.dirname(result)),
                os.path.basename(result),
            )
        else:
            return result
    finally:
        try_restore_focus_after_file_dialog(parent)


def askopenfilename(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/getOpenFile.htm
    parent = _check_dialog_parent(options)
    try:
        return _get_dialog_provider().askopenfilename(**options)
    finally:
        try_restore_focus_after_file_dialog(parent)


def askopenfilenames(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/getOpenFile.htm
    parent = _check_dialog_parent(options)
    try:
        return _get_dialog_provider().askopenfilenames(**options)
    finally:
        try_restore_focus_after_file_dialog(parent)


def askdirectory(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/chooseDirectory.htm
    parent = _check_dialog_parent(options)
    try:
        return _get_dialog_provider().askdirectory(**options)
    finally:
        try_restore_focus_after_file_dialog(parent)


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

    return parent


class _ZenityDialogProvider:
    # https://www.writebash.com/bash-gui/zenity-create-file-selection-dialog-224.html
    # http://linux.byexamples.com/archives/259/a-complete-zenity-dialog-examples-1/
    # http://linux.byexamples.com/archives/265/a-complete-zenity-dialog-examples-2/

    # another possibility is to use PyGobject: https://github.com/poulp/zenipy

    @classmethod
    def askopenfilename(cls, **options):
        if not cls._check_zenity_exists(options["parent"]):
            return None

        args = cls._convert_common_options("Open file", **options)
        return cls._call(args)

    @classmethod
    def askopenfilenames(cls, **options):
        if not cls._check_zenity_exists(options["parent"]):
            return None

        args = cls._convert_common_options("Open files", **options)
        return cls._call(args + ["--multiple"]).split("|")

    @classmethod
    def asksaveasfilename(cls, **options):
        if not cls._check_zenity_exists(options["parent"]):
            return None

        args = cls._convert_common_options("Save as", **options)
        args.append("--save")

        filename = cls._call(args)
        if not filename:
            return None

        return filename

    @classmethod
    def askdirectory(cls, **options):
        if not cls._check_zenity_exists(options["parent"]):
            return None

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
    def _check_zenity_exists(cls, parent) -> bool:
        import shutil

        if shutil.which("zenity"):
            return True
        else:
            messagebox.showerror(
                tr("Error"),
                "Could not find 'zenity'. Is it installed?\n"
                "Please install it or turn off Zenity file dialogs?",
            )
            return False

    @classmethod
    def _call(cls, args):
        args = ["zenity"] + args
        result = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logger.warning(
                "Zenity returned code %r and stderr %r", result.returncode, result.stderr
            )
            return None


def _options_to_zenity_filename(options):
    if options.get("initialdir"):
        if options.get("initialfile"):
            return os.path.join(options["initialdir"], options["initialfile"])
        else:
            return options["initialdir"] + os.path.sep

    return None


class _CustomDialogProvider:
    @classmethod
    def askopenfilename(cls, **options):
        return cls._call("open", **options)

    @classmethod
    def askopenfilenames(cls, **options):
        raise NotImplementedError()

    @classmethod
    def asksaveasfilename(cls, **options):
        return cls._call("save", **options)

    @classmethod
    def askdirectory(cls, **options):
        return cls._call("dir", **options)

    @classmethod
    def _call(cls, kind: Literal["save", "open", "dir"], **options):
        from thonny.base_file_browser import (
            FILE_DIALOG_HEIGHT_EMS_OPTION,
            FILE_DIALOG_WIDTH_EMS_OPTION,
            LocalFileDialog,
        )

        master = options.get("parent") or options.get("master") or get_workbench()
        initial_dir = options.get("initialdir") or get_workbench().get_local_cwd()
        dlg = LocalFileDialog(
            master,
            kind=kind,
            initial_dir=initial_dir,
            filetypes=options.get("filetypes"),
            typevariable=options.get("typevariable"),
        )
        show_dialog(
            dlg,
            master,
            width=ems_to_pixels(get_workbench().get_option(FILE_DIALOG_WIDTH_EMS_OPTION)),
            height=ems_to_pixels(get_workbench().get_option(FILE_DIALOG_HEIGHT_EMS_OPTION)),
        )
        return dlg.result


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
    if shift_is_pressed(event):
        simplified_state |= 0x01

    # print(simplified_state, event.keycode)
    if (simplified_state, event.keycode) in registry:
        if event.keycode != ord(event.char) and event.keysym in (None, "??"):
            # keycode and char doesn't match,
            # this means non-latin keyboard
            for handler, tester in registry[(simplified_state, event.keycode)]:
                if tester is None or tester():
                    handler()


def show_dialog(
    dlg, master=None, width=None, height=None, left=None, top=None, modal=True, transient=True
):
    if getattr(dlg, "closed", False):
        return

    if master is None:
        master = getattr(dlg, "parent", None) or getattr(dlg, "master", None) or tk._default_root

    master = master.winfo_toplevel()

    get_workbench().event_generate("WindowFocusOut")
    # following order seems to give most smooth appearance
    old_focused_widget = master.focus_get()
    if transient and master.winfo_toplevel().winfo_viewable():
        dlg.transient(master.winfo_toplevel())

    saved_size = get_workbench().get_option(get_size_option_name(dlg))
    if saved_size:
        width = min(max(saved_size[0], ems_to_pixels(10)), ems_to_pixels(500))
        height = min(max(saved_size[1], ems_to_pixels(8)), ems_to_pixels(300))

    _place_window(dlg, master, width=width, height=height)

    dlg.lift()
    try:
        dlg.wait_visibility()
    except tk.TclError as e:
        if "was deleted before its visibility changed" in str(e):
            return
        else:
            raise

    if modal:
        try:
            dlg.grab_set()
        except TclError as e:
            logger.warning("Can't grab: %s", e)

    dlg.update_idletasks()
    dlg.focus_set()
    if hasattr(dlg, "set_initial_focus"):
        dlg.set_initial_focus()

    if modal:
        dlg.wait_window(dlg)
        dlg.grab_release()
        master.winfo_toplevel().lift()
        master.winfo_toplevel().focus_force()
        master.winfo_toplevel().grab_set()
        if running_on_mac_os():
            master.winfo_toplevel().grab_release()

        if old_focused_widget is not None:
            try:
                old_focused_widget.focus_force()
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


def create_url_label(master, url, text=None, **kw):
    import webbrowser

    return create_action_label(master, text or url, lambda _: webbrowser.open(url), **kw)


def create_action_label(master, text, click_handler, **kw):
    url_font = tkinter.font.nametofont("TkDefaultFont").copy()
    url_font.configure(underline=1)
    url_label = ttk.Label(
        master, text=text, style="Url.TLabel", cursor=get_hyperlink_cursor(), font=url_font, **kw
    )
    url_label.bind("<Button-1>", click_handler)
    return url_label


def get_size_option_name(window):
    return "layout." + type(window).__name__ + "_size"


def get_default_basic_theme():
    if running_on_windows():
        return "vista"
    elif running_on_mac_os():
        return "aqua"
    else:
        return "clam"


EM_WIDTH = None


def ems_to_pixels(x: float) -> int:
    global EM_WIDTH
    if EM_WIDTH is None:
        EM_WIDTH = tkinter.font.nametofont("TkDefaultFont").measure("m")
    return int(EM_WIDTH * x)


def pixels_to_ems(x: int) -> float:
    global EM_WIDTH
    if EM_WIDTH is None:
        EM_WIDTH = tkinter.font.nametofont("TkDefaultFont").measure("m")
    return x / EM_WIDTH


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


def replace_unsupported_chars(text: str) -> str:
    if get_tk_version_info() < (8, 6, 12):
        # can crash with emojis
        return "".join(c if c < "\U00010000" else "□" for c in text)
    else:
        return text


def windows_known_extensions_are_hidden() -> bool:
    assert running_on_windows()
    import winreg

    reg_key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        0,
        winreg.KEY_READ,
    )
    try:
        return winreg.QueryValueEx(reg_key, "HideFileExt")[0] == 1
    finally:
        reg_key.Close()


class MappingCombobox(ttk.Combobox):
    def __init__(
        self, master, mapping: Dict[str, Any], value_variable: Optional[tk.Variable] = None, **kw
    ):
        self.mapping = mapping
        self.value_variable = value_variable
        self.mapping_desc_variable = tk.StringVar(value="")

        super().__init__(master, **kw)
        self.set_mapping(mapping)
        self.configure(textvariable=self.mapping_desc_variable)

        if kw.get("state", None) == "disabled":
            self.state(["readonly"])
        else:
            self.state(["!disabled", "readonly"])

        self.bind("<<ComboboxSelected>>", self.on_select_value, True)

        if self.value_variable is not None:
            self.select_value(self.value_variable.get())

    def set_mapping(self, mapping: Dict[str, Any]):
        self.mapping = mapping
        self["values"] = list(mapping)
        self.select_clear()

    def add_pair(self, label, value):
        self.mapping[label] = value
        self["values"] = list(self.mapping)

    def on_select_value(self, *event):
        if self.value_variable is not None:
            self.value_variable.set(self.get_selected_value())
        self.select_clear()

    def get_selected_value(self) -> Any:
        desc = self.mapping_desc_variable.get()
        return self.mapping.get(desc, None)

    def select_first_value(self) -> None:
        self.select_value(next(iter(self.mapping.values())))

    def select_value(self, value) -> None:
        for desc in self.mapping:
            if self.mapping[desc] == value:
                self.set(desc)

    def select_none(self) -> None:
        self.mapping_desc_variable.set("")


class AdvancedLabel(ttk.Label):
    def __init__(self, master, **kw):
        self._default_font = tkinter.font.nametofont("TkDefaultFont")
        self._url_font = self._default_font.copy()
        self._url_font.configure(underline=1)
        self._url = None
        super().__init__(master, **kw)
        self.bind("<Button-1>", self._on_click, True)

    def set_url(self, url: Optional[str]) -> None:
        if self._url == url:
            return

        self._url = url
        if url:
            self.configure(style="Url.TLabel", cursor=get_hyperlink_cursor(), font=self._url_font)
        else:
            self.configure(style="TLabel", cursor="", font=self._default_font)

    def get_url(self) -> Optional[str]:
        return self._url

    def _on_click(self, *event):
        if self._url:
            if os.path.isdir(self._url):
                open_with_default_app(self._url)
            else:
                import webbrowser

                webbrowser.open(self._url)


def os_is_in_dark_mode() -> Optional[bool]:
    if running_on_mac_os():
        try:
            return bool(
                int(
                    tk._default_root.eval(
                        f"tk::unsupported::MacWindowStyle isdark {tk._default_root}"
                    )
                )
            )
        except Exception:
            logger.exception("Could not query for dark mode")
            return None

    return None


def check_create_aqua_scrollbar_stripe(master) -> Optional[tk.Frame]:
    stripe_width = lookup_style_option("Vertical.TScrollbar", "rightmost_pixels_to_hide", 0)
    if stripe_width > 0:
        return ScrollbarStripe(master, stripe_width)
    else:
        return None


def check_create_heading_stripe(master) -> Optional[tk.Frame]:
    opts = get_style_configuration("Heading")
    px_to_hide = opts.get("topmost_pixels_to_hide", 0)
    if isinstance(px_to_hide, list):
        # don't know why it happens sometimes
        assert len(px_to_hide) == 1
        px_to_hide = px_to_hide[0]
    elif isinstance(px_to_hide, str):
        px_to_hide = int(px_to_hide)
    background = opts.get("background")
    if px_to_hide > 0 and background is not None:
        return HeadingStripe(master, height=px_to_hide, background=background)
    else:
        return None


def open_with_default_app(path):
    if running_on_windows():
        os.startfile(path)
    elif running_on_mac_os():
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])


def compute_tab_stops(tab_width_in_chars: int, font: tk.font.Font, offset_px=0) -> List[int]:
    tab_pixels = font.measure("n" * tab_width_in_chars)

    tabs = []
    if offset_px > 0:
        tabs.append(offset_px)

    for _ in range(20):
        offset_px += tab_pixels
        tabs.append(offset_px)

    return tabs


def get_last_grid_row(container: tk.Widget) -> int:
    return container.grid_size()[1] - 1


def create_custom_toolbutton_in_frame(master, borderwidth, bordercolor, **kwargs):
    frame = tk.Frame(master, background=bordercolor)
    frame.button = CustomToolbutton(frame, **kwargs)
    frame.button.grid(pady=borderwidth, padx=borderwidth)
    return frame


def set_windows_titlebar_darkness(window: tk.Tk, value: int):
    import ctypes

    window.update()
    winfo_id = window.winfo_id()
    hwnd = ctypes.windll.user32.GetParent(winfo_id)
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19

    # try with DWMWA_USE_IMMERSIVE_DARK_MODE
    result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWA_USE_IMMERSIVE_DARK_MODE,
        ctypes.byref(ctypes.c_int(value)),
        ctypes.sizeof(ctypes.c_int(value)),
    )
    if result != 0:
        result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
            ctypes.byref(ctypes.c_int(value)),
            ctypes.sizeof(ctypes.c_int(value)),
        )
        print("got with second", result)
    else:
        print("got with first", result)


def update_text_height(text: tk.Text, min_lines: int, max_lines: int) -> None:
    if text.winfo_width() < 10:
        logger.info("Skipping text height update because width is %s", text.winfo_width())
        return
    required_height = text.tk.call((text, "count", "-update", "-displaylines", "1.0", "end"))
    text.configure(height=min(max(required_height, min_lines), max_lines))


@dataclass
class TreeviewLayout:
    open_ids: List[str]
    first_visible_iid: str
    selection: Tuple[str]


def export_treeview_layout(tree: ttk.Treeview) -> TreeviewLayout:
    first_visible_iid = tree.identify_row(0)

    return TreeviewLayout(
        open_ids=get_treeview_open_item_ids(tree),
        first_visible_iid=first_visible_iid,
        selection=tree.selection(),
    )


def restore_treeview_layout(tree: ttk.Treeview, state: TreeviewLayout) -> None:
    def open_close_nodes(iid):
        tree.item(iid, open=iid in state.open_ids)
        for child_iid in tree.get_children(iid):
            open_close_nodes(child_iid)

    open_close_nodes("")

    selection = [iid for iid in state.selection if tree.exists(iid)]
    tree.selection_set(selection)

    if tree.exists(state.first_visible_iid):
        tree.see(state.first_visible_iid)


def get_treeview_open_item_ids(tree: ttk.Treeview, parent: str = "") -> List[str]:
    result = []
    for child in tree.get_children(parent):
        if tree.item(child, "open"):
            result.append(child)
            result.extend(get_treeview_open_item_ids(tree, child))

    return result


def parse_text_index(index: str) -> Tuple[int, int]:
    line, col = map(int, index.split(".", maxsplit=1))
    return line, col


if __name__ == "__main__":
    print(windows_known_extensions_are_hidden())
