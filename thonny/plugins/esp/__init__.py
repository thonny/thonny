from logging import getLogger
from typing import List

from thonny.plugins.micropython import BareMetalMicroPythonConfigPage, BareMetalMicroPythonProxy
from thonny.plugins.micropython.esptool_dialog import try_launch_esptool_dialog

# from thonny.plugins.micropython.esptool_dialog import try_launch_esptool_dialog
from thonny.plugins.micropython.mp_front import add_micropython_backend, get_uart_adapter_vids_pids
from thonny.plugins.micropython.uf2dialog import show_uf2_installer

logger = getLogger(__name__)

VIDS_PIDS_TO_AVOID_IN_ESP_BACKENDS = set()


class ESPProxy(BareMetalMicroPythonProxy):
    @classmethod
    def get_vids_pids_to_avoid(self):
        return VIDS_PIDS_TO_AVOID_IN_ESP_BACKENDS

    def _get_backend_launcher_path(self) -> str:
        import thonny.plugins.esp.esp_back

        return thonny.plugins.esp.esp_back.__file__


class ESP8266Proxy(ESPProxy):
    description = "MicroPython on ESP8266"
    config_page_constructor = "ESP8266"

    @classmethod
    def get_known_usb_vids_pids(cls):
        return get_uart_adapter_vids_pids()


class ESP32Proxy(ESPProxy):
    @classmethod
    def get_known_usb_vids_pids(cls):
        return get_uart_adapter_vids_pids()

    @classmethod
    def _is_potential_port(cls, p):
        lower_desc = p.description.lower()
        return (
            super()._is_potential_port(p) or "m5stack" in lower_desc or "esp32" in lower_desc
        ) and "circuitpython" not in lower_desc


class ESPConfigPage(BareMetalMicroPythonConfigPage):
    def _open_flashing_dialog(self, kind: str) -> None:
        if kind == "esptool":
            try_launch_esptool_dialog(self.winfo_toplevel(), "MicroPython")
        elif kind == "UF2":
            show_uf2_installer(self, firmware_name="MicroPython")
        else:
            raise ValueError(f"Unexpected kind{kind}")

    @property
    def allow_webrepl(self):
        return True


class ESP8266ConfigPage(ESPConfigPage):
    def get_flashing_dialog_kinds(self) -> List[str]:
        return ["esptool"]


class ESP32ConfigPage(ESPConfigPage):
    def get_flashing_dialog_kinds(self) -> List[str]:
        return ["esptool", "UF2"]


def load_plugin():
    add_micropython_backend(
        "ESP32",
        ESP32Proxy,
        "MicroPython (ESP32)",
        ESP32ConfigPage,
        sort_key="35",
    )
    add_micropython_backend(
        "ESP8266", ESP8266Proxy, "MicroPython (ESP8266)", ESP8266ConfigPage, sort_key="36"
    )
