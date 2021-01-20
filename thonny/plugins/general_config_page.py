import tkinter as tk
from tkinter import ttk

from thonny import get_workbench, languages, tktextext
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr
from thonny.misc_utils import running_on_linux


class GeneralConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)

        self.add_checkbox(
            "general.single_instance", tr("Allow only single Thonny instance"), row=1, columnspan=2
        )
        self.add_checkbox(
            "general.event_logging", tr("Log program usage events"), row=4, columnspan=2
        )
        self.add_checkbox(
            "file.reopen_all_files",
            tr("Reopen all files from previous session"),
            row=5,
            columnspan=2,
        )
        if running_on_linux():
            self.add_checkbox(
                "file.avoid_zenity",
                tr("Use Tk file dialogs instead of Zenity"),
                tooltip=tr("Select if the file dialogs end up behind the main window"),
                row=6,
                columnspan=2,
            )

        self.add_checkbox(
            "general.disable_notification_sound",
            tr("Disable notification sound"),
            row=7,
            columnspan=2,
        )
        self.add_checkbox(
            "general.debug_mode",
            tr("Debug mode (provides more detailed diagnostic logs)"),
            row=8,
            columnspan=2,
        )

        # language
        self._language_name_var = tk.StringVar(
            value=languages.LANGUAGES_DICT.get(get_workbench().get_option("general.language"), "")
        )

        self._language_label = ttk.Label(self, text=tr("Language"))
        self._language_label.grid(row=10, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self._language_combo = ttk.Combobox(
            self,
            width=20,
            exportselection=False,
            textvariable=self._language_name_var,
            state="readonly",
            height=15,
            values=list(languages.LANGUAGES_DICT.values()),
        )
        self._language_combo.grid(row=10, column=1, sticky=tk.W, pady=(10, 0))

        # Mode
        ttk.Label(self, text=tr("UI mode")).grid(
            row=20, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0)
        )
        self.add_combobox(
            "general.ui_mode",
            ["simple", "regular", "expert"],
            row=20,
            column=1,
            pady=(10, 0),
            width=10,
        )

        # scaling
        self._scaling_label = ttk.Label(self, text=tr("UI scaling factor"))
        self._scaling_label.grid(row=30, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        scalings = ["default"] + sorted({0.5, 0.75, 1.0, 1.25, 1.33, 1.5, 2.0, 2.5, 3.0, 4.0})
        self.add_combobox("general.scaling", scalings, row=30, column=1, pady=(10, 0), width=10)

        self._font_scaling_var = get_workbench().get_variable("general.font_scaling_mode")
        self._font_scaling_label = ttk.Label(self, text=tr("Font scaling mode"))
        self._font_scaling_label.grid(row=40, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.add_combobox(
            "general.font_scaling_mode",
            ["default", "extra", "automatic"],
            row=40,
            column=1,
            pady=(10, 0),
            width=10,
        )

        env_label = ttk.Label(self, text=tr("Environment variables (one KEY=VALUE per line)"))
        env_label.grid(row=90, column=0, sticky=tk.W, pady=(20, 0), columnspan=2)
        self.env_box = tktextext.TextFrame(
            self, horizontal_scrollbar=False, height=4, borderwidth=1, undo=True, wrap="none"
        )
        self.env_box.grid(row=100, column=0, sticky="nsew", pady=(0, 10), columnspan=2)
        for entry in get_workbench().get_option("general.environment"):
            self.env_box.text.insert("end", entry + "\n")

        reopen_label = ttk.Label(
            self,
            text=tr("NB! Restart Thonny after changing these options!"),
            font="BoldTkDefaultFont",
        )
        reopen_label.grid(row=110, column=0, sticky="sw", pady=(20, 0), columnspan=2)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(100, weight=1)

    def apply(self):
        get_workbench().set_option(
            "general.language", languages.get_language_code_by_name(self._language_name_var.get())
        )
        get_workbench().update_debug_mode()

        env = []
        for entry in self.env_box.text.get("1.0", "end").strip("\r\n").splitlines():
            env.append(entry.strip("\r\n"))
        get_workbench().set_option("general.environment", env)


def load_plugin() -> None:
    get_workbench().add_configuration_page("general", tr("General"), GeneralConfigurationPage, 10)
