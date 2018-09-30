import os

from thonny import get_workbench

_OPTION_NAME = "run.dock_user_windows"


def toggle_variable():
    var = get_workbench().get_variable(_OPTION_NAME)
    var.set(not var.get())
    update_environment()


def update_environment():
    os.environ["DOCK_USER_WINDOWS"] = str(get_workbench().get_option(_OPTION_NAME))


def on_window_appear(event):
    get_workbench().become_active_window(force=False)


def load_plugin():
    get_workbench().set_default(_OPTION_NAME, False)
    get_workbench().add_command(
        "toggle_dock_user_windows",
        "run",
        "Dock user windows",
        toggle_variable,
        flag_name=_OPTION_NAME,
        group=35,
    )
    update_environment()

    get_workbench().bind("UserWindowAppeared", on_window_appear, True)
