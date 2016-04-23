from jedi import Script
from jedi.parser import tree
from thonny.globals import get_workbench

GLOBAL_CONF = {'background': 'White', 'foreground': 'Black'}
LOCAL_CONF = {'background': 'Pink', 'foreground': 'Brown'}

class NameHighlighter:

    def __init__(self):
        self.text = None
        self.bound_ids = {}

    def get_positions(self):

        globs = []
        locs = []

        def find_names(node, loc_decl_funcs=[], glob_stmts=[]):
            names = []
            if node.type == "power" and node.children[0].value not in loc_decl_funcs and \
                not (isinstance(node.children[1], tree.BaseNode) and
                            node.children[1].type == "trailer" and node.children[1].children[0].value == "."):
                children = node.children[1:]
                globs.append(node.children[0])
            else:
                children = node.children
            for c in children:
                if isinstance(c, tree.Name):
                    names.append(c)
                elif isinstance(c, tree.GlobalStmt):
                    globs.append(c.children[1])
                    glob_stmts.append(c.children[1].value)
                elif isinstance(c, tree.BaseNode):
                    names.extend(find_names(c, loc_decl_funcs, glob_stmts))
            return names

        def process_subscope(scope, loc_declared_funcs=[]):
            glob_stmts = []
            if isinstance(scope, tree.Class):

                supers = scope.get_super_arglist()
                supers_names = []
                if isinstance(supers, tree.Name):
                    globs.append(supers)
                    supers_names.append(supers)
                else:
                    supers_names.extend(find_names(supers))
                    globs.extend(supers_names)

                children = scope.children[len(supers_names)*2+3:]
            else:
                children = scope.children
            for c in children:
                if isinstance(c, tree.BaseNode):

                    if isinstance(c, tree.ClassOrFunc):
                        loc_declared_funcs.append(c.children[1].value)
                        locs.append(c.children[1])
                        process_subscope(c, loc_declared_funcs=loc_declared_funcs)

                    elif c.type == "simple_stmt" and isinstance(c.children[0], tree.GlobalStmt):
                        glob_name = c.children[0].children[1]
                        glob_stmts.append(glob_name.value)
                        globs.append(glob_name)
                    else:
                        names = find_names(c, loc_decl_funcs=loc_declared_funcs, glob_stmts=glob_stmts)
                        for name in names:
                            if name.value in glob_stmts:
                                globs.append(name)
                            else:
                                locs.append(name)



        index = self.text.index("insert").split(".")
        l, c = int(index[0]), int(index[1])
        script = Script(self.text.get('1.0', 'end'), l, c)
        module = script._parser.module()

        # first find names in module scope
        for child in module.children:
            if isinstance(child, tree.Scope):
                globs.append(child.children[1])     # second child of ClassOrFunc is Name
                if isinstance(child, tree.ClassOrFunc):
                    process_subscope(child)

            elif tree.is_node(child, "simple_stmt"):
                globs.extend(find_names(child))

        loc_pos = set(("%d.%d" % (usage.start_pos[0], usage.start_pos[1]),
                "%d.%d" % (usage.start_pos[0], usage.start_pos[1] + len(usage.value)))
                for usage in locs)
        glob_pos = set(("%d.%d" % (usage.start_pos[0], usage.start_pos[1]),
                "%d.%d" % (usage.start_pos[0], usage.start_pos[1] + len(usage.value)))
                for usage in globs)

        return glob_pos, loc_pos

    def _highlight(self, pos_info):
        if not self.text:
            return

        self.text.tag_delete("GLOBAL_NAME")
        self.text.tag_config("GLOBAL_NAME", GLOBAL_CONF)

        self.text.tag_delete("LOCAL_NAME")
        self.text.tag_config("LOCAL_NAME", LOCAL_CONF)

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

        # ...and bind the paren checking procedure to that widget's cursor move event
        self.bound_ids["<<CursorMove>>"] = self.text.bind("<<CursorMove>>", self._on_change, True)
        self.bound_ids["<<TextChange>>"] = self.text.bind("<<TextChange>>", self._on_change, True)
        self._on_change(None)


def _load_plugin():
    wb = get_workbench()  # type:Workbench
    nb = wb.get_editor_notebook()  # type:EditorNotebook

    name_hl = NameHighlighter()
    nb.bind("<<NotebookTabChanged>>", name_hl._on_editor_change, True)