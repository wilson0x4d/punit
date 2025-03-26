# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT
##

import inspect
from types import FunctionType, MethodType, ModuleType
from typing import Any, Callable, Coroutine
from .TheoryManager import TheoryManager

class Theory:

    __className:str
    __datas:list[tuple]
    __moduleName:str
    __target:FunctionType|MethodType
    __testName:str

    def __init__(self, moduleName:str, target:FunctionType|MethodType, className:str = None, testName:str = None):
        self.__className = className
        self.__datas = []
        self.__moduleName = moduleName
        self.__target = target
        self.__testName = testName

    @property
    def className(self) -> str:
        return self.__className

    @property
    def datas(self) -> list[tuple]:
        return self.__datas

    @property
    def moduleName(self) -> str:
        return self.__moduleName

    @property
    def target(self) -> FunctionType|MethodType:
        return self.__target

    @property
    def testName(self) -> str:
        return self.__testName
    
    @property
    def filterName(self) -> str:
        return f'{self.moduleName}/{"" if self.className is None or len(self.className) == 0 else f"{self.className}/"}{self.testName}'

    async def execute(self, module:ModuleType, data:tuple) -> None:
        coro:Coroutine = None
        if hasattr(self.__target, '__qualname__') and self.__target.__qualname__.find('.') > -1:
            qnparts = self.__target.__qualname__.split('.')
            if isinstance(self.__target, staticmethod):
                coro = self.__target(*data)
                self.__className = '.'.join(qnparts[0:-1])
                self.__testName = qnparts[-1]
            else:
                qntarget = module
                self.__testName = qnparts[-1]
                self.__className = '.'.join(qnparts[0:-1])
                for qnpart in qnparts[0:-1]:
                    qntarget = getattr(qntarget, qnpart)
                if isinstance(self.__target, classmethod):
                    args = (qntarget,) + data
                    coro = self.__target.__func__(*args)
                else:
                    args = (qntarget(),) + data
                    coro = self.__target(*args)
        else:
            self.__className = None
            self.__testName = self.__target.__name__
            coro = self.__target(*data)
        if inspect.iscoroutine(coro):
            await coro

def theory(target:Callable) -> Callable:
    if (not inspect.isfunction(target)) and (not isinstance(target, classmethod)) and (not isinstance(target, staticmethod)):
        raise Exception('@theory can only be applied to functions and methods.')
    theory:Theory = Theory(target.__module__, target)
    TheoryManager.instance().put(theory)
    return target

def inlinedata(*args) -> Callable:
    def wrapper(target:Callable) -> Callable:
        if args is not None and len(args) > 0:
            TheoryManager.instance().withData(target, args)
        return target
    return wrapper
