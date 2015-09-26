# -*- coding: utf-8 -*-

"""
Mostly Encoding related stuff copied from Py 3.3.1 library, because Py 2.7 doesn't have it.
TODO: Don't need Py 2.7 anymore
"""

import re
import io
import os.path
import builtins
import tkinter as tk
import tkinter.messagebox as tkMessageBox

from codecs import lookup, BOM_UTF8
import textwrap
import traceback


class PathSet:
    "implementation of set whose in operator works well for filenames"
    def __init__(self):
        self._normcase_set = set()
        
    def add(self, name):
        self._normcase_set.add(os.path.normcase(name))
    
    def remove(self, name):
        self._normcase_set.remove(os.path.normcase(name))
    
    def clear(self):
        self._normcase_set.clear()
    
    def __contains__(self, name):
        return os.path.normcase(name) in self._normcase_set

    def __iter__(self):
        for item in self._normcase_set:
            yield item

cookie_re = re.compile("coding[:=]\s*([-\w.]+)")

def eqfn(name1, name2):
    return os.path.normcase(name1) == os.path.normcase(name2)

def detect_encoding(readline):
    """
    The detect_encoding() function is used to detect the encoding that should
    be used to decode a Python source file.  It requires one argment, readline,
    in the same way as the tokenize() generator.

    It will call readline a maximum of twice, and return the encoding used
    (as a string) and a list of any lines (left as bytes) it has read in.

    It detects the encoding from the presence of a utf-8 bom or an encoding
    cookie as specified in pep-0263.  If both a bom and a cookie are present,
    but disagree, a SyntaxError will be raised.  If the encoding cookie is an
    invalid charset, raise a SyntaxError.  Note that if a utf-8 bom is found,
    'utf-8-sig' is returned.

    If no encoding is specified, then the default of 'utf-8' will be returned.
    TODO: Python 2 and 3 have different defaults
    """
    try:
        filename = readline.__self__.name
    except AttributeError:
        filename = None
    bom_found = False
    default = 'utf-8'
    def read_or_stop():
        try:
            return readline()
        except StopIteration:
            return b''

    def find_cookie(line):
        try:
            # Decode as UTF-8. Either the line is an encoding declaration,
            # in which case it should be pure ASCII, or it must be UTF-8
            # per default encoding.
            line_string = line.decode('utf-8')
        except UnicodeDecodeError:
            msg = "invalid or missing encoding declaration"
            if filename is not None:
                msg = '{} for {!r}'.format(msg, filename)
            raise SyntaxError(msg)

        matches = cookie_re.findall(line_string)
        if not matches:
            return None
        encoding = _get_normal_name(matches[0])
        try:
            _codec = lookup(encoding)
        except LookupError:
            # This behaviour mimics the Python interpreter
            if filename is None:
                msg = "unknown encoding: " + encoding
            else:
                msg = "unknown encoding for {!r}: {}".format(filename,
                        encoding)
            raise SyntaxError(msg)

        if bom_found:
            if encoding != 'utf-8':
                # This behaviour mimics the Python interpreter
                if filename is None:
                    msg = 'encoding problem: utf-8'
                else:
                    msg = 'encoding problem for {!r}: utf-8'.format(filename)
                raise SyntaxError(msg)
            encoding += '-sig'
        return encoding

    first = read_or_stop()
    if first.startswith(BOM_UTF8):
        bom_found = True
        first = first[3:]
        default = 'utf-8-sig'
    if not first:
        return default, []

    encoding = find_cookie(first)
    if encoding:
        return encoding, [first]

    second = read_or_stop()
    if not second:
        return default, [first]

    encoding = find_cookie(second)
    if encoding:
        return encoding, [first, second]

    return default, [first, second]

def _get_normal_name(orig_enc):
    """Imitates get_normal_name in tokenizer.c."""
    # Only care about the first 12 characters.
    enc = orig_enc[:12].lower().replace("_", "-")
    if enc == "utf-8" or enc.startswith("utf-8-"):
        return "utf-8"
    if enc in ("latin-1", "iso-8859-1", "iso-latin-1") or \
       enc.startswith(("latin-1-", "iso-8859-1-", "iso-latin-1-")):
        return "iso-8859-1"
    return orig_enc


