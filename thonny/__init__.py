import os.path
import sys
import platform
from typing import TYPE_CHECKING, cast, Optional
import traceback
import logging

SINGLE_INSTANCE_DEFAULT = True


def _compute_thonny_user_dir():
    if os.environ.get("THONNY_USER_DIR", ""):
        return os.path.expanduser(os.environ["THONNY_USER_DIR"])
    elif is_portable():
        if platform.system() == "Windows":
            root_dir = os.path.dirname(sys.executable)
        elif platform.system() == "Darwin":
            root_dir = os.path.join(
                os.path.dirname(sys.executable), "..", "..", "..", "..", "..", ".."
            )
        else:
            root_dir = os.path.join(os.path.dirname(sys.executable), "..")
        return os.path.normpath(os.path.abspath(os.path.join(root_dir, "user_data")))
    elif (
        hasattr(sys, "base_prefix")
        and sys.base_prefix != sys.prefix
        or hasattr(sys, "real_prefix")
        and getattr(sys, "real_prefix") != sys.prefix
    ):
        # we're in a virtualenv or venv
        return os.path.join(sys.prefix, ".thonny")
    elif platform.system() == "Windows":
        from thonny import misc_utils

        return os.path.join(misc_utils.get_roaming_appdata_dir(), "Thonny")
    elif platform.system() == "Darwin":
        return os.path.expanduser("~/Library/Thonny")
    else:
        # https://specifications.freedesktop.org/basedir-spec/latest/ar01s02.html
        data_home = os.environ.get(
            "XDG_CONFIG_HOME", os.path.expanduser(os.path.join("~", ".config"))
        )
        return os.path.join(data_home, "Thonny")


def is_portable():
    # it can be explicitly declared as portable or shared ...
    portable_marker_path = os.path.join(os.path.dirname(sys.executable), "portable_thonny.ini")
    shared_marker_path = os.path.join(os.path.dirname(sys.executable), "shared_thonny.ini")

    if os.path.exists(portable_marker_path) and not os.path.exists(shared_marker_path):
        return True
    elif not os.path.exists(portable_marker_path) and os.path.exists(shared_marker_path):
        return False

    # ... or it becomes implicitly portable if it's on a removable drive
    abs_location = os.path.abspath(__file__)
    if platform.system() == "Windows":
        drive = os.path.splitdrive(abs_location)[0]
        if drive.endswith(":"):
            from ctypes import windll

            return windll.kernel32.GetDriveTypeW(drive) == 2  # @UndefinedVariable
        else:
            return False
    elif platform.system() == "Darwin":
        # not exact heuristics
        return abs_location.startswith("/Volumes/")
    else:
        # not exact heuristics
        return abs_location.startswith("/media/") or abs_location.startswith("/mnt/")


def get_version():
    try:
        package_dir = os.path.dirname(sys.modules["thonny"].__file__)
        with open(os.path.join(package_dir, "VERSION"), encoding="ASCII") as fp:
            return fp.read().strip()
    except Exception:
        return "0.0.0"


THONNY_USER_DIR = _compute_thonny_user_dir()
CONFIGURATION_FILE = os.path.join(THONNY_USER_DIR, "configuration.ini")


def _get_ipc_file_path():
    from thonny import misc_utils
    import getpass

    if platform.system() == "Windows":
        base_dir = misc_utils.get_local_appdata_dir()
    else:
        base_dir = os.environ.get("XDG_RUNTIME_DIR")
        if not base_dir or not os.path.exists(base_dir):
            base_dir = os.environ.get("TMPDIR")

    if not base_dir or not os.path.exists(base_dir):
        base_dir = THONNY_USER_DIR

    ipc_dir = os.path.join(base_dir, "thonny-%s" % getpass.getuser())
    os.makedirs(ipc_dir, exist_ok=True)

    if not platform.system() == "Windows":
        os.chmod(ipc_dir, 0o700)

    return os.path.join(ipc_dir, "ipc.sock")


IPC_FILE = _get_ipc_file_path()


def _check_welcome():
    from thonny import misc_utils

    if not os.path.exists(CONFIGURATION_FILE) and not misc_utils.running_on_rpi():
        from thonny.first_run import FirstRunWindow
        from thonny.config import ConfigurationManager

        mgr = ConfigurationManager(CONFIGURATION_FILE)

        win = FirstRunWindow(mgr)
        win.mainloop()
        return win.ok
    else:
        return True


