"""
Mostly Encoding related stuff copied from Py 3.3.1 library, because Py 2.7 doesn't have it.
"""

import re
import io
import os.path
from codecs import lookup, BOM_UTF8
import builtins
import tkinter as tk


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
        if fp != None:
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

