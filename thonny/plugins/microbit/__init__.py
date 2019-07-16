import sys
import os.path
from thonny.plugins.micropython import (
    MicroPythonProxy,
    MicroPythonConfigPage,
    add_micropython_backend,
)
from thonny import get_workbench, ui_utils
from thonny.ui_utils import FileCopyDialog
from thonny.misc_utils import find_volume_by_name
import shutil
from time import sleep


class MicrobitProxy(MicroPythonProxy):
    def _start_background_process(self, clean=None):
        # NB! Sometimes disconnecting and reconnecting (on macOS?)
        # too quickly causes anomalies
        # https://github.com/pyserial/pyserial/issues/176
        # In my Sierra, Calliope and micro:bit seemed to soft-reboot
        # when reconnected too quickly.

        if clean and sys.platform == "darwin":
            sleep(1.0)

        super()._start_background_process(clean)

    def supports_directories(self):
        return False


class MicrobitConfigPage(MicroPythonConfigPage):
    def _get_usb_driver_url(self):
        return "https://microbit-micropython.readthedocs.io/en/latest/devguide/repl.html"


def flash_the_firmware(hex_path):
    mount_path = find_volume_by_name(
        "MICROBIT",
        not_found_msg="Could not find disk '%s'.\n"
        + "Make sure you have micro:bit plugged in!\n\n"
        + "Do you want to continue and locate the disk yourself?",
    )
    if mount_path is None:
        return

    destination_path = os.path.join(mount_path, os.path.basename(hex_path))

    dlg = FileCopyDialog(
        get_workbench(),
        hex_path,
        destination_path,
        "Uploading %s to %s" % (os.path.basename(hex_path), mount_path),
    )
    ui_utils.show_dialog(dlg)

def flash_bundled_firmware():
    flash_the_firmware(os.path.join(os.path.dirname(__file__), "firmware.hex"))

def load_plugin():
    add_micropython_backend(
        "microbit", MicrobitProxy, "MicroPython (BBC micro:bit)", MicrobitConfigPage
    )

    get_workbench().add_command(
        "InstallMicroPythonMicrobit",
        "device",
        _("Install MicroPython to BBC micro:bit"),
        flash_bundled_firmware,
        group=40,
    )
