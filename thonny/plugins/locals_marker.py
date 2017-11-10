import tkinter as tk
from thonny.globals import get_workbench
import logging
import thonny.jedi_utils as jedi_utils

class LocalsHighlighter:

    def __init__(self, text, local_variable_font=None):
        self.text = text
        
        if local_variable_font:
            self.local_variable_font=local_variable_font
        else:
            self.local_variable_font = self.text["font"]
        
        self._configure_tags()
        self._update_scheduled = False
    
    def get_positions(self):
        return self._get_positions_correct_but_using_private_parts()
    
    def _get_positions_simple_but_incorrect(self):
        # goto_assignments only gives you last assignment to given node
        import jedi
        defs = jedi.names(self.text.get('1.0', 'end'), path="",
                           all_scopes=True, definitions=True, references=True)
        result = set()
        for definition in defs:
            if definition.parent().type == "function": # is located in a function
                ass = definition.goto_assignments()
                if len(ass) > 0 and ass[0].parent().type == "function": # is assigned to in a function
                    pos = ("%d.%d" % (definition.line, definition.column),
                           "%d.%d" % (definition.line, definition.column+len(definition.name)))
                    result.add(pos)
        return result
        
    
    def _get_positions_correct_but_using_private_parts(self):
        from jedi import Script
        
        tree = jedi_utils.import_tree()

        locs = []

        def process_scope(scope):
            if isinstance(scope, tree.Function):
                # process all children after name node,
                # (otherwise name of global function will be marked as local def)
                local_names = set() 
                global_names = set()
                for child in scope.children[2:]:
                    process_node(child, local_names, global_names)
            else:
                for child in scope.subscopes:
                    process_scope(child)
        
        def process_node(node, local_names, global_names):
            if isinstance(node, tree.GlobalStmt):
                global_names.update([n.value for n in node.get_global_names()])
                
            elif isinstance(node, tree.Name):
                if node.value in global_names:
                    return
                
                if node.is_definition(): # local def
                    locs.append(node)
                    local_names.add(node.value)
                elif node.value in local_names: # use of local 
                    locs.append(node)
                    
            elif isinstance(node, tree.BaseNode):
                # ref: jedi/parser/grammar*.txt
                if node.type == "trailer" and node.children[0].value == ".":
                    # this is attribute
                    return
                
                if isinstance(node, tree.Function):
                    global_names = set() # outer global statement doesn't have effect anymore
                
                for child in node.children:
                    process_node(child, local_names, global_names)

        source = self.text.get('1.0', 'end')
        script = Script(source + ")") # https://github.com/davidhalter/jedi/issues/897
        module = jedi_utils.get_module_node(script)
        for child in module.children:
            if isinstance(child, tree.BaseNode) and jedi_utils.is_scope(child):
                process_scope(child)

        loc_pos = set(("%d.%d" % (usage.start_pos[0], usage.start_pos[1]),
                "%d.%d" % (usage.start_pos[0], usage.start_pos[1] + len(usage.value)))
                for usage in locs)

        return loc_pos

    def _configure_tags(self):
        self.text.tag_configure("LOCAL_NAME",
                                font=self.local_variable_font, 
                                foreground="#000055")
        self.text.tag_raise("sel")
        
    def _highlight(self, pos_info):
        for pos in pos_info:
            start_index, end_index = pos[0], pos[1]
            self.text.tag_add("LOCAL_NAME", start_index, end_index)

    def schedule_update(self):
        def perform_update():
            try:
                self.update()
            finally:
                self._update_scheduled = False
        
        if not self._update_scheduled:
            self._update_scheduled = True
            self.text.after_idle(perform_update)
            
    def update(self):
        self.text.tag_remove("LOCAL_NAME", "1.0", "end")
        
        if get_workbench().get_option("view.locals_highlighting"):
            try:
                highlight_positions = self.get_positions()
                self._highlight(highlight_positions)
            except:
                logging.exception("Problem when updating local variable tags")


def update_highlighting(event):
    assert isinstance(event.widget, tk.Text)
    text = event.widget
    
    if not hasattr(text, "local_highlighter"):
        text.local_highlighter = LocalsHighlighter(text,
            get_workbench().get_font("ItalicEditorFont"))
        
    text.local_highlighter.schedule_update()


def load_plugin():
    if jedi_utils.get_version_tuple() < (0, 9):
        logging.warning("Jedi version is too old. Disabling locals marker")
        return 
    
    wb = get_workbench()
    wb.set_default("view.locals_highlighting", False)
    wb.bind_class("CodeViewText", "<<TextChange>>", update_highlighting, True)
    wb.bind("<<UpdateAppearance>>", update_highlighting, True)
    
