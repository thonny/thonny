import tkinter as tk
from jedi import Script
from jedi.parser import tree
from thonny.globals import get_workbench

class GlobLocHighlighter:

    def __init__(self, text, local_variable_font=None):
        self.text = text
        
        if local_variable_font:
            self.local_variable_font=local_variable_font
        else:
            self.local_variable_font = self.text["font"]
        
        self._configure_tags()

    def get_positions(self):

        globs = []
        locs = []

        def process_scope(scope):
            if isinstance(scope.get_parent_scope(), tree.Module):
                globs.append(scope.children[1])
            else:
                locs.append(scope.children[1])
            for c in scope.children[2:]:
                if isinstance(c, tree.BaseNode):
                    process_node(c)

        def process_node(node, module_scope=False, local_bindings=[], global_names=[]):
            if isinstance(node, tree.Name):
                if isinstance(node.get_definition(), tree.GlobalStmt):
                    global_names.append(node.value)
                if not module_scope and node.is_definition() and node.value not in global_names:
                    local_bindings.append(node.value)
                if module_scope or node.value not in local_bindings:
                    globs.append(node)
                else:
                    locs.append(node)
            elif isinstance(node, tree.BaseNode):
                if node.is_scope():
                    global_names = []
                for c in node.children:
                    process_node(c, module_scope, local_bindings, global_names)

        def process_module():
            for c in module.children:
                if isinstance(c, tree.BaseNode):
                    if c.is_scope():
                        process_scope(c)
                    else:
                        process_node(c, module_scope=True)

        index = self.text.index("insert").split(".")
        line, column = int(index[0]), int(index[1])
        script = Script(self.text.get('1.0', 'end'), line, column)
        module = script._parser.module()

        process_module()

        loc_pos = set(("%d.%d" % (usage.start_pos[0], usage.start_pos[1]),
                "%d.%d" % (usage.start_pos[0], usage.start_pos[1] + len(usage.value)))
                for usage in locs)
        glob_pos = set(("%d.%d" % (usage.start_pos[0], usage.start_pos[1]),
                "%d.%d" % (usage.start_pos[0], usage.start_pos[1] + len(usage.value)))
                for usage in globs)

        return glob_pos, loc_pos

    def _configure_tags(self):
        self.text.tag_configure("GLOBAL_NAME", {})
        self.text.tag_configure("LOCAL_NAME",
                                font=self.local_variable_font, 
                                foreground="#000055")
        self.text.tag_raise("sel")
        
    def _highlight(self, pos_info):
        self.text.tag_remove("GLOBAL_NAME", "1.0", "end")
        self.text.tag_remove("LOCAL_NAME", "1.0", "end")

        for pos in pos_info[0]:
            start_index, end_index = pos[0], pos[1]
            self.text.tag_add("GLOBAL_NAME", start_index, end_index)

        for pos in pos_info[1]:
            start_index, end_index = pos[0], pos[1]
            self.text.tag_add("LOCAL_NAME", start_index, end_index)

    def update(self, event=None):
        highlight_positions = self.get_positions()
        self._highlight(highlight_positions)


def update_highlighting(event):
    assert isinstance(event.widget, tk.Text)
    text = event.widget
    
    if not hasattr(text, "global_local_highlighter"):
        text.global_local_highlighter = GlobLocHighlighter(text,
            get_workbench().get_font("ItalicEditorFont"))
        
    text.global_local_highlighter.update(event)


def load_plugin():
    wb = get_workbench()
    wb.bind_class("CodeViewText", "<<TextChange>>", update_highlighting, True)
    
    