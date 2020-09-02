import os
import subprocess
import time
import tkinter as tk
from collections import OrderedDict
from tkinter import messagebox, ttk

from thonny import get_runner, get_workbench, ui_utils
from thonny.misc_utils import construct_cmd_line, running_on_mac_os
from thonny.plugins.micropython import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
    add_micropython_backend,
    list_serial_ports_with_descriptions,
)
from thonny.plugins.micropython.serial_connection import SerialConnection
from thonny.running import get_interpreter_for_subprocess
from thonny.ui_utils import (
    CommonDialogEx,
    SubprocessDialog,
    ems_to_pixels,
    show_dialog,
)


class ESPProxy(BareMetalMicroPythonProxy):
    pass


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

    def _get_api_stubs_path(self):
        return os.path.join(os.path.dirname(__file__), "esp8266_api_stubs")


class ESP32Proxy(ESPProxy):
    @property
    def known_usb_vids_pids(self):
        return super().known_usb_vids_pids | {
            # eg. ESP-WROOM-32
            (0x10C4, 0xEA60)  # Silicon Labs CP210x USB to UART Bridge
        }

    def _get_launcher_with_args(self):
        cmd = super()._get_launcher_with_args()

        if self._port == "webrepl":
            cmd.extend(["--min_write_delay", "0.5"])

        return cmd

    def _get_api_stubs_path(self):
        return os.path.join(os.path.dirname(__file__), "esp32_api_stubs")


class ESPConfigPage(BareMetalMicroPythonConfigPage):
    def __init__(self, master, chip, firmware_start_address):
        self._chip = chip
        self._firmware_start_address = firmware_start_address
        super().__init__(master)

    def _get_flashing_frame(self):
        frame = super()._get_flashing_frame()
        return frame

    def _has_flashing_dialog(self):
        return True

    def _open_flashing_dialog(self):
        dlg = ESPFlashingDialog(get_workbench(), self._chip, self._firmware_start_address)
        ui_utils.show_dialog(dlg)

    @property
    def allow_webrepl(self):
        return True


class ESP8266ConfigPage(ESPConfigPage):
    def __init__(self, master):
        super().__init__(master, "esp8266", "0x0")


class ESP32ConfigPage(ESPConfigPage):
    def __init__(self, master):
        super().__init__(master, "esp32", "0x1000")


class ESPFlashingDialog(CommonDialogEx):
    def __init__(self, master, chip, start_address, initial_port_desc=""):
        super().__init__(master)

        self.title("Install %s firmware with esptool" % chip.upper())

        self._chip = chip
        self._start_address = start_address
        self._esptool_command = self._get_esptool_command()
        if not self._esptool_command:
            messagebox.showerror(
                "Can't find esptool",
                "esptool not found.\n"
                + "Install it via 'Tools => Manage plug-ins'\n"
                + "or using your OP-system package manager.",
            )
            self._close()
            return

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

        self._firmware_entry = ttk.Entry(self.main_frame, width=65)
        self._firmware_entry.grid(row=2, column=2, sticky="nsew", padx=ipadx, pady=(ipady, 0))

        browse_button = ttk.Button(self.main_frame, text="Browse...", command=self._browse)
        browse_button.grid(row=2, column=3, sticky="we", padx=(0, epadx), pady=(ipady, 0))

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

        # Buttons
        install_button = ttk.Button(self.main_frame, text="Install", command=self._install)
        install_button.grid(row=6, column=2, columnspan=1, sticky="e", padx=ipadx, pady=(0, epady))

        cancel_button = ttk.Button(self.main_frame, text="Close", command=self._close)
        cancel_button.grid(
            row=6, column=3, columnspan=1, sticky="e", padx=(0, epadx), pady=(0, epady)
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
                return [result]
            else:
                result = shutil.which("esptool.py")
                if result:
                    return [result]
                else:
                    return None

    def _reload_ports(self):
        pairs = list_serial_ports_with_descriptions()
        self._ports_by_desc = OrderedDict(pairs)
        self._port_combo.configure(values=list(self._ports_by_desc.keys()))

    def _browse(self):
        path = ui_utils.askopenfilename(filetypes=[("bin-files", ".bin"), ("all files", ".*")])
        if path:
            self._firmware_entry.delete(0, "end")
            self._firmware_entry.insert(0, path)

    def _check_connection(self, port):
        proxy = get_runner().get_backend_proxy()
        if isinstance(proxy, BareMetalMicroPythonProxy):
            # Most likely it is using the same port
            proxy.disconnect()
            time.sleep(1.5)

        # Maybe another program is connected
        # or the user doesn't have sufficient permissions?
        try:
            conn = SerialConnection(port, 115200, skip_reader=True)
            conn.close()

            return True
        except Exception as e:
            messagebox.showerror(
                "Can't connect", str(e), master=None if running_on_mac_os() else self
            )
            return False

    def _install(self):
        if not self._port_desc_variable.get():
            messagebox.showerror("Select port", "Please select port")
            return

        port = self._ports_by_desc[self._port_desc_variable.get()]

        firmware_path = self._firmware_entry.get()
        if not os.path.exists(firmware_path):
            messagebox.showerror("Bad firmware path", "Can't find firmware, please check path")
            return

        erase_command = self._esptool_command + [
            "--chip",
            self._chip,
            "--port",
            port,
            "erase_flash",
        ]

        write_command = self._esptool_command + [
            "--chip",
            self._chip,
            "--port",
            port,
            "write_flash",
            "--flash_mode",
            self._flashmode.get(),
            self._start_address,
            firmware_path,
        ]

        if not self._check_connection(port):
            return

        # unknown problem with first dialog appearing at 0,0
        # self.update_idletasks()
        if self.winfo_screenwidth() >= 1024:
            min_left = ems_to_pixels(15)
            min_top = ems_to_pixels(5)
        else:
            min_left = 0
            min_top = 0

        def long_desc(cmd):
            return "Command:\n%s\n\nOutput:\n" % construct_cmd_line(cmd)

        self.update_idletasks()
        if self._erase_variable.get():
            proc = self._create_subprocess(erase_command)
            dlg = SubprocessDialog(
                self,
                proc,
                "Erasing flash",
                long_description=long_desc(erase_command),
                autoclose=True,
            )
            show_dialog(dlg, master=self, min_left=min_left, min_top=min_top)
            if dlg.cancelled or dlg.returncode:
                return

        proc = self._create_subprocess(write_command)
        dlg = SubprocessDialog(
            self,
            proc,
            "Installing firmware",
            long_description=long_desc(write_command),
            autoclose=False,
        )
        show_dialog(dlg, master=self, min_left=min_left, min_top=min_top)

    def _create_subprocess(self, cmd):
        return subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )

    def _close(self):
        self.closed = True
        self.destroy()


def load_plugin():
    add_micropython_backend(
        "ESP32", ESP32Proxy, "MicroPython (ESP32)", ESP32ConfigPage, sort_key="32"
    )
    add_micropython_backend(
        "ESP8266", ESP8266Proxy, "MicroPython (ESP8266)", ESP8266ConfigPage, sort_key="33"
    )
