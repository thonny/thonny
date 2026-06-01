import logging
import os.path

from thonny.plugins.cpython_backend import get_backend

logger = logging.getLogger(__name__)

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
            logger.debug("Set MPLBACKEND=TkAgg for matplotlib")
        except ImportError:
            pass

    done = True


def load_plugin():
    # Register the import handler on all platforms, not just macOS.
    # On macOS the MacOSX backend causes window-close issues (#676).
    # On Linux/Raspberry Pi and Windows, matplotlib may also pick an
    # unavailable or broken backend (e.g. GTK3Agg, Qt5Agg) when tkinter
    # is the correct choice inside Thonny.  Setting MPLBACKEND=TkAgg
    # early prevents ImportError cascades caused by missing backend libs.
    # https://github.com/thonny/thonny/issues/676
    backend = get_backend()
    backend.add_import_handler("matplotlib", set_default_backend)
