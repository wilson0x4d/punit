# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT
##

from types import FunctionType, MethodType
from typing import Callable, Optional

from .Trait import Trait


class TraitManager:

    __instance:Optional['TraitManager'] = None
    __traits:dict[Callable|FunctionType|MethodType, dict[str, Trait]]
    
    def __init__(self) -> None:
        if TraitManager.__instance is not None:
            raise Exception('Cannot create more than one instance of TraitManager') # pragma: no cover
        self.__traits = dict[Callable|FunctionType|MethodType, dict[str, Trait]]()

    @staticmethod
    def instance() -> 'TraitManager':
        if TraitManager.__instance is None:
            TraitManager.__instance = TraitManager()
        return TraitManager.__instance
    
    def get(self, callable:Callable|FunctionType|MethodType) -> list[Trait]:
        d = self.__traits.get(callable)
        if d is None:
            d = dict[str, Trait]()
            self.__traits[callable] = d
        return [e for e in d.values()]

    def put(self, callable:Callable, trait:Trait) -> None:
        d = self.__traits.get(callable)
        if d is None:
            d = dict[str,Trait]()
            self.__traits[callable] = d
        d[trait.name] = trait
