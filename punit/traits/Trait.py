# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT
##

from typing import Callable, Optional

from ..theories.TheoryManager import TheoryManager
from ..facts.FactManager import FactManager


class Trait:

    __name:str
    __value:str|None

    def __init__(self, name:str, value:str = None):
        self.__name = name
        self.__value = value

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def value(self) -> str|None:
        return self.__value


def trait(name:str, value:str=None) -> Callable:
    def wrapper(target:Callable) -> Callable:
        trait = Trait(name, value)
        TheoryManager.instance().withTrait(target, trait)
        FactManager.instance().withTrait(target, trait)
        return target
    return wrapper
