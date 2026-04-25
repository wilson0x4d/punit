# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType
from typing import Callable, Coroutine,  Union, cast

from ..metadata import CallableMetadata


class Fact:

    __target:Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]

    def __init__(self, target:Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]):
        self.__metadata = CallableMetadata(target)
        self.__target = target

    @property
    def metadata(self) -> CallableMetadata:
        return self.__metadata

    @property
    def target(self) -> Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]:
        return self.__target


    async def execute(self, module:ModuleType) -> None:
        coro:Coroutine|None = None
        if hasattr(self.__target, '__qualname__') and self.__target.__qualname__.find('.') > -1:
            if isinstance(self.__target, staticmethod):
                coro = self.__target()
            else:
                qnparts = self.__target.__qualname__.split('.')
                qntarget = module
                for qnpart in qnparts[0:-1]:
                    qntarget = getattr(qntarget, qnpart)
                if isinstance(self.__target, classmethod):
                    coro = self.__target.__func__(qntarget)
                else:
                    # every test execution gets a new instance of class
                    coro = self.__target(cast(Callable,qntarget)())
        else:
            coro = self.__target()
        if inspect.iscoroutine(coro):
            await coro


def fact(target:Callable) -> Callable:
    from .FactManager import FactManager
    if (not inspect.isfunction(target)) and (not isinstance(target, classmethod)) and (not isinstance(target, staticmethod)):
        raise Exception('@fact can only be applied to functions and methods.')
    fact:Fact = Fact(target)
    FactManager.instance().put(fact)
    return target
