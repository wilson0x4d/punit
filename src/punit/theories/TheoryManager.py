# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##

import re
from typing import Callable, Optional

from ..traits.Trait import Trait
from .Theory import Theory


class TheoryManager:

    __excludeTraits:list[Trait]
    __filterPatterns:Optional[list[re.Pattern]]
    __includeTraits:list[Trait]
    __instance:Optional['TheoryManager'] = None
    __modules:dict[str, list[Theory]]
    __datas:dict[Callable, list[tuple]]
    __traits:dict[Callable, list[Trait]]
    
    def __init__(self):
        if TheoryManager.__instance is not None:
            raise Exception('Cannot create more than one instance of TheoryManager') # pragma: no cover
        self.__filterPatterns = None
        self.__modules = {}
        self.__datas = {}
        self.__traits = {}

    @staticmethod
    def instance() -> 'TheoryManager':
        if TheoryManager.__instance is None:
            TheoryManager.__instance = TheoryManager()
        return TheoryManager.__instance
        
    @property
    def excludeTraits(self) -> list[Trait]:
        return [] if self.__excludeTraits is None else self.__excludeTraits
    
    @excludeTraits.setter
    def excludeTraits(self, value:list[Trait]) -> None:
        self.__excludeTraits = value

    @property
    def filterPatterns(self) -> Optional[list[re.Pattern]]:
        return self.__filterPatterns
    
    @filterPatterns.setter
    def filterPatterns(self, value:list[re.Pattern]) -> None:
        self.__filterPatterns = value

    @property
    def includeTraits(self) -> list[Trait]:
        return [] if self.__includeTraits is None else self.__includeTraits
    
    @includeTraits.setter
    def includeTraits(self, value:list[Trait]) -> None:
        self.__includeTraits = value

    def __excludeByTraits(self, theory:Theory) -> bool:
        if self.excludeTraits is not None and len(self.__excludeTraits) > 0:
            for trait in self.excludeTraits:
                for L_trait in theory.traits:
                    if trait.name == L_trait.name and (trait.value is None or (trait.value == L_trait.value)):
                        return True
        if self.includeTraits is not None and len(self.includeTraits) > 0:
            for trait in self.includeTraits:
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
        matchesFilterPattern:bool = self.filterPatterns is None
        if self.filterPatterns is not None and len(self.filterPatterns) > 0:
            for filterPattern in self.filterPatterns:
                if len(filterPattern.findall(theory.filterName)) > 0:
                    matchesFilterPattern = True
                    break
        if matchesFilterPattern:
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
