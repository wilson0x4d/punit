# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType
from typing import Callable


def fails(*, reason: str) -> Callable:
    """Mark a test as expected to fail for the given *reason*.

    This is a marker decorator — it does **not** wrap the target function.

    Semantics
    ---------

    A test decorated with ``@fails`` has its pass/fail result **inverted**:

    * Test **fails** → reported as passing.
    * Test **passes** → reported as failing.

    In both cases ``expected_failure_reason`` is set so reporting and
    automation tools can know that the test was expected to fail.

    Usage
    -----

    Stack this decorator *below* ``@fact`` or ``@theory``, closest to the
    function definition:

    .. code-block:: python

        @fact
        @fails(reason='bug #123: assert order is reversed')
        def test_reversed_order():
            assert get_items() == ['b', 'a']

    For parameterized tests:

    .. code-block:: python

        @theory
        @inlinedata('unsorted', [3, 1, 2], [1, 2, 3])
        @fails(reason='edge case in sort comparison')
        def theory_sort(unused: str, unsorted: list[int], then: list[int]):
            assert sorted(unsorted) == then

    Parameters
    ----------
    reason : str
        A human-readable explanation of why the test is expected to fail.

    Returns
    -------
    Callable
        The original, undecorated target -- no wrapper is installed.

    Raises
    ------
    Exception
        If *target* is not a function or method, if it has already been
        decorated by ``@fails``, or if it already carries a ``__punit_decorator``
        attribute set by another pUnit decorator (``@fact``, ``@theory``,
        ``@setup``, ``@teardown``).
    """
    def wrapper(target: Callable) -> Callable:
        unwrapped = inspect.unwrap(target)

        if not isinstance(unwrapped, (FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType)):
            raise Exception('@fails can only be applied to functions and methods.')

        if hasattr(unwrapped, '__punit_fails_reason'):
            raise Exception(
                f'@fails and another @fails cannot decorate the same function. '
                f'Function "{unwrapped.__name__}" is already marked as expected to fail.'
            )

        if hasattr(unwrapped, '__punit_decorator'):
            raise Exception(
                f'@fails and {getattr(unwrapped, "__punit_decorator")} cannot decorate the same function. '
                f'Function "{unwrapped.__name__}" has already been decorated.'
            )

        setattr(unwrapped, '__punit_fails_reason', reason)
        return target

    return wrapper
