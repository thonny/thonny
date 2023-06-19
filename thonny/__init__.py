import logging
import os.path
import sys
import time
from logging import getLogger
from typing import TYPE_CHECKING, List, Optional, cast

from thonny.common import is_private_python, is_virtual_executable

_last_module_count = 0
_last_modules = set()

_last_time = time.time()


logger = getLogger(__name__)


def report_time(label: str) -> None:
    """
    Method for finding unwarranted imports and delays.
    """
    # return

    global _last_time, _last_module_count, _last_modules

    log_modules = True

    t = time.time()
    mod_count = len(sys.modules)
    mod_delta = mod_count - _last_module_count
    if mod_delta > 0:
        mod_info = f"(+{mod_count - _last_module_count} modules)"
    else:
        mod_info = ""
    logger.info("TIME/MODS %s %s %s", f"{t - _last_time:.3f}", label, mod_info)

    if log_modules and mod_delta > 0:
        current_modules = set(sys.modules.keys())
        logger.info("NEW MODS %s", list(sorted(current_modules - _last_modules)))
        _last_modules = current_modules

    _last_time = t
    _last_module_count = mod_count


report_time("After defining report_time")


SINGLE_INSTANCE_DEFAULT = True
BACKEND_LOG_MARKER = "Thonny's backend.log"


def _get_known_folder(ID):
    # http://stackoverflow.com/a/3859336/261181
    # http://www.installmate.com/support/im9/using/symbols/functions/csidls.htm
    import ctypes.wintypes

    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(0, ID, 0, SHGFP_TYPE_CURRENT, buf)
    assert buf.value
    return buf.value


def _get_roaming_appdata_dir():
    return _get_known_folder(26)


def _get_local_appdata_dir():
    return _get_known_folder(28)


def _compute_thonny_user_dir():
    if os.environ.get("THONNY_USER_DIR", ""):
        return os.path.expanduser(os.environ["THONNY_USER_DIR"])
    elif is_portable():
        if sys.platform == "win32":
            root_dir = os.path.dirname(sys.executable)
        elif sys.platform == "darwin":
            root_dir = os.path.join(
                os.path.dirname(sys.executable), "..", "..", "..", "..", "..", ".."
            )
        else:
            root_dir = os.path.join(os.path.dirname(sys.executable), "..")
        return os.path.normpath(os.path.abspath(os.path.join(root_dir, "user_data")))
    elif is_virtual_executable(sys.executable) and not is_private_python(sys.executable):
        return os.path.join(sys.prefix, ".thonny")
    elif sys.platform == "win32":
        return os.path.join(_get_roaming_appdata_dir(), "Thonny")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Thonny")
    else:
        # https://specifications.freedesktop.org/basedir-spec/latest/ar01s02.html
        data_home = os.environ.get(
            "XDG_CONFIG_HOME", os.path.expanduser(os.path.join("~", ".config"))
        )
        return os.path.join(data_home, "Thonny")


def _read_configured_debug_mode():
    if not os.path.exists(CONFIGURATION_FILE):
        return False

    try:
        with open(CONFIGURATION_FILE, encoding="utf-8") as fp:
            for line in fp:
                if "debug_mode" in line and "True" in line:
                    return True
        return False
    except Exception:
        import traceback

        traceback.print_exc()
        return False


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
    if sys.platform == "win32":
        drive = os.path.splitdrive(abs_location)[0]
        if drive.endswith(":"):
            from ctypes import windll

            return windll.kernel32.GetDriveTypeW(drive) == 2  # @UndefinedVariable
        else:
            return False
    elif sys.platform == "darwin":
        # not exact heuristics
        return abs_location.startswith("/Volumes/")
    else:
        # not exact heuristics
        return abs_location.startswith("/media/") or abs_location.startswith("/mnt/")


_THONNY_VERSION = None


