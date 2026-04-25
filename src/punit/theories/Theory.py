# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##

import inspect
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType
from typing import Callable, Coroutine, Optional, Union, cast

from ..metadata import CallableMetadata


class Theory:

    __datas:list[tuple]
    __target:Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]

    def __init__(self, target:Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]):
        self.__datas = []
        self.__metadata = CallableMetadata(target)
        self.__target = target

    @property
    def datas(self) -> list[tuple]:
        return self.__datas

    @property
    def metadata(self) -> CallableMetadata:
        return self.__metadata

    @property
    def target(self) -> Union[FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType, Callable]:
        return self.__target

    async def execute(self, module:ModuleType, data:tuple) -> None:
        coro:Coroutine|None = None
        if hasattr(self.__target, '__qualname__') and self.__target.__qualname__.find('.') > -1:
            qnparts = self.__target.__qualname__.split('.')
            if isinstance(self.__target, staticmethod):
                coro = self.__target(*data)
            else:
                qntarget = module
                for qnpart in qnparts[0:-1]:
                    qntarget = getattr(qntarget, qnpart)
                if isinstance(self.__target, classmethod):
                    args = (qntarget,) + data
                    coro = self.__target.__func__(*args)
                else:
                    # every test execution gets a new instance of class
                    args = (cast(Callable,qntarget)(),) + data
                    coro = self.__target(*args)
        else:
            self.__testName = self.__target.__name__
            coro = self.__target(*data)
        if inspect.iscoroutine(coro):
            await coro


def theory(target:Callable) -> Callable:
    from .TheoryManager import TheoryManager
    if (not inspect.isfunction(target)) and (not isinstance(target, classmethod)) and (not isinstance(target, staticmethod)):
        raise Exception('@theory can only be applied to functions and methods.')
    theory:Theory = Theory(target)
    TheoryManager.instance().put(theory)
    return target


def inlinedata(*args) -> Callable:
    def wrapper(target:Callable) -> Callable:
        if args is not None and len(args) > 0:
            from .TheoryManager import TheoryManager
            TheoryManager.instance().withData(target, args)
        return target
    return wrapper
