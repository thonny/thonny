import logging
import threading
import os.path
import traceback
from tkinter import ttk, messagebox
from typing import Optional
from urllib.request import urlopen

from thonny import get_runner
from thonny.languages import tr
from thonny.plugins.micropython import BareMetalMicroPythonProxy
from thonny.ui_utils import (
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
        return "Can't see your device ..."

    def get_instructions(self) -> Optional[str]:
        return (
            "NB! Installing new firmware will erase all files you may have on your device!\n\n"
            "1. Plug in your device in the bootloader mode\n"
            "2. Wait until 'Target location' shows your the location of your device\n"
            "3. Press 'Install'\n"
            "4. Wait until the latest firmware is downloaded and copied onto your device\n"
            "5. Close the dialog and choose suitable 'MicroPython (...)' interpreter"
        )

    def get_ok_text(self):
        return tr("Install")

    def _get_release_info_url(self):
        raise NotImplementedError()

    def _start_downloading_release_info(self):
        import json
        from urllib.request import urlopen

        def work():
            # TODO: error handling
            with urlopen(self._get_release_info_url()) as fp:
                self._release_info = json.loads(fp.read().decode("UTF-8"))

        threading.Thread(target=work, daemon=True).start()

    def update_ui(self):
        if self._state == "idle":
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
        raise NotImplementedError()

    def is_ready_for_work(self):
        # Called after update_ui
        return self._target_dirs and self._release_info

    def get_target_dirs(self):
        raise NotImplementedError()

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
        proxy = get_runner().get_backend_proxy()
        if isinstance(proxy, BareMetalMicroPythonProxy):
            proxy.disconnect()

        threading.Thread(
            target=self._download_to_the_device, args=[download_url, size, target_dir]
        ).start()
        return True

    def _find_device_id(self, mount_path):
        raise NotImplementedError()

    def _download_to_the_device(self, download_url, size, target_dir):
        """Running in a bg thread"""
        try:
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

                        if self._state == "cancelling":
                            break

                        fdst.write(buf)
                        fdst.flush()
                        os.fsync(fdst.fileno())
                        bytes_copied += len(buf)
                        percent_str = "%.0f%%" % (bytes_copied / size * 100)
                        self.set_action_text("Copying... " + percent_str)
                        self.report_progress(bytes_copied, size)
                        self.replace_last_line(percent_str)
        except Exception as e:
            self.append_text("\n" + "".join(traceback.format_stack()))
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

    def get_title(self):
        return "Install MicroPython firmware"
