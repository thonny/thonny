from __future__ import annotations

import sys
import tkinter as tk
from logging import getLogger
from tkinter import ttk
from typing import Dict, List, Literal, Optional, Union

from thonny.languages import tr

logger = getLogger(__name__)


class CustomNotebook(tk.Frame):
    def __init__(self, master: Union[tk.Widget, tk.Toplevel, tk.Tk], closable: bool = True):
        self.base_style_conf = _get_style_configuration(".")
        self.style_conf = _get_style_configuration("CustomNotebook")
        super().__init__(master, background=self.style_conf["bordercolor"])
        self.closable = closable
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Can't use ttk.Frame, because can't change its color in aqua
        self.tab_row = tk.Frame(self, background=self.style_conf["bordercolor"])
        self.tab_row.grid(row=0, column=0, sticky="new")

        self.filler = tk.Frame(self.tab_row, background=self.base_style_conf["background"])
        self.filler.grid(row=0, column=999, sticky="nsew", padx=(1, 0), pady=(0, 1))
        self.tab_row.columnconfigure(999, weight=1)

        self.current_page: Optional[CustomNotebookPage] = None
        self.pages: List[CustomNotebookPage] = []

    def add(self, child: tk.Widget, text: str) -> None:
        self.insert("end", child, text=text)

    def insert(self, pos: Union[int, Literal["end"]], child: tk.Widget, text: str) -> None:
        tab = CustomNotebookTab(self, title=text, closable=self.closable)
        page = CustomNotebookPage(tab, child)
        if pos == "end":
            self.pages.append(page)
        else:
            self.pages.insert(self.index(pos), page)

        self._rearrange_tabs()
        self.select_tab(page.tab)

    def _rearrange_tabs(self) -> None:
        for i, page in enumerate(self.pages):
            page.tab.grid(row=0, column=i, sticky="nsew", padx=(1, 0), pady=(1, 0))

    def enable_traversal(self) -> None:
        # TODO:
        pass

    def select(self, tab_id: Union[str, tk.Widget, None] = None) -> Optional[str]:
        if tab_id is None:
            if self.current_page:
                return self.current_page.content.winfo_name()
            return None

        return self.select_by_index(self.index(tab_id))

    def select_by_index(self, index: int) -> None:
        new_page = self.pages[index]
        if new_page == self.current_page:
            return

        new_page.content.grid_propagate(False)
        new_page.content.grid(row=1, column=0, sticky="nsew", padx=(1, 1), pady=(0, 1))
        if self.current_page:
            self.current_page.content.grid_remove()
            # new_page.content.tkraise(self.current_page.content)

        new_page.tab.update_state(True)
        if self.current_page:
            self.current_page.tab.update_state(False)

        self.current_page = new_page
        self.event_generate("<<NotebookTabChanged>>")  # TODO:

    def select_tab(self, tab: CustomNotebookTab) -> None:
        for i, page in enumerate(self.pages):
            if page.tab == tab:
                self.select_by_index(i)
                return

        raise ValueError(f"Unknown tab {tab}")

    def select_page(self, page: CustomNotebookPage) -> None:
        self.select_by_index(self.pages.index(page))

    def index(self, tab_id: Optional[str, tk.Widget]) -> int:
        if tab_id == "end":
            return len(self.pages)

        for i, page in enumerate(self.pages):
            if page.content == tab_id or page.content.winfo_name() == tab_id:
                return i
        else:
            raise RuntimeError(f"Can't find {tab_id!r}")

    def tab(self, tab_id: Union[str, tk.Widget], text: str):
        page = self.pages[self.index(tab_id)]
        page.tab.set_title(text)

    def tabs(self) -> List[str]:
        return [page.content.winfo_name() for page in self.pages]

    def winfo_children(self) -> List[tk.Widget]:
        return [page.content for page in self.pages]

    def forget(self, child: tk.Widget) -> None:
        for i, page in enumerate(self.pages):
            if child is page.content:
                break
        else:
            raise ValueError(f"Can't find {child}")

        if page == self.current_page:
            # Choose new active page
            if len(self.pages) > i + 1:
                self.select_page(self.pages[i + 1])  # prefer right neighbor
            elif i > 0:
                self.select_page(self.pages[i - 1])  # left neighbor

        child = self.pages[i].content
        child.grid_forget()
        self.pages[i].tab.grid_forget()

        del self.pages[i]
        self._rearrange_tabs()

        if hasattr(child, "close"):
            child.close()
        else:
            child.destroy()

    def get_child_by_index(self, index: int) -> tk.Widget:
        return self.pages[index].content

    def get_current_child(self) -> Optional[tk.Widget]:
        if self.current_page:
            return self.current_page.content
        return None

    def has_content(self, child: tk.Widget) -> bool:
        for page in self.pages:
            if page.content is child:
                return True

        return False

    def focus_set(self):
        if self.current_page:
            self.current_page.content.focus_set()
        else:
            super().focus_set()

    def get_page_by_tab(self, tab: CustomNotebookTab) -> CustomNotebookPage:
        for page in self.pages:
            if page.tab == tab:
                return page

        raise ValueError(f"Could not find tab {tab}")

    def close_tab(self, index_or_tab: Union[int, CustomNotebookTab]) -> None:
        if isinstance(index_or_tab, int):
            page = self.pages[index_or_tab]
        else:
            page = self.get_page_by_tab(index_or_tab)

        self.forget(page.content)

    def close_tabs(self, except_tab: Optional[CustomNotebookTab] = None):
        for page in reversed(self.pages):
            if page.tab == except_tab:
                continue
            else:
                self.close_tab(page.tab)


