from jedi import Script
from jedi.parser import tree
from thonny.globals import get_workbench

GLOBAL_CONF = {'background': 'White', 'foreground': 'Black'}
LOCAL_CONF = {'underline': 1}


class GlobLocHighlighter:

    def __init__(self):
        self.text = None
        self.bound_ids = {}

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
        self.text.tag_configure("GLOBAL_NAME", GLOBAL_CONF)
        self.text.tag_configure("LOCAL_NAME", LOCAL_CONF)
        self.text.tag_raise("sel")
        
    def _highlight(self, pos_info):
        if not self.text:
            return

        self.text.tag_remove("GLOBAL_NAME", "1.0", "end")
        self.text.tag_remove("LOCAL_NAME", "1.0", "end")

        for pos in pos_info[0]:
            start_index, end_index = pos[0], pos[1]
            self.text.tag_add("GLOBAL_NAME", start_index, end_index)

        for pos in pos_info[1]:
            start_index, end_index = pos[0], pos[1]
            self.text.tag_add("LOCAL_NAME", start_index, end_index)

    def _on_change(self, event):
        highlight_positions = self.get_positions()
        self._highlight(highlight_positions)

    def _on_editor_change(self, event):
        if self.text:
            # unbind events from previous editor's text
            for k, v in self.bound_ids.items():
                self.text.unbind(k, v)

        # get the active text widget from the active editor of the active tab of the editor notebook
        self.text = event.widget.get_current_editor().get_text_widget()
        self._configure_tags()

        # ...and bind the paren checking procedure to that widget's cursor move event
        self.bound_ids["<<CursorMove>>"] = self.text.bind("<<CursorMove>>", self._on_change, True)
        self.bound_ids["<<TextChange>>"] = self.text.bind("<<TextChange>>", self._on_change, True)
        self._on_change(None)


def load_plugin():
    wb = get_workbench()
    nb = wb.get_editor_notebook()

    name_hl = GlobLocHighlighter()
    nb.bind("<<NotebookTabChanged>>", name_hl._on_editor_change, True)