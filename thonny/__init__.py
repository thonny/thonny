import os.path
import sys
import platform
from typing import TYPE_CHECKING, cast, Optional


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
        # http://stackoverflow.com/a/3859336/261181
        # http://www.installmate.com/support/im9/using/symbols/functions/csidls.htm
        import ctypes.wintypes

        CSIDL_APPDATA = 26
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_APPDATA, 0, SHGFP_TYPE_CURRENT, buf)
        return os.path.join(buf.value, "Thonny")
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
CONFIGURATION_FILE_NAME = os.path.join(THONNY_USER_DIR, "configuration.ini")


def _check_welcome():
    from thonny import workbench, misc_utils

    if not os.path.exists(CONFIGURATION_FILE_NAME) and not misc_utils.running_on_rpi():
        from thonny.first_run import FirstRunWindow
        from thonny.config import ConfigurationManager

        mgr = ConfigurationManager(CONFIGURATION_FILE_NAME)

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
    gettext.install("thonny", "locale")

    _prepare_thonny_user_dir()

    try:
        runpy.run_module("thonny.customize", run_name="__main__")
    except ImportError:
        pass

    if not _check_welcome():
        return

    try:
        from thonny import workbench

        if _should_delegate():
            # First check if there is existing Thonny instance to handle the request
            delegation_result = _try_delegate_to_existing_instance(sys.argv[1:])
            if delegation_result == True:  # pylint: disable=singleton-comparison
                # we're done
                print("Delegated to an existing Thonny instance. Exiting now.")
                return 0

            if hasattr(delegation_result, "accept"):
                # we have server socket to put in use
                server_socket = delegation_result
            else:
                server_socket = None

            bench = workbench.Workbench(server_socket)
        else:
            bench = workbench.Workbench()

        try:
            bench.mainloop()
        except SystemExit:
            bench.destroy()
        return 0
    except SystemExit as e:
        from tkinter import messagebox

        messagebox.showerror("System exit", str(e), parent=get_workbench())
        return -1
    except Exception:
        from logging import exception

        exception("Internal launch or mainloop error")
        from thonny import ui_utils
        import traceback

        dlg = ui_utils.LongTextDialog(
            "Internal error", traceback.format_exc(), parent=get_workbench()
        )
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
    from thonny import workbench
    from thonny.config import try_load_configuration

    configuration_manager = try_load_configuration(CONFIGURATION_FILE_NAME)
    # Setting the default
    configuration_manager.set_default("general.single_instance", workbench.SINGLE_INSTANCE_DEFAULT)
    # getting the value (may use the default or return saved value)
    return configuration_manager.get_option("general.single_instance")


def _try_delegate_to_existing_instance(args):
    import socket
    from thonny import workbench

    try:
        # Try to create server socket.
        # This is fastest way to find out if Thonny is already running
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(("localhost", workbench.THONNY_PORT))
        serversocket.listen(10)
        # we were able to create server socket (ie. Thonny was not running)
        # Let's use the socket in Thonny so that requests coming while
        # UI gets constructed don't get lost.
        # (Opening several files with Thonny in Windows results in many
        # Thonny processes opened quickly)
        return serversocket
    except OSError:
        # port was already taken, most likely by previous Thonny instance.
        # Try to connect and send arguments
        try:
            return _delegate_to_existing_instance(args)
        except Exception:
            import traceback

            traceback.print_exc()
            return False


def _delegate_to_existing_instance(args):
    import socket
    from thonny import workbench

    data = repr(args).encode(encoding="utf_8")
    sock = socket.create_connection(("localhost", workbench.THONNY_PORT))
    sock.sendall(data)
    sock.shutdown(socket.SHUT_WR)
    response = bytes([])
    while len(response) < len(workbench.SERVER_SUCCESS):
        new_data = sock.recv(2)
        if len(new_data) == 0:
            break
        else:
            response += new_data

    return response.decode("UTF-8") == workbench.SERVER_SUCCESS


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
