import os.path
import tkinter as tk
import tkinter.font
from tkinter import ttk

import thonny
from thonny import get_workbench, tktextext, ui_utils
from thonny.config import try_load_configuration
from thonny.languages import tr
from thonny.tktextext import TextFrame
from thonny.ui_utils import scrollbar_style


class HelpView(TextFrame):
    def __init__(self, master):
        from thonny import rst_utils

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
        self.language_dir = os.path.join(
            os.path.dirname(thonny.__file__),
            "locale",
            get_workbench().get_option("general.language"),
            "HELP_CONTENT",
        )
        get_workbench().bind("WorkbenchReady", self.on_workbench_ready, True)

    def on_workbench_ready(self, event=None):
        self.load_index()

    def on_show(self):
        self.load_index()

    def load_index(self):
        self.load_rst_file("index.rst")

    def load_topic(self, topic, fragment=None):
        self.load_rst_file(topic + ".rst")
        # TODO: scroll to fragment

    def load_rst_file(self, filename):
        self.text.clear()
        self.text.direct_insert("1.0", "\n")

        if os.path.isabs(filename):
            full_path = filename
        else:
            # try to access filename in a language subdirectory
            full_path = os.path.join(self.language_dir, filename)
            if not os.path.exists(full_path):
                # if the localized file does not exist, default to English
                full_path = os.path.join(os.path.dirname(__file__), filename)

        with open(full_path, encoding="UTF-8") as fp:
            rst_source = fp.read()

        if not filename.endswith("index.rst"):
            rst_source = "`" + tr("Home") + " <index.rst>`_\n\n" + rst_source

        self.text.append_rst(rst_source)


def open_help():
    get_workbench().show_view("HelpView")


def load_plugin() -> None:
    get_workbench().add_view(HelpView, tr("Help"), "ne")
    get_workbench().add_command("help_contents", "help", tr("Help contents"), open_help, group=30)
