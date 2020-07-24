import os

from thonny import get_workbench
from thonny.languages import tr

_OPTION_NAME = "run.pgzero_mode"


def toggle_variable():
    var = get_workbench().get_variable(_OPTION_NAME)
    var.set(not var.get())
    update_environment()


def update_environment():
    if get_workbench().in_simple_mode():
        os.environ["PGZERO_MODE"] = "auto"
    else:
        os.environ["PGZERO_MODE"] = str(get_workbench().get_option(_OPTION_NAME))


def load_plugin():
    get_workbench().set_default(_OPTION_NAME, False)
    get_workbench().add_command(
        "toggle_pgzero_mode",
        "run",
        tr("Pygame Zero mode"),
        toggle_variable,
        flag_name=_OPTION_NAME,
        group=40,
    )
    update_environment()
