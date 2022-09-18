import os.path
import re
import sys
import threading
import time
import traceback
import urllib.request
from dataclasses import dataclass
from logging import getLogger
from tkinter import ttk
from typing import Any, Dict, List, Optional, Set

from thonny import get_runner
from thonny.languages import tr
from thonny.misc_utils import get_win_volume_name, list_volumes
from thonny.ui_utils import AdvancedLabel, MappingCombobox, set_text_if_different
from thonny.workdlg import WorkDialog

logger = getLogger(__name__)

FAKE_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"


@dataclass()
class TargetInfo:
    title: str
    path: str
    family: Optional[str]
    model: Optional[str]
    board_id: Optional[str]


class Uf2FlashingDialog(WorkDialog):
    def __init__(self, master, firmware_name: str):
        self._downloaded_variants: List[Dict[str, Any]] = []

        self._last_handled_target = None
        self._last_handled_variant = None
        self.firmware_name = firmware_name

        threading.Thread(target=self._download_variants, daemon=True).start()

        super().__init__(master, autostart=False)

    def get_variants_url(self) -> str:
        return f"https://raw.githubusercontent.com/thonny/thonny/master/data/{self.firmware_name.lower()}-variants-uf2.json"

    def populate_main_frame(self):
        epadx = self.get_large_padding()
        ipadx = self.get_small_padding()
        epady = epadx
        ipady = ipadx

        target_label = ttk.Label(self.main_frame, text="Target volume")
        target_label.grid(row=1, column=1, sticky="e", padx=(epadx, 0), pady=(epady, 0))
        self._target_combo = MappingCombobox(self.main_frame, exportselection=False)
        self._target_combo.grid(
            row=1, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(epady, 0)
        )

        self._target_info_label = ttk.Label(self.main_frame, text="model")
        self._target_info_label.grid(row=2, column=1, sticky="e", padx=(epadx, 0), pady=(ipady, 0))
        self._target_info_content_label = ttk.Label(self.main_frame)
        self._target_info_content_label.grid(
            row=2, column=2, sticky="w", padx=(ipadx, epadx), pady=(ipady, 0)
        )

        variant_label = ttk.Label(self.main_frame, text=f"{self.firmware_name} variant")
        variant_label.grid(row=5, column=1, sticky="e", padx=(epadx, 0), pady=(epady, 0))
        self._variant_combo = MappingCombobox(self.main_frame, exportselection=False)
        self._variant_combo.grid(
            row=5, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(epady, 0)
        )

        version_label = ttk.Label(self.main_frame, text="version")
        version_label.grid(row=6, column=1, sticky="e", padx=(epadx, 0), pady=(ipady, 0))
        self._version_combo = MappingCombobox(self.main_frame, exportselection=False)
        self._version_combo.grid(
            row=6, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(ipady, 0)
        )

        variant_info_label = ttk.Label(self.main_frame, text="info")
        variant_info_label.grid(row=7, column=1, sticky="e", padx=(epadx, 0), pady=(ipady, 0))
        self._variant_info_content_label = AdvancedLabel(self.main_frame)
        self._variant_info_content_label.grid(
            row=7, column=2, sticky="w", padx=(ipadx, epadx), pady=(ipady, 0)
        )

        self.main_frame.columnconfigure(2, weight=1)

    def update_ui(self):
        if self._state == "idle":
            targets = self.find_targets()
            if targets != self._target_combo.mapping:
                self.show_new_targets(targets)
                self._last_handled_target = None

            current_target = self._target_combo.get_selected_value()
            if not current_target:
                self._variant_combo.set_mapping({})
                self._variant_combo.select_none()
            elif current_target != self._last_handled_target and self._downloaded_variants:
                self._present_variants_for_target(current_target)
                self._last_handled_target = current_target
                self._last_handled_variant = None
            self._update_target_info()

            current_variant = self._variant_combo.get_selected_value()
            if not current_variant:
                self._version_combo.select_none()
                self._version_combo.set_mapping({})
            elif current_variant != self._last_handled_variant:
                self._present_versions_for_variant(current_variant)
                self._last_handled_variant = current_variant
            self._update_variant_info()

        super().update_ui()

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
            except:
                # the disk may have been ejected during read or smth like this
                logger.exception("Could not create target info")

        return result

    def show_new_targets(self, targets: Dict[str, TargetInfo]) -> None:
        self._target_combo.set_mapping(targets)
        if len(targets) == 1:
            self._target_combo.select_value(list(targets.values())[0])
        else:
            self._target_combo.select_none()

    def _update_target_info(self):
        current_target = self._target_combo.get_selected_value()
        if current_target is not None:
            if current_target.model:
                if current_target.model == "Raspberry Pi RP2":
                    # too general to be called model
                    text = "RP2"
                    label = "family"
                else:
                    text = current_target.model
                    label = "model"
            elif current_target.board_id:
                text = current_target.board_id
                label = "board id"
            elif current_target.family:
                text = current_target.family
                label = "family"
            else:
                text = "Unknown board"
                label = "info"

        elif not self._target_combo.mapping:
            text = "[no suitable targets detected]"
            label = ""
        else:
            text = f"[found {len(self._target_combo.mapping)} targets, please select one]"
            label = ""

        set_text_if_different(self._target_info_content_label, text)
        set_text_if_different(self._target_info_label, label)

    def _update_variant_info(self):
        current_variant = self._variant_combo.get_selected_value()
        if not self._downloaded_variants:
            url = None
            text = "[downloading variants info ...]"
        elif current_variant:
            url = current_variant["info_url"]
            text = url
        elif self._variant_combo.mapping:
            url = None
            text = f"[select one from {len(self._variant_combo.mapping)} variants]"
        else:
            url = None
            text = ""

        set_text_if_different(self._variant_info_content_label, text)
        self._variant_info_content_label.set_url(url)

    def _present_variants_for_target(self, target: TargetInfo) -> None:
        assert self._downloaded_variants

        whole_mapping = {self._create_variant_description(v): v for v in self._downloaded_variants}

        if target.family is not None:
            filtered_mapping = {
                item[0]: item[1]
                for item in whole_mapping.items()
                if item[1]["family"].startswith(target.family)
            }
            if not filtered_mapping:
                filtered_mapping = whole_mapping
        else:
            filtered_mapping = whole_mapping

        prev_variant = self._variant_combo.get_selected_value()

        populars = {
            key: variant
            for key, variant in filtered_mapping.items()
            if variant.get("popular", False)
        }
        if populars and len(populars) < len(filtered_mapping):
            enhanced_mapping = {"--- MOST POPULAR " + "-" * 100: {}}
            for variant in populars.values():
                popular_variant = variant.copy()
                # need different title to distinguish it from the same item in ALL VARIANTS
                popular_title = self._create_variant_description(variant) + " "
                popular_variant["title"] = popular_title
                enhanced_mapping[popular_title] = popular_variant

            enhanced_mapping["--- ALL VARIANTS " + "-" * 100] = {}
            enhanced_mapping.update(filtered_mapping)
        else:
            enhanced_mapping = filtered_mapping

        self._variant_combo.set_mapping(enhanced_mapping)
        matches = list(
            filter(
                lambda v: self._variant_is_meant_for_target(v, target), filtered_mapping.values()
            )
        )

        if len(matches) == 1:
            self._variant_combo.select_value(matches[0])
        elif prev_variant and prev_variant in filtered_mapping.values():
            self._variant_combo.select_value(prev_variant)

    def _present_versions_for_variant(self, variant: Dict[str, Any]) -> None:
        versions_mapping = {d["version"]: d for d in variant["downloads"]}
        self._version_combo.set_mapping(versions_mapping)
        if len(versions_mapping) > 0:
            self._version_combo.select_value(list(versions_mapping.values())[0])
        else:
            self._version_combo.select_none()

    def _create_variant_description(self, variant: Dict[str, Any]) -> str:
        return variant["vendor"] + " • " + variant.get("title", variant["model"])

    def _variant_is_meant_for_target(self, variant: Dict[str, Any], target: TargetInfo):
        if target.family is None:
            # Don't assume anything about unknown targets
            return False

        if not variant["family"].startswith(target.family):
            return False

        if target.model is None:
            return False

        # Compare set of words both with and without considering the possibility that one of them
        # may have vendor name added and other not.
        return self._extract_normalized_words(target.model) == self._extract_normalized_words(
            variant["model"]
        ) or self._extract_normalized_words(
            target.model + " " + variant["vendor"]
        ) == self._extract_normalized_words(
            variant["model"] + " " + variant["vendor"]
        )

    def _extract_normalized_words(self, text: str) -> Set[str]:
        return set(text.replace("_", " ").replace("-", "").lower().split())

    def describe_target_path(self, path: str) -> str:
        if sys.platform == "win32":
            try:
                label = get_win_volume_name(path)
                disk = path.strip("\\")
                return f"{label} ({disk})"
            except:
                logger.error("Could not query volume name for %r", path)
                return path
        else:
            return path

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
            title=self.describe_target_path(path),
            path=path,
            family=family,
            model=model,
            board_id=board_id,
        )

    def get_info_file_name(self):
        return "INFO_UF2.TXT"

    def _download_variants(self):
        logger.info("Downloading %r", self.get_variants_url())
        import json
        from urllib.request import urlopen

        try:
            req = urllib.request.Request(
                self.get_variants_url(),
                data=None,
                headers={
                    "User-Agent": FAKE_USER_AGENT,
                    "Cache-Control": "no-cache",
                },
            )
            with urlopen(req) as fp:
                json_str = fp.read().decode("UTF-8")
                # logger.debug("Variants info: %r", json_str)
            variants = json.loads(json_str)
            logger.info("Got %r variants", len(variants))
            self._tweak_variants(variants)
        except Exception:
            msg = f"Could not download variants info from {self.get_variants_url()}"
            logger.exception(msg)
            self.append_text(msg + "\n")
            self.set_action_text("Error!")
            self.grid_progress_widgets()
            return

        self._downloaded_variants = variants

    def _tweak_variants(self, variants):
        """
        A hack for getting the latest pre-release for micropython.org downloads.
        The build that is loaded from the json may already be deleted.
        In order to avoid adding another async operation into the process (after selecting
        a variant and before presenting versions), I'm getting the latest build substring
        from the download page of the first board and downloading it together with the json.
        """
        latest_prerelease_substitute = None
        latest_prerelease_regex: str
        for variant in variants:
            new_regex = variant.get("latest_prerelease_regex", None)
            if new_regex:
                latest_prerelease_regex = new_regex
                import json
                import urllib.request

                logger.info("Downloading %r", variant["info_url"])
                try:
                    req = urllib.request.Request(
                        variant["info_url"],
                        data=None,
                        headers={
                            "User-Agent": FAKE_USER_AGENT,
                            "Cache-Control": "no-cache",
                        },
                    )
                    with urllib.request.urlopen(req) as fp:
                        html_str = fp.read().decode("UTF-8", errors="replace")
                        # logger.debug("Variants info: %r", json_str)

                    match = re.search(latest_prerelease_regex, html_str)
                    if match:
                        latest_prerelease_substitute = match.group(0)
                        logger.info(
                            "Using %r as prerelease substitute", latest_prerelease_substitute
                        )
                    else:
                        latest_prerelease_substitute = None
                except Exception:
                    msg = f"Could not download variants info from {self.get_variants_url()}"
                    logger.exception(msg)
                    self.append_text(msg + "\n")
                    self.set_action_text("Error!")
                    self.grid_progress_widgets()

            if latest_prerelease_substitute:
                assert latest_prerelease_regex
                for i, download in enumerate(variant["downloads"]):
                    patched_url = re.sub(
                        latest_prerelease_regex, latest_prerelease_substitute, download["url"]
                    )
                    if patched_url != download["url"]:
                        logger.debug("Replacing %r with %r", download["url"], patched_url)
                        download["url"] = patched_url
                        download["version"] = latest_prerelease_substitute

    def get_ok_text(self):
        return tr("Install")

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

    def _on_variant_select(self, *args):
        pass

    def get_title(self):
        return f"Install {self.firmware_name}"

    def is_ready_for_work(self):
        return self._target_combo.get_selected_value() and self._version_combo.get_selected_value()

    def start_work(self):
        from thonny.plugins.micropython import BareMetalMicroPythonProxy

        download_info: Dict[str, Any] = self._version_combo.get_selected_value()
        assert download_info
        target: TargetInfo = self._target_combo.get_selected_value()
        assert target

        target_filename = download_info.get("filename", download_info["url"].split("/")[-1])

        self.report_progress(0, 100)
        proxy = get_runner().get_backend_proxy()
        if isinstance(proxy, BareMetalMicroPythonProxy):
            proxy.disconnect()

        threading.Thread(
            target=self._perform_work,
            args=[
                download_info["url"],
                download_info.get("size", None),
                target.path,
                target_filename,
            ],
            daemon=True,
        ).start()
        return True

    def _perform_work(
        self, download_url: str, size: Optional[int], target_dir: str, target_filename: str
    ) -> None:
        from thonny.plugins.micropython import list_serial_ports

        try:
            ports_before = list_serial_ports()
            self._download_to_the_device(download_url, size, target_dir, target_filename)
            if self._state == "working":
                self.perform_post_installation_steps(ports_before)
        except Exception as e:
            self.append_text("\n" + "".join(traceback.format_exc()))
            self.set_action_text("Error...")
            self.report_done(False)
            return

        if self._state == "working":
            self.append_text("\nDone!\n")
            self.set_action_text("Done!")
            self.report_done(True)
        else:
            assert self._state == "cancelling"
            self.append_text("\nCancelled\n")
            self.set_action_text("Cancelled")
            self.report_done(False)

    def _download_to_the_device(
        self, download_url: str, size: Optional[int], target_dir: str, target_filename: str
    ):
        from urllib.request import urlopen

        """Running in a bg thread"""
        target_path = os.path.join(target_dir, target_filename)
        logger.debug("Downloading from %s to %s", download_url, target_path)

        self.set_action_text("Starting...")
        self.append_text("Downloading from %s\n" % download_url)

        req = urllib.request.Request(
            download_url,
            data=None,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
            },
        )

        with urlopen(req, timeout=5) as fsrc:
            if size is None:
                size = int(fsrc.getheader("Content-Length", str(500 * 1024)))

            bytes_copied = 0
            self.append_text("Writing to %s\n" % target_path)
            self.append_text("Starting...")
            if fsrc.length:
                # override (possibly inaccurate) size
                size = fsrc.length

            block_size = 8 * 1024
            with open(target_path, "wb") as fdst:
                while True:

                    block = fsrc.read(block_size)
                    if not block:
                        break

                    if self._state == "cancelling":
                        break

                    fdst.write(block)
                    fdst.flush()
                    os.fsync(fdst.fileno())
                    bytes_copied += len(block)
                    percent_str = "%.0f%%" % (bytes_copied / size * 100)
                    self.set_action_text("Copying... " + percent_str)
                    self.report_progress(bytes_copied, size)
                    self.replace_last_line(percent_str)

    def _wait_for_new_ports(self, old_ports):
        from thonny.plugins.micropython import list_serial_ports

        self.append_text("\nWaiting for the port...\n")
        self.set_action_text("Waiting for the port...")

        wait_time = 0
        step = 0.2
        while wait_time < 10:
            new_ports = list_serial_ports()
            added_ports = set(new_ports) - set(old_ports)
            if added_ports:
                for p in added_ports:
                    self.append_text("Found %s at %s\n" % ("%04x:%04x" % (p.vid, p.pid), p.device))
                    self.set_action_text("Found port")
                return
            if self._state == "cancelling":
                return
            time.sleep(step)
            wait_time += step
        else:
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
