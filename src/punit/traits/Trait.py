# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT
##

from typing import Callable, Optional


class Trait:

    __name:str
    __value:str|None

    def __init__(self, name:str, value:Optional[str] = None):
        self.__name = name
        self.__value = value

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def value(self) -> str|None:
        return self.__value


def trait(name:str, value:Optional[str]=None) -> Callable:
    def wrapper(target:Callable) -> Callable:
        from ..theories.TheoryManager import TheoryManager
        from ..facts.FactManager import FactManager
        trait = Trait(name, value)
        TheoryManager.instance().withTrait(target, trait)
        FactManager.instance().withTrait(target, trait)
        return target
    return wrapper
