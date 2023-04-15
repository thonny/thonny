import io
import os.path
import signal
import subprocess
import threading
import time
import tkinter as tk
from logging import getLogger
from tkinter import messagebox, ttk
from typing import Any, Dict, Optional, Tuple

from thonny import get_runner, get_workbench, ui_utils
from thonny.common import normpath_with_actual_case
from thonny.misc_utils import running_on_windows
from thonny.plugins.micropython import BareMetalMicroPythonProxy, list_serial_ports
from thonny.plugins.micropython.base_flashing_dialog import (
    BaseFlashingDialog,
    TargetInfo,
    family_code_to_name,
)
from thonny.plugins.micropython.mp_front import get_serial_port_label
from thonny.running import get_front_interpreter_for_subprocess
from thonny.ui_utils import EnhancedBooleanVar, MappingCombobox

logger = getLogger(__name__)

LOCAL_VARIANT_TITLE = "<local file>"


class ESPFlashingDialog(BaseFlashingDialog):
    def __init__(self, master, firmware_name: str, esptool_command):
        self._esptool_command = esptool_command
        self._advanced_widgets = []
        self._work_mode = None
        self._proc = None

        super().__init__(master, firmware_name)

        if not get_workbench().get_option("esptool.show_advanced_options"):
            self._hide_advanced_options()

    def get_title(self):
        return f"Install {self.firmware_name} (esptool)"

    def get_target_label(self) -> str:
        return "Target port"

    def get_families_mapping(self) -> Dict[str, str]:
        codes = ["esp32", "esp32s2", "esp32s3", "esp32c3"]
        if self.firmware_name == "MicroPython":
            codes.insert(0, "esp8266")

        return {family_code_to_name(code): code for code in codes}

    def get_instructions(self) -> Optional[str]:
        return (
            "Click the ☰ button to see all features and options. If you're stuck then check the variant's\n"
            f"'info' page for details or ask in {self.firmware_name} forum.\n\n"
            "NB! Some boards need to be put into a special mode before they can be managed here\n"
            "(e.g. by holding the BOOT button while plugging in). Some require hard reset after installing."
        )

    def populate_main_frame(self):
        super().populate_main_frame()
        self._target_info_label.grid_forget()
        self._target_info_content_label.grid_forget()

        epadx = self.get_large_padding()
        ipadx = self.get_small_padding()
        epady = epadx
        ipady = ipadx

        self._erase_variable = EnhancedBooleanVar(
            value=True, modification_listener=self.register_settings_changed
        )
        self._erase_checkbutton = ttk.Checkbutton(
            self.main_frame,
            text="Erase flash before installing",
            variable=self._erase_variable,
        )
        self._erase_checkbutton.grid(row=3, column=2, sticky="w", padx=(ipadx, 0), pady=(ipady, 0))

        x0_target_description = (
            "for CircuitPython and some variants of MicroPython"
            if self.firmware_name == "CircuitPython"
            else "for MicroPython on ESP8266 and ESP32-C3"
        )
        x1000_target_description = "for MicroPython on ESP32, ESP32-S2 and ESP32-S3"
        address_mapping = {
            f"0x0 ({x0_target_description})": "0x0",
            f"0x1000 ({x1000_target_description})": "0x1000",
        }
        address_label = ttk.Label(self.main_frame, text=f"Target address")
        address_label.grid(row=9, column=1, sticky="e", padx=(epadx, 0), pady=(epady, 0))
        self._address_combo = MappingCombobox(
            self.main_frame, exportselection=False, mapping=address_mapping
        )
        self._address_combo.grid(
            row=9, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(epady, 0)
        )
        self._address_combo.bind("<<ComboboxSelected>>", self.register_settings_changed, True)

        self._advanced_widgets += [address_label, self._address_combo]

        speed_mapping = {
            "460800 (supported by some boards)": "460800",
            "230400 (supported by many boards)": "230400",
            "115200 (default)": "115200",
            "38400 (a fallback to try if installation fails at higher speeds)": "38400",
            "9600 (the last resort for ruling out installation speed problems)": "9600",
        }
        speed_label = ttk.Label(self.main_frame, text=f"Install speed")
        speed_label.grid(row=10, column=1, sticky="e", padx=(epadx, 0), pady=(ipady, 0))
        self._speed_combo = MappingCombobox(
            self.main_frame, exportselection=False, mapping=speed_mapping
        )
        self._speed_combo.grid(
            row=10, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(ipady, 0)
        )
        self._speed_combo.select_value("115200")
        self._advanced_widgets += [speed_label, self._speed_combo]
        self._speed_combo.bind("<<ComboboxSelected>>", self.register_settings_changed, True)

        flash_mode_mapping = {
            f"keep (reads the setting from the selected {self.firmware_name} image)": "keep",
            "dio (next to try if 'keep' doesn't give working result)": "dio",
            "qio (another alternative to try if 'keep' fails)": "qio",
            "dout (a less common option)": "dout",
            "qout (a less common option)": "qout",
        }
        flash_mode_label = ttk.Label(self.main_frame, text=f"Flash mode")
        flash_mode_label.grid(row=11, column=1, sticky="e", padx=(epadx, 0), pady=(ipady, 0))
        self._flash_mode_combo = MappingCombobox(
            self.main_frame, exportselection=False, mapping=flash_mode_mapping
        )
        self._flash_mode_combo.grid(
            row=11, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(ipady, 0)
        )
        self._flash_mode_combo.select_value("keep")
        self._advanced_widgets += [flash_mode_label, self._flash_mode_combo]
        self._flash_mode_combo.bind("<<ComboboxSelected>>", self.register_settings_changed, True)

        self._no_stub_variable = EnhancedBooleanVar(
            value=False, modification_listener=self.register_settings_changed
        )
        self._no_stub_checkbutton = ttk.Checkbutton(
            self.main_frame,
            text="Disable stub loader (--no-stub, some boards require this)",
            variable=self._no_stub_variable,
        )
        self._no_stub_checkbutton.grid(
            row=14, column=2, sticky="w", padx=(ipadx, 0), pady=(ipady, 0)
        )
        self._advanced_widgets += [self._no_stub_checkbutton]

    def get_initial_log_line_count(self):
        return 10

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

        sorted_ports = sorted(list_serial_ports(max_cache_age=0), key=port_order)

        result = {}
        for p in sorted_ports:
            desc = get_serial_port_label(p)
            result[desc] = TargetInfo(
                title=desc, path=None, board_id=None, family=None, model=None, port=p
            )

        return result

    def on_change_family(self, family: Optional[str]) -> None:
        super().on_change_family(family)
        if family:
            self._address_combo.select_value(self._compute_start_address(family))

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

        if self._work_mode in ["device_info", "image_info"]:
            self.show_log_frame()

        return {
            "erase_flash": self._erase_variable.get(),
            "family": self._family_combo.get_selected_value(),
            "address": self._address_combo.get_selected_value(),
            "speed": self._speed_combo.get_selected_value(),
            "flash_mode": self._flash_mode_combo.get_selected_value(),
            "no_stub": self._no_stub_variable.get(),
            "port_was_used_in_thonny": port_was_used_in_thonny,
        }

    def _download_to_temp(self, download_info: Dict[str, str]) -> Optional[str]:
        if self._work_mode == "device_info":
            return None
        else:
            return super()._download_to_temp(download_info)

    def allow_single_success(self) -> bool:
        return self._work_mode == "install"

    def perform_core_operation(
        self,
        source_path: str,
        variant_info: Dict[str, Any],
        download_info: Dict[str, str],
        target_info: TargetInfo,
        work_options: Dict[str, Any],
    ) -> bool:
        """Running in a bg thread"""

        self.report_progress(None, None)

        if self._work_mode == "install":
            assert source_path
            assert target_info

            command = self._esptool_command + [
                "--port",
                target_info.port.device,
                "--chip",
                work_options["family"],
                "--baud",
                work_options["speed"],
            ]
            if work_options["no_stub"]:
                command.append("--no-stub")

            command += [
                "write_flash",
                "--flash_mode",
                work_options["flash_mode"],
                "--flash_size",  # default changed in esptool 3.0
                "keep",
            ]

            if work_options["erase_flash"]:
                command.append("--erase-all")

            command += [
                work_options["address"],
                source_path,
            ]

            progress_text = "Installing"

        elif self._work_mode == "device_info":
            assert target_info
            command = self._esptool_command + [
                "--port",
                target_info.port.device,
            ]
            if work_options["no_stub"]:
                command.append("--no-stub")
            command.append("flash_id")

            progress_text = "Querying device info"

        elif self._work_mode == "image_info":
            assert source_path
            command = self._esptool_command + ["image_info", "--version", "2", source_path]
            progress_text = "Reading image info"

        else:
            raise RuntimeError(f"Unknown work mode {self._work_mode!r}")

        if (
            self._work_mode in ["install", "device_info"]
            and work_options["port_was_used_in_thonny"]
        ):
            self.append_text("Disconnecting from REPL...")
            self.set_action_text("Disconnecting from REPL...")
            time.sleep(1.5)

            if not self._check_connection(target_info.port.device):
                self.set_action_text("Problem")
                self.append_text("Could not connect to port\n")
                self.report_done(False)
                return False

        self.set_action_text(progress_text)
        self.append_text(subprocess.list2cmdline(command) + "\n")
        self._proc = self._create_subprocess(command)
        try:
            while True:
                line = self._proc.stdout.readline()
                if not line:
                    break
                self.append_text(line)
                self.set_action_text_smart(line)
            returncode = self._proc.wait()
        finally:
            self._proc = None

        if returncode:
            self.set_action_text("Error")
            self.append_text("\nCommand returned with error code %s" % returncode)
        else:
            self.set_action_text("Done!")
            self.append_text("Done!")

        return returncode == 0

    def _compute_start_address(self, family: str) -> str:
        if self.firmware_name == "MicroPython" and family in ["esp32", "esp32-s2", "esp32-s3"]:
            return "0x1000"
        else:
            return "0x0"

    def _browse_image(self):
        initialdir = os.path.normpath(os.path.expanduser("~/Downloads"))
        if not os.path.isdir(initialdir):
            initialdir = None

        path = ui_utils.askopenfilename(
            filetypes=[("bin-files", ".bin"), ("all files", ".*")],
            parent=self.winfo_toplevel(),
            initialdir=initialdir,
        )
        if not path:
            return

        if running_on_windows():
            path = normpath_with_actual_case(path)

        family = self._infer_firmware_family(path)
        if not family:
            famkey = ui_utils.ask_one_from_choices(
                self,
                title="Problem",
                question="Could not determine image type.\nPlease select the correct family manually!",
                choices=self.get_families_mapping().keys(),
            )

            if not famkey:
                return

            family = self.get_families_mapping()[famkey]

        if family not in self.get_families_mapping().values():
            messagebox.showerror("Error", f"Unkown image type '{family!r}'", parent=self)
            return

        if not self._downloaded_variants:
            self._downloaded_variants = []

        for variant in self._downloaded_variants:
            if variant.get("title", "") == LOCAL_VARIANT_TITLE and variant["family"] == family:
                break
        else:
            variant = {
                "title": LOCAL_VARIANT_TITLE,
                "model": "unknown",
                "family": family,
                "info_url": os.path.dirname(path),
                "downloads": [],
            }
            self._downloaded_variants.insert(0, variant)

        for download in variant["downloads"]:
            if download["url"] == path:
                break
        else:
            download = {"version": os.path.basename(path), "url": path}
            variant["downloads"].insert(0, download)

        self._family_combo.select_value(family)
        self.on_change_family(family)
        self._variant_combo.select_value(variant)
        self._present_versions_for_variant(variant)
        self._update_variant_info()
        self._version_combo.select_value(download)

        # avoid automatic updates
        self._last_handled_family = family
        self._last_handled_family_target = (family, self._target_combo.get_selected_value())
        self._last_handled_variant = variant

    def _infer_firmware_family(self, path: str) -> Optional[str]:
        from contextlib import redirect_stdout

        import esptool

        f = io.StringIO()
        with redirect_stdout(f):
            try:
                esptool.main(["image_info", "--version", "2", path])
            except Exception:
                logger.exception("Could not infer image family")
                return None

        out = f.getvalue()

        for line in out.splitlines():
            if line.startswith("Detected image type:"):
                family = line.split()[-1].lower().replace("-", "").replace("'", "").replace('"', "")
                logger.info("Detected family %r", family)
                return family

        logger.warning("Could not detect image family. image_info output:\n%s", out)
        return None

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

    def on_click_ok_button(self):
        self._work_mode = "install"
        super().on_click_ok_button()

    def _create_subprocess(self, cmd) -> subprocess.Popen:
        return subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )

    def cancel_work(self):
        super().cancel_work()
        if not self._proc:
            return

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

    def has_action_menu(self) -> bool:
        return True

    def populate_action_menu(self, action_menu: tk.Menu) -> None:
        action_menu.add_command(
            label="Select local MicroPython image ...", command=self._browse_image
        )
        action_menu.add_separator()

        action_menu.add_command(
            label="Query device info",
            command=self._query_device_info,
            state="normal" if self._can_query_device_info() else "disabled",
        )
        action_menu.add_command(
            label="Show image info",
            command=self._show_image_info,
            state="normal" if self._can_query_image_info() else "disabled",
        )

        action_menu.add_separator()
        if self._advanced_widgets[0].winfo_ismapped():
            action_menu.add_command(
                label="Hide install options",
                command=self._hide_advanced_options,
            )
        else:
            action_menu.add_command(
                label="Show install options",
                command=self._show_advanced_options,
            )

    def _query_device_info(self) -> None:
        self._work_mode = "device_info"
        self.start_work_and_update_ui()

    def _show_image_info(self) -> None:
        self._work_mode = "image_info"
        self.start_work_and_update_ui()

    def _can_query_device_info(self) -> bool:
        return self._state == "idle" and self._target_combo.get_selected_value() is not None

    def _can_query_image_info(self) -> bool:
        return self._state == "idle" and self._version_combo.get_selected_value() is not None

    def _hide_advanced_options(self) -> None:
        for widget in self._advanced_widgets:
            widget.grid_remove()

        get_workbench().set_option("esptool.show_advanced_options", False)

    def _show_advanced_options(self) -> None:
        for widget in self._advanced_widgets:
            if not widget.winfo_ismapped():
                widget.grid()

        get_workbench().set_option("esptool.show_advanced_options", True)


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
