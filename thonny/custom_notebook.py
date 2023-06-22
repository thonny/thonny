from __future__ import annotations

import os.path
import tkinter as tk
from tkinter import ttk
from typing import List, Literal, Optional, Union

from thonny import get_workbench
from thonny.ui_utils import ems_to_pixels

border_color = "systemWindowBackgroundColor7"


class CustomNotebook(tk.Frame):
    def __init__(self, master: Union[tk.Widget, tk.Toplevel, tk.Tk]):
        super().__init__(master, background=border_color)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Can't use ttk.Frame, because can't change it's color in aqua
        self.tab_row = tk.Frame(self, background=border_color)
        self.tab_row.grid(row=0, column=0, sticky="new")

        self.filler = tk.Frame(self.tab_row, background="systemWindowBackgroundColor")
        self.filler.grid(row=0, column=999, sticky="nsew", padx=(1, 0), pady=(0, 1))
        self.tab_row.columnconfigure(999, weight=1)

        self.current_page: Optional[CustomNotebookPage] = None
        self.pages: List[CustomNotebookPage] = []

    def add(self, child: tk.Widget, text: str) -> None:
        self.insert("end", child, text=text)

    def insert(self, index: Union[int, Literal["end"]], child: tk.Widget, text: str) -> None:
        tab = CustomNotebookTab(self, title=text)
        page = CustomNotebookPage(tab, child)
        if index == "end":
            self.pages.append(page)
        else:
            self.pages.insert(index, page)

        self._reposition_tabs()
        self.select_tab(page.tab)

    def _reposition_tabs(self) -> None:
        for i, page in enumerate(self.pages):
            page.tab.grid(row=0, column=i, sticky="nsew", padx=(1, 0), pady=(1, 0))

    def select(self, index: int) -> None:
        new_page = self.pages[index]
        if new_page == self.current_page:
            return

        # if self.current_page:
        #    self.current_page.content.grid_forget()
        # self.update_idletasks()

        new_page.content.grid_propagate(False)
        new_page.content.grid(row=1, column=0, sticky="nsew", padx=(1, 1), pady=(0, 1))
        new_page.content.tkraise()

        new_page.tab.update_state(True)
        if self.current_page:
            self.current_page.tab.update_state(False)

        self.current_page = new_page

    def select_tab(self, tab: CustomNotebookTab) -> None:
        for i, page in enumerate(self.pages):
            if page.tab == tab:
                self.select(i)
                return

        raise ValueError(f"Unknown tab {tab}")


class CustomNotebookTab(tk.Frame):
    close_image = None
    active_close_image = None

    def __init__(self, notebook: CustomNotebook, title: str):
        super().__init__(notebook.tab_row, borderwidth=0)
        self.notebook = notebook
        self.title = title
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.label = tk.Label(self, text=title)
        self.label.grid(
            row=0,
            column=0,
            padx=(ems_to_pixels(0.3), ems_to_pixels(0.1)),
            sticky="nsw",
            pady=(0, ems_to_pixels(0.1)),
        )
        self.bind("<1>", self.on_click, True)
        self.label.bind("<1>", self.on_click, True)

        if not CustomNotebookTab.close_image:
            CustomNotebookTab.close_image = _get_image("tab-close")
            CustomNotebookTab.active_close_image = _get_image("tab-close-active")
        self.button = tk.Label(self, image=CustomNotebookTab.close_image)
        self.button.grid(row=0, column=1, padx=(0, ems_to_pixels(0.1)))
        self.button.bind("<1>", self.on_button_click, True)
        self.button.bind("<Enter>", self.on_button_enter, True)
        self.button.bind("<Leave>", self.on_button_leave, True)

        self.indicator = tk.Frame(self, height=1, background=border_color)
        self.indicator.grid(row=1, column=0, columnspan=2, sticky="sew")

    def on_click(self, event):
        print("onclick")
        self.notebook.select_tab(self)

    def on_button_click(self, event):
        print("click")

    def on_button_enter(self, event):
        self.button.configure(image=CustomNotebookTab.active_close_image)

    def on_button_leave(self, event):
        self.button.configure(image=CustomNotebookTab.close_image)

    def update_state(self, active: bool) -> None:
        if active:
            main_background = "systemTextBackgroundColor"
            # indicator_background = "systemTextBackgroundColor"
            # indicator_height = 1

            # indicator_background = border_color
            # indicator_height = 1

            indicator_background = "systemLinkColor"
            indicator_height = ems_to_pixels(0.2)
        else:
            main_background = "systemWindowBackgroundColor"
            indicator_background = border_color
            indicator_height = 1

        self.configure(background=main_background)
        self.label.configure(background=main_background)
        self.button.configure(background=main_background)
        self.indicator.configure(background=indicator_background, height=indicator_height)


def _get_image(name):
    for ext in ("png", "gif"):
        path = f"res/{name}.{ext}"
        if os.path.exists(path):
            return tk.PhotoImage(name, file=path)

    raise RuntimeError("image not found")


class CustomNotebookPage:
    def __init__(self, tab: CustomNotebookTab, content: tk.Widget):
        self.tab = tab
        self.content = content


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


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")

    style = ttk.Style()
    style.theme_use("aqua")

    nb = CustomNotebook(root)

    for i in range(4):
        tf = TextFrame(nb)
        tf.text.insert("end", "print('hello world')\n" * i * 30)
        nb.add(tf, f"program{i}.py")

    nb.grid(sticky="nsew", row=0, column=0, padx=15, pady=15)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    root.mainloop()