class CustomNotebookTab(tk.Frame):
    close_image = None
    active_close_image = None

    def __init__(self, notebook: CustomNotebook, title: str, closable: bool):
        super().__init__(notebook.tab_row, borderwidth=0)

        self.base_style = _get_style_configuration(".")
        self.tab_style = _get_style_configuration("CustomNotebook.Tab")
        self.notebook_style_conf = _get_style_configuration("CustomNotebook")

        self.notebook = notebook
        self.title = title
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.label = tk.Label(self, text=title, foreground=self.base_style["foreground"])
        self.label.grid(
            row=0,
            column=0,
            padx=(_ems_to_pixels(0.3), _ems_to_pixels(0.1)),
            sticky="nsw",
            pady=(0, _ems_to_pixels(0.1)),
        )
        self.bind("<1>", self.on_click, True)
        self.label.bind("<1>", self.on_click, True)

        if closable:
            if not CustomNotebookTab.close_image:
                CustomNotebookTab.close_image = _get_image("tab-close")
                CustomNotebookTab.active_close_image = _get_image("tab-close-active")
            self.button = tk.Label(self, image=CustomNotebookTab.close_image)
            self.button.grid(row=0, column=1, padx=(0, _ems_to_pixels(0.1)))
            self.button.bind("<1>", self.on_button_click, True)
            self.button.bind("<Enter>", self.on_button_enter, True)
            self.button.bind("<Leave>", self.on_button_leave, True)

            if sys.platform == "darwin":
                self.label.bind("<ButtonPress-2>", self._right_btn_press, True)
                self.label.bind("<Control-Button-1>", self._right_btn_press, True)
                self.label.bind("<ButtonPress-3>", self._middle_btn_press, True)
            else:
                self.label.bind("<ButtonPress-3>", self._right_btn_press, True)
                self.label.bind("<ButtonPress-2>", self._middle_btn_press, True)

        else:
            self.button = None

        self.indicator = tk.Frame(
            self, height=1, background=self.notebook_style_conf["bordercolor"]
        )
        self.indicator.grid(row=1, column=0, columnspan=2, sticky="sew")

        self.menu = tk.Menu(
            self.winfo_toplevel(), tearoff=False, **_get_style_configuration("Menu")
        )
        self.menu.add_command(label=tr("Close"), command=self._close_tab)
        self.menu.add_command(label=tr("Close others"), command=self._close_other_tabs)
        self.menu.add_command(label=tr("Close all"), command=self._close_all_tabs)

    def set_title(self, text: str) -> None:
        self.label.configure(text=text)

    def _right_btn_press(self, event):
        self.menu.tk_popup(*self.winfo_toplevel().winfo_pointerxy())

    def _middle_btn_press(self, event):
        self._close_tab()

    def _close_tab(self) -> None:
        self.notebook.close_tab(self)

    def _close_all_tabs(self) -> None:
        self.notebook.close_tabs()

    def _close_other_tabs(self) -> None:
        self.notebook.close_tabs(except_tab=self)

    def on_click(self, event):
        self.notebook.select_tab(self)

    def on_button_click(self, event):
        self.notebook.close_tab(self)

    def on_button_enter(self, event):
        self.button.configure(image=CustomNotebookTab.active_close_image)

    def on_button_leave(self, event):
        self.button.configure(image=CustomNotebookTab.close_image)

    def update_state(self, active: bool) -> None:
        if active:
            main_background = self.tab_style["activebackground"]
            # indicator_background = "systemTextBackgroundColor"
            # indicator_height = 1

            # indicator_background = border_color
            # indicator_height = 1

            indicator_background = self.tab_style["indicatorbackground"]
            indicator_height = self.tab_style.get("indicatorheight", _ems_to_pixels(0.2))
        else:
            main_background = self.tab_style["background"]
            indicator_background = self.notebook_style_conf["bordercolor"]
            indicator_height = 1

        self.configure(background=main_background)
        self.label.configure(background=main_background)
        if self.button:
            self.button.configure(background=main_background)
        self.indicator.configure(background=indicator_background, height=indicator_height)


