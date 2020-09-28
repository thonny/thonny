import logging
import sys
import traceback
from html.parser import HTMLParser
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox
from typing import Tuple, List, Any

from thonny import tktextext, ui_utils, get_workbench
from thonny.codeview import get_syntax_options_for_tag
from thonny.languages import tr
from thonny.ui_utils import scrollbar_style, lookup_style_option

EDITOR_CONTENT_NAME = "$EDITOR_CONTENT"

_HOME_KEY = "_home_"


class ExercisesView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, borderwidth=0, relief="flat")

        self._provider_name = None
        self._provider_records_by_name = {
            p["name"]: p for p in get_workbench().get_exercise_providers()
        }

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.vert_scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, style=scrollbar_style("Vertical")
        )
        self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW, rowspan=3)

        tktextext.fixwordbreaks(tk._default_root)
        self.init_header(row=0, column=0)

        self.breadcrumbs_bar.set_links(
            [
                ("_home", tr("Home")),
                ("/", "lahendus.ut.ee"),
                ("/c1", "Programmeerimise algkursus"),
                ("/c1/ch1", "1. Funktsioonid"),
                ("/c1/ch1", "14. Küpsisetort vol. 2"),
            ]
        )

        spacer = ttk.Frame(self, height=1)
        spacer.grid(row=1, sticky="nsew")

        self._html_widget = HtmlText(
            master=self,
            link_and_form_handler=self._on_request_new_page,
            read_only=True,
            wrap="word",
            font="TkDefaultFont",
            padx=10,
            pady=0,
            insertwidth=0,
            borderwidth=0,
            highlightthickness=0,
        )

        self._html_widget.grid(row=1, column=0, sticky="nsew")

        self.go_to_provider_selection_page()

    def init_header(self, row, column):
        header_frame = ttk.Frame(self, style="ViewToolbar.TFrame")
        header_frame.grid(row=row, column=column, sticky="nsew")
        header_frame.columnconfigure(0, weight=1)

        self.breadcrumbs_bar = BreadcrumbsBar(header_frame, self._on_request_new_page)

        self.breadcrumbs_bar.grid(row=0, column=0, sticky="nsew")

        # self.menu_button = ttk.Button(header_frame, text="≡ ", style="ViewToolbar.Toolbutton")
        self.menu_button = ttk.Button(
            header_frame, text=" ≡ ", style="ViewToolbar.Toolbutton", command=self.post_button_menu
        )
        # self.menu_button.grid(row=0, column=1, sticky="ne")
        self.menu_button.place(anchor="ne", rely=0, relx=1)

    def _on_request_new_page(self, target, form_data=None):
        print("target", target)
        if target == _HOME_KEY:
            self.go_to_provider_selection_page()
        elif target.startswith("!"):
            self._provider_name = target[1:]
            self.go_to("/")
        elif target.startswith("/"):
            self.go_to(target, form_data=form_data)
        else:
            get_workbench().open_url(target)

    def post_button_menu(self):
        self.refresh_menu(context="button")
        self.menu.tk_popup(
            self.menu_button.winfo_rootx(),
            self.menu_button.winfo_rooty() + self.menu_button.winfo_height(),
        )

    def go_to(self, url, form_data=None):
        if form_data is None:
            form_data = FormData()

        assert url.startswith("/")
        assert self._provider_name is not None
        provider = self._get_provider()
        html, breadcrumbs = provider.get_html_and_breadcrumbs(url, form_data)
        self._set_page_html(html)
        self.breadcrumbs_bar.set_links(self._get_base_breadcrumb_links() + breadcrumbs)

    def go_to_provider_selection_page(self):
        self._provider_name = None

        provider_records = sorted(
            self._provider_records_by_name.values(), key=lambda p: p["sort_key"]
        )

        html = "\n"
        html += "<ul>\n"
        for provider_record in provider_records:
            html += '<li><a href="!%s">%s</a></li>\n' % (
                provider_record["name"],
                provider_record["title"],
            )
        html += "</ul>\n"

        self._set_page_html(html)
        self.breadcrumbs_bar.set_links(self._get_base_breadcrumb_links())

    def _get_provider(self):
        if self._provider_name is None:
            return None

        rec = self._provider_records_by_name[self._provider_name]
        if "instance" not in rec:
            rec["instance"] = rec["class"](self)

        return rec["instance"]

    def _set_page_html(self, html):
        self._html_widget.set_html_content(html)

    def _get_base_breadcrumb_links(self):
        result = [(_HOME_KEY, tr("Home"))]
        if self._provider_name is not None:
            provider_record = self._provider_records_by_name[self._provider_name]
            result.append(("!" + provider_record["name"], provider_record["title"]))

        return result


