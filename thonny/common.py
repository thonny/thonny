# -*- coding: utf-8 -*-

"""
Classes used both by front-end and back-end
"""
import os.path
import site
import sys
from collections import namedtuple
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Callable, Dict, List, Optional, Tuple  # @UnusedImport

logger = getLogger(__name__)

STRING_PSEUDO_FILENAME = "<string>"
REPL_PSEUDO_FILENAME = "<stdin>"
MESSAGE_MARKER = "\x02"
OBJECT_LINK_START = "[object_link_for_thonny=%d]"
OBJECT_LINK_END = "[/object_link_for_thonny]"
REMOTE_PATH_MARKER = " :: "
PROCESS_ACK = "OK"

IGNORED_FILES_AND_DIRS = [
    "System Volume Information",
    "._.Trashes",
    ".Trashes",
    "__MACOSX",
    ".DS_Store",
]

ValueInfo = namedtuple("ValueInfo", ["id", "repr"])
FrameInfo = namedtuple(
    "FrameInfo",
    [
        "id",
        "filename",
        "module_name",
        "code_name",
        "source",
        "lineno",
        "firstlineno",
        "in_library",
        "locals",
        "globals",
        "freevars",
        "event",
        "focus",
        "node_tags",
        "current_statement",
        "current_root_expression",
        "current_evaluations",
    ],
)

TextRange = namedtuple("TextRange", ["lineno", "col_offset", "end_lineno", "end_col_offset"])


@dataclass(frozen=True)
class DistInfo:
    key: str
    project_name: str
    version: str
    location: str


class Record:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def update(self, e, **kw):
        self.__dict__.update(e, **kw)

    def setdefault(self, **kw):
        "updates those fields that are not yet present (similar to dict.setdefault)"
        for key in kw:
            if not hasattr(self, key):
                setattr(self, key, kw[key])

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        self.__dict__.__delitem__(key)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        keys = self.__dict__.keys()
        items = ("{}={}".format(k, repr(self.__dict__[k])) for k in keys)
        return "{}({})".format(self.__class__.__name__, ", ".join(items))

    def __str__(self):
        keys = sorted(self.__dict__.keys())
        items = ("{}={}".format(k, repr(self.__dict__[k])) for k in keys)
        return "{}({})".format(self.__class__.__name__, ", ".join(items))

    def __eq__(self, other):
        # pylint: disable=unidiomatic-typecheck

        if type(self) != type(other):
            return False

        if len(self.__dict__) != len(other.__dict__):
            return False

        for key in self.__dict__:
            if not hasattr(other, key):
                return False
            self_value = getattr(self, key)
            other_value = getattr(other, key)

            if type(self_value) != type(other_value) or self_value != other_value:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(repr(self))


def range_contains_smaller(one: TextRange, other: TextRange) -> bool:
    this_start = (one.lineno, one.col_offset)
    this_end = (one.end_lineno, one.end_col_offset)
    other_start = (other.lineno, other.col_offset)
    other_end = (other.end_lineno, other.end_col_offset)

    return (
        this_start < other_start
        and this_end > other_end
        or this_start == other_start
        and this_end > other_end
        or this_start < other_start
        and this_end == other_end
    )


def range_contains_smaller_or_equal(one: TextRange, other: TextRange) -> bool:
    return range_contains_smaller(one, other) or one == other


class InputSubmission(Record):
    """For sending data to backend's stdin"""

    def __init__(self, data: str, **kw) -> None:
        super().__init__(**kw)
        self.data = data


class CommandToBackend(Record):
    """Command meant for the back-end"""

    def __init__(self, name: str, **kw) -> None:
        super().__init__(**kw)
        self.name = name


class ImmediateCommand(CommandToBackend):
    pass


class EOFCommand(CommandToBackend):
    def __init__(self, **kw) -> None:
        if "name" in kw:
            del kw["name"]
        super().__init__("eof", **kw)


class ToplevelCommand(CommandToBackend):
    def __init__(self, name: str, argv: List[str] = [], **kw) -> None:
        super().__init__(name, **kw)
        self.argv = argv


class DebuggerCommand(CommandToBackend):
    pass


class InlineCommand(CommandToBackend):
    """
    Can be used both during debugging and in waiting_toplevel_command state
    (eg. for sending variable and heap info requests)
    """

    pass


