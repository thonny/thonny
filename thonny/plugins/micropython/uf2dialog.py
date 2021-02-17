import logging
import threading
import os.path
import time
import traceback
import tkinter.font as tkfont
import urllib.request
from tkinter import ttk, messagebox
from typing import Optional
from urllib.request import urlopen

from thonny import get_runner
from thonny.languages import tr
from thonny.misc_utils import list_volumes
from thonny.plugins.micropython import (
    BareMetalMicroPythonProxy,
    list_serial_ports_with_descriptions,
    list_serial_ports,
)
from thonny.ui_utils import (
    set_text_if_different,
    ems_to_pixels,
)
from thonny.workdlg import WorkDialog

logger = logging.getLogger(__name__)

FAKE_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"


class Uf2FlashingDialog(WorkDialog):
    def __init__(self, master):
        self._release_info = None
        self._possible_targets = []
        super().__init__(master)
        self._start_downloading_release_info()

    def populate_main_frame(self):
        pad = self.get_padding()
        inpad = self.get_internal_padding()

        latest_ver_caption = tr("Version to be installed")
        version_caption_label = ttk.Label(self.main_frame, text=latest_ver_caption + ":")
        version_caption_label.grid(
            row=0, column=0, sticky="w", padx=(pad, inpad), pady=(pad, inpad)
        )
        self._version_label = ttk.Label(self.main_frame, text=tr("please wait") + " ...")
        self._version_label.grid(row=0, column=1, padx=(0, pad), pady=(pad, inpad), sticky="w")

        device_location_caption = tr("Target device location")
        self.target_caption_label = ttk.Label(self.main_frame, text=device_location_caption + ":")
        self.target_caption_label.grid(
            row=1, column=0, padx=(pad, inpad), pady=(0, inpad), sticky="w"
        )

        # add width, so that this label prescribes the width of the dialog and it doesn't grow
        # when the progressbar and action text are gridded
        self.target_label = ttk.Label(self.main_frame, text="", width=self.get_info_text_width())
        self.target_label.grid(row=1, column=1, padx=(0, pad), pady=(0, inpad), sticky="w")

        device_model_caption = tr("Target device model")
        self.model_caption_label = ttk.Label(self.main_frame, text=device_model_caption + ":")
        self.model_caption_label.grid(
            row=2, column=0, padx=(pad, inpad), pady=(0, inpad), sticky="w"
        )
        self.model_label = ttk.Label(self.main_frame, text="", width=self.get_info_text_width())
        self.model_label.grid(row=2, column=1, padx=(0, pad), pady=(0, inpad), sticky="w")

        # Resize progress bar to align with this grid
        default_font = tkfont.nametofont("TkDefaultFont")
        max_caption_len = max(
            [
                default_font.measure(caption + ":")
                for caption in [latest_ver_caption, device_location_caption, device_model_caption]
            ]
        )
        self._progress_bar["length"] = max_caption_len

    def get_info_text_width(self):
        return 40

    def get_action_text_max_length(self):
        return 20

    def get_instructions(self) -> Optional[str]:
        return (
            "This dialog allows you to install or update MicroPython on your device.\n"
            "\n"
            "1. Put your device into bootloader mode.\n"
            "2. Wait until device information appears.\n"
            "3. Click 'Install' and wait for some seconds until done.\n"
            "4. Close the dialog and start programming!"
        )

    def get_ok_text(self):
        return tr("Install")

    def _get_release_info_url(self):
        raise NotImplementedError()

    def _start_downloading_release_info(self):
        self._release_info = None  # invalidate last info if downloading again
        threading.Thread(target=self._download_release_info, daemon=True).start()

    def _download_release_info(self):
        import json
        from urllib.request import urlopen

        try:
            req = urllib.request.Request(
                self._get_release_info_url(),
                data=None,
                headers={
                    "User-Agent": FAKE_USER_AGENT,
                    "Cache-Control": "no-cache",
                },
            )
            with urlopen(req) as fp:
                json_str = fp.read().decode("UTF-8")
                logger.debug("Release info: %r", json_str)
                self._release_info = json.loads(json_str)
                if self._release_info.get("message", "") == "Not Found":
                    self._release_info = None
        except Exception as e:
            self.append_text("Could not find release info from %s\n" % self._get_release_info_url())
            self.set_action_text("Error!")
            self.grid_progress_widgets()

    def update_ui(self):
        if self._state == "idle":
            self._possible_targets = self.get_possible_targets()
            if not self._possible_targets:
                set_text_if_different(self.target_label, "")
                set_text_if_different(self.model_label, "")
            else:
                unpacked = list(zip(*self._possible_targets))
                set_text_if_different(self.target_label, "\n".join(unpacked[0]))
                model_changed = set_text_if_different(self.model_label, "\n".join(unpacked[2]))

            desc = self.get_firmware_description()
            if desc is None:
                set_text_if_different(self._version_label, self.get_unknown_version_text())
            else:
                set_text_if_different(self._version_label, desc)

        super(Uf2FlashingDialog, self).update_ui()

    def get_unknown_version_text(self):
        return tr("Please wait") + "..."

    def model_changed(self):
        pass

    def get_firmware_description(self):
        if self._release_info is None:
            return None
        else:
            return (
                self._release_info["tag_name"]
                + " ("
                + self._release_info["published_at"][:10]
                + ")"
            )

    def get_download_url_and_size(self, board_id):
        if self._release_info is None:
            return None

        candidates = [
            asset
            for asset in self._release_info["assets"]
            if self._is_suitable_asset(asset, board_id)
        ]

        logger.info(
            "Assets from %s: %r", self._get_release_info_url(), self._release_info["assets"]
        )
        if len(candidates) == 0:
            raise RuntimeError(
                "Could not find the right file from the release info (%s)"
                % self._get_release_info_url()
            )
        elif len(candidates) > 1:
            raise RuntimeError(
                "Found several possible files from the release info (%s)"
                % self._get_release_info_url()
            )
        else:
            return (candidates[0]["browser_download_url"], candidates[0]["size"])

    def _is_suitable_asset(self, asset, model_id):
        raise NotImplementedError()

    def is_ready_for_work(self):
        # Called after update_ui
        return self._possible_targets and self._release_info

    @classmethod
    def get_possible_targets(cls):
        all_vol_infos = [
            (vol, cls.find_device_board_id_and_model(vol))
            for vol in list_volumes(skip_letters=["A"])
        ]

        return [(info[0], info[1][0], info[1][1]) for info in all_vol_infos if info[1] is not None]

    def start_work(self):
        if len(self._possible_targets) > 1:
            # size 0 is checked elsewhere
            messagebox.showerror(
                "Can't proceed",
                "You seem to have plugged in %d compatible devices.\n"
                + "Please leave only one and unplug the others!",
                parent=self,
            )
            return False

        target_dir, board_id, _ = self._possible_targets[0]

        try:
            download_url, size = self.get_download_url_and_size(board_id)
        except Exception as e:
            logger.error("Could not determine download url", exc_info=e)
            messagebox.showerror("Could not determine download url", str(e), parent=self)
            return False

        self.report_progress(0, size)
        proxy = get_runner().get_backend_proxy()
        if isinstance(proxy, BareMetalMicroPythonProxy):
            proxy.disconnect()

        threading.Thread(
            target=self._perform_work, args=[download_url, size, target_dir], daemon=True
        ).start()
        return True

    @classmethod
    def find_device_board_id_and_model(cls, mount_path):
        info_path = os.path.join(mount_path, "INFO_UF2.TXT")
        if not os.path.isfile(info_path):
            return None

        board_id = None
        model = None
        with open(info_path, "r", encoding="UTF-8", errors="replace") as fp:
            for line in fp:
                parts = list(map(str.strip, line.split(":", maxsplit=1)))
                if len(parts) == 2:
                    if parts[0] == "Model":
                        model = parts[1]
                    elif parts[0] == "Board-ID":
                        board_id = parts[1]
                        if not cls._is_relevant_board_id(board_id):
                            return None

                    if board_id and model:
                        return board_id, model

        return None

    @classmethod
    def _is_relevant_board_id(cls, board_id):
        return True

    def _get_vid_pids_to_wait_for(self):
        """If result is non-empty then the process completes until a device with one of the vid-pid pairs appears"""
        return set()

    def _perform_work(self, download_url, size, target_dir):
        try:
            self._download_to_the_device(download_url, size, target_dir)
            if self._state == "working" and self._get_vid_pids_to_wait_for():
                self._wait_for_vid_pids()
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

    def _wait_for_vid_pids(self):
        target_set = set(self._get_vid_pids_to_wait_for())
        if not target_set:
            return

        self.append_text("\nWaiting for the port...\n")
        self.set_action_text("Waiting for the port...")

        wait_time = 0
        step = 0.2
        while wait_time < 10:
            for p in list_serial_ports():
                vidpid = (p.vid, p.pid)
                if vidpid in target_set or (p.vid, None) in target_set:
                    self.append_text("Found %s at %s\n" % ("%04x:%04x" % vidpid, p.device))
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

    def _download_to_the_device(self, download_url, size, target_dir):
        """Running in a bg thread"""
        target_path = os.path.join(target_dir, self.get_target_filename())
        logger.debug("Downloading %d bytes from %s to %s", size, download_url, target_path)

        self.set_action_text("Starting...")
        self.append_text("Downloading %d bytes from %s\n" % (size, download_url))

        req = urllib.request.Request(
            download_url,
            data=None,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
            },
        )

        with urlopen(req, timeout=5) as fsrc:
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

    def get_target_filename(self):
        return "firmware"

    def get_title(self):
        return "Install MicroPython firmware"
