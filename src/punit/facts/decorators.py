# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
A **Fact** is a test that validates an invariant arrangement of state.  State is usually hardcoded as part of the test definition.

Facts validate invariant state -- the conditions and assertions are fully codified within the test definition itself. Unlike ``@theory``, facts do not require data providers; each decorated function runs exactly once.
"""

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType
from typing import Any, Callable

from .fact_descriptor import FactDescriptor


def fact(target: Callable[..., Any]) -> Callable[..., Any]:
    """Decorates a function or method as a 'Fact-based' test.

    Args:
        target: The function or method to decorate as a Fact test

    Returns:
        The original, undecorated target -- no wrapper is installed

    Example
    -------

    .. code-block:: python

        from punit import fact

        @fact
        def myFunction():
            assert 1 == 1

        class MyClass:
            @fact
            def myMethod(self):
                assert 1 == 1

    Raises:
        Exception: If target is not a function/method, or if it already carries
            another pUnit decorator attribute.

    """
    from .fact_manager import FactManager
    unwrapped = inspect.unwrap(target)
    if not isinstance(unwrapped, (FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType)):
        raise Exception('@fact can only be applied to functions and methods.')
    if hasattr(unwrapped, '__punit_decorator'):
        raise Exception(
            f'@fact and {getattr(unwrapped, "__punit_decorator")} cannot decorate the same function. '
            f'Function "{unwrapped.__name__}" has already been decorated.'
        )
    setattr(unwrapped, '__punit_decorator', '@fact')
    fact_descriptor: FactDescriptor = FactDescriptor(target)
    FactManager.instance().put(fact_descriptor)
    return target
