from thonny.plugins.micropython import (
    BareMetalMicroPythonConfigPage,
    BareMetalMicroPythonProxy,
    add_micropython_backend,
)
from thonny.plugins.micropython.mp_front import VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND

LEGO_INVENTOR_PRIME_VIDS_PIDS = {
    (0x0694, 0x0009),  # Spike Prime
    (0x0694, 0x000D),  # Spike Essential
    (0x0694, 0x0010),  # Robot Inventor
}


class PrimeInventorMicroPythonProxy(BareMetalMicroPythonProxy):
    @classmethod
    def should_consider_unknown_devices(cls):
        return False

    @classmethod
    def get_known_usb_vids_pids(cls):
        # https://github.com/pybricks/technical-info/blob/master/assigned-numbers.md
        # can be anything
        return LEGO_INVENTOR_PRIME_VIDS_PIDS

    def get_node_label(self):
        return "Robot Inventor / Spike Prime"

    def _get_backend_launcher_path(self) -> str:
        import thonny.plugins.prime_inventor.prime_inventor_back

        return thonny.plugins.prime_inventor.prime_inventor_back.__file__


class PrimeInventorMicroPythonConfigPage(BareMetalMicroPythonConfigPage):
    def _get_intro_text(self):
        return "Instructions:"

    def _get_intro_url(self):
        return "https://github.com/thonny/thonny/wiki/InventorPrime"

    def may_have_rtc(self):
        return False

    @property
    def allow_webrepl(self):
        return False


def _load_plugin():
    add_micropython_backend(
        "PrimeInventorMicroPython",
        PrimeInventorMicroPythonProxy,
        "MicroPython (Robot Inventor / Spike Prime)",
        PrimeInventorMicroPythonConfigPage,
        bare_metal=True,
        sort_key="24",
        validate_time=False,
        sync_time=False,
    )
    VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND.update(LEGO_INVENTOR_PRIME_VIDS_PIDS)