def launch():
    import gettext
    import runpy

    if sys.executable.endswith("thonny.exe"):
        # otherwise some library may try to run its subprocess with thonny.exe
        # NB! Must be pythonw.exe not python.exe, otherwise Runner thinks console
        # is already allocated.
        sys.executable = sys.executable[: -len("thonny.exe")] + "pythonw.exe"

    set_dpi_aware()

    try:
        runpy.run_module("thonny.customize", run_name="__main__")
    except ImportError:
        pass

    gettext.install("thonny", "locale")
    _prepare_thonny_user_dir()

    if not _check_welcome():
        return

    if _should_delegate():
        try:
            _delegate_to_existing_instance(sys.argv[1:])
            print("Delegated to an existing Thonny instance. Exiting now.")
            return 0
        except Exception:
            traceback.print_exc()

    # Did not or could not delegate

    try:
        from thonny import workbench

        bench = workbench.Workbench()
        try:
            bench.mainloop()
        except SystemExit:
            bench.destroy()
        return 0

    except SystemExit as e:
        from tkinter import messagebox

        messagebox.showerror("System exit", str(e))
        return -1

    except Exception:
        from logging import exception

        exception("Internal launch or mainloop error")
        from thonny import ui_utils

        dlg = ui_utils.LongTextDialog("Internal error", traceback.format_exc())
        ui_utils.show_dialog(dlg, get_workbench())
        return -1
    finally:
        runner = get_runner()
        if runner is not None:
            runner.destroy_backend()

    return 0


def _prepare_thonny_user_dir():
    if not os.path.exists(THONNY_USER_DIR):
        os.makedirs(THONNY_USER_DIR, mode=0o700, exist_ok=True)

        # user_dir_template is a post-installation means for providing
        # alternative default user environment in multi-user setups
        template_dir = os.path.join(os.path.dirname(__file__), "user_dir_template")

        if os.path.isdir(template_dir):
            import shutil

            def copy_contents(src_dir, dest_dir):
                # I want the copy to have current user permissions
                for name in os.listdir(src_dir):
                    src_item = os.path.join(src_dir, name)
                    dest_item = os.path.join(dest_dir, name)
                    if os.path.isdir(src_item):
                        os.makedirs(dest_item, mode=0o700)
                        copy_contents(src_item, dest_item)
                    else:
                        shutil.copyfile(src_item, dest_item)
                        os.chmod(dest_item, 0o600)

            copy_contents(template_dir, THONNY_USER_DIR)


def _should_delegate():
    if not os.path.exists(IPC_FILE):
        # no previous instance
        return

    from thonny.config import try_load_configuration

    configuration_manager = try_load_configuration(CONFIGURATION_FILE)
    configuration_manager.set_default("general.single_instance", SINGLE_INSTANCE_DEFAULT)
    return configuration_manager.get_option("general.single_instance")


def _delegate_to_existing_instance(args):
    from thonny import workbench
    import socket

    transformed_args = []
    for arg in args:
        if not arg.startswith("-"):
            arg = os.path.abspath(arg)

        transformed_args.append(arg)

    try:
        sock, secret = _create_client_socket()
    except Exception:
        # Maybe the lock is abandoned
        print("Trying to remove lock")
        os.remove(IPC_FILE)
        print("Successfully removed abandoned lock")
        raise

    data = repr((secret, transformed_args)).encode(encoding="utf_8")

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

    if platform.system() == "Windows":
        with open(IPC_FILE, "r") as fp:
            port = int(fp.readline().strip())
            secret = fp.readline().strip()

        # "localhost" can be much slower than "127.0.0.1"
        client_socket = socket.create_connection(("127.0.0.1", port), timeout=timeout)
    else:
        client_socket = socket.socket(socket.AF_UNIX)  # @UndefinedVariable
        client_socket.settimeout(timeout)
        client_socket.connect(IPC_FILE)
        secret = ""

    return client_socket, secret


def set_dpi_aware():
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


if TYPE_CHECKING:
    # Following imports are required for MyPy
    # http://mypy.readthedocs.io/en/stable/common_issues.html#import-cycles
    import thonny.workbench
    from thonny.workbench import Workbench
    from thonny.running import Runner
    from thonny.shell import ShellView

_workbench = None  # type: Optional[Workbench]


def get_workbench() -> "Workbench":
    return cast("Workbench", _workbench)


_runner = None  # type: Optional[Runner]


def get_runner() -> "Runner":
    return cast("Runner", _runner)


def get_shell() -> "ShellView":
    return cast("ShellView", get_workbench().get_view("ShellView"))
