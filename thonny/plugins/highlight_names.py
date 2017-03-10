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
        l, c = int(index_parts[0]), int(index_parts[1])
        script = Script(self.text.get('1.0', 'end') + ")", line=l, column=c)
        try:
            usages = script.usages()
        except:
            # TODO: Find out what's wrong
            #traceback.print_exc()
            usages = []
        
        result = {("%d.%d" % (usage.start_pos[0], usage.start_pos[1]),
                  "%d.%d" % (usage.start_pos[0], usage.start_pos[1] + len(usage.name)))
                for usage in usages}
        #print(result)
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
    