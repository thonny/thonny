"""
Simple BTree database.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/btree.html

The ``btree`` module implements a simple key-value database using external
storage (disk files, or in general case, a random-access `stream`). Keys are
stored sorted in the database, and besides efficient retrieval by a key
value, a database also supports efficient ordered range scans (retrieval
of values with the keys in a given range). On the application interface
side, BTree database work as close a possible to a way standard `dict`
type works, one notable difference is that both keys and values must
be `bytes`-like objects (so, if you want to store objects of other types, you
need to first serialize them to `str` or `bytes` or another type that supports
the buffer protocol).

The module is based on the well-known BerkelyDB library, version 1.xx.

Example::

    import btree

    # First, we need to open a stream which holds a database
    # This is usually a file, but can be in-memory database
    # using io.BytesIO, a raw flash partition, etc.
    # Oftentimes, you want to create a database file if it doesn't
    # exist and open if it exists. Idiom below takes care of this.
    # DO NOT open database with "a+b" access mode.
    try:
        f = open("mydb", "r+b")
    except OSError:
        f = open("mydb", "w+b")

    # Now open a database itself
    db = btree.open(f)

    # The keys you add will be sorted internally in the database
    db[b"3"] = b"three"
    db[b"1"] = b"one"
    db[b"2"] = b"two"

    # Assume that any changes are cached in memory unless
    # explicitly flushed (or database closed). Flush database
    # at the end of each "transaction".
    db.flush()

    # Prints b'two'
    print(db[b"2"])

    # Iterate over sorted keys in the database, starting from b"2"
    # until the end of the database, returning only values.
    # Mind that arguments passed to values() method are *key* values.
    # Prints:
    #   b'two'
    #   b'three'
    for word in db.values(b"2"):
        print(word)

    del db[b"2"]

    # No longer true, prints False
    print(b"2" in db)

    # Prints:
    #  b"1"
    #  b"3"
    for key in db:
        print(key)

    db.close()

    # Don't forget to close the underlying stream!
    f.close()

---
Module: 'btree' on micropython-v1.25.0-esp32-ESP32_GENERIC-SPIRAM
"""

# MCU: {'variant': 'SPIRAM', 'build': '', 'arch': 'xtensawin', 'port': 'esp32', 'board': 'ESP32_GENERIC', 'board_id': 'ESP32_GENERIC-SPIRAM', 'mpy': 'v6.3', 'ver': '1.25.0', 'family': 'micropython', 'cpu': 'ESP32', 'version': '1.25.0'}
# Stubber: v1.25.0
from __future__ import annotations
from typing import Dict, Iterable, Final
from _typeshed import Incomplete
from _mpy_shed import IOBase_mp
from typing_extensions import Awaitable, TypeAlias, TypeVar

DESC: Final[int] = 2
INCL: Final[int] = 1

def open(
    stream: IOBase_mp,  # [bytes, Any],
    /,
    *,
    flags: int = 0,
    pagesize: int = 0,
    cachesize: int = 0,
    minkeypage: int = 0,
) -> Dict:
    """
    Open a database from a random-access `stream` (like an open file). All
    other parameters are optional and keyword-only, and allow to tweak advanced
    parameters of the database operation (most users will not need them):

    * *flags* - Currently unused.
    * *pagesize* - Page size used for the nodes in BTree. Acceptable range
      is 512-65536. If 0, a port-specific default will be used, optimized for
      port's memory usage and/or performance.
    * *cachesize* - Suggested memory cache size in bytes. For a
      board with enough memory using larger values may improve performance.
      Cache policy is as follows: entire cache is not allocated at once;
      instead, accessing a new page in database will allocate a memory buffer
      for it, until value specified by *cachesize* is reached. Then, these
      buffers will be managed using LRU (least recently used) policy. More
      buffers may still be allocated if needed (e.g., if a database contains
      big keys and/or values). Allocated cache buffers aren't reclaimed.
    * *minkeypage* - Minimum number of keys to store per page. Default value
      of 0 equivalent to 2.

    Returns a BTree object, which implements a dictionary protocol (set
    of methods), and some additional methods described below.
    """
    ...
