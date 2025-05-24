from typing import Protocol, TypeVar, runtime_checkable

_T_Co = TypeVar("_T_Co", covariant=True)

@runtime_checkable
class Subscriptable(Protocol[_T_Co]):
    """A `Protocol` (structurally typed) for an object that is subscriptable and of finite length."""

    __slots__ = ()
    def __len__(self) -> int:
        """Number of elements, normally called via `len(x)` where `x` is an object that implements this protocol."""

    def __getitem__(self, index: int) -> _T_Co:
        """
        Element at the given index,
        normally called via `x[index]` where `x` is an object that implements this protocol.
        """
