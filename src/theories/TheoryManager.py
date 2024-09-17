# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##

from typing import Callable, ForwardRef

Theory = ForwardRef('Theory')
TheoryManager = ForwardRef('TheoryManager')

class TheoryManager:

    __instance:'TheoryManager' = None
    __modules:dict[str, Theory] = {}
    __datas:dict[Callable, list[tuple]] = {}
    
    def __init__(self):
        if TheoryManager.__instance is not None:
            raise Exception('Cannot create more than one instance of TheoryManager')
        self.__modules = {}

    @staticmethod
    def instance() -> TheoryManager:
        if TheoryManager.__instance is None:
            TheoryManager.__instance = TheoryManager()
        return TheoryManager.__instance
        
    def get(self, moduleName:str) -> list[Theory]:
        l = TheoryManager.__modules.get(moduleName)
        if l is None:
            l = []
            TheoryManager.__modules[moduleName] = l
        return l

    def put(self, theory:Theory) -> None:
        l = self.get(theory.moduleName)
        d = self.__datas.get(theory.target)
        if d is not None:
            d.reverse()
            for data in d:
                theory.datas.append(data)
        l.append(theory)

    def withData(self, target:Callable, data:tuple) -> None:
        d = self.__datas.get(target)
        if d is None:
            d = []
            self.__datas[target] = d
        d.append(data)
