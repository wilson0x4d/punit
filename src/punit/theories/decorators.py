# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##

"""
A **Theory** is a `test` that makes `assertions` for a variant arrangement of `state`. For a **Theory**, state is usually acquired from an external source, separated from the test definition. In **pUnit**, **Theories** are tests that have been decorated with ``@theory`` and at least one data decorator such as ``@inlinedata(...)``.
"""

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType
from typing import Any, Callable, Coroutine, Union, cast

from ..metadata import CallableMetadata


def theory(target: Callable) -> Callable:
    """Decorates a function or method as a 'Theory-based' parameterized test.

    Theories validate behavior across a variant arrangement of state. A theory
    decorator alone is insufficient for execution -- you must also supply data
    using at least one data decorator (such as ``@inlinedata``).

    Args:
        target: The function or method to decorate as a Theory test

    Returns:
        The original, undecorated target -- no wrapper is installed

    Example
    -------

    .. code-block:: python

        from punit import theory, inlinedata

        @theory
        @inlinedata(0, 1, 1)
        @inlinedata(1, 1, 2)
        @inlinedata(1, 2, 3)
        def myFunction(a, b, c):
            assert a + b == c

    Raises:
        Exception: If target is not a function/method, or if it already carries
            another pUnit decorator attribute.

    """
    from .theory_descriptor import TheoryDescriptor
    from .theory_manager import TheoryManager
    unwrapped = inspect.unwrap(target)
    if not isinstance(unwrapped, (FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType)):
        raise Exception('@theory can only be applied to functions and methods.')
    if hasattr(unwrapped, '__punit_decorator'):
        raise Exception(
            f'@theory and {getattr(unwrapped, "__punit_decorator")} cannot decorate the same function. '
            f'Function "{unwrapped.__name__}" has already been decorated.'
        )
    setattr(unwrapped, '__punit_decorator', '@theory')
    theory_descriptor: TheoryDescriptor = TheoryDescriptor(target)
    TheoryManager.instance().put(theory_descriptor)
    return target


def inlinedata(*args: Any) -> Callable[..., Any]:
    """Decorates a 'Theory-based' test with inline data points for parameterization.

    Each call to ``@inlinedata`` provides one set of arguments that will be passed
    to the theory function as a tuple. Multiple ``@inlinedata`` decorators may be
    stacked; each one adds another data point.

    Args:
        *args: One or more positional values for this data point. These become
            the tuple of arguments passed to the theory function.

    Returns:
        A wrapper that attaches the data point to the target via TheoryManager

    Example
    -------

    .. code-block:: python

        from punit import theory, inlinedata

        @theory
        @inlinedata(0, 1, 1)
        @inlinedata(1, 1, 2)
        def add_correct(a, b, c):
            assert a + b == c

    """
    def wrapper(target: Callable[..., Any]) -> Callable[..., Any]:
        if args is not None and len(args) > 0:
            from .theory_manager import TheoryManager
            TheoryManager.instance().withData(target, args)
        return target
    return wrapper