class CustomNotebookPage:
    def __init__(self, tab: CustomNotebookTab, content: tk.Widget):
        self.tab = tab
        self.content = content


def _get_image(name: str) -> tk.PhotoImage:
    from thonny import get_workbench

    return get_workbench().get_image(name)


def _ems_to_pixels(x: float) -> int:
    from thonny.ui_utils import ems_to_pixels

    return ems_to_pixels(x)


def _get_style_configuration(name: str) -> Dict:
    from thonny.ui_utils import get_style_configuration

    return get_style_configuration(name)


class TextFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.text = tk.Text(self, highlightthickness=0, borderwidth=0, width=50, height=20)
        # self.text.grid_propagate(True)
        self.text.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical")
        self.scrollbar.grid(row=0, column=1, sticky="nsew")

        if sys.platform == "darwin":
            root = self.winfo_toplevel()
            isdark = int(root.eval(f"tk::unsupported::MacWindowStyle isdark {root}"))
            # Not sure if it is good idea to use fixed colors, but no named (light-dark aware) color matches.
            # Best dynamic alternative is probably systemTextBackgroundColor
            if isdark:
                stripe_color = "#2d2e31"
                print("Dark")
            else:
                stripe_color = "#fafafa"
            stripe = tk.Frame(self, width=1, background=stripe_color)
            stripe.grid(row=0, column=1, sticky="nse")
            stripe.tkraise()

        self.scrollbar["command"] = self.text.yview
        self.text["yscrollcommand"] = self.scrollbar.set


"""
if __name__ == "__main__":
    if sys.platform == "win32":
        import ctypes

        PROCESS_SYSTEM_DPI_AWARE = 1
        ctypes.OleDLL("shcore").SetProcessDpiAwareness(PROCESS_SYSTEM_DPI_AWARE)

    root = tk.Tk()
    root.geometry("800x600")

    style = ttk.Style()
    # style.theme_use("aqua")

    nb = CustomNotebook(root)

    for i in range(4):
        tf = TextFrame(nb)
        tf.text.insert("end", "print('hello world')\n" * i * 30)
        nb.add(tf, f"program{i}.py")

    nb.grid(sticky="nsew", row=0, column=0, padx=15, pady=15)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    root.mainloop()
"""
