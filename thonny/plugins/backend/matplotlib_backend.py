import os.path
import platform

from thonny.plugins.cpython.cpython_backend import get_backend

local_conf_file = "matplotlibrc"
user_conf_file1 = os.path.expanduser("~/.config/matplotlib/matplotlibrc")
user_conf_file2 = os.path.expanduser("~/.matplotlib/matplotlibrc")

done = False


def set_default_backend(matplotlib):
    global done

    # Tried with overwriting settings only when MacOSX backend is selected
    # but querying this failed because of strange import behavior
    if (
        done
        or "MPLBACKEND" in os.environ
        or os.path.exists(local_conf_file)
        or os.path.exists(user_conf_file1)
        or os.path.exists(user_conf_file2)
    ):
        # done or the user knows what (s)he's doing
        pass
    else:

        try:
            import tkinter  # @UnusedImport

            os.environ["MPLBACKEND"] = "TkAgg"
        except ImportError:
            pass

    done = True


def load_plugin():
    if platform.system() == "Darwin":
        # https://github.com/thonny/thonny/issues/676
        backend = get_backend()
        backend.add_import_handler("matplotlib", set_default_backend)
