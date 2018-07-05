import os
from thonny import get_workbench

_OPTION_NAME = "run.keep_user_window_on_top"

def toggle_variable():
    var = get_workbench().get_variable(_OPTION_NAME)
    var.set(not var.get())
    update_environment()

def update_environment():
    os.environ["KEEP_USER_WINDOW_ON_TOP"] = str(get_workbench().get_option(_OPTION_NAME))

def load_plugin():
    get_workbench().set_default(_OPTION_NAME, False)
    get_workbench().add_command("toggle_keep_window_on_top", "run", 
                                "Keep user window on top",
                                toggle_variable,
                                flag_name=_OPTION_NAME)
    update_environment()