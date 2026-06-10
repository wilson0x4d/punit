# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

"""
A **Fact** is a test that validates an invariant arrangement of state.  State is usually hardcoded as part of the test definition.

Facts validate invariant state -- the conditions and assertions are fully codified within the test definition itself. Unlike ``@theory``, facts do not require data providers; each decorated function runs exactly once.
"""

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType
from typing import Any, Callable, Coroutine, Union, cast

from ..metadata import CallableMetadata


class Fact:
    """Wraps a test function or method decorated with ``@fact``.

    Example
    -------

    .. code-block:: python

        from punit import fact

        @fact
        def myFunction():
            assert 1 == 1

    """

    __target: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]

    def __init__(self, target: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]):
        self.__metadata = CallableMetadata(target)
        self.__target = target

    @property
    def metadata(self) -> CallableMetadata:
        return self.__metadata

    @property
    def target(self) -> Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]:
        return self.__target

    async def execute(self, module: ModuleType) -> Any | None:
        class_instance: Any | None = None
        coro: Coroutine | None = None
        if hasattr(self.__target, '__qualname__') and self.__target.__qualname__.find('.') > -1:
            if isinstance(self.__target, staticmethod):
                coro = self.__target()
            else:
                qnparts = [p for p in self.__target.__qualname__.split('.') if p != '<locals>']
                qntarget = module
                for qnpart in qnparts[0:-1]:
                    qntarget = getattr(qntarget, qnpart)
                if isinstance(self.__target, classmethod):
                    coro = self.__target.__func__(qntarget)
                else:
                    # every test execution gets a new instance of class
                    class_instance = cast(Any, cast(Callable, qntarget)())
                    coro = self.__target(class_instance)
        else:
            coro = self.__target()
        if inspect.iscoroutine(coro):
            await coro
        return class_instance


def fact(target: Callable) -> Callable:
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
    from .FactManager import FactManager
    unwrapped = inspect.unwrap(target)
    if not isinstance(unwrapped, (FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType)):
        raise Exception('@fact can only be applied to functions and methods.')
    if hasattr(unwrapped, '__punit_decorator'):
        raise Exception(
            f'@fact and {getattr(unwrapped, "__punit_decorator")} cannot decorate the same function. '
            f'Function "{unwrapped.__name__}" has already been decorated.'
        )
    setattr(unwrapped, '__punit_decorator', '@fact')
    fact: Fact = Fact(target)
    FactManager.instance().put(fact)
    return target
