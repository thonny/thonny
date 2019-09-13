from thonny.plugins.micropython import (
    MicroPythonProxy,
    MicroPythonConfigPage,
    add_micropython_backend,
    list_serial_ports_with_descriptions,
)
from thonny import get_workbench, get_runner, ui_utils
import os
import subprocess
from thonny.ui_utils import (
    SubprocessDialog,
    CommonDialog,
    CommonDialogEx,
    ems_to_pixels,
    show_dialog,
)
from thonny.running import get_frontend_python, get_interpreter_for_subprocess
from time import sleep

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import OrderedDict
import tkinter


class ESPProxy(MicroPythonProxy):
    def _finalize_repl(self):
        # In some cases there may be still something coming.
        sleep(0.1)
        remainder = self._serial.read_all().decode("utf-8", "replace").strip()
        # display it unless it looks like an extra raw prompt
        if remainder and (len(remainder) > 40 or "raw REPL; CTRL-B to exit" not in remainder):
            self._send_error_to_shell(remainder)

    @property
    def firmware_filetypes(self):
        return [("*.bin files", ".bin"), ("all files", ".*")]

    def erase_flash(self):
        self.disconnect()
        cmd = [get_frontend_python(), "-u", "-m", "esptool", "--port", self.port, "erase_flash"]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )
        dlg = SubprocessDialog(get_workbench(), proc, "Erasing flash", autoclose=False)
        dlg.wait_window()

    @property
    def allow_webrepl(self):
        return True


class ESP8266Proxy(ESPProxy):
    description = "MicroPython on ESP8266"
    config_page_constructor = "ESP8266"

    @property
    def known_usb_vids_pids(self):
        return super().known_usb_vids_pids | {
            # eg. Adafruit Feather Huzzah
            (0x10C4, 0xEA60),  # Silicon Labs CP210x USB to UART Bridge,
            (0x1A86, 0x7523),  # USB-SERIAL CH340,
        }

    @property
    def flash_mode(self):
        # "dio" for some boards with a particular FlashROM configuration (e.g. some variants of a NodeMCU board)
        # https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html
        # https://github.com/espressif/esptool/wiki/SPI-Flash-Modes

        # TODO: detect the need for this (or provide conf option for the backend)
        return "keep"
        # return "dio"

    def construct_firmware_upload_command(self, firmware_path):
        return [
            get_frontend_python(),
            "-u",
            "-m",
            "esptool",
            "--port",
            self.port,
            #'--baud', '460800',
            "write_flash",
            #'--flash_size', 'detect',
            # "--flash_mode", self.flash_mode,
            "0x0000",
            firmware_path,
        ]

    def _get_api_stubs_path(self):
        return os.path.join(os.path.dirname(__file__), "esp8266_api_stubs")


class ESP32Proxy(ESPProxy):
    @property
    def known_usb_vids_pids(self):
        return super().known_usb_vids_pids | {
            # eg. ESP-WROOM-32
            (0x10C4, 0xEA60)  # Silicon Labs CP210x USB to UART Bridge
        }

    def construct_firmware_upload_command(self, firmware_path):
        return [
            get_frontend_python(),
            "-u",
            "-m",
            "esptool",
            #'--chip', 'esp32',
            "--port",
            self.port,
            #'--baud', '460800',
            "write_flash",
            #'--flash_size=detect',
            "0x1000",
            firmware_path,
        ]

    def _get_api_stubs_path(self):
        return os.path.join(os.path.dirname(__file__), "esp32_api_stubs")


class ESPConfigPage(MicroPythonConfigPage):
    def __init__(self, master, chip):
        self.chip = chip
        super().__init__(master)

    def _get_flashing_frame(self):
        frame = super()._get_flashing_frame()
        return frame

    def _has_flashing_dialog(self):
        return True

    def _open_flashing_dialog(self):
        dlg = ESPFlashingDialog(get_workbench(), self.chip)
        ui_utils.show_dialog(dlg)


class ESP8266ConfigPage(ESPConfigPage):
    def __init__(self, master):
        super().__init__(master, "esp8266")


class ESP32ConfigPage(ESPConfigPage):
    def __init__(self, master):
        super().__init__(master, "esp32")


