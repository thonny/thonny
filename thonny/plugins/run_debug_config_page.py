from tkinter import ttk

from thonny import get_workbench
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr


class RunDebugConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        self.add_checkbox(
            "run.auto_cd",
            tr("Change working directory to script directory on Run / Debug"),
            row=5,
            columnspan=3,
            pady=(0, 20),
        )

        self.add_checkbox(
            "debugger.frames_in_separate_windows",
            tr("Show function calls (frames) in separate windows"),
            tooltip=tr("Uncheck if you want more traditional experience."),
            row=10,
            columnspan=3,
        )
        self.add_checkbox(
            "debugger.automatic_stack_view",
            tr("Open and close Stack view automatically"),
            tooltip=tr(
                "Opens the Stack view on first call and "
                + "closes it when program returns to main frame."
            ),
            row=20,
            columnspan=3,
        )
        self.add_checkbox(
            "debugger.allow_stepping_into_libraries",
            tr("Allow stepping into libraries (ie. outside of main script directory)"),
            tooltip=tr("May make debugging slower."),
            row=30,
            columnspan=3,
        )

        default_label = ttk.Label(self, text=tr("Preferred debugger"), anchor="w")
        default_label.grid(row=40, column=0, sticky="w", pady=(15, 0))
        self.add_combobox(
            "debugger.preferred_debugger",
            ["nicer", "faster", "birdseye"],
            width=8,
            row=40,
            column=1,
            padx=5,
            pady=(15, 0),
        )
        default_comment_label = ttk.Label(
            self, text=tr("(used when clicking Debug toolbar button)"), anchor="w"
        )
        default_comment_label.grid(row=40, column=2, sticky="w", pady=(15, 0))

        if get_workbench().get_option("run.birdseye_port", None):
            port_label = ttk.Label(self, text=tr("Birdseye port"), anchor="w")
            port_label.grid(row=50, column=0, sticky="w", pady=(5, 0))
            self.add_entry("run.birdseye_port", row=50, column=1, width=5, pady=(5, 0), padx=5)
            port_comment_label = ttk.Label(
                self, text=tr("(restart Thonny after changing this)"), anchor="w"
            )
            port_comment_label.grid(row=50, column=2, sticky="w", pady=(5, 0))

        self.columnconfigure(2, weight=1)


def load_plugin():
    get_workbench().add_configuration_page("run", tr("Run & Debug"), RunDebugConfigurationPage, 50)