class HtmlText(tktextext.TweakableText):
    def __init__(self, master, link_and_form_handler, cnf={}, read_only=False, **kw):

        super().__init__(
            master=master,
            cnf=cnf,
            read_only=read_only,
            **{
                "font": "TkDefaultFont",
                # "cursor" : "",
                **kw,
            }
        )
        self._link_and_form_handler = link_and_form_handler
        self._configure_tags()
        self._reset_renderer()

    def set_html_content(self, html):
        self.clear()
        self._renderer.feed(html)

    def _configure_tags(self):
        main_font = tkfont.nametofont("TkDefaultFont")

        bold_font = main_font.copy()
        bold_font.configure(weight="bold", size=main_font.cget("size"))

        italic_font = main_font.copy()
        italic_font.configure(slant="italic", size=main_font.cget("size"))

        h1_font = main_font.copy()
        h1_font.configure(size=round(main_font.cget("size") * 1.4), weight="bold")

        h2_font = main_font.copy()
        h2_font.configure(size=round(main_font.cget("size") * 1.3), weight="bold")

        h3_font = main_font.copy()
        h3_font.configure(size=main_font.cget("size"), weight="bold")

        small_font = main_font.copy()
        small_font.configure(size=round(main_font.cget("size") * 0.8))
        small_italic_font = italic_font.copy()
        small_italic_font.configure(size=round(main_font.cget("size") * 0.8))

        # Underline on font looks better than underline on tag
        underline_font = main_font.copy()
        underline_font.configure(underline=True)

        self.tag_configure("h1", font=h1_font, spacing3=5)
        self.tag_configure("h2", font=h2_font, spacing3=5)
        self.tag_configure("h3", font=h3_font, spacing3=5)
        self.tag_configure("p", spacing1=0, spacing3=10, spacing2=0)
        self.tag_configure("line_block", spacing1=0, spacing3=10, spacing2=0)
        self.tag_configure("em", font=italic_font)
        self.tag_configure("strong", font=bold_font)

        # TODO: hyperlink syntax options may require different background as well
        self.tag_configure(
            "a",
            **{**get_syntax_options_for_tag("hyperlink"), "underline": False},
            font=underline_font
        )
        self.tag_configure("small", font=small_font)
        self.tag_configure("light", foreground="gray")
        self.tag_configure("remark", font=small_italic_font)
        self.tag_bind("a", "<ButtonRelease-1>", self._hyperlink_click)
        self.tag_bind("a", "<Enter>", self._hyperlink_enter)
        self.tag_bind("a", "<Leave>", self._hyperlink_leave)

        self.tag_configure("topic_title", lmargin2=16, font=bold_font)
        self.tag_configure("topic_body", lmargin1=16, lmargin2=16)
        self.tag_configure(
            "code",
            font="TkFixedFont",
            # wrap="none", # TODO: needs automatic hor-scrollbar and better padding mgmt
            # background="#eeeeee"
        )
        # if ui_utils.get_tk_version_info() >= (8,6,6):
        #    self.tag_configure("code", lmargincolor=self["background"])

        for i in range(1, 6):
            self.tag_configure("list%d" % i, lmargin1=i * 10, lmargin2=i * 10 + 10)

        toti_code_font = bold_font.copy()
        toti_code_font.configure(
            family=tk.font.nametofont("TkFixedFont").cget("family"), size=bold_font.cget("size")
        )
        self.tag_configure("topic_title_code", font=toti_code_font)
        self.tag_raise("topic_title_code", "code")
        self.tag_raise("topic_title_code", "topic_title")
        self.tag_raise("a", "topic_title")

        # TODO: topic_title + em
        self.tag_raise("em", "topic_title")
        self.tag_raise("a", "em")
        self.tag_raise("a", "topic_body")
        self.tag_raise("a", "topic_title")

        if ui_utils.get_tk_version_info() >= (8, 6, 6):
            self.tag_configure("sel", lmargincolor=self["background"])
        self.tag_raise("sel")

    def _reset_renderer(self):
        self._renderer = HtmlRenderer(self, self._link_and_form_handler)

    def clear(self):
        self.direct_delete("1.0", "end")
        self.tag_delete("1.0", "end")
        self._reset_renderer()

    def _hyperlink_click(self, event):
        mouse_index = self.index("@%d,%d" % (event.x, event.y))

        for tag in self.tag_names(mouse_index):
            # formatting tags are alphanumeric
            if self._renderer._is_link_tag(tag):
                self._link_and_form_handler(tag)
                break

    def _hyperlink_enter(self, event):
        self.config(cursor="hand2")

    def _hyperlink_leave(self, event):
        self.config(cursor="")