def get_version():
    global _THONNY_VERSION
    if _THONNY_VERSION:
        return _THONNY_VERSION
    try:
        package_dir = os.path.dirname(sys.modules["thonny"].__file__)
        with open(os.path.join(package_dir, "VERSION"), encoding="ASCII") as fp:
            _THONNY_VERSION = fp.read().strip()
            return _THONNY_VERSION
    except Exception:
        return "0.0.0"


THONNY_USER_DIR = _compute_thonny_user_dir()
CONFIGURATION_FILE = os.path.join(THONNY_USER_DIR, "configuration.ini")
_CONFIGURED_DEBUG = _read_configured_debug_mode()


_IPC_FILE = None


def get_ipc_file_path():
    global _IPC_FILE
    if _IPC_FILE:
        return _IPC_FILE

    if sys.platform == "win32":
        base_dir = _get_local_appdata_dir()
    else:
        base_dir = os.environ.get("XDG_RUNTIME_DIR")
        if not base_dir or not os.path.exists(base_dir):
            base_dir = os.environ.get("TMPDIR")

    if not base_dir or not os.path.exists(base_dir):
        base_dir = THONNY_USER_DIR

    for name in ("LOGNAME", "USER", "LNAME", "USERNAME"):
        if name in os.environ:
            username = os.environ.get(name)
            break
    else:
        username = os.path.basename(os.path.expanduser("~"))

    ipc_dir = os.path.join(base_dir, "thonny-%s" % username)
    os.makedirs(ipc_dir, exist_ok=True)

    if not sys.platform == "win32":
        os.chmod(ipc_dir, 0o700)

    _IPC_FILE = os.path.join(ipc_dir, "ipc.sock")
    return _IPC_FILE


def _check_welcome():
    from thonny import misc_utils

    if not os.path.exists(CONFIGURATION_FILE) and not misc_utils.running_on_rpi():
        from thonny.config import ConfigurationManager
        from thonny.first_run import FirstRunWindow

        mgr = ConfigurationManager(CONFIGURATION_FILE)

        win = FirstRunWindow(mgr)
        win.mainloop()
        return win.ok
    else:
        return True


def launch():
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

    prepare_thonny_user_dir()
    _configure_frontend_logging()

    if not _check_welcome():
        return 0

    if _should_delegate():
        try:
            _delegate_to_existing_instance(sys.argv[1:])
            print("Delegated to an existing Thonny instance. Exiting now.")
            return 0
        except Exception:
            import traceback

            traceback.print_exc()

    # Did not or could not delegate

    try:
        from thonny import workbench

        bench = workbench.Workbench()
        bench.mainloop()
        return 0

    except Exception:
        import tkinter as tk
        import traceback
        from logging import exception

        exception("Internal launch or mainloop error")
        from thonny import ui_utils

        dlg = ui_utils.LongTextDialog("Internal error", traceback.format_exc())
        ui_utils.show_dialog(dlg, tk._default_root)
        return -1
    finally:
        runner = get_runner()
        if runner is not None:
            runner.destroy_backend()

    return 0


def prepare_thonny_user_dir():
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
    if not os.path.exists(get_ipc_file_path()):
        # no previous instance
        return False

    from thonny.config import try_load_configuration

    configuration_manager = try_load_configuration(CONFIGURATION_FILE)
    configuration_manager.set_default("general.single_instance", SINGLE_INSTANCE_DEFAULT)
    return configuration_manager.get_option("general.single_instance")


def _delegate_to_existing_instance(args):
    import socket

    from thonny import workbench

    transformed_args = []
    for arg in args:
        if not arg.startswith("-"):
            arg = os.path.abspath(arg)

        transformed_args.append(arg)

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


def _configure_frontend_logging() -> None:
    _configure_logging(get_frontend_log_file(), _choose_logging_level())


def configure_backend_logging() -> None:
    _configure_logging(get_backend_log_file(), None)


def get_backend_log_file():
    return os.path.join(THONNY_USER_DIR, "backend.log")


