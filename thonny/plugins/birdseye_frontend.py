import atexit
import os.path
import subprocess
from tkinter import messagebox

from thonny import THONNY_USER_DIR, get_runner, get_workbench, running
from thonny.languages import tr

_server_started = False
_server_process = None


def _start_debug_enabled():
    return (
        get_workbench().get_editor_notebook().get_current_editor() is not None
        and "debug" in get_runner().get_supported_features()
    )


def start_server():
    global _server_process

    out_err_filename = os.path.join(THONNY_USER_DIR, "birdseye.log")
    output_file = open(out_err_filename, "w")
    _server_process = subprocess.Popen(
        [
            running.get_interpreter_for_subprocess(),
            "-m",
            "birdseye",
            "-p",
            str(get_workbench().get_option("run.birdseye_port")),
        ],
        stdout=output_file,
        stderr=output_file,
    )
    atexit.register(close_server)


def close_server():
    if _server_process is not None:
        try:
            _server_process.kill()
        except Exception:
            pass


def debug_with_birdseye():
    global _server_started

    try:
        import birdseye  # @UnusedImport
    except ImportError:
        if messagebox.askyesno(
            tr("About Birdseye"),
            tr(
                "Birdseye is a Python debugger which needs to be installed separately.\n\n"
                + "Do you want to open the help page and learn more?"
            ),
            master=get_workbench(),
        ):
            get_workbench().open_help_topic("birdseye")

        return

    if not _server_started:
        start_server()
        _server_started = True

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
        tr("Debug current script (birdseye)"),
        debug_with_birdseye,
        caption="birdseye",
        tester=_start_debug_enabled,
        default_sequence="<Control-B>",
        group=10,
        image=os.path.join(os.path.dirname(__file__), "..", "res", "birdseye.png"),
    )
