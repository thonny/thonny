import os.path
import tkinter as tk
import tkinter.font
from tkinter import ttk

from thonny import get_workbench, rst_utils, tktextext, ui_utils, CONFIGURATION_FILE_NAME
from thonny.config import try_load_configuration
from thonny.tktextext import TextFrame
from thonny.ui_utils import scrollbar_style

class HelpView(TextFrame):
    def __init__(self, master):
        TextFrame.__init__(
            self,
            master,
            text_class=rst_utils.RstText,
            vertical_scrollbar_style=scrollbar_style("Vertical"),
            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            borderwidth=0,
            wrap="word",
            relief="flat",
            padx=20,
            pady=0,
            read_only=True,
        )
        # retrieve the directory of the preferred language
        # for help's .rst files ; this directory is ./ by default
        self.languageDir="."
        self._configuration_manager = try_load_configuration(CONFIGURATION_FILE_NAME)
        self.languageDir=self._configuration_manager.get_option("general.language",".")
        self.load_rst_file("index.rst")

    def load_topic(self, topic, fragment=None):
        self.load_rst_file(topic + ".rst")
        # TODO: scroll to fragment

    def load_rst_file(self, filename):
        self.text.clear()
        self.text.direct_insert("1.0", "\n")

        # try to access filename in a language subdirectory
        if not os.path.isabs(filename):
            filename1 = os.path.join(os.path.dirname(__file__), self.languageDir, filename)
        if not os.path.exists(filename1):
            # if the localized file does not exist, default to English
            filename1 = os.path.join(os.path.dirname(__file__), filename)

        with open(filename1, encoding="UTF-8") as fp:
            self.text.append_rst(fp.read())


def open_help():
    get_workbench().show_view("HelpView")


def load_plugin() -> None:
    get_workbench().add_view(HelpView, "Help", "ne")
    get_workbench().add_command("help_contents", "help", "Help contents", open_help, group=30)
