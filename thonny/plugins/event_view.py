""" Helper view for Thonny developers
"""

import tkinter as tk
from thonny.ui_utils import TextFrame

class EventsView(TextFrame):
    def __init__(self, master, workbench):
        TextFrame.__init__(self, master, readonly=False)
        #self.text.config(wrap=tk.WORD)
        workbench.bind("ShowView", self._log_event)
        workbench.bind("HideView", self._log_event)
    
    
    def _log_event(self, event):
        self.text.insert("end", event.sequence + "\n")
        for name in dir(event):
            if name not in ["sequence", "setdefault", "update"] and not name.startswith("_"):
                self.text.insert("end", "    " + name + ": " + repr(getattr(event, name))[:100] + "\n")


def load_plugin(workbench):
    workbench.add_view(EventsView, "Events", "se")