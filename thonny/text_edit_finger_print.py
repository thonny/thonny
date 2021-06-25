# -*- encoding: utf-8 -*-
"""
"""


import json
import base64
import gzip
import os
import re


# =======
# History
# =======

class TextEditOp:
    INSERT = 0
    DELETE = 1

class TextEditHistory:

    def __init__(self, initial_content=""):
        self.history = []
        if initial_content:
            self.insert((1, 0), initial_content)

    def insert(self, position: (int, int), chars: str):
        self.history.append((TextEditOp.INSERT, (position, chars)))

    def single_delete(self, position: (int, int)):
        next_position = (position[0], position[1] + 1)
        self.delete(position, next_position)

    def delete(self, start: (int, int), stop: (int, int)):
        self.history.append((TextEditOp.DELETE, (start, stop)))

def pretty_print_history(history):
    for op, args in history:
        if op == TextEditOp.INSERT:
            position, chars = args
            print(f"insert({position!r}, {chars!r})")
        elif op == TextEditOp.DELETE:
            start, stop = args
            print(f"delete({start!r}, {stop!r})")
        else:
            raise ValueError(f"unexpected edit operation: {op!r}")

def print_statistics(history, raw_data, compressed_data, encoded_data):
    print(f"history length = {len(history)}; "
          f"raw = {len(raw_data)}B; "
          f"compressed = {len(compressed_data)}B; "
          f"encoded = {len(encoded_data)}B")
    print(f"raw = {len(raw_data)/len(history):.2f}B/item; "
          f"compressed = {len(compressed_data)/len(history):.2f}B/item; "
          f"encoded = {len(encoded_data)/len(history):.2f}B/item")
    print(f"saved space : "
          f"compressed = {1-len(compressed_data)/len(raw_data):.2%}; "
          f"encoded = {1-len(encoded_data)/len(raw_data):.2%}")


# ===========
# Serializers
# ===========

class NaiveHistorySerializer:

    ENCODING = "utf-8"

    def serialize(self, history) -> str:
        self.history = history
        self.raw_data = json.dumps(self.history,
                                   indent=None, separators=(',', ':'))\
                            .encode(self.ENCODING)
        self.compressed_data = gzip.compress(self.raw_data)
        self.encoded_data = base64.b64encode(self.compressed_data)
        # Decode data using ascii encoding (ascii encoding must works since
        # we write finger print in base64), so that we can easily insert
        # the finger print in a str content instead of bytes. It is easier
        # for line separator handling and generation of the wrapping comment.
        return self.encoded_data.decode('ascii')

    def unserialize(self, data):
        self.encoded_data = data
        self.compressed_data = base64.b64decode(self.encoded_data)
        self.raw_data = gzip.decompress(self.compressed_data)
        self.history = json.loads(self.raw_data.decode(self.ENCODING))
        return self.history

    def print_statistics(self):
        print_statistics(self.history, self.raw_data,
                         self.compressed_data, self.encoded_data)

# TODO: Add a compact serializer if the principle of signing file with
#       edit history workout with students.
# The history should an utf-8 encoded string where:
# - a printable character (and \n) represents a single inserted character at
#   current position
# - a group separator (code: 29) begins a bulk insertion of characters ended by an EOT (code 4)
# - a backspace character (code: 8) is a deletion of previous character.
#   (a delete is replaced by a move followed by a backspace)
# - the DEL character (code: 127) for deleting region
# - a XON (code: 17) is a short move and is followed
#   two bytes (line, column) is a relative move of the cursor.
# See explaination of ASCII control character:
#  https://www.lammertbies.nl/comm/info/ascii-characters

# =============================
# Integration into file content
# =============================

# Serializers sorted by version.
_SERIALIZERS = (
    NaiveHistorySerializer,
)


class FingerPrintError(Exception):
    pass

class InvalidFingerPrintVersion(FingerPrintError):

    def __init__(self, version, message=None):
        self.version = version
        self.message = message

    def __str__(self):
        if self.message is None:
            return f"invalid finger print version: {self.version!r}"
        else:
            return self.message

