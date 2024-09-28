# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##

from typing import ForwardRef

Fact = ForwardRef('Fact')
FactManager = ForwardRef('FactManager')

class FactManager:

    __instance:'FactManager' = None
    __modules:dict[str, list[Fact]]
    
    def __init__(self):
        if FactManager.__instance is not None:
            raise Exception('Cannot create more than one instance of FactManager')
        self.__modules = {}

    @staticmethod
    def instance() -> FactManager:
        if FactManager.__instance is None:
            FactManager.__instance = FactManager()
        return FactManager.__instance
        
    def get(self, moduleName:str) -> list[Fact]:
        l = self.__modules.get(moduleName)
        if l is None:
            l = []
            self.__modules[moduleName] = l
        return l

    def put(self, fact:Fact) -> None:
        l = self.get(fact.moduleName)
        l.append(fact)
