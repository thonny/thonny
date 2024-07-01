from __future__ import annotations

import sys
import tkinter as tk
from logging import getLogger
from typing import Any, Dict, List, Literal, Optional, Tuple, Union, cast

from thonny import dnd  # inspired by and very similar to tkinter.dnd
from thonny.languages import tr

logger = getLogger(__name__)


class CustomNotebookTabRow(tk.Frame):
    def __init__(self, master: CustomNotebook, **kw):
        self.notebook = master
        self.root = master.winfo_toplevel()
        super().__init__(master, **kw)
        self.filler = tk.Frame(self, background=self.notebook.get_frame_background())
        self.filler.grid(
            row=0,
            column=999,
            sticky="nsew",
            padx=(0 if master.dynamic_border else 1, 0),
            pady=(0, 1),
        )
        self._insertion_mark = tk.Frame(
            self,
            background=self.notebook.get_label_foreground(),
            width=_ems_to_pixels(0.3),
            height=_ems_to_pixels(2),
        )
        self._insertion_index = None

    def dnd_accept(self, source, event):
        assert isinstance(source, CustomNotebookTab)
        return self

    def dnd_enter(self, source, event):
        self.dnd_motion(source, event)

    def dnd_motion(self, source: CustomNotebookTab, event: tk.Event):
        x = event.x_root - self.winfo_rootx()
        y = event.y_root - self.winfo_rooty()
        insertion_index, insertion_widget = self._compute_insertion_position(x, y)
        source_index = source.notebook.index_of_tab(source)
        if source.notebook is self.notebook and insertion_index in [source_index, source_index + 1]:
            # no point in moving a tab right before or after itself
            self._insertion_mark.place_forget()
        else:
            self._show_insertion_mark(insertion_index, insertion_widget)

    def dnd_leave(self, source, event):
        self.hide_insertion_mark()

    def dnd_commit(self, source, event):
        logger.info("dnd_commit with insertion_index %r", self._insertion_index)
        if self._insertion_index is not None:
            self.notebook.insert_from_another_notebook_or_position(
                self._insertion_index, source.notebook.get_page_by_tab(source)
            )
        self.dnd_leave(source, event)

    def _compute_insertion_position(self, mouse_x: int, mouse_y: int) -> Tuple[int, tk.Widget]:
        dist_from_closest_left_edge = None
        closest_left_edge_widget = None
        closest_left_edge_index = None
        items = [page.tab for page in self.notebook.pages] + [self.filler]
        for i, item in enumerate(items):
            dist_from_left_edge = abs(item.winfo_x() - mouse_x)
            if (
                dist_from_closest_left_edge is None
                or dist_from_left_edge < dist_from_closest_left_edge
            ):
                dist_from_closest_left_edge = dist_from_left_edge
                closest_left_edge_widget = item
                closest_left_edge_index = i

        return closest_left_edge_index, closest_left_edge_widget

    def on_theme_changed(self):
        self.configure(background=self.notebook.get_bordercolor())
        self.filler.configure(background=self.notebook.get_frame_background())

    def _show_insertion_mark(self, insertion_index: int, right_neigbour: tk.Widget) -> None:
        self._insertion_mark.place_configure(
            x=right_neigbour.winfo_x(), y=0, height=self.winfo_height()
        )
        self._insertion_index = insertion_index
        self._insertion_mark.lift()

    def hide_insertion_mark(self) -> None:
        self._insertion_mark.place_forget()
        self._insertion_index = None


