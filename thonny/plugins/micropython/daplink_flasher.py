import os.path
import time
from typing import Dict, Optional

from thonny.plugins.micropython.base_flashing_dialog import TargetInfo
from thonny.plugins.micropython.uf2dialog import Uf2FlashingDialog, create_volume_description


class DaplinkFlashingDialog(Uf2FlashingDialog):
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
            f"This dialog allows you to install or update {self.firmware_name} on your\n"
            f"BBC micro:bit, Calliope mini or another DAPLink-based device.\n"
            "\n"
            "1. Plug in your device.\n"
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

        # https://tech.microbit.org/software/daplink-interface/
        microbit_models = {
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

        calliope_models = {
            "9906": ("Calliope mini 3", "nrf52"),
        }

        with open(info_path, "r", encoding="UTF-8", errors="replace") as fp:
            details_txt = fp.read()

        if "calliope" in details_txt.lower():
            models = calliope_models
        elif "microbit" in details_txt.lower():
            models = microbit_models
        else:
            models = {}

        id_marker = "Unique ID:"
        for line in details_txt.splitlines():
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
        for line in details_txt.splitlines():
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
        return f"Install or update {self.firmware_name} for DAPLink devices"

    def perform_post_installation_steps(self, ports_before):
        # can't check the ports as in the superclass, because the port is always there
        # simply wait for a couple of seconds, just in case
        self.append_text("\nWaiting for device to restart...\n")
        self.set_action_text("Waiting for device to restart...")
        time.sleep(5)
