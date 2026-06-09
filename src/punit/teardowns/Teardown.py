# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType
from typing import Callable, Coroutine, Union, cast

from ..metadata import CallableMetadata


class Teardown:

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
        """Execute the teardown function.

        For module-scoped teardowns, ``obj`` is ignored.
        For class-scoped teardowns on methods, ``obj`` should be an instance
        of the decorated class; it is used as ``self`` via method binding.
        """
        if self.__scope_type == 'module':
            coro: Coroutine | None = None
            coro = self.__target()  # type: ignore[call-arg]
            if inspect.iscoroutine(coro):
                await coro
        else:
            # class-scoped teardown method — execute on the provided instance
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
                # regular instance method — bind to the instance
                bound = getattr(obj_instance, self.__target.__name__)
                if inspect.iscoroutine(bound):
                    await bound
                elif callable(bound):
                    coro = bound()  # type: ignore[bad-assignment]
                    if inspect.iscoroutine(coro):  # type: ignore[possibly-undefined]
                        await coro


def teardown(target: Callable) -> Callable:
    from .TeardownManager import TeardownManager
    unwrapped = inspect.unwrap(target)
    if not isinstance(unwrapped, (FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType)):
        raise Exception('@teardown can only be applied to functions and methods.')
    if hasattr(unwrapped, '__punit_decorator'):
        raise Exception(
            f'@teardown and {getattr(unwrapped, "__punit_decorator")} cannot decorate the same function. '
            f'Function "{unwrapped.__name__}" has already been decorated.'
        )
    setattr(unwrapped, '__punit_decorator', '@teardown')

    td: Teardown = Teardown(target)
    TeardownManager.instance().put(td)
    return target
