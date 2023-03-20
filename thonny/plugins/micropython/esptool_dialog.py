import os.path
import signal
import subprocess
import threading
import time
import tkinter as tk
from logging import getLogger
from tkinter import messagebox, ttk
from typing import Any, Dict, Optional, Tuple

from thonny import get_runner, ui_utils
from thonny.misc_utils import running_on_windows
from thonny.plugins.micropython import BareMetalMicroPythonProxy, list_serial_ports
from thonny.plugins.micropython.base_flashing_dialog import (
    BaseFlashingDialog,
    TargetInfo,
    family_code_to_name,
)
from thonny.running import get_front_interpreter_for_subprocess

logger = getLogger(__name__)


class ESPFlashingDialog(BaseFlashingDialog):
    def __init__(self, master, firmware_name: str, esptool_command):
        self._esptool_command = esptool_command

        super().__init__(master, firmware_name)

    def get_title(self):
        return f"Install {self.firmware_name} (esptool)"

    def get_target_label(self) -> str:
        return "Target port"

    def get_families_mapping(self) -> Dict[str, str]:
        codes = ["esp8266", "esp32", "esp32s2", "esp32s3", "esp32c3"]
        return {family_code_to_name(code): code for code in codes}

    def get_instructions(self) -> Optional[str]:
        return (
            "This dialog allows installing or updating firmware on ESP devices using the most common settings.\n"
            + "If you need to set other options, then please use 'esptool' on the command line.\n\n"
            + "Note that there are many variants of MicroPython for ESP devices. If the firmware provided\n"
            + "at micropython.org/download doesn't work for your device, then there may exist better\n"
            + "alternatives -- look around in your device's documentation or at MicroPython forum."
        )

    def find_targets(self) -> Dict[str, TargetInfo]:
        def port_order(p):
            name = p.device
            if name is None:
                return ""
            elif name.startswith("COM") and len(name) == 4:
                # Make one-digit COM ports go before COM10
                return name.replace("COM", "COM0")
            else:
                return name

        sorted_ports = sorted(list_serial_ports(), key=port_order)

        result = {}
        for p in sorted_ports:
            desc = (
                p.description
                if p.device in p.description
                else p.description + " (" + p.device + ")"
            )
            result[desc] = TargetInfo(
                title=desc, path=None, board_id=None, family=None, model=None, port=p
            )

        return result

    def compute_target_info_text_and_label(self, target: TargetInfo) -> Tuple[str, str]:
        return target.path, "info"

    def _variant_can_be_recommended_for_target(self, variant: Dict[str, Any], target: TargetInfo):
        # TODO: consider certain USB VID/PID-s
        return False

    def get_variants_url(self) -> str:
        return f"https://raw.githubusercontent.com/thonny/thonny/master/data/{self.firmware_name.lower()}-variants-esptool.json"

    def get_action_text_max_length(self):
        return 35

    def prepare_work_get_options(self) -> Dict[str, Any]:
        target = self._target_combo.get_selected_value()
        proxy = get_runner().get_backend_proxy()
        port_was_used_in_thonny = (
            isinstance(proxy, BareMetalMicroPythonProxy) and proxy._port == target.port.device
        )
        if port_was_used_in_thonny:
            proxy.disconnect()

        return {
            "family": self._family_combo.get_selected_value(),
            "flash_mode": "keep",  # TODO:
            "erase_flash": True,  # TODO: self._erase_variable.get(),
            "port_was_used_in_thonny": port_was_used_in_thonny,
        }

    def upload_to_device(
        self,
        source_path: str,
        variant_info: Dict[str, Any],
        download_info: Dict[str, str],
        target_info: TargetInfo,
        work_options: Dict[str, Any],
    ) -> None:
        """Running in a bg thread"""
        assert target_info.port

        if work_options["port_was_used_in_thonny"]:
            time.sleep(1.5)

        erase_command = self._esptool_command + [
            # "--no-stub",
            "--chip",
            work_options["family"],
            "--port",
            target_info.port.device,
            "erase_flash",
        ]

        write_command = self._esptool_command + [
            "--port",
            target_info.port.device,
            "--chip",
            work_options["family"],
            "write_flash",
            "--flash_mode",
            work_options["flash_mode"],
            "--flash_size",  # default changed in esptool 3.0
            "detect",
            self._compute_start_address(work_options["family"]),
            source_path,
        ]

        if not self._check_connection(target_info.port.device):
            self.set_action_text("Problem")
            self.append_text("Could not connect to port\n")
            self.report_done(False)
            return

        if work_options["erase_flash"]:
            self.set_action_text("Erasing flash")
            self.append_text(subprocess.list2cmdline(erase_command) + "\n")
            self._proc = self._create_subprocess(erase_command)
            while True:
                line = self._proc.stdout.readline()
                if not line:
                    break
                self.append_text(line)
                self.set_action_text_smart(line)
            returncode = self._proc.wait()
            if returncode:
                self.set_action_text("Error")
                self.append_text("\nErase command returned with error code %s" % returncode)
                self.report_done(False)
                return
            else:
                self.append_text("Erasing done\n------------------------------------\n\n")

        self.set_action_text("Writing firmware")
        self.append_text(subprocess.list2cmdline(write_command) + "\n")
        self._proc = self._create_subprocess(write_command)
        while True:
            line = self._proc.stdout.readline()
            if not line:
                break
            self.append_text(line)
            self.set_action_text_smart(line)
        returncode = self._proc.wait()
        if returncode:
            self.set_action_text("Error")
            self.append_text("\nWrite command returned with error code %s" % returncode)
        else:
            self.set_action_text("Done!")
            self.append_text("Done!")
        self.report_done(returncode == 0)

    def _compute_start_address(self, family: str) -> str:
        if self.firmware_name == "MicroPython" and family in ["esp32", "esp32-s2", "esp32-s3"]:
            return "0x1000"
        else:
            return "0x0"

    def _old_populate_main_frame(self):
        epadx = self.get_large_padding()
        ipadx = self.get_small_padding()
        epady = epadx
        ipady = ipadx

        # Port
        port_label = ttk.Label(self.main_frame, text="Port")
        port_label.grid(row=1, column=1, sticky="w", padx=(epadx, 0), pady=(epady, 0))

        self._port_desc_variable = tk.StringVar(value="")
        self._port_combo = ttk.Combobox(
            self.main_frame, exportselection=False, textvariable=self._port_desc_variable, values=[]
        )
        self._port_combo.state(["!disabled", "readonly"])
        self._port_combo.grid(row=1, column=2, sticky="nsew", padx=ipadx, pady=(epady, 0))

        port_reload_button = ttk.Button(self.main_frame, text="Reload", command=self._reload_ports)
        port_reload_button.grid(row=1, column=3, sticky="ew", padx=(0, epadx), pady=(epady, 0))

        # Firmware
        firmware_label = ttk.Label(self.main_frame, text="Firmware")
        firmware_label.grid(row=2, column=1, sticky="w", padx=(epadx, 0), pady=(ipady, 0))

        self._firmware_entry = ttk.Entry(self.main_frame, width=50)
        self._firmware_entry.grid(row=2, column=2, sticky="nsew", padx=ipadx, pady=(ipady, 0))

        browse_button = ttk.Button(self.main_frame, text="Browse...", command=self._browse)
        browse_button.grid(row=2, column=3, sticky="we", padx=(0, epadx), pady=(ipady, 0))

        self.main_frame.columnconfigure(2, weight=1)

        # FLASH_MODE
        self._flashmode = tk.StringVar(None, "keep")
        flashmode_group = ttk.Labelframe(self.main_frame, text="Flash mode")
        flashmode_group.grid(
            row=4, column=1, columnspan=2, sticky="w", padx=(epadx, 0), pady=(ipady * 2, 0)
        )

        self._flashmode_keep_radiobutton = ttk.Radiobutton(
            flashmode_group, text="From image file (keep)", variable=self._flashmode, value="keep"
        )
        self._flashmode_keep_radiobutton.grid(row=0, column=0, sticky="w")

        # self._flashmode_variable.value=False
        self._flashmode_qio_radiobutton = ttk.Radiobutton(
            flashmode_group, text="Quad I/O (qio)", variable=self._flashmode, value="qio"
        )
        self._flashmode_qio_radiobutton.grid(row=0, column=1, sticky="w")

        self._flashmode_dio_radiobutton = ttk.Radiobutton(
            flashmode_group, text="Dual I/O (dio)", variable=self._flashmode, value="dio"
        )
        self._flashmode_dio_radiobutton.grid(row=1, column=0, sticky="w")

        self._flashmode_dout_radiobutton = ttk.Radiobutton(
            flashmode_group, text="Dual Output (dout)", variable=self._flashmode, value="dout"
        )
        self._flashmode_dout_radiobutton.grid(row=1, column=1, sticky="w")

        # Erase
        self._erase_variable = tk.BooleanVar(value=True)
        self._erase_checkbutton = ttk.Checkbutton(
            self.main_frame, text="Erase flash before installing", variable=self._erase_variable
        )
        self._erase_checkbutton.grid(
            row=6, column=1, columnspan=2, sticky="w", padx=(epadx, 0), pady=(ipady, epady)
        )

        self._reload_ports()

    def _old_browse(self):
        initialdir = os.path.normpath(os.path.expanduser("~/Downloads"))
        if not os.path.isdir(initialdir):
            initialdir = None

        path = ui_utils.askopenfilename(
            filetypes=[("bin-files", ".bin"), ("all files", ".*")],
            parent=self.winfo_toplevel(),
            initialdir=initialdir,
        )
        if path:
            self._firmware_entry.delete(0, "end")
            self._firmware_entry.insert(0, path)

    def _check_connection(self, port):
        # wait a bit in case existing connection was just closed
        time.sleep(1.5)

        # Maybe another program is connected
        # or the user doesn't have sufficient permissions?
        try:
            import serial

            conn = serial.Serial(port)
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Can't connect", str(e), master=self)
            return False

    def _old_start_work(self):
        port = self._ports_by_desc[self._port_desc_variable.get()]
        if not self._port_desc_variable.get():
            messagebox.showerror("Select port", "Please select port", parent=self)
            return False

        firmware_path = self._firmware_entry.get()
        if not os.path.exists(firmware_path):
            messagebox.showerror(
                "Bad firmware path", "Can't find firmware, please check path", master=self
            )
            return False

        flash_mode = self._flashmode.get()
        erase_flash = self._erase_variable.get()

        proxy = get_runner().get_backend_proxy()
        port_was_used_in_thonny = (
            isinstance(proxy, BareMetalMicroPythonProxy) and proxy._port == port
        )
        if port_was_used_in_thonny:
            proxy.disconnect()

        commands = []
        threading.Thread(
            target=self.work_in_thread,
            daemon=True,
            args=[port, firmware_path, flash_mode, erase_flash, port_was_used_in_thonny],
        ).start()

    def work_in_thread(self, port, firmware_path, flash_mode, erase_flash, port_was_used_in_thonny):
        if port_was_used_in_thonny:
            time.sleep(1.5)

        erase_command = self._esptool_command + [
            "--port",
            port,
            "erase_flash",
        ]

        write_command = self._esptool_command + [
            "--port",
            port,
            "write_flash",
            "--flash_mode",
            flash_mode,
            "--flash_size",  # default changed in esptool 3.0
            "detect",
            self._start_address,
            firmware_path,
        ]

        if not self._check_connection(port):
            self.set_action_text("Problem")
            self.append_text("Could not connect to port\n")
            self.report_done(False)
            return

        if erase_flash:
            self.set_action_text("Erasing flash")
            self.append_text(subprocess.list2cmdline(erase_command) + "\n")
            self._proc = self._create_subprocess(erase_command)
            while True:
                line = self._proc.stdout.readline()
                if not line:
                    break
                self.append_text(line)
                self.set_action_text_smart(line)
            returncode = self._proc.wait()
            if returncode:
                self.set_action_text("Error")
                self.append_text("\nErase command returned with error code %s" % returncode)
                self.report_done(False)
                return
            else:
                self.append_text("Erasing done\n------------------------------------\n\n")

        self.set_action_text("Writing firmware")
        self.append_text(subprocess.list2cmdline(write_command) + "\n")
        self._proc = self._create_subprocess(write_command)
        while True:
            line = self._proc.stdout.readline()
            if not line:
                break
            self.append_text(line)
            self.set_action_text_smart(line)
        returncode = self._proc.wait()
        if returncode:
            self.set_action_text("Error")
            self.append_text("\nWrite command returned with error code %s" % returncode)
        else:
            self.set_action_text("Done!")
            self.append_text("Done!")
        self.report_done(returncode == 0)

    def _create_subprocess(self, cmd) -> subprocess.Popen:
        return subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )

    def cancel_work(self):
        super().cancel_work()
        # try gently first
        try:
            try:
                if running_on_windows():
                    os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # pylint: disable=no-member
                else:
                    os.kill(self._proc.pid, signal.SIGINT)

                self._proc.wait(2)
            except subprocess.TimeoutExpired:
                if self._proc.poll() is None:
                    # now let's be more concrete
                    self._proc.kill()
        except OSError as e:
            messagebox.showerror("Error", "Could not kill subprocess: " + str(e), master=self)
            logger.error("Could not kill subprocess", exc_info=e)


def try_launch_esptool_dialog(master, firmware_name: str):
    try:
        import esptool
    except ImportError:
        messagebox.showerror(
            "Can't find esptool",
            "esptool not found.\n" + "Install it via 'Tools => Manage plug-ins'",
            master=master,
        )
        return

    cmd = [get_front_interpreter_for_subprocess(), "-u", "-m", "esptool"]
    dlg = ESPFlashingDialog(master.winfo_toplevel(), firmware_name, cmd)
    ui_utils.show_dialog(dlg)
