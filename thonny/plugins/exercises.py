import logging
import traceback
from html.parser import HTMLParser
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from thonny import tktextext, ui_utils, get_workbench
from thonny.codeview import get_syntax_options_for_tag
from thonny.languages import tr
from thonny.ui_utils import scrollbar_style, lookup_style_option

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
            link_handler=self._on_link_click,
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

        self.breadcrumbs_bar = BreadcrumbsBar(header_frame, self._on_link_click)

        self.breadcrumbs_bar.grid(row=0, column=0, sticky="nsew")

        # self.menu_button = ttk.Button(header_frame, text="≡ ", style="ViewToolbar.Toolbutton")
        self.menu_button = ttk.Button(
            header_frame, text=" ≡ ", style="ViewToolbar.Toolbutton", command=self.post_button_menu
        )
        # self.menu_button.grid(row=0, column=1, sticky="ne")
        self.menu_button.place(anchor="ne", rely=0, relx=1)

    def _on_link_click(self, target):
        print("target", target)
        if target == _HOME_KEY:
            self.go_to_provider_selection_page()
        elif target.startswith("!"):
            self._provider_name = target[1:]
            self.go_to("/")
        else:
            get_workbench().open_url(target)

    def post_button_menu(self):
        self.refresh_menu(context="button")
        self.menu.tk_popup(
            self.menu_button.winfo_rootx(),
            self.menu_button.winfo_rooty() + self.menu_button.winfo_height(),
        )

    def go_to(self, url):
        assert url.startswith("/")
        assert self._provider_name is not None
        provider = self._get_provider()
        html, breadcrumbs = provider.get_html_and_breadcrumbs(url)
        self._set_page_html(html)
        self.breadcrumbs_bar.set_links(self._get_base_breadcrumb_links() + breadcrumbs)

    def go_to_provider_selection_page(self):
        self._provider_name = None

        provider_records = sorted(
            self._provider_records_by_name.values(), key=lambda p: p["sort_key"]
        )

        html = "algus"
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
    def __init__(self, master, link_handler, cnf={}, read_only=False, **kw):

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
        self._link_handler = link_handler
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
        h1_font.configure(size=main_font.cget("size") * 2, weight="bold")

        h2_font = main_font.copy()
        h2_font.configure(size=round(main_font.cget("size") * 1.5), weight="bold")

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
        self._renderer = HtmlRenderer(self, self._link_handler)

    def clear(self):
        self.direct_delete("1.0", "end")
        self.tag_delete("1.0", "end")
        self._reset_renderer()

    def create_visitor(self, doc, global_tags=()):
        # Pass unique tag count from previous visitor
        # to keep uniqueness

        if self._visitor is None:
            unique_tag_count = 0
        else:
            unique_tag_count = self._visitor.unique_tag_count

        import docutils.nodes

        class TkTextRenderingVisitor(docutils.nodes.GenericNodeVisitor):
            def __init__(self, document, text, global_tags=(), unique_tag_count=0):
                super().__init__(document)

                self._context_tags = list(global_tags)
                self.text = text
                self.section_level = 0
                self.in_topic = False
                self.in_paragraph = False
                self.in_title = False

                self.active_lists = []

                self.unique_tag_count = unique_tag_count

            def visit_document(self, node):
                pass

            def visit_Text(self, node):
                self._append_text(self._node_to_text(node))

            def visit_section(self, node):
                self.section_level += 1

            def depart_section(self, node):
                self.section_level -= 1

            def _get_title_tag(self):
                if self.in_topic:
                    return "topic_title"
                else:
                    return "h%d" % (self.section_level + 1)

            def visit_title(self, node):
                self.in_title = True
                self._add_tag(self._get_title_tag())

            def depart_title(self, node):
                self.in_title = False
                self._append_text("\n")
                self._pop_tag(self._get_title_tag())

            def visit_paragraph(self, node):
                self.in_paragraph = True
                if not self.active_lists:
                    self._add_tag("p")

            def depart_paragraph(self, node):
                self.in_paragraph = False
                self._append_text("\n")
                if not self.active_lists:
                    self._pop_tag("p")

            def visit_line_block(self, node):
                self._add_tag("line_block")

            def depart_line_block(self, node):
                self._pop_tag("line_block")

            def visit_line(self, node):
                pass

            def depart_line(self, node):
                self._append_text("\n")

            def visit_topic(self, node):
                self.in_topic = True

                if "toggle" in node.attributes["classes"]:
                    return self._visit_toggle_topic(node)
                elif "empty" in node.attributes["classes"]:
                    return self._visit_empty_topic(node)
                else:
                    return self.default_visit(node)

            def _visit_toggle_topic(self, node):
                tag = self._create_unique_tag()
                title_id_tag = tag + "_title"
                body_id_tag = tag + "_body"

                def get_toggler_image_name(kind):
                    if get_workbench().uses_dark_ui_theme():
                        return kind + "_light"
                    else:
                        return kind

                if "open" in node.attributes["classes"]:
                    initial_image = get_toggler_image_name("boxminus")
                    initial_elide = False
                else:
                    initial_image = get_toggler_image_name("boxplus")
                    initial_elide = True

                label = tk.Label(
                    self.text,
                    image=get_workbench().get_image(initial_image),
                    borderwidth=0,
                    background=self.text["background"],
                    cursor="arrow",
                )

                def toggle_body(event=None):
                    elide = self.text.tag_cget(body_id_tag, "elide")
                    if elide == "1":
                        elide = True
                    elif elide == "0":
                        elide = False
                    else:
                        elide = bool(elide)

                    elide = not elide

                    self.text.tag_configure(body_id_tag, elide=elide)
                    if self.text.has_selection():
                        self.text.tag_remove("sel", "1.0", "end")

                    if elide:
                        label.configure(
                            image=get_workbench().get_image(get_toggler_image_name("boxplus"))
                        )
                    else:
                        label.configure(
                            image=get_workbench().get_image(get_toggler_image_name("boxminus"))
                        )

                assert isinstance(node.children[0], docutils.nodes.title)

                # self.text.tag_bind(title_id_tag, "<1>", toggle_body, True)
                self._add_tag(title_id_tag)
                self._append_window(label)
                label.bind("<1>", toggle_body, True)
                node.children[0].walkabout(self)
                self._pop_tag(title_id_tag)

                self.text.tag_configure(body_id_tag, elide=initial_elide)
                self._add_tag(body_id_tag)
                self._add_tag("topic_body")
                for child in list(node.children)[1:]:
                    child.walkabout(self)
                self._pop_tag("topic_body")
                self._pop_tag(body_id_tag)

                if "tight" not in node.attributes["classes"]:
                    self._append_text("\n")

                raise docutils.nodes.SkipNode()

            def _visit_empty_topic(self, node):
                img = get_workbench().get_image(
                    "boxdot_light" if get_workbench().uses_dark_ui_theme() else "boxdot"
                )
                label = tk.Label(
                    self.text,
                    image=img,
                    borderwidth=0,
                    background=self.text["background"],
                    cursor="arrow",
                )
                self._append_window(label)
                assert isinstance(node.children[0], docutils.nodes.title)
                node.children[0].walkabout(self)

                if "tight" not in node.attributes["classes"]:
                    self._append_text("\n")

                raise docutils.nodes.SkipNode()

            def depart_topic(self, node):
                # only for non-toggle topics
                self.in_topic = False
                self._append_text("\n")

            def visit_image(self, node):
                self._append_image(node.attributes["uri"])
                if not self.in_paragraph and not self.in_title:
                    self._append_text("\n")

            def visit_reference(self, node):
                tag = self._create_unique_tag()
                node.unique_tag = tag
                self._add_tag("a")
                self._add_tag(tag)

                def handle_click(event):
                    get_workbench().open_url(node.attributes["refuri"])

                self.text.tag_bind(tag, "<ButtonRelease-1>", handle_click)

            def depart_reference(self, node):
                self._pop_tag("a")
                self._pop_tag(node.unique_tag)

            def visit_literal(self, node):
                self._add_tag("code")

            def depart_literal(self, node):
                self._pop_tag("code")

            def visit_inline(self, node):
                for cls in node.attributes["classes"]:
                    self._add_tag(cls)

            def depart_inline(self, node):
                for cls in node.attributes["classes"]:
                    self._pop_tag(cls)

            def visit_literal_block(self, node):
                self._add_tag("code")

            def depart_literal_block(self, node):
                self._pop_tag("code")
                self._append_text("\n\n")

            def visit_bullet_list(self, node):
                self.active_lists.append(node.attributes["bullet"])

            def depart_bullet_list(self, node):
                self._append_text("\n")
                self.active_lists.pop()

            def visit_enumerated_list(self, node):
                self.active_lists.append(node.attributes["enumtype"])

            def depart_enumerated_list(self, node):
                self._append_text("\n")
                self.active_lists.pop()

            def visit_list_item(self, node):
                if self.active_lists[-1] == "*":
                    self._append_text("• ")
                elif self.active_lists[-1] == "arabic":
                    for i, sib in enumerate(node.parent.children):
                        if sib is node:
                            self._append_text("%d. " % (i + 1))
                            break

            def visit_note(self, node):
                self._add_tag("em")

            def depart_note(self, node):
                self._pop_tag("em")

            def visit_target(self, node):
                pass

            def visit_substitution_definition(self, node):
                raise docutils.nodes.SkipNode()

            def visit_system_message(self, node):
                logging.getLogger("thonny").warning(
                    "docutils message: '%s'. Context: %s" % (node.astext(), node.parent)
                )
                raise docutils.nodes.SkipNode

            def visit_emphasis(self, node):
                self._add_tag("em")

            def depart_emphasis(self, node):
                self._pop_tag("em")

            def visit_strong(self, node):
                self._add_tag("strong")

            def depart_strong(self, node):
                self._pop_tag("strong")

            def visit_block_quote(self, node):
                self._add_tag("code")

            def depart_block_quote(self, node):
                self._pop_tag("code")

            def default_visit(self, node):
                self._append_text(self._node_to_text(node))
                print("skipping children", type(node), node)
                raise docutils.nodes.SkipChildren()

            def default_departure(self, node):
                # Pass all other nodes through.
                pass

    def _hyperlink_enter(self, event):
        self.config(cursor="hand2")

    def _hyperlink_leave(self, event):
        self.config(cursor="")