class CustomNotebook(tk.Frame):
    def __init__(self, master: Union[tk.Widget, tk.Toplevel, tk.Tk], closable: bool = True):
        self.dynamic_border = bool(
            _lookup_style_option("CustomNotebook.Tab", "dynamic_border", False)
        )
        super().__init__(master, background=self.get_bordercolor())
        self.closable = closable
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Can't use ttk.Frame, because can't change its color in aqua
        self.tab_row = CustomNotebookTabRow(self, background=self.get_bordercolor())
        self.tab_row.grid(row=0, column=0, sticky="new")
        self.tab_row.columnconfigure(999, weight=1)

        self.current_page: Optional[CustomNotebookPage] = None
        self.pages: List[CustomNotebookPage] = []

        self._on_theme_changed_binding = self.bind("<<ThemeChanged>>", self.on_theme_changed, True)

    def add(self, child: tk.Widget, text: str) -> None:
        self._insert("end", child, text=text)

    def insert(self, pos: Union[int, Literal["end"], tk.Widget], child: tk.Widget, text: str):
        self._insert(pos, child, text)

    def _insert(
        self,
        pos: Union[int, Literal["end"], tk.Widget],
        child: tk.Widget,
        text: str,
        old_notebook: Optional[CustomNotebook] = None,
    ) -> None:
        tab = CustomNotebookTab(self, title=text, closable=self.closable)
        page = CustomNotebookPage(tab, child)
        if isinstance(pos, tk.Widget):
            pos = self.index(pos)

        if pos == "end":
            self.pages.append(page)
        else:
            assert isinstance(pos, int), f"Got {pos!r} instead of int"
            logger.info("Inserting %r to position %r in %r", child, pos, self.pages)
            self.pages.insert(pos, page)

        self._rearrange_tabs()
        self.select_tab(page.tab)
        child.containing_notebook = self

        self.after_insert(pos, page, old_notebook)

    def add_from_another_notebook(self, page: CustomNotebookPage) -> None:
        self.insert_from_another_notebook_or_position("end", page)

    def insert_from_another_notebook_or_position(
        self, pos: Union[int, Literal["end"]], page: CustomNotebookPage
    ) -> None:
        original_notebook = page.tab.notebook
        if original_notebook == self and pos >= self.index_of_tab(page.tab):
            # tab will be removed first, so the new target index will be one less
            pos -= 1

        original_notebook._forget(page.content, new_notebook=self)
        self._insert(pos, page.content, text=page.tab.get_title(), old_notebook=original_notebook)

    def _rearrange_tabs(self) -> None:
        if len(self.pages) == 0:
            self.current_page = None

        for i, page in enumerate(self.pages):
            if self.dynamic_border:
                if page == self.current_page:
                    padx = 1
                    pady = (1, 0)
                else:
                    padx = 0
                    pady = 0
            else:
                padx = (1, 0)
                pady = (1, 0)

            page.tab.grid(row=0, column=i, sticky="nsew", padx=padx, pady=pady)

    def enable_traversal(self) -> None:
        # TODO:
        pass

    def get_bordercolor(self) -> str:
        return _lookup_style_option("CustomNotebook", "bordercolor")

    def get_frame_background(self) -> str:
        return _lookup_style_option(".", "background")

    def get_label_foreground(self) -> str:
        return _lookup_style_option("TLabel", "foreground")

    def on_theme_changed(self, event):
        self.dynamic_border = bool(
            _lookup_style_option("CustomNotebook.Tab", "dynamic_border", False)
        )
        self.configure(background=self.get_bordercolor())
        self.tab_row.on_theme_changed()
        for page in self.pages:
            page.tab.update_style()

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
        new_page.content.grid(row=1, column=0, sticky="nsew", padx=(1, 1), pady=(0, 1), in_=self)
        if self.current_page:
            self.current_page.content.grid_remove()
            # new_page.content.tkraise(self.current_page.content)
        new_page.tab.update_state(True)
        if self.current_page:
            self.current_page.tab.update_state(False)

        self.current_page = new_page
        self.current_page.content.focus_set()
        self.event_generate("<<NotebookTabChanged>>")

    def select_tab(self, tab: CustomNotebookTab) -> None:
        for i, page in enumerate(self.pages):
            if page.tab == tab:
                self.select_by_index(i)
                return

        raise ValueError(f"Unknown tab {tab}")

    def select_another_tab(self, event: tk.Event) -> Optional[str]:
        if len(self.pages) < 2:
            self.bell()
            return None

        from thonny.ui_utils import shift_is_pressed

        if shift_is_pressed(event):
            offset = -1
        else:
            offset = 1

        index = self.index(self.current_page.content)
        new_index = (index + offset) % len(self.pages)
        self.select_by_index(new_index)
        return "break"

    def select_page(self, page: CustomNotebookPage) -> None:
        self.select_by_index(self.pages.index(page))

    def index(self, tab_id: Union[str, tk.Widget]) -> int:
        if tab_id == "end":
            return len(self.pages)

        for i, page in enumerate(self.pages):
            if page.content == tab_id or page.content.winfo_name() == tab_id:
                return i
        else:
            raise RuntimeError(f"Can't find {tab_id!r}")

    def index_of_tab(self, tab: CustomNotebookTab) -> int:
        for i, page in enumerate(self.pages):
            if page.tab is tab:
                return i
        else:
            raise RuntimeError(f"Can't find {tab!r}")

    def tab(self, tab_id: Union[str, tk.Widget], text: str):
        page = self.pages[self.index(tab_id)]
        page.tab.set_title(text)

    def tabs(self) -> List[str]:
        return [page.content.winfo_name() for page in self.pages]

    def winfo_children(self) -> List[tk.Widget]:
        return [page.content for page in self.pages]

    def forget(self, child: tk.Widget) -> None:
        self._forget(child, None)

    def _forget(self, child: tk.Widget, new_notebook: Optional[CustomNotebook]) -> None:
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

        child.containing_notebook = None
        self.after_forget(i, page, new_notebook)

    def after_insert(
        self,
        pos: Union[int, Literal["end"]],
        page: CustomNotebookPage,
        old_notebook: Optional[CustomNotebook],
    ) -> None:
        self.event_generate("<<NotebookTabInserted>>")

    def after_forget(
        self, pos: int, page: CustomNotebookPage, new_notebook: Optional[CustomNotebook]
    ) -> None:
        self.event_generate("<<NotebookTabForgotten>>")

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

        self._forget(page.content, None)

    def close_tabs(self, except_tab: Optional[CustomNotebookTab] = None):
        for page in reversed(self.pages):
            if page.tab == except_tab:
                continue
            else:
                self.close_tab(page.tab)

    def allows_dragging_to_another_notebook(self) -> bool:
        return False

    def destroy(self):
        self.unbind("<<ThemeChanged>>", self._on_theme_changed_binding)
        super().destroy()


