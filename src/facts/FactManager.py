# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT
##

import re
from typing import ForwardRef

Fact = ForwardRef('Fact')
FactManager = ForwardRef('FactManager')

class FactManager:

    __filterPattern:re.Pattern
    __instance:'FactManager' = None
    __modules:dict[str, list[Fact]]
    
    def __init__(self):
        if FactManager.__instance is not None:
            raise Exception('Cannot create more than one instance of FactManager')
        self.__filterPattern = None
        self.__modules = {}

    @staticmethod
    def instance() -> FactManager:
        if FactManager.__instance is None:
            FactManager.__instance = FactManager()
        return FactManager.__instance
        
    @property
    def filterPattern(self) -> re.Pattern:
        return self.__filterPattern
    
    @filterPattern.setter
    def filterPattern(self, value:re.Pattern) -> None:
        self.__filterPattern = value

    def get(self, moduleName:str) -> list[Fact]:
        l = self.__modules.get(moduleName)
        if l is None:
            l = []
            self.__modules[moduleName] = l
        return l

    def put(self, fact:Fact) -> None:
        if len(self.__filterPattern.findall(fact.filterName)) > 0:
            l = self.get(fact.moduleName)
            l.append(fact)