class HtmlRenderer(HTMLParser):
    def __init__(self, text_widget, link_and_form_handler):
        super().__init__()
        self.widget = text_widget
        self.widget.mark_set("mark", "end")
        self._link_and_form_handler = link_and_form_handler
        self._unique_tag_count = 0
        self._context_tags = []
        self._active_lists = []
        self._active_forms = []
        self._block_tags = ["div", "p", "ul", "ol", "li", "pre", "code", "form", "h1", "h2"]
        self._alternatives = {"b": "strong", "i": "em"}
        self._simple_tags = ["strong", "u", "em"]
        self._ignored_tags = ["span"]
        self._active_attrs_by_tag = {}  # assuming proper close tags

    def handle_starttag(self, tag, attrs):
        tag = self._normalize_tag(tag)
        attrs = dict(attrs)
        if tag in self._ignored_tags:
            return
        else:
            self._active_attrs_by_tag[tag] = attrs

        if tag in self._block_tags:
            self._ensure_new_line()

        self._add_tag(tag)

        if tag == "a" and "href" in attrs:
            self._add_tag(attrs["href"])
        elif tag == "ul":
            self._active_lists.append("ul")
        elif tag == "ol":
            self._active_lists.append("ol")
        elif tag == "li":
            if self._active_lists[-1] == "ul":
                self._append_text("• ")
            elif self._active_lists[-1] == "ol":
                self._append_text("? ")
        elif tag == "form":
            form = attrs.copy()
            form["inputs"] = []
            self._active_forms.append(form)
        elif tag == "input":
            if not attrs.get("type"):
                attrs["type"] = "text"

            if attrs["type"] == "hidden":
                self._add_hidden_form_variable(attrs)
            elif attrs["type"] == "file":
                self._append_file_input(attrs)
            elif attrs["type"] == "submit":
                self._append_submit_button(attrs)

    def handle_endtag(self, tag):
        tag = self._normalize_tag(tag)
        if tag in self._ignored_tags:
            return
        else:
            self._active_attrs_by_tag[tag] = {}

        if tag == "ul":
            self._close_active_list("ul")
        elif tag == "ol":
            self._close_active_list("ol")
        elif tag == "form":
            self._active_forms.pop()

        self._pop_tag(tag)

        # prepare for next piece of text
        if tag in self._block_tags:
            self._ensure_new_line()

    def handle_data(self, data):
        self._append_text(self._prepare_text(data))

    def _is_link_tag(self, tag):
        return ":" in tag or "/" in tag or "!" in tag

    def _create_unique_tag(self):
        self._unique_tag_count += 1
        return "_UT_%s" % self._unique_tag_count

    def _normalize_tag(self, tag):
        return self._alternatives.get(tag, tag)

    def _add_tag(self, tag):
        self._context_tags.append(tag)

    def _ensure_new_line(self):
        last_line_without_spaces = self.widget.get("end-2l linestart", "end-1c").replace(" ", "")
        if not last_line_without_spaces.endswith("\n"):
            self.widget.direct_insert("end-1c", "\n")

    def _pop_tag(self, tag):
        while self._context_tags and self._context_tags[-1] != tag:
            # remove unclosed or synthetic other tags
            self._context_tags.pop()

        if self._context_tags:
            assert self._context_tags[-1] == tag
            self._context_tags.pop()

    def _close_active_list(self, tag):
        # TODO: active list may also include list item marker
        while self._active_lists and self._active_lists[-1] != tag:
            # remove unclosed or synthetic other tags
            self._active_lists.pop()

        if self._active_lists:
            assert self._active_lists[-1] == tag
            self._active_lists.pop()

    def _prepare_text(self, text):
        if self._context_tags and self._context_tags[-1] in ["pre", "code"]:
            text = text.replace("\n", " ").replace("\r", " ")
            while "  " in text:
                text = text.replace("  ", " ")

        if self._should_trim_whitespace():
            text = text.strip()

        return text

    def _should_trim_whitespace(self):
        for tag in reversed(self._context_tags):
            if self._is_link_tag(tag):
                continue
            return tag in self._block_tags

        return True

    def _append_text(self, chars, extra_tags=()):
        # print("APPP", chars, tags)
        self.widget.direct_insert("mark", chars, self._get_effective_tags(extra_tags))

    def _append_submit_button(self, attrs):
        form = self._active_forms[-1]

        def handler():
            self._submit_form(form)

        value = attrs.get("value", "Submit")
        btn = ttk.Button(self.widget, text=value, command=handler, width=len(value) + 2)
        btn.html_attrs = attrs
        self._append_window(btn)
        if "name" in attrs:
            form["fields"].append([attrs, value])

    def _submit_form(self, form):
        form_data = FormData()
        print("new_form", form_data)

        for attrs, value in form["inputs"]:
            if not "name" in attrs:
                continue

            if isinstance(value, tk.Variable):
                value = value.get()
            elif isinstance(value, tk.Text):
                value = value.get("1.0", "end")

            if attrs["type"] == "hidden" and attrs["name"] == EDITOR_CONTENT_NAME:
                value = get_workbench().get_editor_notebook().get_current_editor_content()
                if value is None:
                    messagebox.showerror(
                        "Can't submit", "No active editor. Nothing to submit.", master=self
                    )
                    return

            form_data.add(attrs["name"], value)

        # TODO: support default action
        # TODO: support GET forms
        action = form["action"]
        self._link_and_form_handler(action, form_data)

    def _add_hidden_form_variable(self, attrs):
        self._active_forms[-1]["inputs"].append([attrs, attrs.get("value")])

    def _append_file_input(self, attrs):
        # TODO: support also "multiple" flag
        cb = ttk.Combobox(self.widget, values=["<active editor>", "main.py", "kala.py"])
        self._append_window(cb)

    def _append_image(self, name, extra_tags=()):
        index = self.widget.index("mark-1c")
        self.widget.image_create(index, image=get_workbench().get_image(name))
        for tag in self._get_effective_tags(extra_tags):
            self.widget.tag_add(tag, index)

    def _append_window(self, window, extra_tags=()):
        index = self.widget.index("mark-1c")
        self.widget.window_create(index, window=window)
        for tag in self._get_effective_tags(extra_tags):
            self.widget.tag_add(tag, index)

    def _get_effective_tags(self, extra_tags):
        tags = set(extra_tags) | set(self._context_tags)

        if self._active_lists:
            tags.add("list%d" % min(len(self._active_lists), 5))

        # combine tags
        if "code" in tags and "topic_title" in tags:
            tags.remove("code")
            tags.remove("topic_title")
            tags.add("topic_title_code")

        return tuple(sorted(tags))


