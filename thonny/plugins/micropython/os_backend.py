from thonny.plugins.micropython.backend import MicroPythonBackend

FALLBACK_BUILTIN_MODULES = [
    "cmath",
    "gc",
    "math",
    "sys",
    "array",
    # "binascii", # don't include it, as it may give false signal for reader/writer
    "collections",
    "errno",
    "hashlib",
    "heapq",
    "io",
    "json",
    "os",
    "re",
    "select",
    "socket",
    "ssl",
    "struct",
    "time",
    "zlib",
    "_thread",
    "btree",
    "framebuf",
    "micropython",
    "network",
    "cryptolib",
    "ctypes",
]


class MicroPythonOsBackend(MicroPythonBackend):
    pass
