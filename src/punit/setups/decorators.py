# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType
from typing import Any, Callable


def setup(target: Callable[..., Any]) -> Callable[..., Any]:
    """Decorates a function or method as a Setup that runs before each test.

    A setup may be synchronous or asynchronous. If it raises an exception, the
    corresponding test is marked as failed but no further processing occurs for
    that test.

    Args:
        target: The function or method to decorate as a Setup

    Returns:
        The original, undecorated target -- no wrapper is installed

    Example
    -------

    .. code-block:: python

        from punit import fact, setup, teardown

        @setup
        def db_setup():
            global _connection
            _connection = connect_to_database()

        @teardown
        def db_teardown():
            global _connection
            if _connection:
                _connection.close()
                _connection = None

        @fact
        def test_query():
            assert query(_connection) is not None

    Raises:
        Exception: If target is not a function/method, or if it already carries
            another pUnit decorator attribute.

    """
    from .setup_descriptor import SetupDescriptor
    from .setup_manager import SetupManager
    unwrapped = inspect.unwrap(target)
    if not isinstance(unwrapped, (FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType)):
        raise Exception('@setup can only be applied to functions and methods.')
    if hasattr(unwrapped, '__punit_decorator'):
        raise Exception(
            f'@setup and {getattr(unwrapped, "__punit_decorator")} cannot decorate the same function. '
            f'Function "{unwrapped.__name__}" has already been decorated.'
        )
    setattr(unwrapped, '__punit_decorator', '@setup')

    setup_descriptor: SetupDescriptor = SetupDescriptor(target)
    SetupManager.instance().put(setup_descriptor)
    return target
