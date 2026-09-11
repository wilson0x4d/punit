# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
A **Fact** is a test that validates an invariant arrangement of state.  State is usually hardcoded as part of the test definition.

Facts validate invariant state -- the conditions and assertions are fully codified within the test definition itself. Unlike ``@theory``, facts do not require data providers; each decorated function runs exactly once.
"""

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType
from typing import Any, Callable, Union

from .fact_descriptor import FactDescriptor


def fact(
    target: Union[Callable[..., Any], None] = None,
    *,
    timeout: float | None = None,
) -> Union[Callable[..., Any], Callable[[Callable[..., Any]], Callable[..., Any]]]:
    """
    Decorates a function or method as a 'Fact-based' test.

    Facts validate invariant state -- the conditions and assertions are fully
    codified within the test definition itself. Unlike ``@theory``, facts do not
    require data providers; each decorated function runs exactly once.

    Parameters
    ----------

    target : Callable[..., Any]
        The function or method to decorate as a Fact test.
    timeout : float | None
        Maximum execution time in seconds. If ``0`` or ``None``, no timeout
        is enforced.

    Returns
    -------

    Callable[..., Any]
        The original, undecorated target -- no wrapper is installed.

    Example
    -------

    .. code-block:: python

        from punit import fact

        @fact
        def myFunction():
            assert 1 == 1

        @fact(timeout=5)
        def myTimedFunction():
            assert 1 == 1

        class MyClass:
            @fact
            def myMethod(self):
                assert 1 == 1

    NOTE:
        Using ``timeout`` with non-async methods will spawn a thread that may
        not terminate until pUnit exits. Use with caution; for the best
        experience, write async/await tests when using ``timeout``.

    Raises
    ------

    Exception
        If *target* is not a function/method, or if it already carries
        another pUnit decorator attribute.

    """
    from .fact_manager import FactManager

    def _apply_fact(fn: Callable[..., Any], _timeout: float | None = timeout) -> Callable[..., Any]:
        unwrapped = inspect.unwrap(fn)
        if not isinstance(unwrapped, (FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType)):
            raise Exception('@fact can only be applied to functions and methods.')
        if hasattr(unwrapped, '__punit_decorator'):
            raise Exception(
                f'@fact and {getattr(unwrapped, "__punit_decorator")} cannot decorate the same function. '
                f'Function "{unwrapped.__name__}" has already been decorated.'
            )
        setattr(unwrapped, '__punit_decorator', '@fact')
        if _timeout is not None and _timeout <= 0:
            _timeout = None
        if _timeout is not None:
            setattr(unwrapped, '__punit_timeout', _timeout)
        fact_descriptor: FactDescriptor = FactDescriptor(fn)
        FactManager.instance().put(fact_descriptor)
        return fn

    if target is not None:
        # Called without timeout argument: @fact
        # Create a closure that captures the fact that timeout is None
        return _apply_fact(target)

    # Called with timeout argument: @fact(timeout=5)
    # timeout is already bound from the enclosing scope
    return _apply_fact
