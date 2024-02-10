from thonny.languages import tr
from thonny.plugins.micropython import add_micropython_backend
from thonny.plugins.micropython.mp_common import PASTE_SUBMIT_MODE
from thonny.plugins.simplified_micropython.simplified_mp_front import (
    SimplifiedMicroPythonConfigPage,
    SimplifiedMicroPythonProxy,
)


class MicrobitProxy(SimplifiedMicroPythonProxy):
    def _get_backend_launcher_path(self) -> str:
        import thonny.plugins.microbit.microbit_back

        return thonny.plugins.microbit.microbit_back.__file__

    @classmethod
    def _is_potential_port(cls, p):
        return (
            p.vid == 0x0D28 and p.pid == 0x0204 and p.product and "micro:bit" in p.product.lower()
        )


class MicrobitConfigPage(SimplifiedMicroPythonConfigPage):
    def _get_intro_url(self):
        return "https://microbit-micropython.readthedocs.io/en/latest/devguide/repl.html"

    def _get_intro_text(self):
        return (
            tr("Make sure MicroPython has been installed to your micro:bit.")
            + "\n("
            + tr("Don't forget that main.py only works without embedded main script.")
            + ")"
        )


def load_plugin():
    add_micropython_backend(
        "microbit",
        MicrobitProxy,
        "MicroPython (BBC micro:bit)",
        MicrobitConfigPage,
        sort_key="31",
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
        MicrobitProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.micropython.mp_front.VIDS_PIDS_TO_AVOID_IN_GENERIC_BACKEND.update(
        MicrobitProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.esp.VIDS_PIDS_TO_AVOID_IN_ESP_BACKENDS.update(
        MicrobitProxy.get_known_usb_vids_pids()
    )
    thonny.plugins.rp2040.VIDS_PIDS_TO_AVOID_IN_RP2040.update(
        MicrobitProxy.get_known_usb_vids_pids()
    )
