import docutils.core
import docutils.nodes
import tkinter as tk

from thonny.tktextext import TweakableText
from thonny import get_workbench
from thonny.codeview import get_syntax_options_for_tag
import logging

class RstText(TweakableText):
    
    def __init__(self, master=None, cnf={}, read_only=False, **kw):
        
        super().__init__(master=master, cnf=cnf, read_only=read_only, 
                         **{"font" : "TkDefaultFont",
                            "cursor" : "",
                            **kw})
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
        
        self.tag_configure("h1", font=h1_font)
        self.tag_configure("h2", font=h2_font)
        self.tag_configure("h3", font=h3_font)
        self.tag_configure("p", spacing1=10, spacing3=10, spacing2=0)
        self.tag_configure("em", font=italic_font)
        self.tag_configure("strong", font=bold_font)
        self.tag_configure("a", **get_syntax_options_for_tag("hyperlink"))
        self.tag_bind("a", "<Enter>", self._hyperlink_enter)
        self.tag_bind("a", "<Leave>", self._hyperlink_leave)
        
        self.tag_configure("topic_title", font=bold_font, lmargin2=16)
        self.tag_configure("topic_body", lmargin1=16, lmargin2=16)
        self.tag_configure("code", font="TkFixedFont")
        
        for i in range(1,6):
            self.tag_configure("list%d" % i, lmargin1=i*10, lmargin2=i*10+10)
        
        toti_code_font = bold_font.copy()
        toti_code_font.configure(family=tk.font.nametofont("TkFixedFont").cget("family"),
                                 size=bold_font.cget("size"))
        self.tag_configure("topic_title_code", font=toti_code_font)
        self.tag_raise("topic_title_code", "code")
        self.tag_raise("topic_title_code", "topic_title")
    
    def clear(self):
        self.direct_delete("1.0", "end")
    
    def load_rst(self, rst_source):
        self.clear()
        self.append_rst(rst_source)
    
    def append_rst(self, rst_source):
        doc = docutils.core.publish_doctree(rst_source)
        doc.walkabout(self.get_visitor(doc))
    
        # For debugging:
        #self.direct_insert("end", doc.pformat())
    
    def get_visitor(self, doc):
        # Reuse existing visitor if text is being composed 
        # from multiple documents. Otherwise tags won't be unique
        # (Yes, this means second doc won't be attached to the visitor,
        # but it doesn't matter)
        
        if self._visitor is None:
            self._visitor = TkTextRenderingVisitor(doc, self)
        
        return self._visitor
        
    
    def _hyperlink_enter(self, event):
        self.config(cursor="hand2")
        
    def _hyperlink_leave(self, event):
        self.config(cursor="")

class TkTextRenderingVisitor(docutils.nodes.GenericNodeVisitor):
    
    def __init__(self, document, text):
        super().__init__(document)
        
        self._context_tags = []
        self.text = text
        self.section_level = 0
        self.in_topic = False
        self.in_paragraph = False
        self.in_title = False
        
        self.active_lists = []
        
        self.unique_tag_count = 0
    
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
            return "h%d" % (self.section_level+1)
    
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
    
    def visit_topic(self, node):
        self.in_topic = True
        
        if "toggle" in node.attributes["classes"]:
            return self._visit_toggle_topic(node)
        else:
            return self.default_visit(node)
    
    def _visit_toggle_topic(self, node):
        tag = self._create_unique_tag()
        title_id_tag = tag + "_title"
        body_id_tag = tag + "_body"
        
        if "open" in node.attributes["classes"]:
            initial_image = "boxminus"
            initial_elide = False
        else:
            initial_image = "boxplus"
            initial_elide = True
            
        label = tk.Label(self.text,
                         image=get_workbench().get_image(initial_image),
                         borderwidth=0,
                         background="white")
        
        def toggle_body(event=None):
            elide = self.text.tag_cget(body_id_tag, "elide")
            if elide == '1':
                elide = True
            elif elide == '0':
                elide = False
            else:
                elide = bool(elide)
            
            elide = not elide
            
            self.text.tag_configure(body_id_tag, elide=elide)
            if self.text.has_selection():
                self.text.tag_remove("sel", "1.0", "end")
            
            if elide:
                label.configure(image=get_workbench().get_image("boxplus"))
            else:
                label.configure(image=get_workbench().get_image("boxminus"))
        
        assert isinstance(node.children[0], docutils.nodes.title)
        
        self.text.tag_bind(title_id_tag, "<1>", toggle_body, True)
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
        
        raise docutils.nodes.SkipNode()
            
    def depart_topic(self, node):
        self.in_topic = False
    
    def visit_image(self, node):
        self._append_image(node.attributes["uri"])
        if (not self.in_paragraph
            and not self.in_title):
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
                    self._append_text("%d. " % (i+1))
                    break
    
    def visit_substitution_definition(self, node):
        raise docutils.nodes.SkipNode()
    
    def visit_system_message(self, node):
        logging.getLogger("thonny").warning("docutils message: '%s'. Context: %s" 
                                            % (node.astext(), node.parent))
        raise docutils.nodes.SkipNode
    
    def visit_emphasis(self, node):
        self._add_tag("em")    
    def depart_emphasis(self, node):
        self._pop_tag("em")    
    
    def visit_strong(self, node):
        self._add_tag("strong")    
    def depart_strong(self, node):
        self._pop_tag("strong")    
    
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
        return (node.astext()
                .replace("\r", "")
                .replace("\n", " "))
                          
    def _add_tag(self, tag):
        self._context_tags.append(tag)
        
    def _pop_tag(self, tag):
        self._context_tags.remove(tag)
    
    def _append_text(self, chars, extra_tags=()):
        #print("APPP", chars, tags)
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
        

def escape(s):
    return (s
            .replace("\\", "\\\\")
            .replace("*", "\\*")
            .replace("`", "\\`")
            .replace("_", "\\_")
            .replace("..", "\\.."))

