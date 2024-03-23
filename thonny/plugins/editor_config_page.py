import tkinter as tk
from logging import getLogger
from tkinter import ttk
from typing import List

from thonny import get_shell, get_workbench
from thonny.config_ui import (
    ConfigurationPage,
    add_option_checkbox,
    add_option_combobox,
    add_vertical_separator,
)
from thonny.languages import tr
from thonny.ui_utils import ems_to_pixels

logger = getLogger(__name__)


class EditorConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        group_spacing = ems_to_pixels(2)

        try:
            add_option_checkbox(self, "view.name_highlighting", tr("Highlight matching names"))
        except Exception:
            # name matcher may have been disabled
            logger.warning("Couldn't create name matcher checkbox")

        try:
            add_option_checkbox(self, "view.locals_highlighting", tr("Highlight local variables"))
        except Exception:
            # locals highlighter may have been disabled
            logger.warning("Couldn't create name locals highlighter checkbox")

        add_option_checkbox(self, "view.paren_highlighting", tr("Highlight parentheses"))
        add_option_checkbox(self, "view.syntax_coloring", tr("Highlight syntax elements"))
        add_option_checkbox(self, "view.highlight_tabs", tr("Highlight tab characters"))
        add_option_checkbox(
            self,
            "view.highlight_current_line",
            tr("Highlight current line (requires reopening the editor)"),
        )

        add_vertical_separator(self)

        add_option_checkbox(
            self,
            "edit.automatic_calltips",
            tr("Automatically show parameter info after typing '('"),
        )

        add_option_checkbox(
            self,
            "edit.automatic_completions",
            tr("Automatically propose completions while typing"),
        )
        add_option_checkbox(
            self,
            "edit.automatic_completion_details",
            tr("Automatically show documentation for completions"),
        )
        add_option_checkbox(
            self,
            "edit.tab_request_completions_in_editors",
            tr("Request completions with Tab-key in editors"),
        )
        add_option_checkbox(
            self,
            "edit.tab_request_completions_in_shell",
            tr("Request completions with Tab-key in Shell"),
        )

        add_option_checkbox(
            self, "view.show_line_numbers", tr("Show line numbers"), pady=(group_spacing, 0)
        )
        add_option_checkbox(
            self,
            f"file.make_saved_shebang_scripts_executable",
            tr("Make saved shebang scripts executable"),
        )

        add_vertical_separator(self)

        add_option_combobox(
            self,
            "view.recommended_line_length",
            tr("Line length guide (use 0 to turn off)"),
            choices=[0, 60, 70, 80, 88, 90, 100, 110, 120],
            width=4,
        )

        add_option_combobox(
            self,
            "edit.tab_width",
            tr("Maximum width of a tab character"),
            choices=[1, 2, 3, 4, 5, 6, 7, 8],
            width=4,
        )

        add_option_combobox(
            self, "edit.indent_width", tr("Indent width"), choices=[1, 2, 3, 4, 5, 6, 7, 8], width=4
        )

        add_vertical_separator(self)

        add_option_checkbox(
            self,
            "edit.indent_with_tabs",
            tr("Indent with tab characters (not recommended for Python)"),
        )

        self.columnconfigure(1, weight=1)

    def apply(self, changed_options: List[str]):
        get_workbench().get_editor_notebook().update_appearance()
        shell = get_shell(create=False)
        if shell is not None:
            shell.update_appearance()


def load_plugin() -> None:
    get_workbench().add_configuration_page("editor", tr("Editor"), EditorConfigurationPage, 30)
