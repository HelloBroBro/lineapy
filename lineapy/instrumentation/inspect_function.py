from __future__ import annotations

import operator
import sys
import types
from dataclasses import dataclass
from typing import Callable, Iterable, Union

from lineapy import api, lineabuiltins


def inspect_function(
    function: Callable,
    args: list[object],
    kwargs: dict[str, object],
    result: object,
) -> Iterable[Union[ViewOfPointers, MutatedPointer]]:
    """
    Inspects a function and returns how calling it mutates the args/result and
    creates view relationships between them.
    """

    # TODO: We should probably not use use setitem, but instead get particular
    # __setitem__ for class so we can differentiate based on type more easily?
    if function == operator.setitem:
        # setitem(dict, key, value)
        yield MutatedPointer(PositionalArg(0))
        if is_mutable(args[2]):
            yield ViewOfPointers(PositionalArg(2), PositionalArg(0))
        return

    if function == operator.getitem:
        # getitem(dict, key)
        # If both are mutable, they are now views of one another!
        if is_mutable(args[0]) and is_mutable(result):
            yield ViewOfPointers(PositionalArg(0), Result())
            return
    if function == operator.delitem:
        # delitem(dict, key)
        yield MutatedPointer(PositionalArg(0))
        return
    if function == api.save:
        # The lineapy module is mutated when we save
        yield MutatedPointer(BoundSelfOfFunction())
    if function == lineabuiltins.l_list:
        # l_build_list(x1, x2, ...)
        yield ViewOfPointers(
            Result(),
            *(PositionalArg(i) for i, a in enumerate(args) if is_mutable(a))
        )
        return
    if (
        isinstance(function, types.BuiltinMethodType)
        and function.__name__ == "append"
        and isinstance(function.__self__, list)
    ):
        # list.append(value)
        yield MutatedPointer(BoundSelfOfFunction())
        if is_mutable(args[0]):
            yield ViewOfPointers(BoundSelfOfFunction(), PositionalArg(0))
        return

    if imported_module("sklearn"):
        from sklearn.base import BaseEstimator

        if (
            isinstance(function, types.MethodType)
            and function.__name__ == "fit"
            and isinstance(function.__self__, BaseEstimator)
        ):
            # In res = clf.fit(x, y)
            # cff is mutated, and we say that the res and the clf
            # are views of each other, since mutating one will mutate the other
            # since they are the same object.
            yield MutatedPointer(BoundSelfOfFunction())
            yield ViewOfPointers(BoundSelfOfFunction(), Result())
            return
    # Note: Future functions might require normalizing the args/kwargs with
    # inspect.signature.bind(args, kwargs) first
    return []


def imported_module(name: str) -> bool:
    """
    Returns true if we have imported this module before.
    """
    return name in sys.modules


def is_mutable(obj: object) -> bool:
    """
    Returns true if the object is mutable.
    """
    # Assume all hashable objects are immutable
    try:
        hash(obj)
    except Exception:
        return True
    return False


@dataclass(frozen=True)
class PositionalArg:
    index: int


@dataclass(frozen=True)
class KeywordArg:
    name: str


@dataclass(frozen=True)
class BoundSelfOfFunction:
    """
    If the function is a bound method, this refers to the instance that was
    bound of the method.
    """

    pass


@dataclass(frozen=True)
class Result:
    """
    The result of a function call, used to describe a View.
    """

    pass


Pointer = Union[PositionalArg, KeywordArg, Result, BoundSelfOfFunction]


@dataclass
class ViewOfPointers:
    """
    A set of values which all potentially refer to shared pointers
    So that if one is mutated, the rest might be as well.
    """

    # They are unique, like a set, but ordered for deterministc behaviour
    pointers: list[Pointer]

    def __init__(self, *xs: Pointer) -> None:
        self.pointers = list(xs)


@dataclass(frozen=True)
class MutatedPointer:
    """
    A value that is mutated when the function is called
    """

    pointer: Pointer
