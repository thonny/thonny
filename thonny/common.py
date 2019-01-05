# -*- coding: utf-8 -*-

"""
Classes used both by front-end and back-end
"""
import logging
import os.path
import platform
import site
import sys
import tokenize
from collections import namedtuple
from typing import List, Optional  # @UnusedImport
import subprocess

MESSAGE_MARKER = "\x02"

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

TextRange = namedtuple(
    "TextRange", ["lineno", "col_offset", "end_lineno", "end_col_offset"]
)


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
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(self.__class__.__name__, ", ".join(items))

    def __str__(self):
        keys = sorted(self.__dict__.keys())
        items = ("{}={!r}".format(k, str(self.__dict__[k])) for k in keys)
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


class InlineResponse(MessageFromBackend):
    def __init__(self, command_name: str, **kw) -> None:
        super().__init__(**kw)
        self.command_name = command_name
        self.event_type = self.command_name + "_response"


def serialize_message(msg: Record) -> str:
    # I want to transfer only ASCII chars because encodings are not reliable
    # (eg. can't find a way to specify PYTHONIOENCODING for cx_freeze'd program)
    return MESSAGE_MARKER + repr(msg).encode("UTF-7").decode("ASCII")


def parse_message(msg_string: str) -> Record:
    # DataFrames may have nan
    # pylint: disable=unused-variable
    nan = float("nan")  # @UnusedVariable
    assert msg_string[0] == MESSAGE_MARKER
    return eval(msg_string[1:].encode("ASCII").decode("UTF-7"))


def normpath_with_actual_case(name: str) -> str:
    """In Windows return the path with the case it is stored in the filesystem"""
    assert os.path.isabs(name)
    assert os.path.exists(name)

    if os.name == "nt":
        name = os.path.realpath(name)

        from ctypes import create_unicode_buffer, windll

        buf = create_unicode_buffer(512)
        windll.kernel32.GetShortPathNameW(name, buf, 512)  # @UndefinedVariable
        windll.kernel32.GetLongPathNameW(buf.value, buf, 512)  # @UndefinedVariable
        assert len(buf.value) >= 2

        result = buf.value
        assert isinstance(result, str)

        if result[1] == ":":
            # ensure drive letter is capital
            return result[0].upper() + result[1:]
        else:
            return result
    else:
        return os.path.normpath(name)


def is_same_path(name1: str, name2: str) -> bool:
    return os.path.normpath(os.path.normcase(name1)) == os.path.normpath(
        os.path.normcase(name2)
    )


def path_startswith(child_name: str, dir_name: str) -> bool:
    normchild = os.path.normpath(os.path.normcase(child_name))
    normdir = os.path.normpath(os.path.normcase(dir_name))
    return normdir == normchild or normchild.startswith(
        normdir.rstrip(os.path.sep) + os.path.sep
    )


def read_source(filename):
    with tokenize.open(filename) as fp:
        return fp.read()


def get_exe_dirs():
    result = []
    if site.ENABLE_USER_SITE:
        if platform.system() == "Windows":
            if site.getusersitepackages():
                result.append(site.getusersitepackages()
                              .replace("site-packages", "Scripts"))
        else:
            if site.getuserbase():
                result.append(site.getuserbase() + "/bin")
    
    main_scripts = os.path.join(sys.prefix, "Scripts")
    if os.path.isdir(main_scripts) and main_scripts not in result:
        result.append(main_scripts)
    
    if os.path.dirname(sys.executable) not in result:
        result.append(os.path.dirname(sys.executable))
    
    return result

def get_site_dir(symbolic_name, executable=None):
    if not executable or executable == sys.executable:
        result = getattr(site, symbolic_name, "")
    else:
        result = subprocess.check_output(
            [executable, '-m', 'site', 
                '--' + symbolic_name.lower().replace("_", "-")],
            universal_newlines=True
        ).decode().strip()
    
    return result if result else None

def get_base_executable():
    if sys.exec_prefix == sys.base_exec_prefix:
        return sys.executable
    
    if platform.system() == "Windows":
        result = sys.base_exec_prefix + "\\" + os.path.basename(sys.executable)
        result = normpath_with_actual_case(result)
    else:
        result = sys.executable.replace(sys.exec_prefix, sys.base_exec_prefix)
    
    if not os.path.isfile(result):
        raise RuntimeError("Can't locate base executable")
    
    return result

def get_augmented_system_path(extra_dirs):
    path_items = os.environ.get("PATH", "").split(os.pathsep)
    
    for d in reversed(extra_dirs):
        if d not in path_items:
            path_items.insert(0, d)
    
    return os.pathsep.join(path_items)

def update_system_path(env, value):
    # in Windows, env keys are not case sensitive
    # this is important if env is a dict (not os.environ)
    if platform.system() == "Windows":
        found = False
        for key in env:
            if key.upper() == "PATH":
                found = True
                env[key] = value
        
        if not found:
            env["PATH"] = value
    else:
        env["PATH"] = value

class UserError(RuntimeError):
    """Errors of this class are meant to be presented without stacktrace"""

    pass

