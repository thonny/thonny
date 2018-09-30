import logging
import tkinter as tk
from tkinter import ttk

from thonny import get_workbench
from thonny.config_ui import ConfigurationPage


class EditorConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)

        try:
            self.add_checkbox("view.name_highlighting", "Highlight matching names")
        except Exception:
            # name matcher may have been disabled
            logging.warning("Couldn't create name matcher checkbox")

        try:
            self.add_checkbox("view.locals_highlighting", "Highlight local variables")
        except Exception:
            # locals highlighter may have been disabled
            logging.warning("Couldn't create name locals highlighter checkbox")

        self.add_checkbox("view.paren_highlighting", "Highlight parentheses")
        self.add_checkbox("view.syntax_coloring", "Highlight syntax elements")
        self.add_checkbox(
            "view.highlight_current_line",
            "Highlight current line (requires reopening the editor)",
        )

        self.add_checkbox(
            "edit.tab_complete_in_editor",
            "Allow code completion with Tab-key in editors",
            columnspan=2,
            pady=(20, 0),
        )
        self.add_checkbox(
            "edit.tab_complete_in_shell",
            "Allow code completion with Tab-key in Shell",
            columnspan=2,
        )

        self.add_checkbox("view.show_line_numbers", "Show line numbers", pady=(20, 0))
        self._line_length_var = get_workbench().get_variable(
            "view.recommended_line_length"
        )
        label = ttk.Label(
            self,
            text="Recommended maximum line length\n(Set to 0 to turn off margin line)",
        )
        label.grid(row=20, column=0, sticky=tk.W)
        self._line_length_combo = ttk.Combobox(
            self,
            width=4,
            exportselection=False,
            textvariable=self._line_length_var,
            state="readonly",
            values=[0, 60, 70, 80, 90, 100, 110, 120],
        )
        self._line_length_combo.grid(row=20, column=1, sticky=tk.E)

        self.columnconfigure(0, weight=1)

    def apply(self):
        ConfigurationPage.apply(self)
        get_workbench().get_editor_notebook().update_appearance()


def load_plugin() -> None:
    get_workbench().add_configuration_page("Editor", EditorConfigurationPage)
