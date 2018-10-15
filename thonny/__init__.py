import os.path
import sys
import platform
from typing import TYPE_CHECKING, cast, Optional


def _get_default_thonny_data_folder():
    if platform.system() == "Windows":
        # http://stackoverflow.com/a/3859336/261181
        # http://www.installmate.com/support/im9/using/symbols/functions/csidls.htm
        import ctypes.wintypes

        CSIDL_APPDATA = 26
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(
            0, CSIDL_APPDATA, 0, SHGFP_TYPE_CURRENT, buf
        )
        return os.path.join(buf.value, "Thonny")
    elif platform.system() == "Darwin":
        return os.path.expanduser("~/Library/Thonny")
    else:
        # https://specifications.freedesktop.org/basedir-spec/latest/ar01s02.html
        data_home = os.environ.get(
            "XDG_CONFIG_HOME", os.path.expanduser(os.path.join("~", ".config"))
        )
        return os.path.join(data_home, "Thonny")


if os.environ.get("THONNY_USER_DIR", ""):
    THONNY_USER_DIR = os.environ["THONNY_USER_DIR"]
elif (
    hasattr(sys, "base_prefix")
    and sys.base_prefix != sys.prefix
    or hasattr(sys, "real_prefix")
    and getattr(sys, "real_prefix") != sys.prefix
):
    # we're in a virtualenv or venv
    THONNY_USER_DIR = os.path.join(sys.prefix, ".thonny")
else:
    THONNY_USER_DIR = _get_default_thonny_data_folder()


def launch():
    _prepare_thonny_user_dir()
    _misc_prepare()

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

        dlg = ui_utils.LongTextDialog("Internal error", 
                                      traceback.format_exc(), 
                                      parent=get_workbench())
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

    configuration_manager = try_load_configuration(workbench.CONFIGURATION_FILE_NAME)
    # Setting the default
    configuration_manager.set_default(
        "general.single_instance", workbench.SINGLE_INSTANCE_DEFAULT
    )
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


def _misc_prepare():
    if os.name == "nt":
        import ctypes

        # TODO: see also SetProcessDPIAwareness (Win 8.1+)
        # https://stackoverflow.com/questions/36134072/setprocessdpiaware-seems-not-to-work-under-windows-10
        ctypes.windll.user32.SetProcessDPIAware()


def get_version():
    try:
        package_dir = os.path.dirname(sys.modules["thonny"].__file__)
        with open(os.path.join(package_dir, "VERSION"), encoding="ASCII") as fp:
            return fp.read().strip()
    except Exception:
        return "0.0.0"


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
