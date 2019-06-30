from thonny.running import SubprocessProxy
from thonny.common import CommandToBackend, InterruptCommand, UserError, BackendEvent
from typing import Optional
import logging
from thonny.plugins.micropython import MicroPythonConfigPage
import sys
from thonny import running, get_runner, get_workbench
from os.path import os
import platform
import serial.tools
from textwrap import dedent


class NewMicroPythonProxy(SubprocessProxy):
    def __init__(self, clean):
        self._port = get_workbench().get_option(self.backend_name + ".port")

        if self._port == "auto":
            potential = self._detect_potential_ports()
            if len(potential) == 1:
                self._port = potential[0][0]
            else:
                self._port = None
                message = dedent(
                    """\
                    Couldn't find the device automatically. 
                    Check the connection (making sure the device is not in bootloader mode)
                    or choose "Tools → Options → Backend" to select the port manually."""
                )

                if len(potential) > 1:
                    _, descriptions = zip(*potential)
                    message += "\n\nLikely candidates are:\n * " + "\n * ".join(descriptions)

                self._show_error(message)

        super().__init__(clean, running.get_frontend_python())

    def _get_launcher_with_args(self):
        import thonny.plugins.micropython.backend

        return [thonny.plugins.micropython.backend.__file__, str(self._port)]

    def interrupt(self):
        self._send_msg(InterruptCommand())
        """
        if self._proc is not None and self._proc.poll() is None:
            if running_on_windows():
                try:
                    os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # @UndefinedVariable
                except Exception:
                    logging.exception("Could not interrupt backend process")
            else:
                self._proc.send_signal(signal.SIGINT)
        """

    def _clear_environment(self):
        "TODO:"

    def _detect_potential_ports(self):
        all_ports = list_serial_ports()
        """
        for p in all_ports:
            print(p.description,
                  p.device,
                  None if p.vid is None else hex(p.vid),
                  None if p.pid is None else hex(p.pid),
                  )
        """
        return [
            (p.device, p.description)
            for p in all_ports
            if (p.vid, p.pid) in self.known_usb_vids_pids
            or p.description in self.known_port_descriptions
            or ("USB" in p.description and "serial" in p.description.lower())
            or "UART" in p.description
            or "DAPLink" in p.description
        ]

    @property
    def known_usb_vids_pids(self):
        """Return set of pairs of USB device VID, PID"""
        return set()

    @property
    def known_port_descriptions(self):
        return set()

    def has_own_filesystem(self):
        return self._proc is not None

    def uses_local_filesystem(self):
        return False

    def can_do_file_operations(self):
        return self._proc is not None and get_runner().is_waiting_toplevel_command()

    def is_connected(self):
        return self._proc is not None

    def is_functional(self):
        return self.is_connected()

    def _show_error(self, text):
        self._response_queue.append(
            BackendEvent(event_type="ProgramOutput", stream_name="stderr", data="stderr")
        )


class NewGenericConfPage(MicroPythonConfigPage):
    pass


def list_serial_ports():
    # serial.tools.list_ports.comports() can be too slow
    # because os.path.islink can be too slow (https://github.com/pyserial/pyserial/pull/303)
    # Workarond: temporally patch os.path.islink
    try:
        old_islink = os.path.islink
        if platform.system() == "Windows":
            os.path.islink = lambda _: False
        return list(serial.tools.list_ports.comports())
    finally:
        os.path.islink = old_islink
