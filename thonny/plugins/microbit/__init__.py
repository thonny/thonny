import os.path
import sys
import threading
from time import sleep
from tkinter import messagebox, ttk

from thonny import get_workbench, ui_utils
from thonny.languages import tr
from thonny.misc_utils import find_volume_by_name
from thonny.plugins.micropython import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
    add_micropython_backend,
)
from thonny.ui_utils import CommonDialog, FileCopyDialog, ems_to_pixels

LATEST_RELEASE_URL = "https://api.github.com/repos/bbcmicrobit/micropython/releases/latest"


class MicrobitProxy(BareMetalMicroPythonProxy):
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

    @property
    def consider_unknown_devices(self):
        return False

    @property
    def known_usb_vids_pids(self):
        """Copied from https://github.com/mu-editor/mu/blob/master/mu/modes/adafruit.py"""
        return {(0x0D28, 0x0204)}  # Adafruit CRICKit M0


class MicrobitConfigPage(BareMetalMicroPythonConfigPage):
    def _get_usb_driver_url(self):
        return "https://microbit-micropython.readthedocs.io/en/latest/devguide/repl.html"

    def _get_flashing_frame(self):
        frame = super()._get_flashing_frame()
        self._flashing_label.configure(
            text=tr("Make sure MicroPython has been installed to your micro:bit.")
            + "\n("
            + tr("Don't forget that main.py only works without embedded main script.")
            + ")"
        )
        return frame

    def _has_flashing_dialog(self):
        return True

    def _open_flashing_dialog(self):
        mount_path = find_volume_by_name(
            "MICROBIT",
            not_found_msg=tr("Could not find disk '%s'.")
            + "\n"
            + tr("Make sure you have micro:bit plugged in!")
            + "\n\n"
            + tr("Do you want to continue and locate the disk yourself?"),
        )
        if mount_path is None:
            return

        dlg = FlashingDialog(get_workbench(), mount_path)
        ui_utils.show_dialog(dlg)


class FlashingDialog(CommonDialog):
    def __init__(self, master, target_dir):
        self._release_info = None
        self._hex_url = None
        self._hex_size = None
        self._target_dir = target_dir
        self._bytes_copied = 0

        self._state = "starting"

        super().__init__(master)

        main_frame = ttk.Frame(self)  # To get styled background
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        main_frame.columnconfigure(1, weight=1)

        self.title(tr("Install latest MicroPython to BBC micro:bit"))

        target_caption_label = ttk.Label(main_frame, text=tr("micro:bit location:"))
        target_caption_label.grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")
        target_label = ttk.Label(main_frame, text=self._target_dir)
        target_label.grid(row=0, column=1, padx=15, pady=(15, 0), sticky="w", columnspan=2)

        version_caption_label = ttk.Label(main_frame, text=tr("Version to be installed:"))
        version_caption_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))
        self._version_label = ttk.Label(main_frame, text=tr("please wait") + " ...")
        self._version_label.grid(row=1, column=1, columnspan=2, padx=15, pady=(0, 15), sticky="w")

        self._state_label = ttk.Label(
            main_frame, text=tr("NB! All files on micro:bit will be deleted!")
        )
        self._state_label.grid(row=2, column=0, columnspan=3, sticky="w", padx=15, pady=(0, 15))

        self._progress_bar = ttk.Progressbar(main_frame, length=ems_to_pixels(30))
        self._progress_bar.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=15, pady=0)

        self._install_button = ttk.Button(
            main_frame, text=tr("Install"), command=self._start_installing
        )
        self._install_button.grid(row=4, column=0, columnspan=2, sticky="ne", padx=0, pady=15)

        self._close_button = ttk.Button(main_frame, text=tr("Cancel"), command=self._close)
        self._close_button.grid(row=4, column=2, sticky="ne", padx=15, pady=15)
        self._progress_bar.focus_set()

        main_frame.columnconfigure(1, weight=1)

        self.bind("<Escape>", self._close, True)  # escape-close only if process has completed
        self.protocol("WM_DELETE_WINDOW", self._close)

        self._start_downloading_release_info()
        self._update_state()

    def _locate_microbit(self):
        pass

    def _start_downloading_release_info(self):
        import json
        from urllib.request import urlopen

        def work():
            with urlopen(LATEST_RELEASE_URL) as fp:
                self._release_info = json.loads(fp.read().decode("UTF-8"))

        threading.Thread(target=work, daemon=True).start()

    def _process_release_info(self):
        version_str = (
            self._release_info["tag_name"] + " (" + self._release_info["published_at"][:10] + ")"
        )
        self._version_label.configure(text=version_str)
        # self._install_button.configure(text=tr("Install") + " " + version_str)

        candidates = [
            asset
            for asset in self._release_info["assets"]
            if asset["name"].endswith(".hex")
            and "micropython" in asset["name"].lower()
            and 400000 < asset["size"] < 800000
        ]
        if len(candidates) == 0:
            self._close_with_error(
                "Could not find the right hex file from the release info (%s)" % LATEST_RELEASE_URL
            )
        elif len(candidates) > 1:
            self._close_with_error(
                "Found several possible hex files from the release info (%s)" % LATEST_RELEASE_URL
            )
        else:
            self._hex_url = candidates[0]["browser_download_url"]
            self._hex_size = candidates[0]["size"]

    def _close_with_error(self, text):
        messagebox.showerror("Error", text)
        self._close()

    def _update_state(self):
        if self._state in ["closing", "closed"]:
            return

        if self._state == "starting" and self._release_info is not None:
            self._process_release_info()
            self._state = "ready"

        if self._state == "ready":
            self._install_button.state(["!disabled"])
        else:
            self._install_button.state(["disabled"])

        if self._state == "installing":
            self._progress_bar.configure(value=self._bytes_copied)
            self._old_bytes_copied = self._bytes_copied
            self._state_label.configure(text=tr("Installing ..."))

        if self._state == "done":
            self._progress_bar.configure(value=0)
            self._state_label.configure(
                text=tr("Done!") + " " + tr("You can now close this dialog.")
            )
            self._close_button.configure(text=tr("Close"))

        if self._state != "done":
            self.after(200, self._update_state)

    def _start_installing(self):
        from urllib.request import urlopen

        self._progress_bar.configure(maximum=self._hex_size)

        def work():
            self._copy_progess = 0

            target = os.path.join(self._target_dir, "micropython.hex")

            with urlopen(self._hex_url, timeout=5) as fsrc:
                with open(target, "wb") as fdst:
                    while True:
                        buf = fsrc.read(8 * 1024)
                        if not buf:
                            break

                        fdst.write(buf)
                        fdst.flush()
                        os.fsync(fdst)
                        self._bytes_copied += len(buf)

            self._state = "done"

        self._state = "installing"
        threading.Thread(target=work, daemon=True).start()

    def _close(self):
        if self._state == "installing" and not messagebox.askyesno(
            "Really cancel?", "Are you sure you want to cancel?"
        ):
            return

        self._state = "closing"
        self.destroy()
        self._state = "closed"


def load_plugin():
    add_micropython_backend(
        "microbit",
        MicrobitProxy,
        "MicroPython (BBC micro:bit)",
        MicrobitConfigPage,
        sort_key="31",
        validate_time=False,
        sync_time=False,
    )
