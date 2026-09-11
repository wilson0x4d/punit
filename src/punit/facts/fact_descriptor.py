# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType
from typing import Any, Callable, Coroutine, Union, cast

from ..metadata import CallableMetadata


class FactDescriptor:
    """Wraps a test function or method decorated with ``@fact``.

    Example
    -------

    .. code-block:: python

        from punit import fact

        @fact
        def myFunction():
            assert 1 == 1

    """

    __target: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable[..., Any]]

    def __init__(self, target: Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable[..., Any]]):
        self.__metadata = CallableMetadata(target)
        self.__target = target

    @property
    def metadata(self) -> CallableMetadata:
        return self.__metadata

    @property
    def target(self) -> Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable[..., Any]]:
        return self.__target

    async def execute(
        self,
        module: ModuleType,
        class_instance: Any | None = None,
        *,
        timeout: float | None = None,
    ) -> Any | None:
        """Execute the fact, optionally using *class_instance*.

        When *class_instance* is ``None`` and the target is a class-method,
        a fresh instance is created.  Otherwise the provided instance is used
        directly, allowing lifecycle managers to control instance creation.
        """
        if timeout is not None:
            return await asyncio.wait_for(
                asyncio.to_thread(self.__execute, module, class_instance),
                timeout=timeout,
            )
        coro, class_instance = self.__resolve_and_call(module, class_instance)
        if inspect.iscoroutine(coro):
            await coro
        return class_instance

    def __execute(self, module: ModuleType, class_instance: Any | None = None) -> Any | None:
        """Resolve class instance, call the target, and return the result.

        If the target returns a coroutine it is awaited via ``asyncio.run``
        so it completes before this thread returns.  Otherwise the result is
        returned directly.

        This method is called either directly on the event loop (when no
        timeout is set) or inside a worker thread (when timeout is set).
        """
        coro, class_instance = self.__resolve_and_call(module, class_instance)
        if inspect.iscoroutine(coro):
            return asyncio.run(coro)
        return class_instance

    def __resolve_and_call(
        self,
        module: ModuleType,
        class_instance: Any | None = None,
    ) -> tuple[Coroutine[Any, Any, Any] | None, Any | None]:
        """Resolve class instance and call ``__target``.

        Returns a tuple of ``(coroutine_or_none, class_instance)``.
        """
        coro: Coroutine[Any, Any, Any] | None = None
        if class_instance is not None or (
            hasattr(self.__target, '__qualname__')
            and self.__target.__qualname__.find('.') > -1
        ):
            if isinstance(self.__target, staticmethod):
                coro = self.__target()
            else:
                qnparts = [
                    p
                    for p in self.__target.__qualname__.split('.')
                    if p != '<locals>'
                ]
                qntarget: Any = module
                for qnpart in qnparts[0:-1]:
                    qntarget = getattr(qntarget, qnpart)
                if isinstance(self.__target, classmethod):
                    coro = self.__target.__func__(qntarget)
                else:
                    if class_instance is None:
                        class_instance = cast(
                            Any, cast(Callable[..., Any], qntarget)()
                        )
                    coro = self.__target(class_instance)
        else:
            coro = self.__target()
        return coro, class_instance
