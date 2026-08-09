# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType
from typing import Any, Callable


def teardown(target: Callable[..., Any]) -> Callable[..., Any]:
    """Decorates a function or method as a Teardown that runs after each test.

    A teardown may be synchronous or asynchronous, just like Facts and Theories.
    If a teardown raises an exception, the corresponding test is marked as failed.

    Args:
        target: The function or method to decorate as a Teardown

    Returns:
        The original, undecorated target -- no wrapper is installed

    Example
    -------

    .. code-block:: python

        from punit import fact, teardown

        class MyTestClass:
            @fact
            def test_a(self):
                assert True

            @teardown
            def tearDownClass(self):
                reset_temp_files()

    Raises:
        Exception: If target is not a function/method, or if it already carries
            another pUnit decorator attribute.

    """
    from .teardown_descriptor import TeardownDescriptor
    from .teardown_manager import TeardownManager
    unwrapped = inspect.unwrap(target)
    if not isinstance(unwrapped, (FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType)):
        raise Exception('@teardown can only be applied to functions and methods.')
    if hasattr(unwrapped, '__punit_decorator'):
        raise Exception(
            f'@teardown and {getattr(unwrapped, "__punit_decorator")} cannot decorate the same function. '
            f'Function "{unwrapped.__name__}" has already been decorated.'
        )
    setattr(unwrapped, '__punit_decorator', '@teardown')

    td: TeardownDescriptor = TeardownDescriptor(target)
    TeardownManager.instance().put(td)
    return target
