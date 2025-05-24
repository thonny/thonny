"""
IRQ object types, used in the machine, bluetooth, _rp2 and rp2 modules

_IRQ  is a union of the types _IRQ_ESP32, _IRQ_RP2 and _IRQ_PYB 
to allow the same stubs to support of the different ports of MicroPython.

"""

from typing import Type

from _typeshed import Incomplete
from typing_extensions import TypeAlias

class _IRQ_ESP32:
    def trigger(self) -> int: ...
    # def flags(self) -> int: ...

class _IRQ_RP2:
    # rp2040
    # object <irq> is of type irq
    #   flags -- <function>
    #   trigger -- <function>
    def flags(self) -> int: ...
    def trigger(self) -> int: ...

# pybv11
# TODO: Not sure what the correct implementation is
# NoneType
_IRQ_PYB: TypeAlias = None

_IRQ: TypeAlias = Type[_IRQ_ESP32] | Type[_IRQ_RP2] | Type[_IRQ_PYB] | Incomplete
