import threading
import tkinter as tk
import os.path
from tkinter import ttk, messagebox
from typing import Optional

from thonny import get_workbench
from thonny.misc_utils import list_volumes
from thonny.ui_utils import create_url_label, askopenfilename


class Uf2FlashingDialog(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)

        self._copy_progess = None
        self._device_info = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, ipadx=15, ipady=15)

        self.title(self._get_title())
        # self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self._close)

        ttk.Label(main_frame, text="Download .uf2 file:").grid(
            row=1, column=0, sticky="nw", pady=(15, 0), padx=15
        )
        url_label = create_url_label(main_frame, url="https://circuitpython.org/downloads")
        url_label.grid(row=1, column=1, columnspan=2, sticky="nw", pady=(15, 0), padx=15)

        ttk.Label(main_frame, text="Select the file:").grid(
            row=2, column=0, sticky="nw", pady=(10, 0), padx=15
        )
        self._path_var = tk.StringVar(value="")
        self._path_entry = ttk.Entry(main_frame, textvariable=self._path_var, width=60)
        self._path_entry.grid(
            row=2, column=1, columnspan=1, sticky="nsew", pady=(10, 0), padx=(15, 10)
        )
        file_button = ttk.Button(main_frame, text=" ... ", command=self._select_file)
        file_button.grid(row=2, column=2, sticky="nsew", pady=(10, 0), padx=(0, 15))

        ttk.Label(main_frame, text="Prepare device:").grid(
            row=3, column=0, sticky="nw", pady=(10, 0), padx=15
        )
        self.device_label = ttk.Label(main_frame, text="<not found>")
        self.device_label.grid(row=3, column=1, columnspan=2, sticky="nw", pady=(10, 0), padx=15)

        main_frame.rowconfigure(3, weight=1)
        main_frame.columnconfigure(1, weight=1)

        command_bar = ttk.Frame(main_frame)
        command_bar.grid(row=4, column=0, columnspan=3, sticky="nsew")
        command_bar.columnconfigure(0, weight=1)

        self._install_button = ttk.Button(
            command_bar, text="Install", command=self._start_install, width=20
        )
        self._install_button.grid(row=0, column=1, pady=15, padx=15, sticky="ne")
        self._install_button.focus_set()

        close_button = ttk.Button(command_bar, text="Cancel", command=self._close)
        close_button.grid(row=0, column=2, pady=15, padx=(0, 15), sticky="ne")

        self.bind("<Escape>", self._close, True)

        self._update_state()

    def _get_title(self):
        return "Install firmware"

    def _check_find_device_type(self, mount_path: str) -> Optional[str]:
        """If this mount path is possible target, then return device type. Otherwise return None"""
        raise NotImplementedError()

    def _get_missing_device_instructions(self):
        return "Can't find your device. Please plug it in it in bootloader mode!"

    def _select_file(self):
        result = askopenfilename(
            filetypes=[("UF2 files", ".uf2")],
            initialdir=get_workbench().get_option("run.working_directory"),
            parent=self.winfo_toplevel(),
        )

        if result:
            self._path_var.set(os.path.normpath(result))

    def _update_state(self):
        self._update_device_info()

        if isinstance(self._copy_progess, int):
            self._install_button.configure(text="Installing (%d %%)" % self._copy_progess)
        elif self._copy_progess == "done":
            self._install_button.configure(text="Installing (100%)")
            self.update_idletasks()
            messagebox.showinfo(
                "Done",
                "Firmware installation is complete.\nDevice will be back in normal mode.",
                master=self,
            )
            self._copy_progess = None
            self._close()
            return
        else:
            self._install_button.configure(text="Install")

        if (
            os.path.isfile(self._get_file_path())
            and self._copy_progess is None
            and self._device_info
        ):
            self._install_button.state(["!disabled"])
        else:
            self._install_button.state(["disabled"])

        self.after(200, self._update_state)

    def _get_file_path(self):
        return self._path_var.get()

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