class MessageFromBackend(Record):
    def __init__(self, **kw) -> None:
        self.event_type = type(self).__name__  # allow event_type to be overridden by kw
        super().__init__(**kw)
        if not hasattr(self, "sequence"):
            self.sequence = self.event_type


class ToplevelResponse(MessageFromBackend):
    pass


class DebuggerResponse(MessageFromBackend):
    pass


class BackendEvent(MessageFromBackend):
    def __init__(self, event_type: str, **kw) -> None:
        super().__init__(**kw)
        self.event_type = event_type


class OscEvent(BackendEvent):
    def __init__(self, text: str):
        self.text = text
        super().__init__("OscEvent")

    def __repr__(self):
        return f"OscEvent({self.text!r})"


class InlineResponse(MessageFromBackend):
    def __init__(self, command_name: str, **kw) -> None:
        super().__init__(**kw)
        self.command_name = command_name
        self.event_type = self.command_name + "_response"


def serialize_message(msg: Record, max_line_length=65536) -> str:
    # I want to transfer only ASCII chars because encodings are not reliable
    # (eg. can't find a way to specify PYTHONIOENCODING for cx_freeze'd program)
    # The possibility for splitting message into several lines is required because of
    # default (safe) window size in Paramiko (https://github.com/thonny/thonny/issues/1680)
    msg_str = ascii(msg)

    lines = []
    for i in range(0, len(msg_str), max_line_length):
        lines.append(msg_str[i : i + max_line_length])

    return MESSAGE_MARKER + str(len(lines)) + " " + "\n".join(lines)


def parse_message(msg_string: str) -> Record:
    # DataFrames may have nan
    # pylint: disable=unused-variable
    nan = float("nan")  # @UnusedVariable
    assert msg_string[0] == MESSAGE_MARKER
    assert msg_string.strip().endswith(")")
    msg_start = msg_string.index(" ")
    line_count = int(msg_string[1:msg_start])
    assert line_count == msg_string.strip().count("\n") + 1
    return eval(msg_string[msg_start:].replace("\n", ""))


def normpath_with_actual_case(name: str) -> str:
    """In Windows return the path with the case it is stored in the filesystem"""
    if not os.path.exists(name):
        return os.path.normpath(name)

    if os.name == "nt":
        try:
            # https://stackoverflow.com/questions/2113822/python-getting-filename-case-as-stored-in-windows/2114975
            norm_name = os.path.normpath(name)

            from ctypes import create_unicode_buffer, windll

            buf = create_unicode_buffer(512)
            # GetLongPathNameW alone doesn't fix filename part
            windll.kernel32.GetShortPathNameW(norm_name, buf, 512)  # @UndefinedVariable
            windll.kernel32.GetLongPathNameW(buf.value, buf, 512)  # @UndefinedVariable
            result = buf.value

            if result.casefold() != norm_name.casefold():
                # Sometimes GetShortPathNameW + GetLongPathNameW doesn't work
                # see eg. https://github.com/thonny/thonny/issues/925
                windll.kernel32.GetLongPathNameW(norm_name, buf, 512)  # @UndefinedVariable
                result = buf.value

                if result.casefold() != norm_name.casefold():
                    result = norm_name

            if result[1] == ":":
                # ensure drive letter is capital
                return result[0].upper() + result[1:]
            else:
                return result
        except Exception:
            logger.warning(
                "Could not compute normpath_with_actual_case for %r", name, exc_info=True
            )
            return os.path.normpath(name)
    else:
        # easy on Linux
        # too difficult on mac
        # https://stackoverflow.com/questions/14515073/in-python-on-osx-with-hfs-how-can-i-get-the-correct-case-of-an-existing-filenam
        # Hopefully only correct case comes into Thonny (eg. via open dialog)
        return os.path.normpath(name)


def is_same_path(name1: str, name2: str) -> bool:
    return os.path.normpath(os.path.normcase(name1)) == os.path.normpath(os.path.normcase(name2))


def path_startswith(child_name: str, dir_name: str) -> bool:
    normchild = os.path.normpath(os.path.normcase(child_name))
    normdir = os.path.normpath(os.path.normcase(dir_name))
    return normdir == normchild or normchild.startswith(normdir.rstrip(os.path.sep) + os.path.sep)


def read_source(filename):
    import tokenize

    with tokenize.open(filename) as fp:
        return fp.read()


