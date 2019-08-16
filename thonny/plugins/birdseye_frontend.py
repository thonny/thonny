import os.path
from threading import Thread
from tkinter import messagebox

from thonny import get_workbench, get_runner
import logging

_server_started = False


def _start_debug_enabled():
    return (
        get_workbench().get_editor_notebook().get_current_editor() is not None
        and "debug" in get_runner().get_supported_features()
    )


def start_server():
    try:
        from birdseye import server

        server.app.run(
            port=get_workbench().get_option("run.birdseye_port"), debug=False, use_reloader=False
        )
    except Exception:
        logging.getLogger("thonny").exception("Problem running Birdseye server")


def debug_with_birdseye():
    global _server_started

    try:
        import birdseye  # @UnusedImport
    except ImportError:
        if messagebox.askyesno(
            _("About Birdseye"),
            _(
                "Birdseye is a Python debugger which needs to be installed separately.\n\n"
                + "Do you want to open the help page and learn more?"
            ),
        ):
            get_workbench().open_help_topic("birdseye")

        return

    if not _server_started:
        _server_started = True
        Thread(target=start_server, daemon=True).start()

    os.environ["BIRDSEYE_PORT"] = str(get_workbench().get_option("run.birdseye_port"))
    get_runner().execute_current("Birdseye")


# order_key makes the plugin to be loaded later than other same tier plugins
# This way it gets positioned after main debug commands in the Run menu
load_order_key = "zz"


def load_plugin():
    get_workbench().set_default("run.birdseye_port", 7777)
    get_workbench().add_command(
        "birdseye",
        "run",
        _("Debug current script (birdseye)"),
        debug_with_birdseye,
        caption="birdseye",
        tester=_start_debug_enabled,
        default_sequence="<Control-B>",
        group=10,
        image=os.path.join(os.path.dirname(__file__), "..", "res", "birdseye.png"),
    )
