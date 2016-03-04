from jedi import Script
from thonny.globals import get_workbench

NAME_CONF = {'background': 'Black', 'foreground': 'White'}


class NameHighlighter:

    def __init__(self):
        self.text = None
        self.bound_ids = {}

    def _highlight(self):
        if not self.text:
            return
        self.text.tag_delete("NAME")
        self.text.tag_config("NAME", NAME_CONF)
        index = self.text.index("insert").split(".")
        l, c = int(index[0]), int(index[1])
        script = Script(self.text.get('1.0', 'end'), l, c)
        m = script._parser.module()

        for u in script.usages():

            print(u)
            line, column = (u.line, u.column)
            if None not in (line, column):
                begin = "%d.%d" % (line, column)
                end = begin + ("+%dc" % len(u.name))
                self.text.tag_add("NAME", "%d.%d" % (line, column), end)

    def _on_change(self, event):
        self._highlight()

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


def load_plugin():
    wb = get_workbench()  # type:Workbench
    nb = wb.get_editor_notebook()  # type:EditorNotebook

    name_hl = NameHighlighter()

    nb.bind("<<NotebookTabChanged>>", name_hl._on_editor_change, True)