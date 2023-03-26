import os.path
import sys
import time
from time import sleep
from typing import Dict, List, Optional

from thonny import ui_utils
from thonny.languages import tr
from thonny.plugins.micropython import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
    add_micropython_backend,
)
from thonny.plugins.micropython.mp_common import PASTE_SUBMIT_MODE
from thonny.plugins.micropython.uf2dialog import (
    TargetInfo,
    Uf2FlashingDialog,
    create_volume_description,
)

LATEST_RELEASE_URL = "https://api.github.com/repos/bbcmicrobit/micropython/releases/latest"


class MicrobitProxy(BareMetalMicroPythonProxy):
    def _get_backend_launcher_path(self) -> str:
        import thonny.plugins.microbit.microbit_back

        return thonny.plugins.microbit.microbit_back.__file__

    def _start_background_process(self, clean=None, extra_args=[]):
        # NB! Sometimes disconnecting and reconnecting (on macOS?)
        # too quickly causes anomalies
        # https://github.com/pyserial/pyserial/issues/176
        # In my Sierra, Calliope and micro:bit seemed to soft-reboot
        # when reconnected too quickly.

        if clean and sys.platform == "darwin":
            sleep(1.0)

        super()._start_background_process(clean)

    def supports_remote_directories(self):
        return False

    @classmethod
    def should_consider_unknown_devices(cls):
        return False

    @classmethod
    def get_known_usb_vids_pids(cls):
        return {(0x0D28, 0x0204)}


class MicrobitConfigPage(BareMetalMicroPythonConfigPage):
    def _get_intro_url(self):
        return "https://microbit-micropython.readthedocs.io/en/latest/devguide/repl.html"

    def _get_intro_text(self):
        return (
            super()._get_intro_text()
            + "\n\n"
            + tr("Make sure MicroPython has been installed to your micro:bit.")
            + "\n("
            + tr("Don't forget that main.py only works without embedded main script.")
            + ")"
        )

    def get_flashing_dialog_kinds(self) -> List[str]:
        return [""]

    def _open_flashing_dialog(self, kind: str) -> None:
        assert kind == ""
        dlg = MicrobitFlashingDialog(self, "MicroPython")
        ui_utils.show_dialog(dlg)


class MicrobitFlashingDialog(Uf2FlashingDialog):
    """
    Technically micro:bit doesn't use UF2, but Uf2FlashingDialog is similar enough to be used
    as baseclass here.
    """

    def get_variants_url(self) -> str:
        return f"https://raw.githubusercontent.com/thonny/thonny/master/data/{self.firmware_name.lower()}-variants-daplink.json"

    def get_families_mapping(self) -> Dict[str, str]:
        return {
            "nRF51": "nrf51",
            "nRF52": "nrf52",
        }

    def get_instructions(self) -> Optional[str]:
        return (
            f"This dialog allows you to install or update {self.firmware_name} on your micro:bit.\n"
            "\n"
            "1. Plug in your micro:bit.\n"
            "2. Wait until device information appears.\n"
            "3. Click 'Install' and wait for some seconds until done.\n"
            "4. Close the dialog and start programming!\n"
            "\n"
            f"NB! Installing {self.firmware_name} will erase all files you may have on your\n"
            "device. Make sure you have important files backed up!"
        )

    def get_info_file_name(self):
        return "DETAILS.TXT"

    def create_target_info(self, path: str) -> Optional[TargetInfo]:
        info_path = os.path.join(path, self.get_info_file_name())

        # https://tech.microbit.org/latest-revision/editors/
        models = {
            "9900": ("BBC micro:bit v1.3", "nrf51"),
            "9901": ("BBC micro:bit v1.5", "nrf51"),
            "9903": ("BBC micro:bit v2.0 (9903)", "nrf52"),
            "9904": ("BBC micro:bit v2.0", "nrf52"),
            "9905": ("BBC micro:bit v2.2 (9905)", "nrf52"),
            "9906": ("BBC micro:bit v2.2 (9906)", "nrf52"),
            "9907": ("BBC micro:bit ??? (9907)", "nrf52"),
            "9908": ("BBC micro:bit ??? (9908)", "nrf52"),
            "9909": ("BBC micro:bit ??? (9909)", "nrf52"),
        }

        with open(info_path, "r", encoding="UTF-8", errors="replace") as fp:
            id_marker = "Unique ID:"
            for line in fp:
                if line.startswith(id_marker):
                    board_id = line[len(id_marker) :].strip()[:4]
                    if board_id in models:
                        model, family = models[board_id]
                        return TargetInfo(
                            title=create_volume_description(path),
                            path=path,
                            family=family,
                            model=model,
                            board_id=board_id,
                            port=None,
                        )

            # With older bootloaders, the file may be different
            fp.seek(0)
            for line in fp:
                if "Version: 0234" in line:
                    board_id = "9900"
                    model, family = models[board_id]
                    return TargetInfo(
                        title=create_volume_description(path),
                        path=path,
                        family=family,
                        model=model,
                        board_id=board_id,
                        port=None,
                    )

        # probably not micro:bit
        return None

    def get_title(self):
        return f"Install or update {self.firmware_name} for BBC micro:bit"

    def perform_post_installation_steps(self, ports_before):
        # can't check the ports as in the superclass, because the port is always there
        # simply wait for a couple of seconds, just in case
        self.append_text("\nWaiting for device to restart...\n")
        self.set_action_text("Waiting for device to restart...")
        time.sleep(5)


def load_plugin():
    add_micropython_backend(
        "microbit",
        MicrobitProxy,
        "MicroPython (BBC micro:bit)",
        MicrobitConfigPage,
        sort_key="31",
        validate_time=False,
        sync_time=False,
        submit_mode=PASTE_SUBMIT_MODE,
        write_block_size=128,
    )

    # Don't consider micro:bit in generic backends
    # The main reason is to reduce the number of items in the backend switcher menu
    import thonny.plugins.circuitpython
    import thonny.plugins.esp
    import thonny.plugins.micropython
    import thonny.plugins.rp2040

    thonny.plugins.circuitpython.cirpy_front.VIDS_PIDS_TO_AVOID.update(
        MicrobitProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.micropython.mp_front.VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND.update(
        MicrobitProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.esp.VIDS_PIDS_TO_AVOID_IN_ESP_BACKENDS.update(
        MicrobitProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.rp2040.VIDS_PIDS_TO_AVOID_IN_RP2040.update(
        MicrobitProxy.get_known_usb_vids_pids()
    )
