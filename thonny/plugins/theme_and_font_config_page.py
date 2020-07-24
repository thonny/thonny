import textwrap
import tkinter as tk
from tkinter import font as tk_font
from tkinter import ttk

from thonny import get_workbench, tktextext, ui_utils
from thonny.codeview import CodeView
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr
from thonny.shell import BaseShellText
from thonny.ui_utils import create_string_var, scrollbar_style


class ThemeAndFontConfigurationPage(ConfigurationPage):
    def __init__(self, master):

        ConfigurationPage.__init__(self, master)

        self._init_themes()
        self._init_fonts()
        self._init_previews()

        self.columnconfigure(2, weight=1)
        self.columnconfigure(4, weight=1)

        self.rowconfigure(31, weight=1)
        self.rowconfigure(21, weight=1)

    def _init_themes(self):
        self._original_ui_theme = get_workbench().get_option("view.ui_theme")
        self._original_syntax_theme = get_workbench().get_option("view.syntax_theme")

        self._ui_theme_variable = create_string_var(
            self._original_ui_theme, modification_listener=self._update_appearance
        )
        self._syntax_theme_variable = create_string_var(
            self._original_syntax_theme, modification_listener=self._update_appearance
        )

        ttk.Label(self, text=tr("UI theme")).grid(
            row=1, column=1, sticky="w", pady=(0, 10), padx=(0, 5)
        )
        self._ui_theme_combo = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=self._ui_theme_variable,
            state="readonly",
            height=15,
            values=get_workbench().get_usable_ui_theme_names(),
        )
        self._ui_theme_combo.grid(row=1, column=2, sticky="nwe", pady=(0, 5))

        ttk.Label(self, text=tr("Syntax theme")).grid(
            row=2, column=1, sticky="w", pady=(0, 10), padx=(0, 5)
        )
        self._syntax_theme_combo = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=self._syntax_theme_variable,
            state="readonly",
            height=15,
            values=get_workbench().get_syntax_theme_names(),
        )
        self._syntax_theme_combo.grid(row=2, column=2, sticky="nwe", pady=(0, 5))

    def _init_fonts(self):
        self._original_editor_family = get_workbench().get_option("view.editor_font_family")
        self._original_editor_size = get_workbench().get_option("view.editor_font_size")
        self._original_io_family = get_workbench().get_option("view.io_font_family")
        self._original_io_size = get_workbench().get_option("view.io_font_size")

        self._editor_family_variable = create_string_var(
            self._original_editor_family, modification_listener=self._update_appearance
        )
        self._editor_size_variable = create_string_var(
            self._original_editor_size, modification_listener=self._update_appearance
        )
        self._io_family_variable = create_string_var(
            self._original_io_family, modification_listener=self._update_appearance
        )
        self._io_size_variable = create_string_var(
            self._original_io_size, modification_listener=self._update_appearance
        )

        ttk.Label(self, text=tr("Editor font")).grid(
            row=1, column=3, sticky="w", pady=(0, 5), padx=(25, 5)
        )
        editor_family_combo = ttk.Combobox(
            self,
            exportselection=False,
            state="readonly",
            height=15,
            textvariable=self._editor_family_variable,
            values=self._get_families_to_show(),
        )
        editor_family_combo.grid(row=1, column=4, sticky="nwe", pady=(0, 5))
        editor_size_combo = ttk.Combobox(
            self,
            width=4,
            exportselection=False,
            textvariable=self._editor_size_variable,
            state="readonly",
            height=15,
            values=[str(x) for x in range(3, 73)],
        )
        editor_size_combo.grid(row=1, column=5, sticky="nwe", pady=(0, 5), padx=(5, 0))

        ttk.Label(self, text=tr("IO font")).grid(
            row=2, column=3, sticky="w", pady=(0, 5), padx=(25, 5)
        )
        io_family_combo = ttk.Combobox(
            self,
            exportselection=False,
            state="readonly",
            height=15,
            textvariable=self._io_family_variable,
            values=self._get_families_to_show(),
        )
        io_family_combo.grid(row=2, column=4, sticky="nwe", pady=(0, 5))

        io_size_combo = ttk.Combobox(
            self,
            width=4,
            exportselection=False,
            textvariable=self._io_size_variable,
            state="readonly",
            height=15,
            values=[str(x) for x in range(3, 73)],
        )
        io_size_combo.grid(row=2, column=5, sticky="nwe", pady=(0, 5), padx=(5, 0))

    def _init_previews(self):
        ttk.Label(self, text=tr("Preview")).grid(
            row=20, column=1, sticky="w", pady=(5, 2), columnspan=5
        )
        self._preview_codeview = CodeView(
            self, height=6, font="EditorFont", relief="groove", borderwidth=1, line_numbers=True
        )

        self._preview_codeview.set_content(
            textwrap.dedent(
                """
            def foo(bar):
                if bar is None: # """
                + tr("This is a comment")
                + """
                    print('"""
                + tr("The answer is")
                + """', 33)

            """
                + tr("unclosed_string")
                + ''' = "'''
                + tr("blah, blah")
                + "\n"
            ).strip()
        )
        self._preview_codeview.grid(row=21, column=1, columnspan=5, sticky=tk.NSEW)

        self._shell_preview = tktextext.TextFrame(
            self,
            text_class=BaseShellText,
            height=4,
            vertical_scrollbar_style=scrollbar_style("Vertical"),
            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            relief="groove",
            borderwidth=1,
            font="EditorFont",
        )
        self._shell_preview.grid(row=31, column=1, columnspan=5, sticky=tk.NSEW, pady=(5, 5))
        self._shell_preview.text.set_read_only(True)
        self._insert_shell_text()

        ttk.Label(
            self,
            text=tr("NB! Some style elements change only after restarting Thonny!"),
            font="BoldTkDefaultFont",
        ).grid(row=40, column=1, columnspan=5, sticky="w", pady=(5, 0))

    def apply(self):
        # don't do anything, as preview already did the thing
        return

    def cancel(self):
        if (
            getattr(self._editor_family_variable, "modified")
            or getattr(self._editor_size_variable, "modified")
            or getattr(self._ui_theme_variable, "modified")
            or getattr(self._syntax_theme_variable, "modified")
        ):
            get_workbench().set_option("view.ui_theme", self._original_ui_theme)
            get_workbench().set_option("view.syntax_theme", self._original_syntax_theme)
            get_workbench().set_option("view.editor_font_size", self._original_editor_size)
            get_workbench().set_option("view.editor_font_family", self._original_editor_family)
            get_workbench().set_option("view.io_font_size", self._original_io_size)
            get_workbench().set_option("view.io_font_family", self._original_io_family)
            get_workbench().reload_themes()
            get_workbench().update_fonts()

    def _update_appearance(self):
        get_workbench().set_option("view.ui_theme", self._ui_theme_variable.get())
        get_workbench().set_option("view.syntax_theme", self._syntax_theme_variable.get())
        get_workbench().set_option("view.editor_font_size", int(self._editor_size_variable.get()))
        get_workbench().set_option("view.editor_font_family", self._editor_family_variable.get())
        get_workbench().set_option("view.io_font_size", int(self._io_size_variable.get()))
        get_workbench().set_option("view.io_font_family", self._io_family_variable.get())
        get_workbench().reload_themes()
        get_workbench().update_fonts()

    def _insert_shell_text(self):
        text = self._shell_preview.text
        text._insert_prompt()
        text.direct_insert("end", "%Run demo.py\n", ("magic", "before_io"))
        text.tag_add("before_io", "1.0", "1.0 lineend")
        text.direct_insert("end", tr("Enter an integer") + ": ", ("io", "stdout"))
        text.direct_insert("end", "2.5\n", ("io", "stdin"))
        text.direct_insert(
            "end", "ValueError: invalid literal for int() with base 10: '2.5'\n", ("io", "stderr")
        )

    def _get_families_to_show(self):
        # In Linux, families may contain duplicates (actually different fonts get same names)
        return sorted(set(filter(lambda name: name[0].isalpha(), tk_font.families())))


def load_plugin() -> None:
    get_workbench().add_configuration_page(
        "theme", tr("Theme & Font"), ThemeAndFontConfigurationPage, 40
    )
