from tkinter import ttk

from thonny.config_ui import ConfigurationPage
from thonny import get_workbench, ui_utils
from thonny.tktextext import TextFrame
from thonny.ui_utils import scrollbar_style


class AssistantConfigPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        self.add_checkbox(
            "assistance.open_assistant_on_errors",
            "Open Assistant automatically when program crashes with an exception",
            row=1,
        )

        self.add_checkbox(
            "assistance.open_assistant_on_warnings",
            "Open Assistant automatically when it has warnings for your code",
            row=2,
        )

        disabled_checks_label = ttk.Label(
            self, text="Disabled checks (one id per line)"
        )
        disabled_checks_label.grid(row=3, sticky="nw", pady=(10, 0))

        self.disabled_checks_box = TextFrame(
            self,
            vertical_scrollbar_style=scrollbar_style("Vertical"),
            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            wrap="word",
            font="TkDefaultFont",
            # cursor="arrow",
            padx=5,
            pady=5,
            height=4,
            borderwidth=1,
            relief="groove",
        )
        self.disabled_checks_box.grid(row=4, sticky="nsew", pady=(0, 10))
        self.disabled_checks_box.text.insert(
            "1.0", "\n".join(get_workbench().get_option("assistance.disabled_checks"))
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

    def apply(self):
        disabled_checks_str = (
            self.disabled_checks_box.text.get("1.0", "end")
            .replace("\r", "")
            .replace('"', "")
            .replace("'", "")
            .strip()
        )
        get_workbench().set_option(
            "assistance.disabled_checks", disabled_checks_str.splitlines()
        )


def load_plugin():
    get_workbench().add_configuration_page("Assistant", AssistantConfigPage)
