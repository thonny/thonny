from thonny import get_workbench
from thonny.config_ui import (
    ConfigurationPage,
    add_option_checkbox,
    add_option_combobox,
    add_vertical_separator,
)
from thonny.languages import tr


class RunDebugConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        add_option_checkbox(
            self,
            "run.allow_running_unnamed_programs",
            tr("Allow running unnamed programs"),
        )

        add_option_checkbox(
            self,
            "run.auto_cd",
            tr("Change working directory to script directory on Run / Debug"),
        )
        add_option_checkbox(
            self,
            "run.warn_module_shadowing",
            tr("Warn if a user module shadows a library module"),
        )

        add_vertical_separator(self)

        add_option_checkbox(
            self,
            "debugger.frames_in_separate_windows",
            tr("Show function calls (frames) in separate windows"),
            tooltip=tr("Uncheck if you want more traditional experience."),
        )
        add_option_checkbox(
            self,
            "debugger.automatic_stack_view",
            tr("Open and close Stack view automatically"),
            tooltip=tr(
                "Opens the Stack view on first call and closes it when program returns to main frame."
            ),
        )
        add_option_checkbox(
            self,
            "debugger.allow_stepping_into_libraries",
            tr("Allow stepping into libraries (ie. outside of main script directory)"),
            tooltip=tr("May make debugging slower."),
        )

        add_vertical_separator(self)

        add_option_combobox(
            self,
            "debugger.preferred_debugger",
            tr("Preferred debugger"),
            choices=["nicer", "faster", "birdseye"],
            width=8,
            tooltip=tr("(used when clicking Debug toolbar button)"),
        )

        add_option_combobox(
            self,
            "run.birdseye_port",
            tr("Birdseye port"),
            choices=[7777, 7778, 7779],
            width=8,
            tooltip="Change if the first port is used by something else.\nRestart Thonny after changing.",
        )

        self.columnconfigure(1, weight=1)


def load_plugin():
    get_workbench().add_configuration_page("run", tr("Run & Debug"), RunDebugConfigurationPage, 50)
