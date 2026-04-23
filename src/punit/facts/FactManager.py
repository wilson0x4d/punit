# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##

import re
from typing import Callable, Optional

from ..filters.FilterManager import FilterManager
from ..traits.Trait import Trait
from .Fact import Fact


class FactManager:

    __excludeTraits:list[Trait]    
    __instance:Optional['FactManager'] = None
    __includeTraits:list[Trait]
    __modules:dict[str, list[Fact]]
    __traits:dict[Callable, list[Trait]]
    
    def __init__(self) -> None:
        if FactManager.__instance is not None:
            raise Exception('Cannot create more than one instance of FactManager') # pragma: no cover
        self.__modules = {}
        self.__traits = {}

    @staticmethod
    def instance() -> 'FactManager':
        if FactManager.__instance is None:
            FactManager.__instance = FactManager()
        return FactManager.__instance
    
    @property
    def excludeTraits(self) -> list[Trait]:
        return [] if self.__excludeTraits is None else self.__excludeTraits

    @excludeTraits.setter
    def excludeTraits(self, value:list[Trait]) -> None:
        self.__excludeTraits = value

    @property
    def includeTraits(self) -> list[Trait]:
        return [] if self.__includeTraits is None else self.__includeTraits
    
    @includeTraits.setter
    def includeTraits(self, value:list[Trait]) -> None:
        self.__includeTraits = value

    def __excludeByTraits(self, fact:Fact) -> bool:
        if self.excludeTraits is not None and len(self.excludeTraits) > 0:
            for trait in self.excludeTraits:
                for L_trait in fact.traits:
                    if trait.name == L_trait.name and (trait.value is None or (trait.value == L_trait.value)):
                        return True
        if self.includeTraits is not None and len(self.includeTraits) > 0:
            for trait in self.includeTraits:
                for L_trait in fact.traits:
                    if trait.name == L_trait.name and (trait.value is None or (trait.value == L_trait.value)):
                        return False
            return True
        return False

    def get(self, moduleName:str) -> list[Fact]:
        l = self.__modules.get(moduleName)
        if l is None:
            l = []
            self.__modules[moduleName] = l
        return l

    def put(self, fact:Fact) -> None:
        filters = FilterManager.instance().filters
        matches_filter:bool = False
        for filter in filters:
            if filter.re.fullmatch(fact.filterName) is not None:
                matches_filter = not filter.isExclude
                break
        if matches_filter:
            l = self.get(fact.moduleName)
            t = self.__traits.get(fact.target)
            if t is not None:
                for trait in t:
                    fact.traits.append(trait)
            if not self.__excludeByTraits(fact):
                l.append(fact)

    def withTrait(self, target:Callable, trait:Trait) -> None:
        t = self.__traits.get(target)
        if t is None:
            t = []
            self.__traits[target] = t
        t.append(trait)
