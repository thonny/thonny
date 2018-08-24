import tkinter as tk
import tkinter.font
import os.path
from tkinter import ttk
from thonny import tktextext, rst_utils, ui_utils
from thonny import get_workbench
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
        
        self.load_rst_file("demo.rst")

    def load_rst_file(self, filename):
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
    