"""
collection and container types.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/collections.rst.
====================================================

.. module:: collections
   :synopsis: collection and container types

|see_cpython_module| :mod:`python:collections`.

This module implements advanced collection and container types to
hold/accumulate various objects.
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from typing import overload, Any, Type, Iterable, TypeVar, Generic, Mapping, Dict, Final

_KT: Final = TypeVar("_KT")
_VT: Final = TypeVar("_VT")

def namedtuple(name: str, fields: str | Iterable[str]) -> Type[tuple[Any, ...]]:
    """
    This is factory function to create a new namedtuple type with a specific
    name and set of fields. A namedtuple is a subclass of tuple which allows
    to access its fields not just by numeric index, but also with an attribute
    access syntax using symbolic field names. Fields is a sequence of strings
    specifying field names. For compatibility with CPython it can also be a
    a string with space-separated field named (but this is less efficient).
    Example of use::
    
        from collections import namedtuple
    
        MyTuple = namedtuple("MyTuple", ("id", "name"))
        t1 = MyTuple(1, "foo")
        t2 = MyTuple(2, "bar")
        print(t1.name)
        assert t2.name == t2[1]
   """

# noinspection PyPep8Naming
class deque:
    """
Minimal implementation of a deque that implements a FIFO buffer.
   """

    def __init__(self, iterable: tuple[Any], maxlen: int, flags: int = 0, /):
        """
       Deques (double-ended queues) are a list-like container that support O(1)
       appends and pops from either side of the deque.  New deques are created
       using the following arguments:
       
           - *iterable* must be the empty tuple, and the new deque is created empty.
       
           - *maxlen* must be specified and the deque will be bounded to this
             maximum length.  Once the deque is full, any new items added will
             discard items from the opposite end.
       
           - The optional *flags* can be 1 to check for overflow when adding items.
      """
    def __bool__(self) -> bool:
        """
      Returns true if the `deque` isn't empty.
      
      **Note:** The method isn't listed by ``dir(deque)`` and can't be called directly, 
      however ``bool(deque)`` and automatic conversion work!
      """
    def __len__(self) -> int:
        """
      Returns the number of items in the `deque`.
      
      **Note:** The method isn't listed by ``dir(deque)`` and can't be called directly, 
      however ``len(deque)`` works!
      """
    def append(self, x: Any, /) -> None:
        """
           Add *x* to the right side of the deque.
           Raises IndexError if overflow checking is enabled and there is no more room left.
      """
    def popleft(self) -> Any:
        """
           Remove and return an item from the left side of the deque.
           Raises IndexError if no items are present.
      """

class OrderedDict(Dict[_KT, _VT], Generic[_KT, _VT]):
    """
W
h
e
n
 
o
r
d
e
r
e
d
 
d
i
c
t
 
i
s
 
i
t
e
r
a
t
e
d
 
o
v
e
r
,
 
k
e
y
s
/
i
t
e
m
s
 
a
r
e
 
r
e
t
u
r
n
e
d
 
i
n
 
t
h
e
 
o
r
d
e
r
 
t
h
e
y
 
w
e
r
e
 
a
d
d
e
d
.
   """

    @overload
    def __init__(self):
        """
       ``dict`` type subclass which remembers and preserves the order of keys
       added. When ordered dict is iterated over, keys/items are returned in
       the order they were added::
       
           from collections import OrderedDict
       
           # To make benefit of ordered keys, OrderedDict should be initialized
           # from sequence of (key, value) pairs.
           d = OrderedDict([("z", 1), ("a", 2)])
           # More items can be added as usual
           d["w"] = 5
           d["b"] = 3
           for k, v in d.items():
               print(k, v)
       
       Output::
       
           z 1
           a 2
           w 5
           b 3
      """
    @overload
    def __init__(self, **kwargs: _VT):
        """
       ``dict`` type subclass which remembers and preserves the order of keys
       added. When ordered dict is iterated over, keys/items are returned in
       the order they were added::
       
           from collections import OrderedDict
       
           # To make benefit of ordered keys, OrderedDict should be initialized
           # from sequence of (key, value) pairs.
           d = OrderedDict([("z", 1), ("a", 2)])
           # More items can be added as usual
           d["w"] = 5
           d["b"] = 3
           for k, v in d.items():
               print(k, v)
       
       Output::
       
           z 1
           a 2
           w 5
           b 3
      """
    @overload
    def __init__(self, map: Mapping[_KT, _VT], **kwargs: _VT):
        """
       ``dict`` type subclass which remembers and preserves the order of keys
       added. When ordered dict is iterated over, keys/items are returned in
       the order they were added::
       
           from collections import OrderedDict
       
           # To make benefit of ordered keys, OrderedDict should be initialized
           # from sequence of (key, value) pairs.
           d = OrderedDict([("z", 1), ("a", 2)])
           # More items can be added as usual
           d["w"] = 5
           d["b"] = 3
           for k, v in d.items():
               print(k, v)
       
       Output::
       
           z 1
           a 2
           w 5
           b 3
      """
