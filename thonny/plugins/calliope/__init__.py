from thonny.languages import tr
from thonny.plugins.micropython import add_micropython_backend
from thonny.plugins.micropython.mp_common import PASTE_SUBMIT_MODE
from thonny.plugins.simplified_micropython.simplified_mp_front import (
    SimplifiedMicroPythonConfigPage,
    SimplifiedMicroPythonProxy,
)


class CalliopeMiniProxy(SimplifiedMicroPythonProxy):
    def _get_backend_launcher_path(self) -> str:
        import thonny.plugins.calliope.calliope_back

        return thonny.plugins.calliope.calliope_back.__file__

    @classmethod
    def _is_potential_port(cls, p):
        return p.vid == 0x0D28 and p.pid == 0x0204 and p.product and "calliope" in p.product.lower()


class CalliopeMiniConfigPage(SimplifiedMicroPythonConfigPage):
    def _get_intro_url(self):
        return "https://github.com/calliope-mini/calliope-mini-micropython"

    def _get_intro_text(self):
        return (
            tr("Make sure MicroPython has been installed to your Calliope mini.")
            + "\n("
            + tr("Don't forget that main.py only works without embedded main script.")
            + ")"
        )


def load_plugin():
    add_micropython_backend(
        "calliope",
        CalliopeMiniProxy,
        "MicroPython (Calliope mini)",
        CalliopeMiniConfigPage,
        sort_key="32",
        validate_time=False,
        sync_time=False,
        submit_mode=PASTE_SUBMIT_MODE,
        write_block_size=128,
    )

    # Don't consider micro:bit in generic backends
    # The main reason is to reduce the number of items in the backend switcher menu
    import thonny.plugins.circuitpython
    import thonny.plugins.esp
    import thonny.plugins.micropython
    import thonny.plugins.rp2040

    thonny.plugins.circuitpython.cirpy_front.VIDS_PIDS_TO_AVOID.update(
        CalliopeMiniProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.micropython.mp_front.VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND.update(
        CalliopeMiniProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.esp.VIDS_PIDS_TO_AVOID_IN_ESP_BACKENDS.update(
        CalliopeMiniProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.rp2040.VIDS_PIDS_TO_AVOID_IN_RP2040.update(
        CalliopeMiniProxy.get_known_usb_vids_pids()
    )