class CustomNotebookTab(tk.Frame):
    close_image = None
    active_close_image = None

    def __init__(self, notebook: CustomNotebook, title: str, closable: bool):
        super().__init__(notebook.tab_row, borderwidth=0)
        self._active = False
        self._hover = False

        self.notebook = notebook
        self.title = title
        self.drag_start_x_root = 0
        self.drag_start_y_root = 0

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.label = tk.Label(self, text=title, foreground=self.notebook.get_label_foreground())
        self.label.grid(
            row=0,
            column=0,
            padx=(_ems_to_pixels(0.3), 0 if self.notebook.closable else _ems_to_pixels(0.3)),
            sticky="nsw",
            pady=(0, _ems_to_pixels(0.1)),
        )
        self.bind("<1>", self.on_click, True)
        self.label.bind("<1>", self.on_click, True)

        self.bind("<Enter>", self.on_enter, True)
        self.bind("<Leave>", self.on_leave, True)

        if closable:
            if not CustomNotebookTab.close_image:
                CustomNotebookTab.close_image = _get_image("tab-close")
                CustomNotebookTab.active_close_image = _get_image("tab-close-active")
            self.button = tk.Label(self, image=CustomNotebookTab.close_image, anchor="center")
            self.button.grid(row=0, column=1, padx=(_ems_to_pixels(0.1), _ems_to_pixels(0.48)))
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

        self.indicator = tk.Frame(self, height=1, background=self.notebook.get_bordercolor())
        self.indicator.grid(row=1, column=0, columnspan=2, sticky="sew")

        self.menu = tk.Menu(
            self.winfo_toplevel(), tearoff=False, **_get_style_configuration("Menu")
        )
        self.menu.add_command(label=tr("Close"), command=self._close_tab)
        self.menu.add_command(label=tr("Close others"), command=self._close_other_tabs)
        self.menu.add_command(label=tr("Close all"), command=self._close_all_tabs)

    def set_title(self, text: str) -> None:
        self.label.configure(text=text)

    def get_title(self) -> str:
        return self.label.cget("text")

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

    def update_style(self, only_background=False):
        self.label.configure(foreground=self.notebook.get_label_foreground())

        if self._active:
            main_background = self._get_tab_style_option("activebackground")
        elif self._hover:
            main_background = self._get_tab_style_option("hoverbackground")
        else:
            main_background = self._get_tab_style_option("background")

        self.configure(background=main_background)
        self.label.configure(background=main_background)
        if self.button:
            self.button.configure(background=main_background)

        if only_background:
            return

        if self._active:
            indicator_background = self._get_tab_style_option("indicatorbackground")
            indicator_height = self._get_tab_style_option("indicatorheight", _ems_to_pixels(0.2))
            if self.notebook.dynamic_border:
                self.grid(padx=1, pady=(1, 0))
        else:
            indicator_background = self.notebook.get_bordercolor()
            indicator_height = 1
            if self.notebook.dynamic_border:
                self.grid(padx=0, pady=0)

        self.indicator.configure(background=indicator_background, height=indicator_height)

        self.menu.configure(**_get_style_configuration("Menu"))

    def _get_tab_style_option(self, option_name, default=None) -> Any:
        return _lookup_style_option("CustomNotebook.Tab", option_name, default)

    def on_click(self, event: tk.Event):
        self.notebook.select_tab(self)
        self.drag_start_x_root = event.x_root
        self.drag_start_y_root = event.y_root
        dnd.dnd_start(self, event)

    def on_button_click(self, event):
        self.notebook.close_tab(self)

    def on_enter(self, event):
        self._hover = True
        self.update_style(only_background=True)

    def on_leave(self, event):
        self._hover = False
        self.update_style(only_background=True)

    def on_button_enter(self, event):
        self.button.configure(image=CustomNotebookTab.active_close_image)

    def on_button_leave(self, event):
        self.button.configure(image=CustomNotebookTab.close_image)

    def update_state(self, active: bool) -> None:
        self._active = active
        self.update_style()

    def dnd_motion_anywhere(self, source: CustomNotebookTab, event: tk.Event):
        toplevel = self.winfo_toplevel()
        delta_x = abs(source.drag_start_x_root - event.x_root)
        delta_y = abs(source.drag_start_y_root - event.y_root)
        moved_enough = _ems_to_pixels(2)
        if (
            (delta_x > moved_enough or delta_y > moved_enough)
            and hasattr(toplevel, "show_notebook_drop_targets")
            and self.notebook.allows_dragging_to_another_notebook()
        ):
            toplevel.show_notebook_drop_targets()

    def dnd_end(self, target, event):
        logger.info("Ending DND operation with target %r", target)
        toplevel = self.winfo_toplevel()
        if (
            hasattr(toplevel, "hide_notebook_drop_targets")
            and self.notebook.allows_dragging_to_another_notebook()
        ):
            toplevel.hide_notebook_drop_targets()


