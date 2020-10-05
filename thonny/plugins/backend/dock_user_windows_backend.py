import os

from thonny.common import BackendEvent
from thonny.plugins.cpython.cpython_backend import get_backend

_last_pos = (None, None)
_notification_is_sent = False
_LAST_POS_SETTING = "dock_user_windows.last_position"


def on_configure(event):
    global _last_pos, _notification_is_sent
    pos = event.x, event.y
    if pos != _last_pos:
        get_backend().set_option(_LAST_POS_SETTING, pos)

    if not _notification_is_sent:
        get_backend().send_message(BackendEvent("UserWindowAppeared"))
        _notification_is_sent = True


def patch_tkinter(module):
    flag_name = "has_docking_patch"
    if getattr(module, flag_name, False):
        return

    original_constructor = module.Tk.__init__

    def patched_Tk_constructor(self, *args, **kw):
        original_constructor(self, *args, **kw)

        try:
            # move window to the same place it was previously
            last_pos = get_backend().get_option(_LAST_POS_SETTING)
            if isinstance(last_pos, tuple):
                self.geometry("+%d+%d" % last_pos)

            self.wm_attributes("-topmost", 1)
            # self.overrideredirect(1)

            # I'm using bind_class because turtle._Screen later overwrites the bind handler
            self.bind_class("Tk", "<Configure>", on_configure, True)
        except Exception:
            # expected to fail when constructing Tcl for _cmd_process_gui_events
            pass

    module.Tk.__init__ = patched_Tk_constructor
    setattr(module, flag_name, True)


def patch_turtle(module):
    # Turtle needs more tweaking because it later overrides the position set in the Tk constructor
    turtle_config = getattr(module, "_CFG", None)
    if isinstance(turtle_config, dict):
        last_pos = get_backend().get_option(_LAST_POS_SETTING)
        if isinstance(last_pos, tuple):
            turtle_config["leftright"], turtle_config["topbottom"] = last_pos


def load_plugin():
    if os.environ.get("DOCK_USER_WINDOWS", "False").lower() == "true":
        backend = get_backend()
        backend.add_import_handler("tkinter", patch_tkinter)
        backend.add_import_handler("turtle", patch_turtle)
