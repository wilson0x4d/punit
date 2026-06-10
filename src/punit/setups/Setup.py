# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType
from typing import Callable, Coroutine, Union, cast

from ..metadata import CallableMetadata


class Setup:
    """Wraps a ``@setup``-decorated initialization function or method.

    Setups execute immediately before each test runs, allowing you to prepare
    resources or reset state without cluttering test bodies with try/finally blocks.

    Setups come in two scopes: module-scoped (bare function) and class-scoped
    (method inside a test class). The two scopes are independent of each other.

    Example
    -------

    .. code-block:: python

        from punit import fact, setup

        @setup
        def my_setup():
            prepare_database()

        @fact
        def test_something():
            assert True

    """

    __metadata: CallableMetadata
    __scope_type: str  # "module" or "class"
    __wrapped_target: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]
    __target: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]

    def __init__(self, target: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]):
        # For descriptors (staticmethod/classmethod), unwrap to get the raw function
        if isinstance(target, (staticmethod, classmethod)):
            self.__wrapped_target = target
            self.__target = cast(FunctionType, target.__func__)  # type: ignore[arg-type]
        else:
            self.__wrapped_target = target
            self.__target = target
        self.__metadata = CallableMetadata(self.__target)
        # Determine scope from class_name: non-empty means class-scoped method
        if (hasattr(self.__target, '__qualname__') and '.' in self.__target.__qualname__):
            self.__scope_type = 'class'
        else:
            self.__scope_type = 'module'

    @property
    def metadata(self) -> CallableMetadata:
        return self.__metadata

    @property
    def scope_type(self) -> str:
        return self.__scope_type

    @property
    def target(self) -> Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]:
        return self.__wrapped_target

    async def execute(self, module: ModuleType, obj: object | None = None) -> None:
        """Execute the setup function.

        For module-scoped setups, ``obj`` is ignored.
        For class-scoped setups on methods, ``obj`` should be an instance
        of the decorated class; it is used as ``self`` via method binding.
        """
        if self.__scope_type == 'module':
            coro: Coroutine | None = None
            coro = self.__target()  # type: ignore[call-arg]
            if inspect.iscoroutine(coro):
                await coro
        else:
            # class-scoped setup method;  execute on the provided instance
            # or create one if none was supplied (defensive fallback).
            obj_instance = obj
            if obj_instance is None:
                cls_name = self.__metadata.class_name
                if cls_name:
                    cls = getattr(module, cls_name)  # type: ignore[union-attr]
                    obj_instance = cls()
                else:
                    obj_instance = cast(Callable, self.__target)()
            if isinstance(self.__wrapped_target, staticmethod):
                coro = self.__wrapped_target()
            elif isinstance(self.__wrapped_target, classmethod):
                qnparts = self.__wrapped_target.__qualname__.split('.')
                cls = getattr(module, qnparts[-2])
                args = (cls,)
                coro = self.__wrapped_target.__func__(*args)
            else:
                # regular instance method;  bind to the instance
                bound = getattr(obj_instance, self.__target.__name__)
                if inspect.iscoroutine(bound):
                    await bound
                elif callable(bound):
                    coro = bound()  # type: ignore[bad-assignment]
                    if inspect.iscoroutine(coro):  # type: ignore[possibly-undefined]
                        await coro


def setup(target: Callable) -> Callable:
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
    from .SetupManager import SetupManager
    unwrapped = inspect.unwrap(target)
    if not isinstance(unwrapped, (FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType)):
        raise Exception('@setup can only be applied to functions and methods.')
    if hasattr(unwrapped, '__punit_decorator'):
        raise Exception(
            f'@setup and {getattr(unwrapped, "__punit_decorator")} cannot decorate the same function. '
            f'Function "{unwrapped.__name__}" has already been decorated.'
        )
    setattr(unwrapped, '__punit_decorator', '@setup')

    sd: Setup = Setup(target)
    SetupManager.instance().put(sd)
    return target
