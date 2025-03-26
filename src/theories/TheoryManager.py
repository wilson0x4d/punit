# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT
##

import re
from typing import Callable, ForwardRef

Theory = ForwardRef('Theory')
TheoryManager = ForwardRef('TheoryManager')

class TheoryManager:

    __filterPattern:re.Pattern
    __instance:'TheoryManager' = None
    __modules:dict[str, list[Theory]]
    __datas:dict[Callable, list[tuple]]
    
    def __init__(self):
        if TheoryManager.__instance is not None:
            raise Exception('Cannot create more than one instance of TheoryManager')
        self.__filterPattern = None
        self.__modules = {}
        self.__datas = {}

    @staticmethod
    def instance() -> TheoryManager:
        if TheoryManager.__instance is None:
            TheoryManager.__instance = TheoryManager()
        return TheoryManager.__instance
        
    @property
    def filterPattern(self) -> re.Pattern:
        return self.__filterPattern
    
    @filterPattern.setter
    def filterPattern(self, value:re.Pattern) -> None:
        self.__filterPattern = value

    def get(self, moduleName:str) -> list[Theory]:
        l = self.__modules.get(moduleName)
        if l is None:
            l = []
            self.__modules[moduleName] = l
        return l

    def put(self, theory:Theory) -> None:
        if len(self.__filterPattern.findall(theory.filterName)) > 0:
            l = self.get(theory.moduleName)
            d = self.__datas.get(theory.target)
            if d is not None:
                d.reverse()
                for data in d:
                    theory.datas.append(data)
            l.append(theory)

    def withData(self, target:Callable, data:tuple) -> None:
        # TODO: data acquisition should be deferred until put() since that is where filterPattern
        # is applied, but for current implementation `@inlinedata()` is not affected. more advanced
        # data decorators may benefit from deferral (for example, data coming from an API or DB.)
        d = self.__datas.get(target)
        if d is None:
            d = []
            self.__datas[target] = d
        d.append(data)
