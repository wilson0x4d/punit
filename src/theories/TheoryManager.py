# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT
##

import re
from typing import Callable, ForwardRef

Theory = ForwardRef('Theory')
TheoryManager = ForwardRef('TheoryManager')
Trait = ForwardRef('Trait')


class TheoryManager:

    __excludeTraits:list[Trait]
    __filterPattern:re.Pattern
    __includeTraits:list[Trait]
    __instance:'TheoryManager' = None
    __modules:dict[str, list[Theory]]
    __datas:dict[Callable, list[tuple]]
    __traits:dict[Callable, list[Trait]]
    
    def __init__(self):
        if TheoryManager.__instance is not None:
            raise Exception('Cannot create more than one instance of TheoryManager')
        self.__filterPattern = None
        self.__modules = {}
        self.__datas = {}
        self.__traits = {}

    @staticmethod
    def instance() -> TheoryManager:
        if TheoryManager.__instance is None:
            TheoryManager.__instance = TheoryManager()
        return TheoryManager.__instance
    @property
    def excludeTraits(self) -> list[Trait]:
        return [] if self.__excludeTraits is None else self.excludeTraits
    
    @excludeTraits.setter
    def excludeTraits(self, value:list[Trait]) -> None:
        self.__excludeTraits = value

    @property
    def filterPattern(self) -> re.Pattern:
        return self.__filterPattern
    
    @filterPattern.setter
    def filterPattern(self, value:re.Pattern) -> None:
        self.__filterPattern = value

    @property
    def includeTraits(self) -> list[Trait]:
        return [] if self.__includeTraits is None else self.includeTraits
    
    @includeTraits.setter
    def includeTraits(self, value:list[Trait]) -> None:
        self.__includeTraits = value

    def __excludeByTraits(self, theory:Theory) -> bool:
        if self.__excludeTraits is not None and len(self.__excludeTraits) > 0:
            for trait in self.__excludeTraits:
                for L_trait in theory.traits:
                    if trait.name == L_trait.name and (trait.value is None or (trait.value == L_trait.value)):
                        return True
        if self.__includeTraits is not None and len(self.__includeTraits) > 0:
            for trait in self.__includeTraits:
                for L_trait in theory.traits:
                    if trait.name == L_trait.name and (trait.value is None or (trait.value == L_trait.value)):
                        return False
            return True
        return False

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
            t = self.__traits.get(theory.target)
            if t is not None:
                for trait in t:
                    theory.traits.append(trait)
            if not self.__excludeByTraits(theory):
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

    def withTrait(self, target:Callable, trait:Trait) -> None:
        t = self.__traits.get(target)
        if t is None:
            t = []
            self.__traits[target] = t
        t.append(trait)
