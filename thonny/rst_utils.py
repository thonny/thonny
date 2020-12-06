import logging
import tkinter as tk
import traceback

from thonny import get_workbench, ui_utils
from thonny.codeview import get_syntax_options_for_tag
from thonny.tktextext import TweakableText

logger = logging.getLogger(__name__)


class RstText(TweakableText):
    def __init__(self, master=None, cnf={}, read_only=False, **kw):

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
        self.configure_tags()
        self._visitor = None

    def configure_tags(self):
        main_font = tk.font.nametofont("TkDefaultFont")

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
        hyperlink_opts = get_syntax_options_for_tag("hyperlink")
        hyperlink_opts["underline"] = False
        hyperlink_opts["font"] = underline_font
        self.tag_configure("a", **hyperlink_opts)

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

    def clear(self):
        self.direct_delete("1.0", "end")

    def load_rst(self, rst_source, global_tags=()):
        self.clear()
        self.append_rst(rst_source, global_tags)

    def append_rst(self, rst_source, global_tags=()):
        try:
            import docutils.core

            doc = docutils.core.publish_doctree(rst_source)
            doc.walkabout(self.create_visitor(doc, global_tags))
        except Exception:
            self.direct_insert("end", "RST SOURCE:\n" + rst_source + "\n\n")
            self.direct_insert("end", traceback.format_exc())

        # For debugging:
        # self.direct_insert("end", doc.pformat())
        # self.direct_insert("end", rst_source)

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
                logger.warning("docutils message: '%s'. Context: %s" % (node.astext(), node.parent))
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

            def _create_unique_tag(self):
                self.unique_tag_count += 1
                return "_UT_%s" % self.unique_tag_count

            def _node_to_text(self, node):
                if node.parent.attributes.get("xml:space") == "preserve":
                    return node.astext()
                else:
                    return node.astext().replace("\r", "").replace("\n", " ")

            def _add_tag(self, tag):
                self._context_tags.append(tag)

            def _pop_tag(self, tag):
                self._context_tags.remove(tag)

            def _append_text(self, chars, extra_tags=()):
                # print("APPP", chars, tags)
                self.text.direct_insert("end", chars, self._get_effective_tags(extra_tags))

            def _append_image(self, name, extra_tags=()):
                index = self.text.index("end-1c")
                self.text.image_create(index, image=get_workbench().get_image(name))
                for tag in self._get_effective_tags(extra_tags):
                    self.text.tag_add(tag, index)

            def _append_window(self, window, extra_tags=()):
                index = self.text.index("end-1c")
                self.text.window_create(index, window=window)
                for tag in self._get_effective_tags(extra_tags):
                    self.text.tag_add(tag, index)

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

        self._visitor = TkTextRenderingVisitor(doc, self, global_tags, unique_tag_count)

        return self._visitor

    def _hyperlink_enter(self, event):
        self.config(cursor="hand2")

    def _hyperlink_leave(self, event):
        self.config(cursor="")


def escape(s):
    return (
        s.replace("\\", "\\\\")
        .replace("*", "\\*")
        .replace("`", "\\`")
        .replace("_", "\\_")
        .replace("..", "\\..")
    )


def create_title(text, line_symbol="="):
    text = text.replace("\r\n", "\n").replace("\n", " ").strip()
    return text + "\n" + line_symbol * len(text) + "\n"