class CustomNotebookPage:
    def __init__(self, tab: CustomNotebookTab, content: tk.Widget):
        self.tab = tab
        self.content = content

    def __repr__(self):
        return f"CustomNotebookPage({self.tab.title}, {self.content})"


class NotebookTabDropTarget(tk.Canvas):
    def __init__(
        self,
        master: Union[tk.Tk, tk.Toplevel, tk.Widget],
        notebook: CustomNotebook,
        width: int,
        height: int,
    ):
        self.notebook = notebook
        self.inactive_color = "#E4E4E4"
        self.active_color = "gray"
        super().__init__(
            master=master,
            width=width,
            height=height,
            borderwidth=0,
            highlightthickness=0,
            background=self.inactive_color,
        )

        borderwidth = _ems_to_pixels(0.2)
        dash_step = _ems_to_pixels(0.5)
        self.rect_id = self.create_rectangle(
            1,
            1,
            width - borderwidth,
            height - borderwidth,
            dash=(dash_step, dash_step * 2),
            width=borderwidth,
            fill=self.inactive_color,
        )

    def dnd_accept(self, source: CustomNotebookTab, event: tk.Event):
        assert isinstance(source, CustomNotebookTab)
        return self

    def dnd_enter(self, source: CustomNotebookTab, event: tk.Event):
        self.configure(background=self.active_color)
        self.itemconfigure(self.rect_id, fill=self.active_color)
        self.dnd_motion(source, event)

    def dnd_motion(self, source: CustomNotebookTab, event: tk.Event):
        pass

    def dnd_leave(self, source: CustomNotebookTab, event: tk.Event):
        self.configure(background=self.inactive_color)
        self.itemconfigure(self.rect_id, fill=self.inactive_color)

    def dnd_commit(self, source: CustomNotebookTab, event: tk.Event):
        self.dnd_leave(source, event)
        self.notebook.add_from_another_notebook(source.notebook.get_page_by_tab(source))


def _get_image(name: str) -> tk.PhotoImage:
    from thonny import get_workbench

    return get_workbench().get_image(name)


def _ems_to_pixels(x: float) -> int:
    from thonny.ui_utils import ems_to_pixels

    return ems_to_pixels(x)


def _get_style_configuration(name: str) -> Dict:
    from thonny.ui_utils import get_style_configuration

    return get_style_configuration(name)


def _lookup_style_option(style_name, option_name, default=None) -> Any:
    from thonny.ui_utils import lookup_style_option

    return lookup_style_option(style_name, option_name, default)


"""

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
