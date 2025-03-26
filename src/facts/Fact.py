# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

import inspect
from types import FunctionType, MethodType, ModuleType
from typing import Any, Callable, Coroutine
from .FactManager import FactManager

class Fact:

    __className:str
    __moduleName:str
    __target:FunctionType|MethodType
    __testName:str

    def __init__(self, moduleName:str, target:FunctionType|MethodType, className:str = None, testName:str = None):
        self.__className = className
        self.__moduleName = moduleName
        self.__target = target
        self.__testName = testName

    @property
    def className(self) -> str:
        return self.__className

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

    async def execute(self, module:ModuleType) -> None:
        coro:Coroutine = None
        if hasattr(self.__target, '__qualname__') and self.__target.__qualname__.find('.') > -1:
            qnparts = self.__target.__qualname__.split('.')
            if isinstance(self.__target, staticmethod):
                coro = self.__target()
                self.__className = '.'.join(qnparts[0:-1])
                self.__testName = qnparts[-1]
            else:
                qntarget = module
                self.__className = '.'.join(qnparts[0:-1])
                self.__testName = qnparts[-1]
                for qnpart in qnparts[0:-1]:
                    qntarget = getattr(qntarget, qnpart)
                if isinstance(self.__target, classmethod):
                    coro = self.__target.__func__(qntarget)
                else:
                    coro = self.__target(qntarget())
        else:
            self.__className = None
            self.__testName = self.__target.__name__
            coro = self.__target()
        if inspect.iscoroutine(coro):
            await coro

def fact(target:Callable) -> Callable:
    if (not inspect.isfunction(target)) and (not isinstance(target, classmethod)) and (not isinstance(target, staticmethod)):
        raise Exception('@fact can only be applied to functions and methods.')
    fact:Fact = Fact(target.__module__, target)
    FactManager.instance().put(fact)
    return target
