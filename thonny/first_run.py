import os.path
import tkinter as tk
from logging import getLogger
from tkinter import ttk

from thonny import is_portable, languages, ui_utils

logger = getLogger(__name__)

STD_MODE_TEXT = "Regular"
SIMPLE_MODE_TEXT = "Simplified"
RPI_MODE_TEXT = "Simplified, with Raspberry Pi theme and defaults"


class FirstRunWindow(tk.Tk):
    def __init__(self, configuration_manager):
        logger.info("Creating FirstRunWindow")
        super().__init__(className="Thonny")
        ttk.Style().theme_use(ui_utils.get_default_basic_theme())

        self.title("Welcome to Thonny!" + "   [portable]" if is_portable() else "")
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.ok = False

        self.conf = configuration_manager

        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=1, column=1, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.main_frame.rowconfigure(1, weight=1)

        logo_file = os.path.join(os.path.dirname(__file__), "res", "thonny.png")
        self.logo = tk.PhotoImage(file=logo_file)

        logo_label = ttk.Label(self.main_frame, image=self.logo)
        logo_label.grid(row=1, rowspan=3, column=1, sticky="nsew")

        self.padx = ui_utils.ems_to_pixels(3)
        self.pady = ui_utils.ems_to_pixels(3)

        self.language_variable = ui_utils.create_string_var(
            languages.BASE_LANGUAGE_NAME, self.on_change_language
        )
        self.add_combo(
            1, "Language:", self.language_variable, list(languages.LANGUAGES_DICT.values())
        )

        self.mode_variable = tk.StringVar(value=STD_MODE_TEXT)
        self.add_combo(
            2, "UI mode:", self.mode_variable, [STD_MODE_TEXT, SIMPLE_MODE_TEXT, RPI_MODE_TEXT]
        )

        ok_button = ttk.Button(self.main_frame, text="Let's go!", command=self.on_ok)
        ok_button.grid(
            row=3, column=3, padx=(0, self.padx), pady=(self.pady * 0.7, self.pady), sticky="se"
        )

        self.center()

    def on_change_language(self):
        print(self.language_variable.get())

    def add_combo(self, row, label_text, variable, values):
        pady = ui_utils.ems_to_pixels(0.7)
        label = ttk.Label(self.main_frame, text=label_text)
        label.grid(row=row, column=2, sticky="sw", pady=(pady, 0))
        assert isinstance(variable, tk.Variable)
        combobox = ttk.Combobox(
            self.main_frame,
            exportselection=False,
            textvariable=variable,
            state="readonly",
            height=15,
            # Actual length of longest value creates too wide combobox
            width=33 if ui_utils.running_on_mac_os() else 40,
            values=values,
        )
        combobox.grid(
            row=row,
            column=3,
            padx=(ui_utils.ems_to_pixels(1), self.padx),
            sticky="sw",
            pady=(pady, 0),
        )

    def center(self):
        # https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
        self.eval("tk::PlaceWindow . center")

    def on_ok(self):
        if self.mode_variable.get() in [SIMPLE_MODE_TEXT, RPI_MODE_TEXT]:
            self.conf.set_option("general.ui_mode", "simple")
            if self.mode_variable.get() == RPI_MODE_TEXT:
                self.conf.set_option("debugger.preferred_debugger", "faster")
                self.conf.set_option("view.ui_theme", "Raspberry Pi")

        self.conf.set_option(
            "general.language", languages.get_language_code_by_name(self.language_variable.get())
        )

        self.conf.save()

        self.ok = True
        self.destroy()