def get_exe_dirs():
    result = []
    if site.ENABLE_USER_SITE:
        if sys.platform == "win32":
            if site.getusersitepackages():
                result.append(site.getusersitepackages().replace("site-packages", "Scripts"))
        else:
            if site.getuserbase():
                result.append(site.getuserbase() + "/bin")

    main_scripts = os.path.join(sys.prefix, "Scripts")
    if os.path.isdir(main_scripts) and main_scripts not in result:
        result.append(main_scripts)

    if os.path.dirname(sys.executable) not in result:
        result.append(os.path.dirname(sys.executable))

    # These entries are used by Anaconda
    for part in [
        "Library/mingw-w64/bin",
        "Library/usr/bin",
        "Library/bin",
        "Scripts",
        "bin",
        "condabin",
    ]:
        dirpath = os.path.join(sys.prefix, part.replace("/", os.sep))
        if os.path.isdir(dirpath) and dirpath not in result:
            result.append(dirpath)

    if sys.platform != "win32" and "/usr/local/bin" not in result:
        # May be missing on macOS, when started as bundle
        # (yes, more may be missing, but this one is most useful)
        result.append("/usr/local/bin")

    return result


def get_site_dir(symbolic_name, executable=None):
    if not executable or executable == sys.executable:
        result = getattr(site, symbolic_name, "")
    else:
        import subprocess

        result = (
            subprocess.check_output(
                [executable, "-m", "site", "--" + symbolic_name.lower().replace("_", "-")],
                universal_newlines=True,
            )
            .decode()
            .strip()
        )

    return result if result else None


def get_base_executable():
    if sys.exec_prefix == sys.base_exec_prefix:
        return sys.executable

    if sys.platform == "win32":
        guess = sys.base_exec_prefix + "\\" + os.path.basename(sys.executable)
        if os.path.isfile(guess):
            return normpath_with_actual_case(guess)

    if os.path.islink(sys.executable):
        return os.path.realpath(sys.executable)

    raise RuntimeError("Don't know how to locate base executable")


def get_augmented_system_path(extra_dirs):
    path_items = os.environ.get("PATH", "").split(os.pathsep)

    for d in reversed(extra_dirs):
        if d not in path_items:
            path_items.insert(0, d)

    return os.pathsep.join(path_items)


def update_system_path(env, value):
    # in Windows, env keys are not case sensitive
    # this is important if env is a dict (not os.environ)
    if sys.platform == "win32":
        found = False
        for key in env:
            if key.upper() == "PATH":
                found = True
                env[key] = value

        if not found:
            env["PATH"] = value
    else:
        env["PATH"] = value


@dataclass
class SignatureParameter:
    kind: str
    name: str
    annotation: Optional[str]
    default: Optional[str]


@dataclass
class SignatureInfo:
    name: str
    params: List[SignatureParameter]
    return_type: Optional[str]
    current_param_index: Optional[int] = None
    call_bracket_start: Optional[Tuple[int, int]] = None


@dataclass
class CompletionInfo:
    name: str
    name_with_symbols: str
    full_name: str
    type: str
    prefix_length: int  # the number of chars to be deleted before inserting name
    signatures: Optional[List[SignatureInfo]]
    docstring: Optional[str]
    module_name: Optional[str]
    module_path: Optional[str]


@dataclass
class NameReference:
    module_name: str
    module_path: str
    row: int
    column: int
    length: int


class UserError(RuntimeError):
    """Errors of this class are meant to be presented without stacktrace"""

    pass


def is_hidden_or_system_file(path: str) -> bool:
    if os.path.basename(path).startswith("."):
        return True
    elif sys.platform == "win32":
        from ctypes import windll

        FILE_ATTRIBUTE_HIDDEN = 0x2
        FILE_ATTRIBUTE_SYSTEM = 0x4
        return bool(
            windll.kernel32.GetFileAttributesW(path)  # @UndefinedVariable
            & (FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM)
        )
    else:
        return False


def get_dirs_children_info(
    paths: List[str], include_hidden: bool = False
) -> Dict[str, Optional[Dict[str, Dict]]]:
    return {path: get_single_dir_child_data(path, include_hidden) for path in paths}


