from tkinter import messagebox
from typing import List

from thonny import get_workbench, languages
from thonny.config_ui import (
    ConfigurationPage,
    add_label_and_box_for_list_of_strings,
    add_option_checkbox,
    add_option_combobox,
    add_text_row,
    add_vertical_separator,
)
from thonny.languages import tr
from thonny.misc_utils import running_on_linux
from thonny.ui_utils import get_last_grid_row


class GeneralConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        add_option_checkbox(
            self, "general.single_instance", tr("Allow only single Thonny instance")
        )
        add_option_checkbox(self, "general.event_logging", tr("Log program usage events"))
        add_option_checkbox(
            self,
            "file.reopen_all_files",
            tr("Reopen all files from previous session"),
        )
        if running_on_linux():
            add_option_checkbox(
                self,
                "file.avoid_zenity",
                tr("Use Tk file dialogs instead of Zenity"),
                tooltip=tr("Select if the file dialogs end up behind the main window"),
            )

        add_option_checkbox(
            self,
            "general.disable_notification_sound",
            tr("Disable notification sound"),
        )
        add_option_checkbox(
            self,
            "general.debug_mode",
            tr("Debug mode (provides more detailed diagnostic logs)"),
        )

        add_vertical_separator(self)

        add_option_combobox(
            self,
            "general.language",
            tr("Language"),
            choices={value: key for (key, value) in languages.LANGUAGES_DICT.items()},
            width=20,
        )

        add_option_combobox(
            self, "general.ui_mode", tr("UI mode"), choices=["simple", "regular"], width=10
        )

        add_option_combobox(
            self,
            "general.scaling",
            tr("UI scaling factor"),
            choices=["default"] + sorted({0.5, 0.75, 1.0, 1.25, 1.33, 1.5, 2.0, 2.5, 3.0, 4.0}),
            width=10,
        )

        add_option_combobox(
            self,
            "general.font_scaling_mode",
            tr("Font scaling mode"),
            choices=["default", "extra", "automatic"],
            width=10,
        )

        add_vertical_separator(self)

        self.env_box = add_label_and_box_for_list_of_strings(
            self,
            tr("Environment variables (one KEY=VALUE per line)"),
            get_workbench().get_option("general.environment"),
        )
        self.rowconfigure(get_last_grid_row(self), weight=1)
        self.columnconfigure(1, weight=1)

        add_vertical_separator(self)

        add_text_row(
            self,
            tr("NB! Restart Thonny after changing these options!"),
            font="BoldTkDefaultFont",
        )

    def apply(self, changed_options: List[str]):
        get_workbench().update_debug_mode()

        env = []
        for entry in self.env_box.text.get("1.0", "end").strip("\r\n").splitlines():
            entry = entry.strip("\r\n")
            env.append(entry)

        if any(entry.endswith("'") or entry.endswith('"') for entry in env):
            if not messagebox.askyesno(
                tr("Warning"),
                tr(
                    "If you quote the value of an environment variable, the quotes will"
                    " be part of the value.\nDid you intend this?"
                ),
                parent=self,
            ):
                return False

        get_workbench().set_option("general.environment", env)


def load_plugin() -> None:
    get_workbench().add_configuration_page("general", tr("General"), GeneralConfigurationPage, 10)
