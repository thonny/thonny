import argparse
import logging
import os
import sys
from typing import Any, Dict, List

import thonny
from thonny import (
    SINGLE_INSTANCE_DEFAULT,
    choose_logging_level,
    configure_logging,
    get_configuration_file,
    get_ipc_file_path,
    get_runner,
    get_thonny_user_dir,
    get_version,
    prepare_thonny_user_dir,
)

logger = logging.getLogger(__name__)


def run() -> int:
    # First make sure the command line is good
    parsed_args = _parse_arguments_to_dict(sys.argv[1:])

    # Temporary compatibility measure for the breaking change introduced in version 5.0
    thonny.THONNY_USER_DIR = get_thonny_user_dir()

    import runpy

    if sys.executable.endswith("thonny.exe"):
        # otherwise some library may try to run its subprocess with thonny.exe
        # NB! Must be pythonw.exe not python.exe, otherwise Runner thinks console
        # is already allocated.
        sys.executable = sys.executable[: -len("thonny.exe")] + "pythonw.exe"

    _set_dpi_aware()

    try:
        runpy.run_module("thonny.customize", run_name="__main__")
    except ImportError:
        pass

    prepare_thonny_user_dir()
    configure_logging(_get_frontend_log_file(), choose_logging_level())

    if not _check_welcome():
        return 0

    if _should_delegate():
        try:
            _delegate_to_existing_instance(parsed_args)
            print("Delegated to an existing Thonny instance. Exiting now.")
            return 0
        except Exception:
            import traceback

            traceback.print_exc()

    # Did not or could not delegate

    try:
        from thonny import workbench

        bench = workbench.Workbench(parsed_args)
        bench.mainloop()
        return 0

    except Exception:
        logger.exception("Internal launch or mainloop error")

        import tkinter as tk

        if tk._default_root is not None:
            import traceback

            from thonny import ui_utils

            dlg = ui_utils.LongTextDialog("Internal error", traceback.format_exc())
            ui_utils.show_dialog(dlg, tk._default_root)

        return -1
    finally:
        runner = get_runner()
        if runner is not None:
            runner.destroy_backend()


def _check_welcome():
    from thonny import misc_utils

    if not os.path.exists(get_configuration_file()) and not misc_utils.running_on_rpi():
        from thonny.config import ConfigurationManager
        from thonny.first_run import FirstRunWindow

        mgr = ConfigurationManager(get_configuration_file())

        win = FirstRunWindow(mgr)
        win.mainloop()
        return win.ok
    else:
        return True


def _should_delegate():
    if not os.path.exists(get_ipc_file_path()):
        # no previous instance
        return False

    from thonny.config import try_load_configuration

    configuration_manager = try_load_configuration(get_configuration_file())
    configuration_manager.set_default("general.single_instance", SINGLE_INSTANCE_DEFAULT)
    return configuration_manager.get_option("general.single_instance")


def _delegate_to_existing_instance(parsed_args: Dict[str, Any]):
    import socket

    from thonny import workbench

    try:
        sock, secret = _create_client_socket()
    except Exception:
        # Maybe the lock is abandoned or the content is corrupted
        try:
            os.remove(get_ipc_file_path())
        except Exception:
            import traceback

            traceback.print_exc()
        raise

    data = repr((secret, parsed_args)).encode(encoding="utf_8")

    sock.settimeout(2.0)
    sock.sendall(data)
    sock.shutdown(socket.SHUT_WR)
    response = bytes([])
    while len(response) < len(workbench.SERVER_SUCCESS):
        new_data = sock.recv(2)
        if len(new_data) == 0:
            break
        else:
            response += new_data

    if response.decode("UTF-8") != workbench.SERVER_SUCCESS:
        raise RuntimeError("Unsuccessful delegation")


def _create_client_socket():
    import socket

    timeout = 2.0

    if sys.platform == "win32":
        with open(get_ipc_file_path(), "r") as fp:
            port = int(fp.readline().strip())
            secret = fp.readline().strip()

        # "localhost" can be much slower than "127.0.0.1"
        client_socket = socket.create_connection(("127.0.0.1", port), timeout=timeout)
    else:
        client_socket = socket.socket(socket.AF_UNIX)  # @UndefinedVariable
        client_socket.settimeout(timeout)
        client_socket.connect(get_ipc_file_path())
        secret = ""

    return client_socket, secret


def _set_dpi_aware():
    # https://stackoverflow.com/questions/36134072/setprocessdpiaware-seems-not-to-work-under-windows-10
    # https://bugs.python.org/issue33656
    # https://msdn.microsoft.com/en-us/library/windows/desktop/dn280512(v=vs.85).aspx
    # https://github.com/python/cpython/blob/master/Lib/idlelib/pyshell.py
    if sys.platform == "win32":
        try:
            import ctypes

            PROCESS_SYSTEM_DPI_AWARE = 1
            ctypes.OleDLL("shcore").SetProcessDpiAwareness(PROCESS_SYSTEM_DPI_AWARE)
        except (ImportError, AttributeError, OSError):
            pass


def _get_frontend_log_file():
    return os.path.join(get_thonny_user_dir(), "frontend.log")


def _parse_arguments_to_dict(raw_args: List[str]) -> Dict[str, Any]:
    parser = argparse.ArgumentParser(
        description="Python IDE for beginners",
        allow_abbrev=False,
        add_help=False,
    )

    parser.add_argument(
        "-h",
        "" "--help",
        help="Show this help message and exit",
        action="help",
    )

    parser.add_argument(
        "--version", help="Show Thonny version and exit", action="version", version=get_version()
    )

    parser.add_argument(
        "files",
        help="",
        nargs="*",
        metavar="<python_file>",
    )

    parser.add_argument(
        "--replayer",
        help="Open the log file in Replayer. Pass empty string to open Replayer without loading a file",
        metavar="<log_file>",
    )

    parsed_args = vars(parser.parse_args(args=raw_args))
    # Need to store CWD, because Thonny may be with different cwd by the time of opening the files
    parsed_args["cwd"] = os.getcwd()
    return parsed_args
