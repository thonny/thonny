import os.path
import tkinter as tk
import tkinter.font
from tkinter import ttk

from thonny import get_workbench, rst_utils, tktextext, ui_utils
from thonny.tktextext import TextFrame
from thonny.ui_utils import scrollbar_style


class HelpView(TextFrame):
    def __init__(self, master):
        TextFrame.__init__(
            self, master,
            text_class=rst_utils.RstText, 
            vertical_scrollbar_style=scrollbar_style("Vertical"), 
            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            borderwidth=0, 
            wrap="word",
            relief="flat",
            padx=10,
            pady=0,
        )
        
        self.load_rst_file("help.rst")
    
    def load_topic(self, topic, fragment=None):
        self.load_rst_file(topic + ".rst")
        # TODO: scroll to fragment
    
    def load_rst_file(self, filename):
        self.text.clear()
        
        if not os.path.isabs(filename):
            filename = os.path.join(os.path.dirname(__file__), filename) 
            
        with open(filename, encoding="UTF-8") as fp:
            self.text.append_rst(fp.read())


def open_help():
    get_workbench().show_view("HelpView")

def load_plugin() -> None:
    get_workbench().add_view(HelpView, "Help", "ne")
    get_workbench().add_command("help_contents", "help", "Help contents",
                                open_help,
                                group=30)
