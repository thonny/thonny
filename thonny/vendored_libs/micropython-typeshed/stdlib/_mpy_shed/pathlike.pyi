"""
pathlike is used in multiple stdlib stubs - but does not exists in MicroPython
copied from typeshed/stdlib/os.pyi as os.pyi cannot import from a module with the same name
"""

import abc
from typing import Protocol, Tuple, runtime_checkable

from _typeshed import AnyStr_co

# mypy and pyright object to this being both ABC and Protocol.
# At runtime it inherits from ABC and is not a Protocol, but it will be
# on the allowlist for use as a Protocol starting in 3.14.
@runtime_checkable
class PathLike(ABC, Protocol[AnyStr_co]):  # type: ignore[misc]  # pyright: ignore[reportGeneralTypeIssues]
    @abc.abstractmethod
    def __fspath__(self) -> AnyStr_co: ...