def read_python_file(filename):
    fp = None
    try:
        fp, encoding = open_py_file(filename)
        return fp.read(), encoding
    finally:
        if fp is not None:
            fp.close()
    
def open_py_file(filename):
    """Open a file in read only mode using the encoding detected by
    detect_encoding().
    TODO: Python 2 and 3 have different defaults
    """
    buffer = builtins.open(filename, 'rb')
    encoding, _ = detect_encoding(buffer.readline)
    buffer.seek(0)
    content = io.BytesIO(buffer.read())
    buffer.close()
    text = io.TextIOWrapper(content, encoding, line_buffering=True)
    text.mode = 'r'
    return text, encoding

def running_on_windows():
    return tk._default_root.call('tk', 'windowingsystem') == "win32"
    
def running_on_mac_os():
    return tk._default_root.call('tk', 'windowingsystem') == "aqua"
    
def running_on_linux():
    return tk._default_root.call('tk', 'windowingsystem') == "x11"

def is_hidden_or_system_file(path):
    if os.path.basename(path).startswith("."):
        return True
    elif running_on_windows():
        from ctypes import windll
        FILE_ATTRIBUTE_HIDDEN = 0x2
        FILE_ATTRIBUTE_SYSTEM = 0x4
        return bool(windll.kernel32.GetFileAttributesW(path)  # @UndefinedVariable
                & (FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM))
    else:
        return False 
    
def get_win_drives():
    # http://stackoverflow.com/a/2288225/261181
    # http://msdn.microsoft.com/en-us/library/windows/desktop/aa364939%28v=vs.85%29.aspx
    import string
    from ctypes import windll
    
    all_drive_types = ['DRIVE_UNKNOWN', 
                       'DRIVE_NO_ROOT_DIR',
                       'DRIVE_REMOVABLE',
                       'DRIVE_FIXED',
                       'DRIVE_REMOTE',
                       'DRIVE_CDROM',
                       'DRIVE_RAMDISK']
    
    required_drive_types = ['DRIVE_REMOVABLE',
                            'DRIVE_FIXED',
                            'DRIVE_REMOTE',
                            'DRIVE_RAMDISK']

    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()  # @UndefinedVariable
    for letter in string.ascii_uppercase:
        drive_type = all_drive_types[windll.kernel32.GetDriveTypeW("%s:\\" % letter)]  # @UndefinedVariable
        if bitmask & 1 and drive_type in required_drive_types:
            drives.append(letter + ":\\")
        bitmask >>= 1

    return drives



def has_line_numbers(text):
    lines = text.splitlines()
    return (len(lines) > 2 
            and all([len(split_after_line_number(line)) == 2 for line in lines]))

def split_after_line_number(s): 
    parts = re.split("(^\s*\d+\.?)", s)
    if len(parts) == 1:
        return parts
    else:
        assert len(parts) == 3 and parts[0] == ''
        return parts[1:]

def remove_line_numbers(s):
    cleaned_lines = []
    for line in s.splitlines():
        parts = split_after_line_number(line)
        if len(parts) != 2:
            return s
        else:
            cleaned_lines.append(parts[1])
    
    return textwrap.dedent(("\n".join(cleaned_lines)) + "\n")
    
    
def try_remove_linenumbers(text, master):
    try:        
        if has_line_numbers(text) and tkMessageBox.askyesno (
                  title="Remove linenumbers",
                  message="Do you want to remove linenumbers from pasted text?",
                  default=tkMessageBox.YES,
                  master=master):
            return remove_line_numbers(text)
        else:
            return text
    except:
        traceback.print_exc()
        return text

def shorten_repr(original_repr, max_len=1000):
    if len(original_repr) > max_len:
        return original_repr[:max_len] + " ... [{} chars truncated]".format(len(original_repr) - max_len)
    else:
        return original_repr
        
