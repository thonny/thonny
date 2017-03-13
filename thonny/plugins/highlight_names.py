from jedi import Script
from thonny.globals import get_workbench
import tkinter as tk
import logging

NAME_CONF = {'background' : '#e6ecfe'}


class NameHighlighter:

    def __init__(self, text):
        self.text = text
        self.text.tag_configure("NAME", NAME_CONF)
        self.text.tag_raise("sel")
        self._update_scheduled = False


    def get_positions(self):
        index = self.text.index("insert")
        
        # ignore if cursor in STRING_OPEN
        if self.text.tag_prevrange("STRING_OPEN", index):
            return set()

        index_parts = index.split('.')
        line, column = int(index_parts[0]), int(index_parts[1])
        
        # With path="" I get current script usages with module_name == ""
        script = Script(self.text.get('1.0', 'end') + ")", line=line, column=column, path="")
        
        usages = script.usages()
        
        result = {("%d.%d" % (usage.line, usage.column),
                  "%d.%d" % (usage.line, usage.column + len(usage.name)))
                for usage in usages if usage.module_name == ""}
        
        return result


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
        self.text.tag_remove("NAME", "1.0", "end")
        
        if get_workbench().get_option("view.name_highlighting"):
            try:
                for pos in self.get_positions():
                    start_index, end_index = pos[0], pos[1]
                    self.text.tag_add("NAME", start_index, end_index)
            except:
                logging.exception("Problem when updating name highlighting")


def update_highlighting(event):
    assert isinstance(event.widget, tk.Text)
    text = event.widget
    
    if not hasattr(text, "name_highlighter"):
        text.name_highlighter = NameHighlighter(text)
        
    text.name_highlighter.schedule_update()


def load_plugin():
    wb = get_workbench()  # type:Workbench
    wb.add_option("view.name_highlighting", True)
    wb.bind_class("CodeViewText", "<<CursorMove>>", update_highlighting, True)
    wb.bind_class("CodeViewText", "<<TextChange>>", update_highlighting, True)
    wb.bind("<<UpdateAppearance>>", update_highlighting, True)
    