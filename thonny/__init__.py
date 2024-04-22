import logging
import os.path
import sys
import time
from logging import getLogger
from typing import TYPE_CHECKING, List, Optional, cast

if TYPE_CHECKING:
    # Following imports are required for MyPy
    # http://mypy.readthedocs.io/en/stable/common_issues.html#import-cycles
    from thonny.running import Runner
    from thonny.shell import ShellView
    from thonny.workbench import Workbench


def get_vendored_libs_dir() -> str:
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "vendored_libs"))


# Required both for front- and back-end
sys.path.insert(
    1,
    get_vendored_libs_dir(),
)


SINGLE_INSTANCE_DEFAULT = True
BACKEND_LOG_MARKER = "Thonny's backend.log"
REPORT_TIME = False


logger = getLogger(__name__)

# lazily assigned cache variables
_thonny_user_dir = None
_configuration_file = None
_in_debug_mode = None
_version = None
_ipc_file = None


# variables assigned elsewhere
_workbench = None
_runner = None


# For timing
_last_module_count = 0
_last_modules = set()
_last_time = time.time()


def report_time(label: str) -> None:
    """
    Method for finding unwarranted imports and delays.
    """
    global _last_time, _last_module_count, _last_modules

    if not REPORT_TIME:
        return

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


def get_version():
    global _version
    if _version:
        return _version
    try:
        package_dir = os.path.dirname(sys.modules["thonny"].__file__)
        with open(os.path.join(package_dir, "VERSION"), encoding="ASCII") as fp:
            _version = fp.read().strip()
            return _version
    except Exception:
        logger.warning("Could not determine Thonny version", exc_info=True)
        return "0.0.0"


def get_workbench() -> "Workbench":
    return cast("Workbench", _workbench)


def get_runner() -> "Runner":
    return cast("Runner", _runner)


def get_shell(create: bool = True) -> "ShellView":
    return cast("ShellView", get_workbench().get_view("ShellView", create=create))


def get_ipc_file_path():
    global _ipc_file
    if _ipc_file:
        return _ipc_file

    if sys.platform == "win32":
        from thonny.misc_utils import get_local_appdata_dir

        base_dir = get_local_appdata_dir()
    else:
        base_dir = os.environ.get("XDG_RUNTIME_DIR")
        if not base_dir or not os.path.exists(base_dir):
            base_dir = os.environ.get("TMPDIR")

    if not base_dir or not os.path.exists(base_dir):
        base_dir = get_thonny_user_dir()

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

    _ipc_file = os.path.join(ipc_dir, "ipc.sock")
    return _ipc_file


def in_debug_mode() -> bool:
    global _in_debug_mode
    if _in_debug_mode is None:
        _in_debug_mode = (
            os.environ.get("THONNY_DEBUG", False)
            in [
                "1",
                1,
                "True",
                True,
                "true",
            ]
        ) or _read_configured_debug_mode()

    return _in_debug_mode


def is_portable() -> bool:
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


def get_thonny_user_dir() -> str:
    global _thonny_user_dir
    if _thonny_user_dir is None:
        _thonny_user_dir = _compute_thonny_user_dir()
    return _thonny_user_dir


def get_configuration_file() -> str:
    global _configuration_file
    if _configuration_file is None:
        _configuration_file = os.path.join(get_thonny_user_dir(), "configuration.ini")

    return _configuration_file


def prepare_thonny_user_dir():
    if not os.path.exists(get_thonny_user_dir()):
        os.makedirs(get_thonny_user_dir(), mode=0o700, exist_ok=True)

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

            copy_contents(template_dir, get_thonny_user_dir())


def set_logging_level(level=None):
    if level is None:
        level = choose_logging_level()

    logging.getLogger("thonny").setLevel(level)


def choose_logging_level():
    if in_debug_mode():
        return logging.DEBUG
    else:
        return logging.INFO


def configure_backend_logging() -> None:
    configure_logging(get_backend_log_file(), None)


def get_backend_log_file():
    return os.path.join(get_thonny_user_dir(), "backend.log")


def configure_logging(log_file, console_level=None):
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
        logger.setLevel(choose_logging_level())
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

    fault_out = open(os.path.join(get_thonny_user_dir(), "frontend_faults.log"), mode="w")
    faulthandler.enable(fault_out)


def get_user_base_directory_for_plugins() -> str:
    return os.path.join(get_thonny_user_dir(), "plugins")


def get_sys_path_directory_containg_plugins() -> str:
    from thonny.misc_utils import get_user_site_packages_dir_for_base

    return get_user_site_packages_dir_for_base(get_user_base_directory_for_plugins())


def _compute_thonny_user_dir():
    env_var = os.environ.get("THONNY_USER_DIR", "")
    if env_var:
        # back-end processes always choose this path
        return os.path.expanduser(env_var)

    # Following is only for the front-end process
    from thonny.common import is_private_python, running_in_virtual_environment
    from thonny.misc_utils import get_roaming_appdata_dir

    if is_portable():
        if sys.platform == "win32":
            root_dir = os.path.dirname(sys.executable)
        elif sys.platform == "darwin":
            root_dir = os.path.join(
                os.path.dirname(sys.executable), "..", "..", "..", "..", "..", ".."
            )
        else:
            root_dir = os.path.join(os.path.dirname(sys.executable), "..")
        return os.path.normpath(os.path.abspath(os.path.join(root_dir, "user_data")))
    elif running_in_virtual_environment() and not is_private_python(sys.executable):
        return os.path.join(sys.prefix, ".thonny")
    elif sys.platform == "win32":
        return os.path.join(get_roaming_appdata_dir(), "Thonny")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Thonny")
    else:
        # https://specifications.freedesktop.org/basedir-spec/latest/ar01s02.html
        data_home = os.environ.get(
            "XDG_CONFIG_HOME", os.path.expanduser(os.path.join("~", ".config"))
        )
        return os.path.join(data_home, "Thonny")


def _read_configured_debug_mode():
    if not os.path.exists(get_configuration_file()):
        return False

    try:
        with open(get_configuration_file(), encoding="utf-8") as fp:
            for line in fp:
                if "debug_mode" in line and "True" in line:
                    return True
        return False
    except Exception:
        import traceback

        traceback.print_exc()
        return False


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
