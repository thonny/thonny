import os.path
import sys
import time
from logging import getLogger
from typing import Any, Dict, List, Optional, Set, Tuple

from thonny.common import UserError
from thonny.misc_utils import get_win_volume_name, list_volumes
from thonny.plugins.micropython.base_flashing_dialog import (
    BaseFlashingDialog,
    TargetInfo,
    family_code_to_name,
)
from thonny.plugins.micropython.mp_front import list_serial_ports

logger = getLogger(__name__)


class Uf2FlashingDialog(BaseFlashingDialog):
    def get_target_label(self) -> str:
        return "Target volume"

    def get_variants_url(self) -> str:
        return f"https://raw.githubusercontent.com/thonny/thonny/master/data/{self.firmware_name.lower()}-variants-uf2.json"

    def get_families_mapping(self) -> Dict[str, str]:
        codes = ["rp2", "samd21", "samd51", "esp32s2", "esp32s3", "nrf52"]
        return {family_code_to_name(code): code for code in codes}

    def find_targets(self) -> Dict[str, TargetInfo]:
        paths = [
            vol
            for vol in list_volumes(skip_letters=["A"])
            if os.path.isfile(os.path.join(vol, self.get_info_file_name()))
        ]

        result = {}
        for path in paths:
            try:
                target_info = self.create_target_info(path)
                if target_info:
                    result[target_info.title] = target_info
            except Exception:
                # the disk may have been ejected during read or smth like this
                logger.exception("Could not create target info")

        return result

    def compute_target_info_text_and_label(self, target: TargetInfo) -> Tuple[str, str]:
        if target.model:
            if target.model == "Raspberry Pi RP2":
                # too general to be called model
                return "RP2", "family"
            else:
                text = target.model
                if target.family:
                    text += f"   ({family_code_to_name(target.family)})"
                return text, "model"
        elif target.board_id:
            text = target.board_id
            if target.family:
                text += f"   ({family_code_to_name(target.family)})"
            return text, "board id"
        elif target.family:
            return target.family, "family"
        else:
            return "Unknown board", "info"

    def _variant_can_be_recommended_for_target(self, variant: Dict[str, Any], target: TargetInfo):
        if target.family is None:
            # Don't assume anything about unknown targets
            return False

        if not variant["family"].startswith(target.family):
            return False

        if target.model is None:
            return False

        # Compare set of words both with and without considering the possibility that one of them
        # may have vendor name added and other not.
        return _extract_normalized_words(target.model) == _extract_normalized_words(
            variant["model"]
        ) or _extract_normalized_words(
            target.model + " " + variant["vendor"]
        ) == _extract_normalized_words(
            variant["model"] + " " + variant["vendor"]
        )

    def create_target_info(self, path: str) -> Optional[TargetInfo]:
        info_path = os.path.join(path, self.get_info_file_name())
        assert os.path.isfile(info_path)
        with open(info_path, encoding="utf-8") as fp:
            info_content = fp.read()
        info_lines = info_content.splitlines()
        normalized_content = info_content.lower().replace(" ", "").replace("_", "").replace("-", "")

        model = find_uf2_property(info_lines, "Model")
        board_id = find_uf2_property(info_lines, "Board-ID")

        if "boardid:rpirp2" in normalized_content:
            family = "rp2"
        else:
            for keyword in ["samd21", "samd51", "nrf51", "nrf52", "esp32s3", "esp32s3"]:
                if keyword in normalized_content:
                    family = keyword
                    break
            else:
                family = None

        return TargetInfo(
            title=create_volume_description(path),
            path=path,
            family=family,
            model=model,
            board_id=board_id,
            port=None,
        )

    def get_info_file_name(self):
        return "INFO_UF2.TXT"

    def get_instructions(self) -> Optional[str]:
        return (
            f"Here you can install or update {self.firmware_name} for devices having an UF2 bootloader\n"
            "(this includes most boards meant for beginners).\n"
            "\n"
            "1. Put your device into bootloader mode: \n"
            "     - some devices have to be plugged in while holding the BOOTSEL button,\n"
            "     - some require double-tapping the RESET button with proper rythm.\n"
            "2. Wait for couple of seconds until the target volume appears.\n"
            "3. Select desired variant and version.\n"
            "4. Click 'Install' and wait for some seconds until done.\n"
            "5. Close the dialog and start programming!"
        )

    def get_title(self):
        return f"Install or update {self.firmware_name} (UF2)"

    def perform_core_operation(
        self,
        source_path: Optional[str],
        variant_info: Optional[Dict[str, Any]],
        download_info: Optional[Dict[str, str]],
        target_info: Optional[TargetInfo],
        work_options: Dict[str, Any],
    ) -> bool:
        assert source_path
        assert variant_info
        assert download_info
        assert target_info

        """Running in a bg thread"""
        size = os.path.getsize(source_path)
        target_path = os.path.join(target_info.path, os.path.basename(source_path))

        logger.debug("Copying from %s to %s", source_path, target_path)

        self.set_action_text("Starting...")
        self.append_text("Copying to %s\n" % target_path)

        ports_before = list_serial_ports_with_hw_info()
        logger.debug("Ports before: %s", ports_before)

        with open(source_path, "rb") as fsrc:
            bytes_copied = 0
            self.append_text("Writing to %s\n" % target_path)
            self.append_text("Starting...")

            block_size = 8 * 1024
            with open(target_path, "wb") as fdst:
                while True:
                    block = fsrc.read(block_size)
                    if not block:
                        break

                    if self._state == "cancelling":
                        raise UserError("Cancelling copying per user request")

                    fdst.write(block)
                    bytes_copied += len(block)
                    fdst.flush()
                    try:
                        # May fail after last block
                        os.fsync(fdst.fileno())
                    except Exception:
                        if bytes_copied == size:
                            logger.warning("Could not fsync last block")
                        else:
                            logger.exception("Could not fsync")
                    percent_copied = bytes_copied / size * 100
                    percent_str = "%.0f%%" % (percent_copied)
                    self.set_action_text("Copying... " + percent_str)
                    # use the right half of the progress bar for copying
                    self.report_progress(percent_copied + 100, 200)
                    self.replace_last_line(percent_str)

        if self._state == "working":
            self.perform_post_installation_steps(ports_before)

        return True

    def _wait_for_new_ports(self, old_ports):
        self.append_text("\nWaiting for the port...\n")
        self.set_action_text("Waiting for the port...")

        wait_time = 0
        step = 0.2
        while wait_time < 10:
            new_ports = list_serial_ports_with_hw_info()
            added_ports = set(new_ports) - set(old_ports)
            if added_ports:
                for p in added_ports:
                    self.append_text("Found port %s\n" % p)
                    self.set_action_text("Found port")
                return
            if self._state == "cancelling":
                return
            time.sleep(step)
            wait_time += step
        else:
            logger.debug("Ports after: %s", list_serial_ports_with_hw_info())
            self.set_action_text("Warning: Could not find port")
            self.append_text("Warning: Could not find port in %s seconds\n" % int(wait_time))
            # leave some time to see the warning
            time.sleep(2)

    def perform_post_installation_steps(self, ports_before):
        self._wait_for_new_ports(ports_before)


def find_uf2_property(lines: List[str], prop_name: str) -> Optional[str]:
    marker = prop_name + ": "
    for line in lines:
        if line.startswith(marker):
            return line[len(marker) :]

    return None


def show_uf2_installer(master, firmware_name: str) -> None:
    dlg = Uf2FlashingDialog(master, firmware_name=firmware_name)
    from thonny import ui_utils

    ui_utils.show_dialog(dlg)


def uf2_device_is_present_in_bootloader_mode() -> bool:
    for vol in list_volumes(skip_letters=["A"]):
        info_path = os.path.join(vol, "INFO_UF2.TXT")
        if os.path.isfile(info_path):
            return True

    return False


def _extract_normalized_words(text: str) -> Set[str]:
    return set(text.replace("_", " ").replace("-", "").lower().split())


def create_volume_description(path: str) -> str:
    if sys.platform == "win32":
        try:
            label = get_win_volume_name(path)
            disk = path.strip("\\")
            return f"{label} ({disk})"
        except Exception:
            logger.error("Could not query volume name for %r", path)
            return path
    else:
        return path


def list_serial_ports_with_hw_info():
    return [f"{p.device} ({p.hwid})" for p in list_serial_ports(max_cache_age=0)]