def get_single_dir_child_data(path: str, include_hidden: bool = False) -> Optional[Dict[str, Dict]]:
    if path == "":
        if sys.platform == "win32":
            return {**get_windows_volumes_info(), **get_windows_network_locations()}
        else:
            return get_single_dir_child_data("/", include_hidden)

    elif os.path.isdir(path) or os.path.ismount(path):
        result = {}

        try:
            for child in os.listdir(path):
                full_child_path = os.path.join(path, child)
                if not os.path.exists(full_child_path):
                    # must be broken link
                    continue
                full_child_path = normpath_with_actual_case(full_child_path)
                hidden = is_hidden_or_system_file(full_child_path)
                if not hidden or include_hidden:
                    name = os.path.basename(full_child_path)
                    st = os.stat(full_child_path, dir_fd=None, follow_symlinks=True)
                    result[name] = {
                        "size": None if os.path.isdir(full_child_path) else st.st_size,
                        "modified": st.st_mtime,
                        "hidden": hidden,
                    }
        except PermissionError:
            result["<not accessible>"] = {
                "kind": "error",
                "size": -1,
                "modified": None,
                "hidden": None,
            }

        return result
    else:
        return None


def get_windows_volumes_info():
    # http://stackoverflow.com/a/2288225/261181
    # http://msdn.microsoft.com/en-us/library/windows/desktop/aa364939%28v=vs.85%29.aspx
    import string
    from ctypes import windll

    all_drive_types = [
        "DRIVE_UNKNOWN",
        "DRIVE_NO_ROOT_DIR",
        "DRIVE_REMOVABLE",
        "DRIVE_FIXED",
        "DRIVE_REMOTE",
        "DRIVE_CDROM",
        "DRIVE_RAMDISK",
    ]

    required_drive_types = ["DRIVE_REMOVABLE", "DRIVE_FIXED", "DRIVE_REMOTE", "DRIVE_RAMDISK"]

    result = {}

    bitmask = windll.kernel32.GetLogicalDrives()  # @UndefinedVariable
    for letter in string.ascii_uppercase:
        if not bitmask & 1:
            pass
        else:
            drive_type = all_drive_types[
                windll.kernel32.GetDriveTypeW("%s:\\" % letter)
            ]  # @UndefinedVariable

            # NB! Drive A can be present in bitmask but actually missing.
            # In this case querying information about it would freeze the UI
            # for several seconds.
            # One solution is to uninstall the device in device manager,
            # but OS may restore the drive later.
            # Therefore it is safest to skip A drive (user can access it via Open dialog)

            if drive_type in required_drive_types and (
                letter != "A" or drive_type != "DRIVE_REMOVABLE"
            ):
                drive = letter + ":"
                path = drive + "\\"

                try:
                    st = os.stat(path)
                    volume_name = get_windows_volume_name(path)
                    if not volume_name:
                        volume_name = "Disk"

                    label = volume_name + " (" + drive + ")"
                    result[path] = {
                        "label": label,
                        "size": None,
                        "modified": max(st.st_mtime, st.st_ctime),
                    }
                except OSError as e:
                    logger.warning("Could not get information for %s", path, exc_info=e)

        bitmask >>= 1

    return result


def get_windows_volume_name(path):
    # https://stackoverflow.com/a/12056414/261181
    import ctypes

    kernel32 = ctypes.windll.kernel32
    volume_name_buffer = ctypes.create_unicode_buffer(1024)
    file_system_name_buffer = ctypes.create_unicode_buffer(1024)
    serial_number = None
    max_component_length = None
    file_system_flags = None

    result = kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(path),
        volume_name_buffer,
        ctypes.sizeof(volume_name_buffer),
        serial_number,
        max_component_length,
        file_system_flags,
        file_system_name_buffer,
        ctypes.sizeof(file_system_name_buffer),
    )

    if result:
        return volume_name_buffer.value
    else:
        return None


def get_windows_network_locations():
    import ctypes.wintypes

    CSIDL_NETHOOD = 0x13
    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_NETHOOD, 0, SHGFP_TYPE_CURRENT, buf)
    shortcuts_dir = buf.value
    if not buf.value:
        logger.warning("Could not determine windows shortcuts directory")
        return {}

    result = {}
    for entry in os.scandir(shortcuts_dir):
        # full_path = normpath_with_actual_case(entry.path)
        lnk_path = os.path.join(entry.path, "target.lnk")
        if os.path.exists(lnk_path):
            try:
                target = get_windows_lnk_target(lnk_path)
                result[target] = {
                    "label": entry.name + " (" + target + ")",
                    "size": None,
                    "modified": None,
                }
            except Exception:
                logger.error("Can't get target from %s", lnk_path, exc_info=True)

    return result