def get_serializer_class_by_version(version):
    if not isinstance(version, int):
        raise InvalidFingerPrintVersion(version,
                                        "version must be int, not {}"
                                        .format(type(version).__name__))
    if version <= 0:
        raise InvalidFingerPrintVersion(
            version,
            f"version number must be positive (not {version})")

    try:
        return _SERIALIZERS[version-1]
    except IndexError:
        raise InvalidFingerPrintVersion(version,
                                        f"unsupported version: {version}")

def split_data(data, chunk_size):
    """Yield chunk of size +chunk_size+ of the data +data+."""

    if not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be int, not {}"
                        .format(type(chunk_size).__name__))
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive (not {})"
                         .format(chunk_size))

    for i in range(0, len(data), chunk_size):
        yield data[i:i+chunk_size]


_TAG = "-*-"
_STARTER = "#fp "

def insert_finger_print(content: str, history, version=1, newline=os.linesep,
                        chunk_size=160):
    """Insert the finger print into the content of a file.
    """
    # TODO: assert that the history matches the content_bytes by simulating edition
    serializer_class = get_serializer_class_by_version(version)
    serializer = serializer_class()
    header = dict(version=version)
    data = newline*2 + _STARTER + f"{_TAG} finger print begin: {json.dumps(header)} {_TAG}"
    finger_print = serializer.serialize(history)
    delimiter = newline + _STARTER
    data += delimiter + delimiter.join(split_data(finger_print, chunks_size))
    data += delimiter + f"{_TAG} finger print end {_TAG}" + newline
    return content + data

_re_vars = {'st': re.escape(_STARTER), 'tag': re.escape(_TAG)}
_FP_BEGIN = re.compile(
    r"^%(st)s%(tag)s finger print begin: (?P<header>.*?) %(tag)s$" % _re_vars,
    re.MULTILINE)
_FP_CHUNK = re.compile(
    r"^%(st)s(?P<chunk>[a-zA-Z0-9+/=]+)$" % _re_vars,
    re.MULTILINE)
_FP_END = re.compile(
    r"^%(st)s%(tag)s finger print end %(tag)s$" % _re_vars,
    re.MULTILINE)

class FingerPrintTainted(FingerPrintError):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def extract_finger_print(content: str):
    mo = _FP_BEGIN.search(content)
    if mo is None:
        # No finger print found, return the content unmodified,
        # and an empty history
        return content, [], None
    start_pos = mo.start()

    header_data = mo.group("header")
    try:
        header = json.loads(header_data)
    except JSONDecodeError as e:
        raise FingerPrintTainted(f"invalid header - {e.msg} (doc: {e.doc})")
    version = header.get("version", 1)
    serializer_class = get_serializer_class_by_version(version)
    serializer = serializer_class()

    chunks = []
    while True:
        pos = mo.end()
        mo = _FP_CHUNK.search(content, pos)
        if mo is None:
            break
        if mo.start() - pos > 2:
            raise FingerPrintTainted("non-contiguous finger print")
        chunks.append(mo.group("chunk"))

    mo = _FP_END.search(content, pos)
    if mo is None:
        raise FingerPrintTainted("cannot find the end of the finger print")
    if mo.start() - pos > 2:
        raise FingerPrintTainted("non-contiguous finger print end marker")
    end_pos = mo.end()

    finger_print = "".join(chunks)
    history = serializer.unserialize(finger_print)

    # minus 2 to eat the two newlines inserted before the finger print
    cleaned_content = content[:start_pos-2] + content[end_pos:]

    return cleaned_content, history, serializer


if __name__ == "__main__":

    import sys
    import argparse

    def readall(filepath, **kwargs):
        """Read all the content of `filepath` and return it."""
        with open(filepath, **kwargs) as f:
            return f.read()

    def build_cli():
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument(
            "--stat",
            action="store_true",
            default=False,
            help="Whether to print statistics along with history.")
        parser.add_argument(
            "path",
            action="store",
            help="Path to the file to read the finger print from.")
        return parser

    def main(argv):
        cli = build_cli()
        options = cli.parse_args(argv[1:])
        content = readall(options.path)
        new_content, history, serializer = extract_finger_print(content)
        pretty_print_history(history)
        if options.stat:
            print("---")
            serializer.print_statistics()
        return 0

    sys.exit(main(sys.argv))
