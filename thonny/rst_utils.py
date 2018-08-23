import docutils.core
import docutils.frontend
import docutils.utils
import docutils.parsers.rst
import tkinter as tk

from thonny.tktextext import TweakableText
from thonny import get_workbench

class RstText(TweakableText):
    
    def __init__(self, master=None, cnf={}, read_only=False, **kw):
        
        super().__init__(master=master, cnf=cnf, read_only=read_only, 
                         **{"font" : "TkDefaultFont",
                            "cursor" : "xterm",
                            **kw})
        self.configure_tags()
    
    def configure_tags(self):
        main_font = tk.font.nametofont("TkDefaultFont")
        
        bold_font = main_font.copy()
        bold_font.configure(weight="bold", size=main_font.cget("size"))
        
        h1_font = main_font.copy()
        h1_font.configure(size=main_font.cget("size") * 2, weight="bold")
        
        h2_font = main_font.copy()
        h2_font.configure(size=round(main_font.cget("size") * 1.5), weight="bold")
        
        h3_font = main_font.copy()
        h3_font.configure(size=main_font.cget("size"), weight="bold")
        
        self.tag_configure("h1", font=h1_font)
        self.tag_configure("h2", font=h2_font)
        self.tag_configure("h3", font=h3_font)
        self.tag_configure("p", spacing1=10, spacing3=10)
        self.tag_configure("a", foreground="blue", underline=True)
        
        self.tag_configure("topic_title", font=bold_font)
        self.tag_configure("code", font="TkFixedFont")
        
        toti_code_font = bold_font.copy()
        toti_code_font.configure(family=tk.font.nametofont("TkFixedFont").cget("family"))
        self.tag_configure("topic_title_code", font=toti_code_font)
        self.tag_raise("topic_title_code", "code")
        self.tag_raise("topic_title_code", "topic_title")
    
    def clear(self):
        self.direct_delete("1.0", "end")
    
    def load_rst(self, rst_source):
        self.clear()
        self.append_rst(rst_source)
    
    def render_node(self, section_level=0):
        pass
    
    def append_rst(self, rst_source):
        doc = docutils.core.publish_doctree(rst_source)
        
        visitor = TkTextRenderingVisitor(doc, self)
        doc.walkabout(visitor)
    
        self.direct_insert("end", doc.pformat())
    

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
        self._add_tag("p")
    def depart_paragraph(self, node):
        self.in_paragraph = False
        self._append_text("\n")
        self._pop_tag("p")
    
    def visit_topic(self, node):
        self.in_topic = True
        if "toggle" in node.attributes["classes"]:
            print("TO", node.children)
            
    def depart_topic(self, node):
        self.in_topic = False
    
    def visit_image(self, node):
        self._append_image(node.attributes["uri"])
        if (not self.in_paragraph
            and not self.in_title):
            self._append_text("\n")
    
    def visit_reference(self, node):
        self._add_tag("a")
    def depart_reference(self, node):
        self._pop_tag("a")
    
    def visit_literal(self, node):
        self._add_tag("code")
    def depart_literal(self, node):
        self._pop_tag("code")
    
    def visit_bullet_list(self, node):
        self.active_lists.append(node.attributes["bullet"])
        
    def depart_bullet_list(self, node):
        self.active_lists.pop()
    
    def visit_list_item(self, node):
        if self.active_lists[-1] == "*":
            self._append_text("• ")
        pass
    
    def visit_substitution_definition(self, node):
        raise docutils.nodes.SkipNode()
        
    
    def default_visit(self, node):
        self._append_text(self._node_to_text(node))
        print("skipping children", type(node), node)
        raise docutils.nodes.SkipChildren()

    def default_departure(self, node):
        # Pass all other nodes through.
        pass        
    
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
            
    def _get_effective_tags(self, extra_tags):
        tags = set(extra_tags) | set(self._context_tags)
        # combine tags
        if "code" in tags and "topic_title" in tags:
            tags.remove("code")
            tags.remove("topic_title")
            tags.add("topic_title_code")
        
        return tuple(sorted(tags))
        
        