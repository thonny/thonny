from typing import List

from thonny import get_workbench
from thonny.config_ui import (
    ConfigurationPage,
    add_label_and_box_for_list_of_strings,
    add_option_checkbox,
    add_vertical_separator,
)
from thonny.languages import tr
from thonny.ui_utils import get_last_grid_row


class AssistantConfigPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        add_option_checkbox(
            self,
            "assistance.open_assistant_on_errors",
            tr("Open Assistant automatically when program crashes with an exception"),
        )

        add_option_checkbox(
            self,
            "assistance.open_assistant_on_warnings",
            tr("Open Assistant automatically when it has warnings for your code"),
        )

        if get_workbench().get_option("assistance.use_pylint", "missing") != "missing":
            add_option_checkbox(self, "assistance.use_pylint", tr("Perform selected Pylint checks"))

        if get_workbench().get_option("assistance.use_mypy", "missing") != "missing":
            add_option_checkbox(self, "assistance.use_mypy", tr("Perform MyPy checks"))

        add_vertical_separator(self)
        self.disabled_checks_box = add_label_and_box_for_list_of_strings(
            self,
            tr("Disabled checks (one id per line)"),
            get_workbench().get_option("assistance.disabled_checks"),
        )
        self.columnconfigure(1, weight=1)
        self.rowconfigure(get_last_grid_row(self), weight=1)

    def apply(self, changed_options: List[str]):
        disabled_checks_str = (
            self.disabled_checks_box.text.get("1.0", "end")
            .replace("\r", "")
            .replace('"', "")
            .replace("'", "")
            .strip()
        )
        get_workbench().set_option("assistance.disabled_checks", disabled_checks_str.splitlines())


def load_plugin():
    get_workbench().add_configuration_page("assistant", tr("Assistant"), AssistantConfigPage, 80)