class BreadcrumbsBar(tktextext.TweakableText):
    def __init__(self, master, click_handler):
        super(BreadcrumbsBar, self).__init__(
            master,
            borderwidth=0,
            relief="flat",
            height=1,
            font="TkDefaultFont",
            wrap="word",
            padx=6,
            pady=5,
            insertwidth=0,
            highlightthickness=0,
            background=lookup_style_option("ViewToolbar.TFrame", "background"),
            read_only=True,
        )

        self._changing = False
        self.bind("<Configure>", self.update_height, True)

        self.tag_configure("_link", foreground=lookup_style_option("Url.TLabel", "foreground"))
        self.tag_configure("_underline", underline=True)
        self.tag_bind("_link", "<1>", self._link_click)
        self.tag_bind("_link", "<Enter>", self._link_enter)
        self.tag_bind("_link", "<Leave>", self._link_leave)
        self.tag_bind("_link", "<Motion>", self._link_motion)

        self._click_handler = click_handler

    def set_links(self, links):
        try:
            self._changing = True

            self.direct_delete("1.0", "end")
            if not links:
                return

            # remove trailing newline
            links = links[:]
            links[-1] = (links[-1][0], links[-1][1].rstrip("\r\n"))

            for key, label in links:
                self.direct_insert("end", "/\xa0")
                if not label.endswith("\n"):
                    label += " "

                self.direct_insert("end", label, ("_link", key))
        finally:
            self._changing = False
            self.update_height()

    def update_height(self, event=None):
        if self._changing:
            return
        height = self.tk.call((self, "count", "-update", "-displaylines", "1.0", "end"))
        self.configure(height=height)

    def _link_click(self, event):
        mouse_index = self.index("@%d,%d" % (event.x, event.y))
        user_tags = [
            tag for tag in self.tag_names(mouse_index) if tag not in ["_link", "_underline"]
        ]
        if len(user_tags) == 1:
            self._click_handler(user_tags[0])

    def _get_link_range(self, event):
        mouse_index = self.index("@%d,%d" % (event.x, event.y))
        return self.tag_prevrange("_link", mouse_index + "+1c")

    def _link_motion(self, event):
        self.tag_remove("_underline", "1.0", "end")
        dir_range = self._get_link_range(event)
        if dir_range:
            range_start, range_end = dir_range
            self.tag_add("_underline", range_start, range_end)

    def _link_enter(self, event):
        self.config(cursor="hand2")

    def _link_leave(self, event):
        self.config(cursor="")
        self.tag_remove("_underline", "1.0", "end")


class FormData:
    """Used for representing form fields"""

    def __init__(self, pairs: List[Tuple[Any, Any]] = None):
        if pairs is None:
            pairs = []
        self.pairs = pairs

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def add(self, key, value):
        self.pairs.append((key, value))

    def getlist(self, key):
        result = []
        for a_key, value in self.pairs:
            if a_key == key:
                result.append(value)

        return result

    def __getitem__(self, key):
        for a_key, value in self.pairs:
            if a_key == key:
                return value
        raise KeyError(key)

    def __len__(self):
        return len(self.pairs)

    def __contains__(self, key):
        for a_key, _ in self.pairs:
            if a_key == key:
                return True
        return False

    def __str__(self):
        return repr(self.pairs)

    def __bool__(self):
        return bool(len(self.pairs))


class ExerciseProvider:
    def get_html_and_breadcrumbs(
        self, url: str, form_data: FormData
    ) -> Tuple[str, List[Tuple[str, str]]]:
        raise NotImplementedError()