class ESPFlashingDialog(CommonDialogEx):
    def __init__(self, master, chip, initial_port_desc=""):
        super().__init__(master)

        self.title("Install %s firmware with esptool" % chip.upper())

        self.chip = chip
        self._esptool_command = self._get_esptool_command()
        if not self._esptool_command:
            messagebox.showerror(
                "Can't find esptool",
                "esptool not found.\n"
                + "Install it via 'Tools => Manage plug-ins'\n"
                + "or using your OP-system package manager.",
            )
            return self._cancel()

        self.main_frame.columnconfigure(2, weight=1)

        epadx = ems_to_pixels(2)
        ipadx = ems_to_pixels(0.5)
        epady = epadx
        ipady = ipadx

        # Port
        port_label = ttk.Label(self.main_frame, text="Port")
        port_label.grid(row=1, column=1, sticky="w", padx=(epadx, 0), pady=(epady, 0))

        self._port_desc_variable = tk.StringVar(value=initial_port_desc)
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

        self._firmware_entry = ttk.Entry(self.main_frame, width=80)
        self._firmware_entry.grid(row=2, column=2, sticky="nsew", padx=ipadx, pady=(ipady, 0))

        browse_button = ttk.Button(self.main_frame, text="Browse...", command=self._browse)
        browse_button.grid(row=2, column=3, sticky="we", padx=(0, epadx), pady=(ipady, 0))

        # Erase
        self._erase_variable = tk.BooleanVar(value=True)
        self._erase_checkbutton = ttk.Checkbutton(
            self.main_frame, text="Erase flash before installing", variable=self._erase_variable
        )
        self._erase_checkbutton.grid(
            row=3, column=1, columnspan=3, sticky="w", padx=(epadx, 0), pady=(ipady, 0)
        )

        # Buttons
        install_button = ttk.Button(self.main_frame, text="Install", command=self._install)
        install_button.grid(row=4, column=1, columnspan=2, sticky="e", padx=ipadx, pady=(0, epady))

        cancel_button = ttk.Button(self.main_frame, text="Cancel", command=self._cancel)
        cancel_button.grid(
            row=4, column=3, columnspan=1, sticky="we", padx=(0, epadx), pady=(0, epady)
        )

        self._reload_ports()

    def _get_esptool_command(self):
        try:
            import esptool

            return [get_interpreter_for_subprocess(), "-u", "-m", "esptool"]
        except ImportError:
            import shutil

            result = shutil.which("esptool")
            if result:
                return result
            else:
                return shutil.which("esptool.py")

    def _reload_ports(self):
        pairs = list_serial_ports_with_descriptions()
        self._ports_by_desc = OrderedDict(pairs)
        self._port_combo.configure(values=list(self._ports_by_desc.keys()))

    def _browse(self):
        path = ui_utils.askopenfilename(filetypes=[("bin-files", ".bin"), ("all files", ".*")])
        if path:
            self._firmware_entry.delete(0, "end")
            self._firmware_entry.insert(0, path)

    def _install(self):
        if not self._port_desc_variable.get():
            messagebox.showerror("Select port", "Please select port")
            return

        port = self._ports_by_desc[self._port_desc_variable.get()]

        firmware_path = self._firmware_entry.get()
        if not os.path.exists(firmware_path):
            messagebox.showerror("Bad firmware path", "Can't find firmware, please check path")
            return

        write_command = self._esptool_command + [
            "--chip",
            self.chip,
            "--port",
            port,
            "write_flash",
            "0x1000",
            firmware_path,
        ]

        erase_command = self._esptool_command + ["--chip", self.chip, "--port", port, "erase_flash"]

        if self._erase_variable.get():
            proc = self._create_subprocess(erase_command)
            dlg = SubprocessDialog(self, proc, "Erasing flash", autoclose=False)
            show_dialog(dlg)
            if dlg.cancelled or dlg.returncode:
                return

        proc = self._create_subprocess(write_command)
        dlg = SubprocessDialog(self, proc, "Installing firmware", autoclose=False)
        show_dialog(dlg)

    def _create_subprocess(self, cmd):
        return subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )

    def _cancel(self):
        self.destroy()


def load_plugin():
    add_micropython_backend("ESP8266", ESP8266Proxy, "MicroPython (ESP8266)", ESP8266ConfigPage)
    add_micropython_backend("ESP32", ESP32Proxy, "MicroPython (ESP32)", ESP32ConfigPage)

    def upload_micropython():
        proxy = get_runner().get_backend_proxy()
        proxy.select_and_upload_micropython()

    def upload_micropython_enabled():
        proxy = get_runner().get_backend_proxy()
        return getattr(proxy, "micropython_upload_enabled", False) and isinstance(proxy, ESPProxy)

    def erase_flash():
        proxy = get_runner().get_backend_proxy()
        proxy.erase_flash()

    def erase_flash_enabled():
        return (
            isinstance(get_runner().get_backend_proxy(), ESPProxy)
            and get_runner().get_backend_proxy().micropython_upload_enabled
        )

    get_workbench().add_command(
        "uploadmicropythonesp",
        "device",
        "Install MicroPython to ESP8266/ESP32 ...",
        upload_micropython,
        upload_micropython_enabled,
        group=40,
    )

    get_workbench().add_command(
        "erasespflash",
        "device",
        "Erase ESP8266/ESP32 flash",
        erase_flash,
        tester=erase_flash_enabled,
        group=40,
    )