def get_frontend_log_file():
    return os.path.join(THONNY_USER_DIR, "frontend.log")


def _get_orig_argv() -> Optional[List[str]]:
    try:
        from sys import orig_argv  # since 3.10

        return sys.orig_argv
    except ImportError:
        # https://stackoverflow.com/a/57914236/261181
        import ctypes

        argc = ctypes.c_int()
        argv = ctypes.POINTER(ctypes.c_wchar_p if sys.version_info >= (3,) else ctypes.c_char_p)()
        try:
            ctypes.pythonapi.Py_GetArgcArgv(ctypes.byref(argc), ctypes.byref(argv))
        except AttributeError:
            # See https://github.com/thonny/thonny/issues/2206
            # and https://bugs.python.org/issue40910
            # This symbol is not available in thonny.exe built agains Python 3.8
            return None

        # Ctypes are weird. They can't be used in list comprehensions, you can't use `in` with them, and you can't
        # use a for-each loop on them. We have to do an old-school for-i loop.
        arguments = list()
        for i in range(argc.value):
            arguments.append(argv[i])

        return arguments


def _configure_logging(log_file, console_level=None):
    logFormatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d [%(threadName)s] %(levelname)-7s %(name)s: %(message)s", "%H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file, encoding="UTF-8", mode="w")
    file_handler.setFormatter(logFormatter)

    main_logger = logging.getLogger("thonny")
    contrib_logger = logging.getLogger("thonnycontrib")
    pipkin_logger = logging.getLogger("pipkin")

    # NB! Don't mess with the main root logger, because (CPython) backend runs user code
    for logger in [main_logger, contrib_logger, pipkin_logger]:
        logger.setLevel(_choose_logging_level())
        logger.propagate = False  # otherwise it will be also reported by IDE-s root logger
        logger.addHandler(file_handler)

    if console_level is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logFormatter)
        console_handler.setLevel(console_level)
        for logger in [main_logger, contrib_logger]:
            logger.addHandler(console_handler)

    # Log most important info as soon as possible
    main_logger.info("Thonny version: %s", get_version())
    main_logger.info("cwd: %s", os.getcwd())
    main_logger.info("original argv: %s", _get_orig_argv())
    main_logger.info("sys.executable: %s", sys.executable)
    main_logger.info("sys.argv: %s", sys.argv)
    main_logger.info("sys.path: %s", sys.path)
    main_logger.info("sys.flags: %s", sys.flags)

    import faulthandler

    fault_out = open(os.path.join(THONNY_USER_DIR, "frontend_faults.log"), mode="w")
    faulthandler.enable(fault_out)


def get_user_base_directory_for_plugins() -> str:
    return os.path.join(THONNY_USER_DIR, "plugins")


def get_sys_path_directory_containg_plugins() -> str:
    from thonny.misc_utils import get_user_site_packages_dir_for_base

    return get_user_site_packages_dir_for_base(get_user_base_directory_for_plugins())


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
    from thonny.running import Runner
    from thonny.shell import ShellView
    from thonny.workbench import Workbench

_workbench = None  # type: Optional[Workbench]


def get_workbench() -> "Workbench":
    return cast("Workbench", _workbench)


_runner = None  # type: Optional[Runner]


def set_logging_level(level=None):
    if level is None:
        level = _choose_logging_level()

    logging.getLogger("thonny").setLevel(level)


def _choose_logging_level():
    if in_debug_mode():
        return logging.DEBUG
    else:
        return logging.INFO


def in_debug_mode() -> bool:
    # Value may be something other than string when it is set in Python code
    return (
        os.environ.get("THONNY_DEBUG", False)
        in [
            "1",
            1,
            "True",
            True,
            "true",
        ]
        or _CONFIGURED_DEBUG
    )


def get_runner() -> "Runner":
    return cast("Runner", _runner)


def get_shell() -> "ShellView":
    return cast("ShellView", get_workbench().get_view("ShellView"))


report_time("After loading thonny module")
