import os.path
import tkinter as tk
from tkinter import ttk

from thonny import is_portable, languages, ui_utils

STD_MODE_TEXT = "Standard"
RPI_MODE_TEXT = "Raspberry Pi"


class FirstRunWindow(tk.Tk):
    def __init__(self, configuration_manager):
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

        self.padx = 50
        self.pady = 50

        self.language_variable = ui_utils.create_string_var(
            languages.BASE_LANGUAGE_NAME, self.on_change_language
        )
        self.add_combo(
            1, "Language:", self.language_variable, list(languages.LANGUAGES_DICT.values())
        )

        self.mode_variable = tk.StringVar(value=STD_MODE_TEXT)
        self.add_combo(2, "Initial settings:", self.mode_variable, [STD_MODE_TEXT, RPI_MODE_TEXT])

        ok_button = ttk.Button(self.main_frame, text="Let's go!", command=self.on_ok)
        ok_button.grid(
            row=3, column=3, padx=(0, self.padx), pady=(self.pady * 0.7, self.pady), sticky="se"
        )

        self.center()

    def on_change_language(self):
        print(self.language_variable.get())

    def add_combo(self, row, label_text, variable, values):
        pady = 7
        label = ttk.Label(self.main_frame, text=label_text)
        label.grid(row=row, column=2, sticky="sw", pady=(pady, 0))
        assert isinstance(variable, tk.Variable)
        combobox = ttk.Combobox(
            self.main_frame,
            exportselection=False,
            textvariable=variable,
            state="readonly",
            height=15,
            width=20,
            values=values,
        )
        combobox.grid(row=row, column=3, padx=(10, self.padx), sticky="sw", pady=(pady, 0))

    def center(self):
        width = max(self.winfo_reqwidth(), 640)
        height = max(self.winfo_reqheight(), 300)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        if screen_width > screen_height * 2:
            # probably dual monitors
            screen_width //= 2

        left = max(int(screen_width / 2 - width / 2), 0)
        top = max(int(screen_height / 2 - height / 2), 0)

        # Positions the window in the center of the page.
        self.geometry("+{}+{}".format(left, top))

    def on_ok(self):
        if self.mode_variable.get() == RPI_MODE_TEXT:
            self.conf.set_option("debugger.preferred_debugger", "faster")
            self.conf.set_option("view.ui_theme", "Raspberry Pi")
            self.conf.set_option("general.ui_mode", "simple")

        self.conf.set_option(
            "general.language", languages.get_language_code_by_name(self.language_variable.get())
        )

        self.conf.save()

        self.ok = True
        self.destroy()
