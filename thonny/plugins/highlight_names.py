from jedi import Script
from jedi.parser import tree
from thonny.globals import get_workbench
import tkinter as tk

NAME_CONF = {'background' : '#e6ecfe'}


class NameHighlighter:

    def __init__(self, text):
        self.text = text
        self.text.tag_configure("NAME", NAME_CONF)
        self.text.tag_raise("sel")

    @staticmethod
    def is_name_function_call_name(name):
        stmt = name.get_definition()
        return stmt.type == "power" and stmt.children[0] == name

    @staticmethod
    def is_name_function_definition(name):
        scope = name.get_definition()
        return isinstance(scope, tree.Function) and scope.children[1].value == name.value

    @staticmethod
    def get_def_from_function_params(func_node, name):
        params = func_node.params
        for param in params:
            if param.children[0].value == name.value:
                return param.children[0]
        return None

    # copied from jedi's tree.py with a few modifications
    @staticmethod
    def get_statement_for_position(node, pos):
        for c in node.children:
            # sorted here, because the end_pos property depends on the last child having the last position,
            # there seems to be a problem with jedi, where the children of a node are not always in the right order
            if isinstance(c, tree.Class):
                c.children.sort(key=lambda x: x.end_pos)
            if c.start_pos <= pos <= c.end_pos:
                if c.type not in ('decorated', 'simple_stmt', 'suite') \
                        and not isinstance(c, (tree.Flow, tree.ClassOrFunc)):
                    return c
                else:
                    try:
                        return c.get_statement_for_position(pos)
                    except AttributeError:
                        print("error")
                        pass
        return None

    @staticmethod
    def is_global_stmt_with_name(node, name_str):
        return isinstance(node, tree.BaseNode) and node.type == "simple_stmt" and \
               isinstance(node.children[0], tree.GlobalStmt) and \
               node.children[0].children[1].value == name_str

    @staticmethod
    def find_definition(scope, name):

        # if the name is the name of a function definition
        if isinstance(scope, tree.Function):
            if scope.children[1] == name:
                return scope.children[1]  # 0th child is keyword "def", 1st is name
            else:
                definition = NameHighlighter.get_def_from_function_params(scope, name)
                if definition:
                    return definition

        for c in scope.children:
            if isinstance(c, tree.BaseNode) and c.type == "simple_stmt" and isinstance(c.children[0], tree.ImportName):
                for n in c.children[0].get_defined_names():
                    if n.value == name.value:
                        return n
                # print(c.path_for_name(name.value))
            if isinstance(c, tree.Function) and c.children[1].value == name.value and \
                    not isinstance(c.get_parent_scope(), tree.Class):
                return c.children[1]
            if isinstance(c, tree.BaseNode) and c.type == "suite":
                for x in c.children:
                    if NameHighlighter.is_global_stmt_with_name(x, name.value):
                        return NameHighlighter.find_definition(scope.get_parent_scope(), name)
                    if isinstance(x, tree.Name) and x.is_definition() and x.value == name.value:
                        return x
                    def_candidate = NameHighlighter.find_def_in_simple_node(x, name)
                    if def_candidate:
                        return def_candidate

        if not isinstance(scope, tree.Module):
            return NameHighlighter.find_definition(scope.get_parent_scope(), name)

        # if name itself is the left side of an assignment statement, then the name is the definition
        if name.is_definition():
            return name

        return None

    @staticmethod
    def find_def_in_simple_node(node, name):
        if isinstance(node, tree.Name) and node.is_definition() and node.value == name.value:
            return name
        if not isinstance(node, tree.BaseNode):
            return None
        for c in node.children:
            return NameHighlighter.find_def_in_simple_node(c, name)

    @staticmethod
    def get_dot_names(stmt):
        try:
            if stmt.children[1].children[0].value == ".":
                return stmt.children[0], stmt.children[1].children[1]
        except:
            return ()
        return ()

    @staticmethod
    def find_usages(name, stmt, module):
        # check if stmt is dot qualified, disregard these
        dot_names = NameHighlighter.get_dot_names(stmt)
        if len(dot_names) > 1 and dot_names[1].value == name.value:
            return set()

        # search for definition
        definition = NameHighlighter.find_definition(name.get_parent_scope(), name)

        searched_scopes = set()

        is_function_definition = NameHighlighter.is_name_function_definition(definition) if definition else False

        def find_usages_in_node(node, global_encountered=False):
            names = []
            if isinstance(node, tree.BaseNode):
                if node.is_scope():
                    global_encountered = False
                    if node in searched_scopes:
                        return names
                    searched_scopes.add(node)
                    if isinstance(node, tree.Function):
                        d = NameHighlighter.get_def_from_function_params(node, name)
                        if d and d != definition:
                            return []

                for c in node.children:
                    dot_names = NameHighlighter.get_dot_names(c)
                    if len(dot_names) > 1 and dot_names[1].value == name.value:
                        continue
                    sub_result = find_usages_in_node(c, global_encountered=global_encountered)

                    if sub_result is None:
                        if not node.is_scope():
                            return None if definition and node != definition.get_parent_scope() else [definition]
                        else:
                            sub_result = []
                    names.extend(sub_result)
                    if NameHighlighter.is_global_stmt_with_name(c, name.value):
                        global_encountered = True
            elif isinstance(node, tree.Name) and node.value == name.value:
                if definition and definition != node:
                    if NameHighlighter.is_name_function_definition(node):
                        if isinstance(node.get_parent_scope().get_parent_scope(), tree.Class):
                            return []
                        else:
                            return None
                    if node.is_definition() and not global_encountered and \
                            (is_function_definition or node.get_parent_scope() != definition.get_parent_scope()):
                            return None
                    if NameHighlighter.is_name_function_definition(definition) and \
                            isinstance(definition.get_parent_scope().get_parent_scope(), tree.Class):
                        return None
                names.append(node)
            return names

        if definition:
            if NameHighlighter.is_name_function_definition(definition):
                scope = definition.get_parent_scope().get_parent_scope()
            else:
                scope = definition.get_parent_scope()
        else:
            scope = name.get_parent_scope()

        usages = find_usages_in_node(scope)
        return usages

    def get_positions(self):
        index = self.text.index("insert")
        
        # ignore if cursor in STRING_OPEN
        if self.text.tag_prevrange("STRING_OPEN", index):
            return set()

        index_parts = index.split('.')
        l, c = int(index_parts[0]), int(index_parts[1])
        script = Script(self.text.get('1.0', 'end') + ")", l, c)
        
        name = None
        stmt = NameHighlighter.get_statement_for_position(script._parser.module(), script._pos)

        if isinstance(stmt, tree.Name):
            name = stmt
        elif isinstance(stmt, tree.BaseNode):
            name = stmt.name_for_position(script._pos)

        if not name:
            return set()

        # format usage positions as tkinter text widget indices
        return set(("%d.%d" % (usage.start_pos[0], usage.start_pos[1]),
                      "%d.%d" % (usage.start_pos[0], usage.start_pos[1] + len(name.value)))
                        for usage in NameHighlighter.find_usages(name, stmt, script._parser.module()))


    def update(self):
        self.text.tag_remove("NAME", "1.0", "end")

        for pos in self.get_positions():
            start_index, end_index = pos[0], pos[1]
            self.text.tag_add("NAME", start_index, end_index)


def update_highlighting(event):
    assert isinstance(event.widget, tk.Text)
    text = event.widget
    
    if not hasattr(text, "name_highlighter"):
        text.name_highlighter = NameHighlighter(text)
        
    text.name_highlighter.update()


def load_plugin():
    wb = get_workbench()  # type:Workbench

    wb.bind_class("CodeViewText", "<<CursorMove>>", update_highlighting, True)
    wb.bind_class("CodeViewText", "<<TextChange>>", update_highlighting, True)
    