def get_windows_lnk_target(lnk_file_path):
    import subprocess

    import thonny

    script_path = os.path.join(os.path.dirname(thonny.__file__), "res", "PrintLnkTarget.vbs")
    cmd = ["cscript", "/NoLogo", script_path, lnk_file_path]
    result = subprocess.check_output(cmd, universal_newlines=True, timeout=3)

    return result.strip()


def execute_system_command(cmd, cwd=None, disconnect_stdin=False):
    import subprocess

    logger.debug("execute_system_command, cmd=%r, cwd=%s", cmd, cwd)
    env = dict(os.environ).copy()
    encoding = "utf-8"
    env["PYTHONIOENCODING"] = encoding
    # Make sure this python interpreter and its scripts are available
    # in PATH
    update_system_path(env, get_augmented_system_path(get_exe_dirs()))
    popen_kw = dict(
        env=env,
        universal_newlines=True,
        bufsize=0,
    )

    if cwd and os.path.isdir(cwd):
        popen_kw["cwd"] = cwd

    if disconnect_stdin:
        popen_kw["stdin"] = subprocess.DEVNULL

    if sys.version_info >= (3, 6):
        popen_kw["errors"] = "replace"
        popen_kw["encoding"] = encoding

    if isinstance(cmd.cmd_line, str) and cmd.cmd_line.startswith("!"):
        cmd_line = cmd.cmd_line[1:]
        popen_kw["shell"] = True
    else:
        assert isinstance(cmd.cmd_line, list)
        cmd_line = cmd.cmd_line
    logger.debug("Popen(%r, ...)", cmd_line)
    proc = subprocess.Popen(cmd_line, **popen_kw)
    proc.communicate()
    return proc.wait()


def universal_dirname(path: str) -> str:
    if "/" in path:
        sep = "/"
    elif "\\" in path:
        sep = "\\"
    else:
        # micro:bit
        return ""

    path = path.rstrip(sep)
    result = path[: path.rindex(sep)]
    if not result:
        return sep
    else:
        return result


def universal_relpath(path: str, context: str) -> str:
    """Tries to give relative path"""
    if "/" in path:
        import pathlib

        p = pathlib.PurePosixPath(path)
        try:
            return str(p.relative_to(context))
        except ValueError:
            return path
    else:
        return os.path.relpath(path, context)


def get_python_version_string():
    result = sys.version.split()[0]

    if sys.maxsize <= 2**32:
        result += ", 32-bit"

    return result


def execute_with_frontend_sys_path(function: Callable) -> Any:
    import ast

    try:
        frontend_sys_path = ast.literal_eval(os.environ["THONNY_FRONTEND_SYS_PATH"])
        assert isinstance(frontend_sys_path, list)
        logger.info("Using THONNY_FRONTEND_SYS_PATH %s", frontend_sys_path)
    except Exception as e:
        logger.debug("Could not get THONNY_FRONTEND_SYS_PATH", exc_info=e)
        frontend_sys_path = []

    extra_items = [item for item in frontend_sys_path if item not in sys.path]
    sys.path = sys.path + extra_items
    try:
        return function()
    finally:
        for item in extra_items:
            if item in sys.path:
                sys.path.remove(item)


def try_load_modules_with_frontend_sys_path(module_names):
    def load():
        from importlib import import_module

        for name in module_names:
            try:
                import_module(name)
            except ImportError:
                pass

    execute_with_frontend_sys_path(load)


def read_one_incoming_message_str(line_reader):
    msg_str = line_reader()

    if msg_str == "":
        return ""

    if not msg_str.startswith(MESSAGE_MARKER):
        return msg_str

    line_count = int(msg_str[1:].split(maxsplit=1)[0])
    read_lines = 1
    while read_lines < line_count:
        msg_str += line_reader()
        read_lines += 1

    return msg_str


def is_virtual_executable(executable):
    exe_dir = os.path.dirname(executable)
    return os.path.exists(os.path.join(exe_dir, "activate")) or os.path.exists(
        os.path.join(exe_dir, "activate.bat")
    )


def is_private_python(executable):
    result = os.path.exists(os.path.join(os.path.dirname(executable), "thonny_python.ini"))
    logger.debug("is_private_python(%r) == %r", executable, result)
    return result


def is_remote_path(s: str) -> bool:
    return REMOTE_PATH_MARKER in s


def is_local_path(s: str) -> bool:
    return not is_remote_path(s) and not s.startswith("<")