class HtmlRenderer(HTMLParser):
    def __init__(self, text_widget, link_handler):
        super().__init__()
        self.widget = text_widget
        self._link_handler = link_handler
        self._unique_tag_count = 0
        self._context_tags = []
        self.active_lists = []
        self._block_tags = ["div", "p", "ul", "ol", "pre", "code", "form"]
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

        if tag == "a":
            if "href" in attrs:
                self._add_tag("a")
                link_tag = self._create_unique_tag()
                self._add_tag(link_tag)

                def handle_click(event):
                    self._link_handler(attrs["href"])

                self.widget.tag_bind(tag, "<ButtonRelease-1>", handle_click)

        if tag in self._simple_tags:
            self._add_tag(tag)
        elif tag in self._block_tags:
            self._append_text("\n")

    def handle_endtag(self, tag):
        tag = self._normalize_tag(tag)
        if tag in self._ignored_tags:
            return
        else:
            self._active_attrs_by_tag[tag] = {}

        if tag in self._simple_tags:
            self._pop_tag(tag)
        elif tag in self._block_tags:
            self._append_text("\n")

    def handle_data(self, data):
        self._append_text(self._prepare_text(data))

    def _create_unique_tag(self):
        self._unique_tag_count += 1
        return "_UT_%s" % self._unique_tag_count

    def _normalize_tag(self, tag):
        return self._alternatives.get(tag, tag)

    def _add_tag(self, tag):
        self._context_tags.append(tag)

    def _pop_tag(self, tag):
        while self._context_tags and self._context_tags[-1] != "tag":
            # remove unclosed or synthetic other tags
            self._context_tags.pop()

        if self._context_tags:
            assert self._context_tags[-1] == "tag"
            self._context_tags.pop()

    def _prepare_text(self, text):
        if self._context_tags and self._context_tags[-1] in ["pre", "code"]:
            return text
        else:
            text = text.replace("\n", " ").replace("\r", " ")
            while "  " in text:
                text = text.replace("  ", " ")
            return text

    def _append_text(self, chars, extra_tags=()):
        # print("APPP", chars, tags)
        self.widget.direct_insert("end", chars, self._get_effective_tags(extra_tags))

    def _append_image(self, name, extra_tags=()):
        index = self.widget.index("end-1c")
        self.widget.image_create(index, image=get_workbench().get_image(name))
        for tag in self._get_effective_tags(extra_tags):
            self.widget.tag_add(tag, index)

    def _append_window(self, window, extra_tags=()):
        index = self.widget.index("end-1c")
        self.widget.window_create(index, window=window)
        for tag in self._get_effective_tags(extra_tags):
            self.widget.tag_add(tag, index)

    def _get_effective_tags(self, extra_tags):
        tags = set(extra_tags) | set(self._context_tags)

        if self.active_lists:
            tags.add("list%d" % min(len(self.active_lists), 5))

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


class ExerciseProvider:
    pass


class DemoExerciseProvider(ExerciseProvider):
    def __init__(self, exercises_view):
        self.exercises_view = exercises_view

    def get_html_and_breadcrumbs(self, url):
        return ("<h1>Demo</h1>", [])


def load_plugin():
    get_workbench().add_view(ExercisesView, tr("Exercises"), "ne")
    get_workbench().add_exercise_provider("demo", "Demo provider", DemoExerciseProvider)
