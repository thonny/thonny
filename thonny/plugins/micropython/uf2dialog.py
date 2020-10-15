import logging
import threading
import tkinter as tk
import os.path
from tkinter import ttk, messagebox
from typing import Optional
from urllib.request import urlopen

from thonny import get_workbench
from thonny.languages import tr
from thonny.misc_utils import list_volumes
from thonny.ui_utils import (
    create_url_label,
    askopenfilename,
    WorkDialog,
    set_text_if_different,
    ems_to_pixels,
)

logger = logging.getLogger(__name__)


class Uf2FlashingDialog(WorkDialog):
    def __init__(self, master):
        self._release_info = None
        self._target_dirs = []
        super().__init__(master)
        self._start_downloading_release_info()

    def populate_main_frame(self):
        pad = self.get_padding()
        inpad = self.get_internal_padding()

        version_caption_label = ttk.Label(self.main_frame, text=tr("Latest version:"))
        version_caption_label.grid(
            row=0, column=0, sticky="w", padx=(pad, inpad), pady=(pad, inpad)
        )
        self._version_label = ttk.Label(self.main_frame, text=tr("please wait") + " ...")
        self._version_label.grid(row=0, column=1, padx=(0, pad), pady=(pad, inpad), sticky="w")

        self.target_caption_label = ttk.Label(self.main_frame, text=tr("Target location:"))
        self.target_caption_label.grid(
            row=1, column=0, padx=(pad, inpad), pady=(0, inpad), sticky="w"
        )

        # add width, so that this label prescribes the width of the dialog and it doesn't grow
        # when the progressbar and action text are gridded
        self.target_label = ttk.Label(self.main_frame, text="", width=30)
        self.target_label.grid(row=1, column=1, padx=(0, pad), pady=(0, inpad), sticky="w")

    def init_action_frame(self):
        super(Uf2FlashingDialog, self).init_action_frame()
        self._progress_bar["length"] = ems_to_pixels(10)

    def get_action_text_max_length(self):
        return 15

    def get_missing_device_text(self):
        return "< No micro:bit in sight >"

    def get_instructions(self) -> Optional[str]:
        return (
            "NB! Installing new firmware will erase all files you may have on your micro:bit!\n\n"
            "1. Plug in your micro:bit\n"
            "2. Wait until 'Target location' shows your micro:bit location\n"
            "3. Press 'Install'\n"
            "4. Wait until the latest firmware is downloaded and copied onto your device\n"
            "5. Close the dialog and choose 'MicroPython (BBC micro:bit)' as Thonny's back-end"
        )

    def get_ok_text(self):
        return tr("Install")

    def _get_release_info_url(self):
        return "https://api.github.com/repos/bbcmicrobit/micropython/releases/latest"

    def _start_downloading_release_info(self):
        import json
        from urllib.request import urlopen

        def work():
            # TODO: error handling
            with urlopen(self._get_release_info_url()) as fp:
                self._release_info = json.loads(fp.read().decode("UTF-8"))

        threading.Thread(target=work, daemon=True).start()

    def update_ui(self):
        if self._state == "preparing":
            self._target_dirs = self.get_target_dirs()
            if not self._target_dirs:
                set_text_if_different(self.target_label, self.get_missing_device_text())
            else:
                set_text_if_different(self.target_label, "\n".join(self._target_dirs))

            unknown_version_text = tr("Please wait") + "..."
            desc = self.get_firmware_description()
            if desc is None:
                set_text_if_different(self._version_label, unknown_version_text)
            else:
                set_text_if_different(self._version_label, desc)

        super(Uf2FlashingDialog, self).update_ui()

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

    def get_download_url_and_size(self, model_id):
        if self._release_info is None:
            return None

        candidates = [
            asset
            for asset in self._release_info["assets"]
            if self._is_suitable_asset(asset, model_id)
        ]
        if len(candidates) == 0:
            raise RuntimeError(
                "Could not find the right hex file from the release info (%s)"
                % self._get_release_info_url()
            )
        elif len(candidates) > 1:
            raise RuntimeError(
                "Found several possible hex files from the release info (%s)"
                % self._get_release_info_url()
            )
        else:
            return (candidates[0]["browser_download_url"], candidates[0]["size"])

    def _is_suitable_asset(self, asset, model_id):
        return (
            asset["name"].endswith(".hex")
            and "micropython" in asset["name"].lower()
            and 400000 < asset["size"] < 800000
        )

    def is_ready_for_work(self):
        # Called after update_ui
        return self._target_dirs and self._release_info

    def get_target_dirs(self):
        return [
            vol
            for vol in list_volumes(skip_letters=["A"])
            if os.path.exists(os.path.join(vol, "MICROBIT.HTM"))
        ]

    def start_work(self):
        if len(self._target_dirs) > 1:
            # size 0 is checked elsewhere
            messagebox.showerror(
                "Can't proceed",
                "You seem to have plugged in %d compatible devices.\n"
                + "Please leave only one and unplug the others!",
                parent=self,
            )
            return False

        target_dir = self._target_dirs[0]

        try:
            download_url, size = self.get_download_url_and_size(self._find_device_id(target_dir))
        except Exception as e:
            logger.error("Could not determine download url", exc_info=e)
            messagebox.showerror("Could not determine download url", str(e), parent=self)
            return False

        self.report_progress(0, size)
        threading.Thread(
            target=self._download_to_the_device, args=[download_url, size, target_dir]
        ).start()
        return True

    def _find_device_id(self, mount_path):
        info_path = os.path.join(mount_path, "DETAILS.TXT")
        assert os.path.isfile(info_path)

        # https://tech.microbit.org/latest-revision/editors/
        with open(info_path, "r", encoding="UTF-8", errors="replace") as fp:
            id_marker = "Unique ID:"
            for line in fp:
                if line.startswith(id_marker):
                    unique_id = line[len(id_marker) :].strip()
                    return unique_id[:4]

    def _download_to_the_device(self, download_url, size, target_dir):
        """Running in a bg thread"""

        target_path = os.path.join(target_dir, "micropython.hex")

        self.set_action_text("Starting...")
        self.append_text("Downloading %d bytes from %s\n" % (size, download_url))
        with urlopen(download_url, timeout=5) as fsrc:
            bytes_copied = 0
            self.append_text("Writing to %s\n" % target_path)
            self.append_text("Starting...")
            with open(target_path, "wb") as fdst:
                while True:
                    buf = fsrc.read(8 * 1024)
                    if not buf:
                        break

                    fdst.write(buf)
                    fdst.flush()
                    os.fsync(fdst.fileno())
                    bytes_copied += len(buf)
                    percent_str = "%.0f%%" % (bytes_copied / size * 100)
                    self.set_action_text("Copying... " + percent_str)
                    self.report_progress(bytes_copied, size)
                    self.replace_last_line(percent_str)

        self.append_text("\nDone!")
        self.set_action_text("Done!")
        self.report_done(True)

    def get_title(self):
        return "Install MicroPython firmware for BBC micro:bit"

    def _update_device_info(self):
        info_file_name = "INFO_UF2.TXT"
        suitable_volumes = {
            vol
            for vol in list_volumes(skip_letters=["A"])
            if os.path.exists(os.path.join(vol, info_file_name))
        }

        if len(suitable_volumes) == 0:
            self._device_info = None
            device_text = self._get_missing_device_instructions()
        elif len(suitable_volumes) > 1:
            self._device_info = None
            device_text = (
                "Found more than one device:\n  "
                + "\n  ".join(sorted(suitable_volumes))
                + "\n\n"
                + "Please keep only one in bootloader mode!"
            )
        else:
            vol = suitable_volumes.pop()
            model = "Unknown device"
            with open(os.path.join(vol, info_file_name), encoding="utf-8") as fp:
                for line in fp:
                    if line.startswith("Model:"):
                        model = line[len("Model:") :].strip()
                        break

            self._device_info = {"volume": vol, "model": model}
            device_text = "%s at %s is ready" % (model, vol)

        self.device_label.configure(text=device_text)

    def _start_install(self):
        assert os.path.isfile(self._get_file_path())
        assert self._device_info

        dest_path = os.path.join(
            self._device_info["volume"], os.path.basename(self._get_file_path())
        )
        size = os.path.getsize(self._get_file_path())

        def work():
            self._copy_progess = 0

            with open(self._get_file_path(), "rb") as fsrc:
                with open(dest_path, "wb") as fdst:
                    copied = 0
                    while True:
                        buf = fsrc.read(16 * 1024)
                        if not buf:
                            break

                        fdst.write(buf)
                        fdst.flush()
                        os.fsync(fdst)
                        copied += len(buf)

                        self._copy_progess = int(copied / size * 100)

            self._copy_progess = "done"

        threading.Thread(target=work).start()

    def _close(self, event=None):
        self.destroy()


class GitHubUf2FlashingDialog(Uf2FlashingDialog):
    pass
